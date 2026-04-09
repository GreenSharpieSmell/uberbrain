"""
sim/benchmarks/adversarial.py
==============================
Uberbrain Benchmark — Adversarial Scenario Library

Implements adversarial perturbations for each simulation layer.
These are the "break it" tests — scenarios specifically designed to
expose failure modes and characterize the envelope of operation.

Each function returns a perturbed version of its input.
All perturbations are deterministic given a seed.

License: CC0 — Public Domain
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter


# ─────────────────────────────────────────────────────────────────────────────
# SIM 1 ADVERSARIAL — holographic perturbations
# ─────────────────────────────────────────────────────────────────────────────

def sim1_structured_perturbation(
    hologram: np.ndarray,
    seed: int = 42,
    stride: int = 16,
    patch_size: int = 3
) -> np.ndarray:
    """
    Structured perturbation: regular grid of zeroed patches.

    Adversarial goal: preserve global SSIM while destroying local structure.
    Grid patterns can fool global metrics because damage is distributed.

    The VERIFY command must detect this despite low global delta.
    """
    rng      = np.random.default_rng(seed)
    perturbed = hologram.copy()
    size      = hologram.shape[0]

    for y in range(0, size - patch_size, stride):
        for x in range(0, size - patch_size, stride):
            # Add small random offset to each patch location
            dy = rng.integers(-2, 3)
            dx = rng.integers(-2, 3)
            py = max(0, min(size - patch_size, y + dy))
            px = max(0, min(size - patch_size, x + dx))
            perturbed[py:py+patch_size, px:px+patch_size] = 0.0

    return perturbed


def sim1_phase_jitter_burst(
    hologram: np.ndarray,
    sigma: float = 0.15,
    seed: int = 42
) -> np.ndarray:
    """
    Phase jitter burst: spatially-correlated phase noise.

    Models a brief vibration event (truck passing, footstep, HVAC pulse).
    Unlike the smooth vibration model, this is a burst — localized in time,
    creating correlated damage in a spatial region.

    sigma: jitter amplitude in radians (0.15 rad ≈ 10nm at 405nm).
    """
    rng  = np.random.default_rng(seed)
    size = hologram.shape[0]

    # Spatially correlated noise (burst region)
    burst_center_x = rng.integers(size // 4, 3 * size // 4)
    burst_center_y = rng.integers(size // 4, 3 * size // 4)
    burst_radius   = rng.integers(size // 8, size // 4)

    noise = rng.normal(0, sigma, (size, size))
    noise = gaussian_filter(noise, sigma=burst_radius // 4)

    # Apply only within burst radius
    y_coords, x_coords = np.ogrid[:size, :size]
    dist_mask = ((x_coords - burst_center_x)**2 +
                 (y_coords - burst_center_y)**2) > burst_radius**2
    noise[dist_mask] = 0.0

    phase_field = np.exp(1j * noise)
    perturbed   = np.real(hologram.astype(complex) * phase_field)
    return np.clip(
        (perturbed - perturbed.min()) / (perturbed.max() - perturbed.min() + 1e-12),
        0, 1
    )


def sim1_blur_plus_drop_patch(
    hologram: np.ndarray,
    blur_sigma: float = 1.5,
    drop_fraction: float = 0.03,
    seed: int = 42
) -> np.ndarray:
    """
    Combined thermal blur + random patch drop.

    Models: ambient heat slowly relaxing quartz nanostructures (blur)
    combined with localized physical damage (drop).

    This is a realistic compound failure mode, not a clean single perturbation.
    """
    rng      = np.random.default_rng(seed)
    blurred  = gaussian_filter(hologram, sigma=blur_sigma)

    # Random patch drop
    perturbed = blurred.copy()
    size      = hologram.shape[0]
    n_drops   = int(drop_fraction * size * size / 16)  # 4x4 patches

    for _ in range(n_drops):
        x = rng.integers(0, size - 4)
        y = rng.integers(0, size - 4)
        perturbed[y:y+4, x:x+4] = 0.0

    return np.clip(perturbed, 0, 1)


# ─────────────────────────────────────────────────────────────────────────────
# SIM 2 ADVERSARIAL — oomphlap channel perturbations
# ─────────────────────────────────────────────────────────────────────────────

def sim2_threshold_drift(
    readings: list[float],
    drift: float = 0.05
) -> list[float]:
    """
    Shift all reflectivity readings by a constant drift.

    Models: slow DC bias in the photodiode amplifier, temperature-induced
    offset in the detection circuit, or systematic GST aging.

    drift > 0: readings shift up (crystalline more likely)
    drift < 0: readings shift down (amorphous more likely)
    """
    return [max(0.0, min(1.0, r + drift)) for r in readings]


def sim2_correlated_noise(
    readings: list[float],
    sigma: float = 0.03,
    rho: float = 0.7,
    seed: int = 42
) -> list[float]:
    """
    Correlated noise across channels.

    rho: correlation coefficient between channel noise terms (0=independent, 1=fully correlated)

    Models: common-mode noise from the laser driver, electromagnetic interference,
    or thermal fluctuations affecting all channels simultaneously.

    Uncorrelated noise (rho=0) is easier to reject. Correlated noise (rho→1)
    is the adversarial case — it shifts all channels together, making
    the combined state ambiguous.
    """
    rng = np.random.default_rng(seed)
    n   = len(readings)

    # Common-mode component
    common = rng.normal(0, sigma)
    # Independent component per channel
    indep  = rng.normal(0, sigma * np.sqrt(1 - rho**2), n)

    noisy = [
        max(0.0, min(1.0, r + rho * common + indep[i]))
        for i, r in enumerate(readings)
    ]
    return noisy


def sim2_single_channel_failure(
    readings: list[float],
    failed_channel: int = 0,
    failure_mode: str = "stuck_low"
) -> list[float]:
    """
    Simulate complete failure of one channel.

    failure_mode:
      "stuck_low"  — channel reads 0.0 always (dead sensor)
      "stuck_high" — channel reads 1.0 always (saturated sensor)
      "random"     — channel reads random noise (flapping sensor)

    This is the catastrophic case — one channel out of three is dead.
    The system must detect this via VERIFY and route to correction.
    """
    import random
    out = list(readings)
    if failure_mode == "stuck_low":
        out[failed_channel] = 0.0
    elif failure_mode == "stuck_high":
        out[failed_channel] = 1.0
    elif failure_mode == "random":
        out[failed_channel] = random.random()
    return out


# ─────────────────────────────────────────────────────────────────────────────
# SIM 3 ADVERSARIAL — memory graph perturbations
# ─────────────────────────────────────────────────────────────────────────────

def sim3_label_shift(
    graph,
    shift_ratio: float = 0.2,
    seed: int = 42
) -> object:
    """
    Randomly flip the stale/fidelity labels of shift_ratio fraction of nodes.

    Models: metadata corruption — the Consolicant's bookkeeping is wrong
    for some nodes. The triple-filter should be robust to moderate label noise.

    Returns a copy of the graph with perturbed attributes.
    """
    import random as _random
    import networkx as nx

    rng   = _random.Random(seed)
    G     = graph.copy()
    nodes = list(G.nodes())
    n_shift = int(len(nodes) * shift_ratio)
    to_shift = rng.sample(nodes, n_shift)

    for node in to_shift:
        # Flip stale_time across the threshold
        st = G.nodes[node].get("stale_time", 50)
        G.nodes[node]["stale_time"] = 100 - st

        # Flip fidelity across the threshold
        fi = G.nodes[node].get("fidelity", 0.5)
        G.nodes[node]["fidelity"] = 1.0 - fi

    return G


def sim3_non_scale_free_graph(n_nodes: int = 300, seed: int = 42):
    """
    Generate an Erdős-Rényi random graph (not scale-free).

    The Barabási-Albert model used in sim3 has preferential attachment,
    creating hubs. Erdős-Rényi has no hubs — more uniform degree distribution.

    The Consolicant must produce valid partitions on this topology.
    """
    import networkx as nx
    return nx.erdos_renyi_graph(n_nodes, 0.02, seed=seed)


def sim3_stale_fidelity_adversarial(
    graph,
    n_adversarial: int = 20,
    seed: int = 42
) -> object:
    """
    Inject adversarial nodes: high centrality + stale + degraded.

    These are hub nodes that are both important (high connectivity)
    AND look like bleach candidates (stale + degraded).

    The triple-filter must NOT bleach them because their centrality
    is above the orphan threshold. This is the hardest adversarial case.
    """
    import random as _random
    import networkx as nx

    rng   = _random.Random(seed)
    G     = graph.copy()

    # Find high-centrality nodes
    cent  = nx.degree_centrality(G)
    hubs  = sorted(G.nodes(), key=lambda n: cent[n], reverse=True)[:n_adversarial]

    for node in hubs:
        G.nodes[node]["stale_time"] = 99.0   # Very stale
        G.nodes[node]["fidelity"]   = 0.1    # Very degraded
        # centrality remains high — triple filter must protect them

    return G, hubs


# ─────────────────────────────────────────────────────────────────────────────
# SIM 4 ADVERSARIAL — pipeline-level perturbations
# ─────────────────────────────────────────────────────────────────────────────

def sim4_cascading_faults(
    state: dict,
    fault_rate: float = 0.1,
    seed: int = 42
) -> dict:
    """
    Inject random faults at multiple pipeline stages simultaneously.

    Models: correlated hardware failure (power fluctuation, EMI burst)
    that corrupts multiple layers at once rather than one at a time.

    state: dict with keys like 'hologram', 'oomphlap_bits', 'graph'
    Returns a perturbed copy of state.

    fault_rate: probability of fault at each stage (0=none, 1=all fail)
    """
    import random as _random
    rng  = _random.Random(seed)
    out  = dict(state)

    if "hologram" in out and rng.random() < fault_rate:
        noise = np.random.default_rng(seed).normal(0, 0.1, out["hologram"].shape)
        out["hologram"] = np.clip(out["hologram"] + noise, 0, 1)

    if "oomphlap_bits" in out and rng.random() < fault_rate:
        bits = list(out["oomphlap_bits"])
        flip_idx = rng.randint(0, len(bits) - 1)
        bits[flip_idx] = 1 - bits[flip_idx]
        out["oomphlap_bits"] = bits

    if "ssim_score" in out and rng.random() < fault_rate:
        # Corrupt the fidelity score itself
        out["ssim_score"] = max(0.0, out["ssim_score"] - rng.uniform(0.1, 0.4))

    return out


def sim4_partial_correction_failure(
    hologram_clean: np.ndarray,
    hologram_corrupted: np.ndarray,
    correction_success_rate: float = 0.7,
    seed: int = 42
) -> np.ndarray:
    """
    Model partial correction: write pulse succeeds on only some pixels.

    correction_success_rate: fraction of corrupted pixels actually fixed.
    1.0 = perfect correction, 0.0 = no correction at all.

    Returns hologram that is partially corrected — worse than clean
    but better than corrupted. Tests VERIFY's ability to detect
    incomplete correction and flag for re-attempt.
    """
    rng       = np.random.default_rng(seed)
    corrected = hologram_corrupted.copy()

    diff_mask = np.abs(hologram_clean - hologram_corrupted) > 0.1
    repair_mask = diff_mask & (rng.random(hologram_clean.shape) < correction_success_rate)
    corrected[repair_mask] = hologram_clean[repair_mask]

    return corrected
