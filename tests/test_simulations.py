import importlib.util
from itertools import product
from pathlib import Path

import numpy as np


def find_repo_root(start: Path) -> Path:
    """Find the repository root by locating sim/sim1_holographic.py upward."""
    candidates = [start] + list(start.parents)
    for candidate in candidates:
        if (candidate / "sim" / "sim1_holographic.py").exists():
            return candidate
    raise FileNotFoundError(
        "Could not find repo root containing sim/sim1_holographic.py"
    )


ROOT = find_repo_root(Path(__file__).resolve())


def load_module(name: str, relpath: str):
    path = ROOT / relpath
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


sim1 = load_module("sim1_holographic", "sim/sim1_holographic.py")
sim2 = load_module("sim2_oomphlap", "sim/sim2_oomphlap.py")
sim3 = load_module("sim3_consolicant", "sim/sim3_consolicant.py")
sim4 = load_module("sim4_pipeline", "sim/sim4_pipeline.py")


def test_sim1_corruption_triggers_degradation_at_default_region():
    data = sim1.create_data_pattern(sim1.GRID_SIZE, sim1.SEED)
    hologram_clean, _ = sim1.encode_hologram(data)
    reconstruction_clean = sim1.reconstruct(hologram_clean)

    hologram_corrupted = sim1.corrupt_hologram(
        hologram_clean,
        sim1.CORRUPTION_X,
        sim1.CORRUPTION_Y,
        sim1.CORRUPTION_W,
        sim1.CORRUPTION_H,
    )
    reconstruction_corrupted = sim1.reconstruct(hologram_corrupted)

    fidelity_ssim, _, status, _ = sim1.verify_fidelity(
        reconstruction_clean, reconstruction_corrupted
    )

    assert fidelity_ssim < sim1.FIDELITY_WARN
    assert "DEGRADED" in status


def test_sim1_larger_corruption_at_same_location_reduces_fidelity():
    data = sim1.create_data_pattern(sim1.GRID_SIZE, sim1.SEED)
    hologram_clean, _ = sim1.encode_hologram(data)
    reconstruction_clean = sim1.reconstruct(hologram_clean)

    center_x, center_y = 96, 96

    def ssim_for_square(square_size: int) -> float:
        hc = sim1.corrupt_hologram(
            hologram_clean, center_x, center_y, square_size, square_size
        )
        rc = sim1.reconstruct(hc)
        ssim_score, _, _, _ = sim1.verify_fidelity(reconstruction_clean, rc)
        return float(ssim_score)

    s_small = ssim_for_square(10)
    s_medium = ssim_for_square(25)
    s_large = ssim_for_square(40)

    assert s_small >= s_medium - 1e-6
    assert s_medium >= s_large - 1e-6


def test_sim2_truth_table_all_binary_states_round_trip_correct():
    oomphlap = sim2.Oomphlap(sim2.CHANNELS)
    results = sim2.demonstrate_binary_truth_table(oomphlap)

    assert len(results) == 2 ** len(sim2.CHANNELS)
    assert all(row["correct"] for row in results)


def test_sim2_noise_causes_nonzero_error_at_high_sigma():
    rng = np.random.default_rng(1)
    states = list(product([0, 1], repeat=3))

    def state_error_rate(sigma: float, trials: int = 1500) -> float:
        total = 0
        wrong = 0
        for s in states:
            ideal = [sim2.MLC_LEVELS[b * 3] for b in s]
            for _ in range(trials):
                noisy = [x + rng.normal(0.0, sigma) for x in ideal]
                read = tuple(1 if x >= sim2.GST_THRESHOLD else 0 for x in noisy)
                wrong += int(read != s)
                total += 1
        return wrong / total

    low_noise_error = state_error_rate(0.01)
    high_noise_error = state_error_rate(0.08)

    assert low_noise_error < 0.001
    assert high_noise_error > low_noise_error


def test_sim3_consolidation_partitions_every_node_and_bleach_rule_holds():
    graph = sim3.build_memory_graph(sim3.NUM_NODES)
    bleach, repair, protected = sim3.run_consolidate_cycle(graph)

    assert len(bleach) + len(repair) + len(protected) == sim3.NUM_NODES

    for node in bleach:
        data = graph.nodes[node]
        assert data["stale_time"] > sim3.THRESH_STALE
        assert data["fidelity"] < sim3.THRESH_FIDELITY
        assert data["centrality"] < sim3.THRESH_ORPHAN


