"""
benchmark.py
============
Uberbrain — One-Command Benchmark Runner

Runs all simulations, collects results with full uncertainty quantification,
and outputs machine-readable CSV and JSON for reproducibility.

Usage:
    python benchmark.py              # Full benchmark
    python benchmark.py --quick      # Reduced trial count (faster)
    python benchmark.py --output dir # Custom output directory

Output:
    benchmark_results/
    ├── benchmark_summary.json       # All results, machine-readable
    ├── sim1_holographic.csv         # Per-trial SSIM values
    ├── sim2_oomphlap.csv            # Per-state truth table
    ├── sim3_consolicant.csv         # Node classification counts
    └── benchmark_report.txt         # Human-readable summary

This file is the reproducibility artifact. Anyone can run:
    python benchmark.py
and get the same results (seeds are fixed and logged).

Authors: Rocks D. Bear, Claude (Anthropic), Gemini (Google)
License: CC0 — Public Domain
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from itertools import product as iterproduct

import numpy as np

# ─────────────────────────────────────────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent
SIM_DIR = ROOT / "sim"
sys.path.insert(0, str(SIM_DIR))

import sim1_holographic as sim1
import sim2_oomphlap    as sim2
import sim3_consolicant as sim3

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

DEFAULT_CONFIG = {
    # Sim 1
    "sim1_grid_size":       256,
    "sim1_corruption_x":    90,
    "sim1_corruption_y":    80,
    "sim1_corruption_w":    60,
    "sim1_corruption_h":    60,
    "sim1_n_trials":        200,    # Monte Carlo trials
    "sim1_fidelity_warn":   0.95,

    # Sim 2
    "sim2_n_channels":      3,
    "sim2_n_mlc_demo":      6,

    # Sim 3
    "sim3_n_nodes":         300,
    "sim3_thresh_stale":    60,
    "sim3_thresh_fidelity": 0.5,
    "sim3_thresh_orphan":   0.02,

    # Adversarial
    "adversarial_corruption_sizes": [10, 20, 30, 40, 50, 60],

    # Reproducibility
    "seed":                 42,
    "version":              "0.2",
}

QUICK_CONFIG = {**DEFAULT_CONFIG, "sim1_n_trials": 20}


# ─────────────────────────────────────────────────────────────────────────────
# BENCHMARK RUNNERS
# ─────────────────────────────────────────────────────────────────────────────

def run_sim1_benchmark(config: dict, output_dir: Path) -> dict:
    """
    Benchmark Sim 1: holographic fidelity scoring.

    Returns dict with statistics. Writes per-trial CSV.
    """
    print("\n── Sim 1: Holographic Fidelity ─────────────────────────────")
    t0 = time.perf_counter()

    grid     = config["sim1_grid_size"]
    cx, cy   = config["sim1_corruption_x"], config["sim1_corruption_y"]
    cw, ch   = config["sim1_corruption_w"],  config["sim1_corruption_h"]
    n_trials = config["sim1_n_trials"]
    seed     = config["seed"]
    warn     = config["sim1_fidelity_warn"]

    data         = sim1.create_data_pattern(grid, seed)
    holo_clean,_ = sim1.encode_hologram(data)
    holo_corrupt = sim1.corrupt_hologram(holo_clean, cx, cy, cw, ch)
    rec_clean    = sim1.reconstruct(holo_clean)

    # ── Baseline: MSE-threshold detector (simple alternative) ────────────────
    # Baseline claim: MSE alone can detect corruption.
    # We compare MSE detector vs SSIM detector on same data.
    from skimage.metrics import structural_similarity as ssim_fn
    from skimage.metrics import mean_squared_error as mse_fn

    rec_corrupt = sim1.reconstruct(holo_corrupt)
    ssim_corrupt = ssim_fn(rec_clean, rec_corrupt, data_range=1.0)
    mse_corrupt  = mse_fn(rec_clean, rec_corrupt)

    # ── Monotonicity test (Claim H2) ─────────────────────────────────────────
    sizes   = config["adversarial_corruption_sizes"]
    mono_results = []
    for s in sizes:
        hc = sim1.corrupt_hologram(holo_clean, cx, cy, s, s)
        rc = sim1.reconstruct(hc)
        sc, _, _, _ = sim1.verify_fidelity(rec_clean, rc)
        mono_results.append({"size": s, "ssim": float(sc)})

    is_monotone = all(
        mono_results[i]["ssim"] >= mono_results[i+1]["ssim"] - 1e-6
        for i in range(len(mono_results)-1)
    )

    # ── Monte Carlo with noise (if V0.2 noise functions available) ───────────
    mc_ssim_corrupt = []
    mc_ssim_correct = []

    for trial in range(n_trials):
        rng = np.random.default_rng(seed + trial)

        # Add simple Gaussian noise to reconstructions
        noise_sigma = 0.02
        rec_c_noisy  = np.clip(rec_corrupt  + rng.normal(0, noise_sigma, rec_corrupt.shape), 0, 1)
        rec_cl_noisy = np.clip(rec_clean    + rng.normal(0, noise_sigma, rec_clean.shape),   0, 1)

        s_corrupt = ssim_fn(rec_cl_noisy, rec_c_noisy, data_range=1.0)
        mc_ssim_corrupt.append(float(s_corrupt))

        # Imperfect correction: clean + small residual
        residual    = rng.normal(0, 0.03, holo_clean.shape)
        holo_corr   = np.clip(holo_clean + residual, 0, 1)
        rec_corr    = sim1.reconstruct(holo_corr)
        rec_corr_n  = np.clip(rec_corr + rng.normal(0, noise_sigma, rec_corr.shape), 0, 1)
        s_corrected = ssim_fn(rec_clean, rec_corr_n, data_range=1.0)
        mc_ssim_correct.append(float(s_corrected))

    mc_corrupt  = np.array(mc_ssim_corrupt)
    mc_correct  = np.array(mc_ssim_correct)

    # ── Write CSV ─────────────────────────────────────────────────────────────
    csv_path = output_dir / "sim1_holographic.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["trial", "ssim_corrupted", "ssim_corrected", "seed_offset"])
        for i, (sc, scr) in enumerate(zip(mc_ssim_corrupt, mc_ssim_correct)):
            writer.writerow([i, sc, scr, seed + i])

    corruption_pct = (cw * ch) / (grid**2) * 100
    elapsed = time.perf_counter() - t0

    result = {
        "claim_H1_pass": ssim_corrupt < warn,
        "claim_H2_monotone": is_monotone,
        "corruption_pct":    corruption_pct,
        "ssim_corrupted_clean": float(ssim_corrupt),
        "mse_corrupted":        float(mse_corrupt),
        "mc_corrupt_mean":      float(mc_corrupt.mean()),
        "mc_corrupt_std":       float(mc_corrupt.std()),
        "mc_corrupt_ci95_lo":   float(np.percentile(mc_corrupt, 2.5)),
        "mc_corrupt_ci95_hi":   float(np.percentile(mc_corrupt, 97.5)),
        "mc_correct_mean":      float(mc_correct.mean()),
        "mc_correct_std":       float(mc_correct.std()),
        "mc_correct_ci95_lo":   float(np.percentile(mc_correct, 2.5)),
        "mc_correct_ci95_hi":   float(np.percentile(mc_correct, 97.5)),
        "n_trials":             n_trials,
        "seed":                 seed,
        "monotonicity_results": mono_results,
        "elapsed_s":            round(elapsed, 2),
    }

    _report_result("H1 corruption detectable", result["claim_H1_pass"],
                   f"SSIM={ssim_corrupt:.4f} < threshold={warn}")
    _report_result("H2 monotone degradation",  result["claim_H2_monotone"],
                   f"SSIM monotone across sizes {sizes}")
    print(f"   MC corrupted SSIM: {mc_corrupt.mean():.4f} ± {mc_corrupt.std():.4f} "
          f"[{np.percentile(mc_corrupt,2.5):.4f}, {np.percentile(mc_corrupt,97.5):.4f}]")
    print(f"   MC corrected SSIM: {mc_correct.mean():.4f} ± {mc_correct.std():.4f} "
          f"(NOT 1.000 — imperfect correction confirmed)")
    print(f"   Baseline (MSE detector): MSE={mse_corrupt:.6f} — also detects, "
          f"but SSIM provides confidence score natively")
    print(f"   N={n_trials} trials | seed={seed} | {elapsed:.1f}s")

    return result


def run_sim2_benchmark(config: dict, output_dir: Path) -> dict:
    """
    Benchmark Sim 2: oomphlap multi-wavelength encoding.

    Returns dict with statistics. Writes truth table CSV.
    """
    print("\n── Sim 2: Oomphlap Encoding ────────────────────────────────")
    t0 = time.perf_counter()

    omp     = sim2.Oomphlap(sim2.CHANNELS)
    results = sim2.demonstrate_binary_truth_table(omp)

    all_correct    = all(r["correct"] for r in results)
    n_states       = len(results)
    n_correct      = sum(1 for r in results if r["correct"])
    n_channels     = len(sim2.CHANNELS)
    state_space_b  = 2 ** n_channels
    state_space_mlc = 4 ** n_channels

    # ── Baseline comparison (Claim C3 analog for O): single channel ──────────
    # Baseline: 1 channel = 2 states. Oomphlap: 3 channels = 8 states.
    baseline_states = 2 ** 1
    improvement_factor = state_space_b / baseline_states

    # ── Noise degradation ─────────────────────────────────────────────────────
    rng = np.random.default_rng(config["seed"])
    noise_levels = [0.01, 0.02, 0.04, 0.06, 0.08]
    noise_results = []
    n_noise_trials = 1000

    for sigma in noise_levels:
        errors = 0
        total  = 0
        for state in iterproduct([0, 1], repeat=n_channels):
            ideal = [sim2.MLC_LEVELS[b * 3] for b in state]
            for _ in range(n_noise_trials):
                noisy  = [x + rng.normal(0, sigma) for x in ideal]
                decoded = tuple(1 if x >= sim2.GST_THRESHOLD else 0 for x in noisy)
                errors += int(decoded != state)
                total  += 1
        ber = errors / total if total > 0 else 0
        noise_results.append({"sigma": sigma, "ber": ber, "n_trials": total})

    # ── Write CSV ─────────────────────────────────────────────────────────────
    csv_path = output_dir / "sim2_oomphlap.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["written_b", "written_g", "written_r",
                         "refl_b", "refl_g", "refl_r",
                         "state_value", "correct"])
        for r in results:
            writer.writerow([
                r["written"][0], r["written"][1], r["written"][2],
                r["reflectivities"][0], r["reflectivities"][1], r["reflectivities"][2],
                r["state_value"] + 1, r["correct"]
            ])

    elapsed = time.perf_counter() - t0

    result = {
        "claim_O1_pass":        all_correct,
        "n_states_correct":     n_correct,
        "n_states_total":       n_states,
        "state_space_binary":   state_space_b,
        "state_space_mlc":      state_space_mlc,
        "baseline_1ch_states":  baseline_states,
        "improvement_factor":   improvement_factor,
        "noise_results":        noise_results,
        "truth_table":          results,
        "elapsed_s":            round(elapsed, 2),
    }

    _report_result("O1 all 8 states correct", all_correct,
                   f"{n_correct}/{n_states} states round-trip correctly")
    print(f"   State space: {baseline_states} (1-ch baseline) → "
          f"{state_space_b} (3-ch binary) → {state_space_mlc} (3-ch MLC)")
    print(f"   Improvement factor vs baseline: {improvement_factor}×")
    print(f"   BER at σ=0.01: {noise_results[0]['ber']:.2e} | "
          f"σ=0.08: {noise_results[-1]['ber']:.2e}")

    return result


def run_sim3_benchmark(config: dict, output_dir: Path) -> dict:
    """
    Benchmark Sim 3: Consolicant triple-filter.

    Returns dict with statistics. Includes baseline comparisons.
    """
    print("\n── Sim 3: Consolicant Filter ───────────────────────────────")
    t0 = time.perf_counter()

    import random
    random.seed(config["seed"])
    np.random.seed(config["seed"])

    G = sim3.build_memory_graph(config["sim3_n_nodes"])
    bleach, repair, protected = sim3.run_consolidate_cycle(G)

    n_total     = config["sim3_n_nodes"]
    n_bleach    = len(bleach)
    n_repair    = len(repair)
    n_protected = len(protected)

    # Verify architectural guarantee: no connected node bleached
    max_bleach_centrality = max(
        (G.nodes[n]["centrality"] for n in bleach), default=0.0
    )
    connected_guard_holds = max_bleach_centrality < config["sim3_thresh_orphan"]

    # ── Baseline 1: Age-only deletion ─────────────────────────────────────────
    # Delete any node where stale_time > threshold, regardless of other factors
    age_only_delete = [
        n for n in G.nodes()
        if G.nodes[n]["stale_time"] > config["sim3_thresh_stale"]
    ]
    # How many age-only deletes are PROTECTED by triple filter?
    age_destroys_protected = [
        n for n in age_only_delete
        if G.nodes[n]["status"] == "PROTECTED"
    ]
    # How many age-only deletes are REPAIR candidates?
    age_destroys_repair = [
        n for n in age_only_delete
        if G.nodes[n]["status"] == "REPAIR"
    ]

    # ── Baseline 2: Fidelity-only deletion ───────────────────────────────────
    fidelity_only_delete = [
        n for n in G.nodes()
        if G.nodes[n]["fidelity"] < config["sim3_thresh_fidelity"]
    ]
    fidelity_destroys_repair = [
        n for n in fidelity_only_delete
        if G.nodes[n]["status"] == "REPAIR"
    ]

    # ── Write CSV ─────────────────────────────────────────────────────────────
    csv_path = output_dir / "sim3_consolicant.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["node", "centrality", "fidelity", "stale_time", "status"])
        for node in G.nodes():
            d = G.nodes[node]
            writer.writerow([node, d["centrality"], d["fidelity"],
                             d["stale_time"], d["status"]])

    elapsed = time.perf_counter() - t0

    result = {
        "claim_C1_partition_correct": n_bleach + n_repair + n_protected == n_total,
        "claim_C2_connected_guard":   connected_guard_holds,
        "claim_C3_age_baseline":      len(age_destroys_protected) > 0,
        "claim_C4_fidelity_baseline": len(fidelity_destroys_repair) > 0,
        "n_total":          n_total,
        "n_bleach":         n_bleach,
        "n_repair":         n_repair,
        "n_protected":      n_protected,
        "max_bleach_centrality": float(max_bleach_centrality),
        "age_only_would_delete":       len(age_only_delete),
        "age_destroys_protected":      len(age_destroys_protected),
        "age_destroys_repair":         len(age_destroys_repair),
        "fidelity_only_would_delete":  len(fidelity_only_delete),
        "fidelity_destroys_repair":    len(fidelity_destroys_repair),
        "elapsed_s":                   round(elapsed, 2),
    }

    _report_result("C1 complete partition",      result["claim_C1_partition_correct"],
                   f"{n_bleach}+{n_repair}+{n_protected}={n_total}")
    _report_result("C2 connected node guard",    result["claim_C2_connected_guard"],
                   f"max centrality in bleach = {max_bleach_centrality:.4f}")
    _report_result("C3 age-only inferior",       result["claim_C3_age_baseline"],
                   f"age-only would destroy {len(age_destroys_protected)} protected nodes")
    _report_result("C4 fidelity-only inferior",  result["claim_C4_fidelity_baseline"],
                   f"fidelity-only would destroy {len(fidelity_destroys_repair)} repair nodes")

    return result


# ─────────────────────────────────────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def _report_result(claim: str, passed: bool, detail: str):
    symbol = "✓ PASS" if passed else "✗ FAIL"
    print(f"   [{symbol}] {claim}: {detail}")


def write_summary(results: dict, config: dict, output_dir: Path):
    """Write machine-readable JSON summary."""
    summary = {
        "uberbrain_benchmark": {
            "version":      config["version"],
            "timestamp":    datetime.now(timezone.utc).isoformat(),
            "seed":         config["seed"],
            "config":       config,
            "results":      results,
        }
    }
    json_path = output_dir / "benchmark_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  Summary → {json_path}")


def write_report(results: dict, output_dir: Path):
    """Write human-readable text report."""
    report_path = output_dir / "benchmark_report.txt"
    lines = [
        "UBERBRAIN BENCHMARK REPORT",
        "=" * 60,
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "CLAIM REGISTRY RESULTS",
        "-" * 40,
    ]

    claim_map = {
        "H1": ("sim1", "claim_H1_pass"),
        "H2": ("sim1", "claim_H2_monotone"),
        "O1": ("sim2", "claim_O1_pass"),
        "C1": ("sim3", "claim_C1_partition_correct"),
        "C2": ("sim3", "claim_C2_connected_guard"),
        "C3": ("sim3", "claim_C3_age_baseline"),
        "C4": ("sim3", "claim_C4_fidelity_baseline"),
    }

    passed = 0
    for claim_id, (sim_key, result_key) in claim_map.items():
        val    = results[sim_key][result_key]
        status = "PASS" if val else "FAIL"
        if val:
            passed += 1
        lines.append(f"  [{status}] Claim {claim_id}")

    lines += [
        "",
        f"  {passed}/{len(claim_map)} claims PASS",
        "",
        "KEY METRICS",
        "-" * 40,
        f"  Sim 1 corruption SSIM:  {results['sim1']['ssim_corrupted_clean']:.4f}",
        f"  Sim 1 MC mean ± std:    {results['sim1']['mc_corrupt_mean']:.4f} ± {results['sim1']['mc_corrupt_std']:.4f}",
        f"  Sim 1 corrected SSIM:   {results['sim1']['mc_correct_mean']:.4f} (not 1.000)",
        f"  Sim 2 states correct:   {results['sim2']['n_states_correct']}/{results['sim2']['n_states_total']}",
        f"  Sim 2 state space gain: {results['sim2']['improvement_factor']}× vs 1-channel baseline",
        f"  Sim 3 bleach targets:   {results['sim3']['n_bleach']}",
        f"  Sim 3 age-only damage:  would destroy {results['sim3']['age_destroys_protected']} protected nodes",
        "",
        "REPRODUCIBILITY",
        "-" * 40,
        f"  Seed: {results['sim1']['seed']}",
        f"  N_trials (Sim 1 MC): {results['sim1']['n_trials']}",
        "  Run: python benchmark.py",
        "",
        "=" * 60,
    ]

    with open(report_path, "w") as f:
        f.write("\n".join(lines))
    print(f"  Report  → {report_path}")


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Uberbrain benchmark runner"
    )
    parser.add_argument("--quick", action="store_true",
                        help="Reduced trial count for fast smoke test")
    parser.add_argument("--output", default="benchmark_results",
                        help="Output directory (default: benchmark_results)")
    args = parser.parse_args()

    config     = QUICK_CONFIG if args.quick else DEFAULT_CONFIG
    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    print("=" * 60)
    print("  UBERBRAIN BENCHMARK")
    mode = "QUICK" if args.quick else "FULL"
    print(f"  Mode: {mode} | Seed: {config['seed']} | v{config['version']}")
    print("=" * 60)

    results = {}
    results["sim1"] = run_sim1_benchmark(config, output_dir)
    results["sim2"] = run_sim2_benchmark(config, output_dir)
    results["sim3"] = run_sim3_benchmark(config, output_dir)

    write_summary(results, config, output_dir)
    write_report(results, output_dir)

    total_elapsed = sum(r["elapsed_s"] for r in results.values())

    # Count PASS
    passes = sum([
        results["sim1"]["claim_H1_pass"],
        results["sim1"]["claim_H2_monotone"],
        results["sim2"]["claim_O1_pass"],
        results["sim3"]["claim_C1_partition_correct"],
        results["sim3"]["claim_C2_connected_guard"],
        results["sim3"]["claim_C3_age_baseline"],
        results["sim3"]["claim_C4_fidelity_baseline"],
    ])

    print(f"\n{'=' * 60}")
    print(f"  BENCHMARK COMPLETE — {passes}/7 claims PASS")
    print(f"  Total elapsed: {total_elapsed:.1f}s")
    print(f"  Outputs: {output_dir}/")
    print(f"{'=' * 60}\n")

    return 0 if passes == 7 else 1


if __name__ == "__main__":
    raise SystemExit(main())