def test_sim4_trial_reports_failure_fields():
    scenario = sim4.sample_pipeline_scenario(42)
    result = sim4.simulate_pipeline_trial(scenario)

    assert "overall_success" in result
    assert "failure_reason" in result
    assert "failure_detail" in result
    assert "graph_critical_ratio" in result
    assert "graph_repair_backlog_ratio" in result
    assert "hologram_damage_fraction" in result
    assert "hologram_missing_fraction" in result
    assert "hologram_severity_score" in result
    assert "hologram_geometry_score" in result
    assert "hologram_damage_cluster_count" in result
    assert "hologram_largest_cluster_share" in result
    assert "hologram_threshold_crossed_after_recovery" in result
    assert "correction_attempts_used" in result
    assert "correction_focus_strength" in result
    assert "correction_rewrite_applied" in result
    assert "correction_rewrite_coverage_fraction" in result
    assert "correction_rewrite_recovery_delta" in result
    assert "correction_total_recovery_delta" in result
    assert result["failure_reason"]
    assert result["failure_detail"]
    assert result["hologram_damage_fraction"] >= 0.0
    assert result["hologram_missing_fraction"] >= 0.0
    assert result["hologram_severity_score"] >= 0.0
    assert result["hologram_geometry_score"] >= 0.0
    assert result["hologram_damage_cluster_count"] >= 0
    assert 0.0 <= result["hologram_largest_cluster_share"] <= 1.0
    assert result["hologram_threshold_crossed_after_recovery"] in {0, 1}
    assert result["correction_attempts_used"] <= result["correction_attempts_planned"]
    assert result["correction_focus_strength"] >= 0.0
    assert result["correction_rewrite_applied"] in {0, 1}
    assert result["correction_rewrite_coverage_fraction"] >= 0.0
    assert result["correction_rewrite_recovery_delta"] >= 0.0
    assert result["correction_total_recovery_delta"] >= 0.0


def test_sim4_correction_path_never_lowers_best_hologram_score():
    scenario = sim4.sample_pipeline_scenario(42)
    scenario.update({
        "hologram_mode": "block_dropout",
        "corrupt_size": 46,
        "corrupt_x": 18,
        "corrupt_y": 18,
        "max_correction_passes": 2,
    })

    result = sim4.simulate_pipeline_trial(
        scenario,
        enable_verify=True,
        enable_correction_write=True,
        enable_consolidate_bleach=True,
    )

    assert result["ssim_after"] >= result["ssim_before"] - 1e-9
    assert result["correction_total_recovery_delta"] >= 0.0
    assert result["correction_rewrite_recovery_delta"] >= 0.0
    assert result["correction_second_pass_recovery_delta"] >= 0.0


def test_sim4_block_dropout_uses_contiguous_rewrite_when_repair_is_triggered():
    scenario = sim4.sample_pipeline_scenario(42)
    scenario.update({
        "hologram_mode": "block_dropout",
        "corrupt_size": 46,
        "corrupt_x": 18,
        "corrupt_y": 18,
        "max_correction_passes": 2,
    })

    result = sim4.simulate_pipeline_trial(
        scenario,
        enable_verify=True,
        enable_correction_write=True,
        enable_consolidate_bleach=True,
    )

    assert result["ssim_before"] < sim4.FIDELITY_WARN
    assert result["correction_rewrite_applied"] == 1
    assert result["correction_rewrite_coverage_fraction"] > 0.0
    assert result["correction_rewrite_recovery_delta"] >= 0.0


def test_sim4_block_dropout_geometry_is_more_clustered_than_distributed_dropout():
    block_scenario = sim4.sample_pipeline_scenario(42)
    block_scenario.update({
        "hologram_mode": "block_dropout",
        "corrupt_size": 40,
        "corrupt_x": 24,
        "corrupt_y": 24,
    })
    distributed_scenario = sim4.sample_pipeline_scenario(42)
    distributed_scenario.update({
        "hologram_mode": "distributed_dropout",
        "corrupt_size": 40,
        "distributed_stride": 12,
    })

    block = sim4.simulate_pipeline_trial(block_scenario)
    distributed = sim4.simulate_pipeline_trial(distributed_scenario)

    assert (
        block["hologram_largest_cluster_bbox_fraction"]
        >= distributed["hologram_largest_cluster_bbox_fraction"]
    )
    assert block["hologram_geometry_score"] >= distributed["hologram_geometry_score"]
    assert block["correction_focus_strength"] >= distributed["correction_focus_strength"]


def test_sim4_no_consolidate_worsens_graph_health_under_stress():
    scenario = sim4.sample_pipeline_scenario(123)
    scenario.update({
        "graph_cycles": 5,
        "graph_degrade_fraction": 0.24,
        "graph_fidelity_drop": 0.16,
        "graph_stale_increment": 20.0,
        "graph_adversarial_hubs": 16,
    })

    full = sim4.simulate_pipeline_trial(
        scenario,
        enable_verify=True,
        enable_correction_write=True,
        enable_consolidate_bleach=True,
    )
    no_consolidate = sim4.simulate_pipeline_trial(
        scenario,
        enable_verify=True,
        enable_correction_write=True,
        enable_consolidate_bleach=False,
    )

    assert full["graph_critical_ratio"] <= no_consolidate["graph_critical_ratio"] + 1e-9
    assert (
        full["graph_repair_backlog_ratio"]
        <= no_consolidate["graph_repair_backlog_ratio"] + 1e-9
    )
