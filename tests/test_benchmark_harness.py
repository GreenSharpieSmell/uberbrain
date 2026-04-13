"""
tests/test_benchmark_harness.py
================================
Tests for the benchmark infrastructure itself.

Verifies that io.py, metrics.py, baselines.py, and adversarial.py
work correctly before trusting any results they produce.

License: CC0 — Public Domain
"""

from __future__ import annotations

import json
import math
import tempfile
from pathlib import Path

import numpy as np
import pytest

# ── Setup ─────────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT / "sim" / "benchmarks"))
sys.path.insert(0, str(ROOT / "sim"))

import bench_io
import bench_metrics
import bench_baselines
import adversarial as bench_adv


def _load_run_matrix():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "run_matrix_under_test",
        ROOT / "sim" / "benchmarks" / "run_matrix.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ─────────────────────────────────────────────────────────────────────────────
# io.py tests
# ─────────────────────────────────────────────────────────────────────────────

class TestIO:
    def test_make_run_dir_creates_directory(self, tmp_path):
        run_dir = bench_io.make_run_dir(str(tmp_path), "test_run_001")
        assert Path(run_dir).exists()
        assert Path(run_dir).is_dir()

    def test_save_config_writes_valid_json(self, tmp_path):
        bench_io.save_config(str(tmp_path), {"seed": 42, "trials": 100})
        config_path = tmp_path / "config.json"
        assert config_path.exists()
        with open(config_path) as f:
            data = json.load(f)
        assert data["seed"] == 42
        assert data["trials"] == 100
        assert "saved_at" in data
        assert "python" in data

    def test_save_metrics_csv_writes_all_rows(self, tmp_path):
        rows = [
            {"trial": 0, "ssim": 0.95, "label": 1},
            {"trial": 1, "ssim": 0.88, "label": 0},
        ]
        bench_io.save_metrics_csv(str(tmp_path), rows)
        csv_path = tmp_path / "metrics.csv"
        assert csv_path.exists()
        content = csv_path.read_text()
        assert "trial" in content
        assert "ssim" in content
        assert "0.95" in content

    def test_save_summary_json_writes_valid_json(self, tmp_path):
        summary = {
            "run_id":         "test_001",
            "overall_status": "PASS",
            "claims":         {"c1": {"status": "PASS"}},
        }
        bench_io.save_summary_json(str(tmp_path), summary)
        path = tmp_path / "summary.json"
        assert path.exists()
        with open(path) as f:
            data = json.load(f)
        assert data["overall_status"] == "PASS"

    def test_check_required_artifacts_detects_missing(self, tmp_path):
        artifacts = bench_io.check_required_artifacts(str(tmp_path))
        assert all(not v for v in artifacts.values())

    def test_make_run_id_returns_nonempty_string(self):
        run_id = bench_io.make_run_id("test")
        assert isinstance(run_id, str)
        assert len(run_id) > 0
        assert "test" in run_id


# ─────────────────────────────────────────────────────────────────────────────
# metrics.py tests
# ─────────────────────────────────────────────────────────────────────────────

class TestMetrics:
    def test_mean_empty(self):
        assert bench_metrics.mean([]) == 0.0

    def test_mean_single(self):
        assert bench_metrics.mean([5.0]) == 5.0

    def test_mean_values(self):
        assert abs(bench_metrics.mean([1.0, 2.0, 3.0]) - 2.0) < 1e-9

    def test_std_empty(self):
        assert bench_metrics.std([]) == 0.0

    def test_std_single(self):
        assert bench_metrics.std([42.0]) == 0.0

    def test_std_known(self):
        # std([2,4,4,4,5,5,7,9]) = 2.0 (population), ~2.138 (sample)
        result = bench_metrics.std([2, 4, 4, 4, 5, 5, 7, 9])
        assert abs(result - 2.138) < 0.01

    def test_percentile_median(self):
        values = list(range(1, 11))  # 1..10
        assert abs(bench_metrics.percentile(values, 50) - 5.5) < 0.01

    def test_percentile_min_max(self):
        values = [1.0, 2.0, 3.0, 4.0, 5.0]
        assert bench_metrics.percentile(values, 0)   == 1.0
        assert bench_metrics.percentile(values, 100) == 5.0

    def test_confidence_interval_contains_mean(self):
        rng    = np.random.default_rng(42)
        values = rng.normal(5.0, 1.0, 1000).tolist()
        lo, hi = bench_metrics.confidence_interval(values, 0.95)
        m      = bench_metrics.mean(values)
        assert lo < m < hi

    def test_roc_auc_perfect(self):
        y_true  = [0, 0, 0, 1, 1, 1]
        y_score = [0.1, 0.2, 0.3, 0.7, 0.8, 0.9]
        auc = bench_metrics.roc_auc(y_true, y_score)
        assert abs(auc - 1.0) < 0.01

    def test_roc_auc_random(self):
        rng     = np.random.default_rng(42)
        y_true  = rng.integers(0, 2, 200).tolist()
        y_score = rng.random(200).tolist()
        auc = bench_metrics.roc_auc(y_true, y_score)
        # Random classifier should be near 0.5
        assert 0.35 < auc < 0.65

    def test_roc_auc_degenerate_single_class(self):
        auc = bench_metrics.roc_auc([0, 0, 0], [0.1, 0.5, 0.9])
        assert auc == 0.5

    def test_ece_perfect_calibration(self):
        # Perfect calibration: score = actual frequency in each bin
        y_true  = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
        y_score = [0.05, 0.05, 0.05, 0.05, 0.05, 0.95, 0.95, 0.95, 0.95, 0.95]
        ece = bench_metrics.expected_calibration_error(y_true, y_score)
        assert ece < 0.1

    def test_fnr_all_caught(self):
        y_true = [1, 1, 1, 0, 0]
        y_pred = [1, 1, 1, 0, 0]
        assert bench_metrics.false_negative_rate(y_true, y_pred) == 0.0

    def test_fnr_all_missed(self):
        y_true = [1, 1, 1]
        y_pred = [0, 0, 0]
        assert bench_metrics.false_negative_rate(y_true, y_pred) == 1.0

    def test_precision_recall_f1(self):
        y_true = [1, 1, 1, 0, 0, 0]
        y_pred = [1, 1, 0, 0, 1, 0]
        prec, rec, f1 = bench_metrics.precision_recall_f1(y_true, y_pred)
        assert abs(prec - 2/3) < 0.01
        assert abs(rec  - 2/3) < 0.01

    def test_evaluate_gate_all_operators(self):
        assert bench_metrics.evaluate_gate(0.95, ">=", 0.90) is True
        assert bench_metrics.evaluate_gate(0.85, ">=", 0.90) is False
        assert bench_metrics.evaluate_gate(0.03, "<=", 0.05) is True
        assert bench_metrics.evaluate_gate(0.06, "<=", 0.05) is False
        assert bench_metrics.evaluate_gate(1.0,  ">",  0.9)  is True
        assert bench_metrics.evaluate_gate(0.9,  ">",  0.9)  is False


# ─────────────────────────────────────────────────────────────────────────────
# baselines.py tests
# ─────────────────────────────────────────────────────────────────────────────

class TestBaselines:
    def _make_graph(self, n=100):
        import networkx as nx
        import random
        random.seed(42)
        np.random.seed(42)
        G = nx.barabasi_albert_graph(n, 2, seed=42)
        cent = nx.degree_centrality(G)
        for node in G.nodes():
            G.nodes[node]["centrality"] = cent[node]
            G.nodes[node]["fidelity"]   = np.random.uniform(0.1, 1.0)
            G.nodes[node]["stale_time"] = np.random.uniform(0, 100)
        return G

    def test_mse_detector_clean_is_intact(self):
        img = np.ones((64, 64)) * 0.5
        assert bench_baselines.sim1_mse_detector(img, img) == 0

    def test_mse_detector_corrupted_is_degraded(self):
        clean  = np.zeros((64, 64))
        corrupt = np.ones((64, 64))
        assert bench_baselines.sim1_mse_detector(clean, corrupt) == 1

    def test_psnr_detector_clean_is_intact(self):
        img = np.ones((64, 64)) * 0.5
        assert bench_baselines.sim1_psnr_detector(img, img) == 0

    def test_psnr_detector_corrupted_is_degraded(self):
        clean   = np.zeros((64, 64))
        corrupt = np.ones((64, 64))
        assert bench_baselines.sim1_psnr_detector(clean, corrupt) == 1

    def test_age_only_returns_correct_count(self):
        G      = self._make_graph(100)
        budget = 20
        result = bench_baselines.sim3_age_only_policy(G, budget)
        assert len(result) == budget

    def test_age_only_returns_stalest_nodes(self):
        G      = self._make_graph(100)
        budget = 10
        result = bench_baselines.sim3_age_only_policy(G, budget)
        min_stale_in_result = min(G.nodes[n]["stale_time"] for n in result)
        max_stale_not_in    = max(
            G.nodes[n]["stale_time"] for n in G.nodes() if n not in result
        )
        assert min_stale_in_result >= max_stale_not_in - 1e-6

    def test_fidelity_only_returns_lowest_fidelity(self):
        G      = self._make_graph(100)
        budget = 10
        result = bench_baselines.sim3_fidelity_only_policy(G, budget)
        max_fidelity_in_result = max(G.nodes[n]["fidelity"] for n in result)
        min_fidelity_not_in    = min(
            G.nodes[n]["fidelity"] for n in G.nodes() if n not in result
        )
        assert max_fidelity_in_result <= min_fidelity_not_in + 1e-6

    def test_random_policy_returns_correct_count(self):
        G      = self._make_graph(100)
        result = bench_baselines.sim3_random_policy(G, 25, seed=42)
        assert len(result) == 25

    def test_regret_higher_for_hub_deletion(self):
        G    = self._make_graph(100)
        import networkx as nx
        cent = nx.degree_centrality(G)
        # High-centrality nodes = hubs
        hubs     = sorted(G.nodes(), key=lambda n: cent[n], reverse=True)[:5]
        leaves   = sorted(G.nodes(), key=lambda n: cent[n])[:5]
        r_hubs   = bench_baselines.sim3_compute_regret(G, hubs)
        r_leaves = bench_baselines.sim3_compute_regret(G, leaves)
        assert r_hubs > r_leaves


# ─────────────────────────────────────────────────────────────────────────────
# adversarial.py tests
# ─────────────────────────────────────────────────────────────────────────────

class TestAdversarial:
    def _make_hologram(self):
        rng = np.random.default_rng(42)
        H   = rng.uniform(0, 1, (64, 64))
        return (H - H.min()) / (H.max() - H.min())

    def test_structured_perturbation_changes_hologram(self):
        H      = self._make_hologram()
        H_pert = bench_adv.sim1_structured_perturbation(H, seed=42)
        assert not np.allclose(H, H_pert)

    def test_structured_perturbation_stays_in_range(self):
        H      = self._make_hologram()
        H_pert = bench_adv.sim1_structured_perturbation(H, seed=42)
        assert H_pert.min() >= 0.0
        assert H_pert.max() <= 1.0

    def test_phase_jitter_burst_changes_hologram(self):
        H      = self._make_hologram()
        H_pert = bench_adv.sim1_phase_jitter_burst(H, sigma=0.5, seed=42)
        assert not np.allclose(H, H_pert)
        assert H_pert.min() >= 0.0
        assert H_pert.max() <= 1.0

    def test_blur_plus_drop_reduces_peak(self):
        H      = self._make_hologram()
        H_pert = bench_adv.sim1_blur_plus_drop_patch(H, seed=42)
        # Blurring and zeroing should reduce or preserve max
        assert H_pert.max() <= H.max() + 0.01

    def test_threshold_drift_shifts_readings(self):
        readings = [0.4, 0.5, 0.6]
        drifted  = bench_adv.sim2_threshold_drift(readings, drift=0.1)
        for orig, shifted in zip(readings, drifted):
            assert abs(shifted - (orig + 0.1)) < 1e-6

    def test_threshold_drift_clips_to_range(self):
        readings = [0.95, 0.05]
        drifted  = bench_adv.sim2_threshold_drift(readings, drift=0.2)
        assert all(0.0 <= r <= 1.0 for r in drifted)

    def test_correlated_noise_changes_readings(self):
        readings = [0.38, 0.55, 0.72]
        noisy    = bench_adv.sim2_correlated_noise(readings, sigma=0.05, rho=0.8, seed=42)
        assert readings != noisy
        assert all(0.0 <= r <= 1.0 for r in noisy)

    def test_single_channel_failure_stuck_low(self):
        readings = [0.72, 0.38, 0.72]
        failed   = bench_adv.sim2_single_channel_failure(readings, 0, "stuck_low")
        assert failed[0] == 0.0
        assert failed[1] == readings[1]
        assert failed[2] == readings[2]

    def test_single_channel_failure_stuck_high(self):
        readings = [0.38, 0.38, 0.38]
        failed   = bench_adv.sim2_single_channel_failure(readings, 2, "stuck_high")
        assert failed[2] == 1.0

    def test_label_shift_changes_attributes(self):
        import networkx as nx
        G    = nx.barabasi_albert_graph(50, 2, seed=42)
        cent = nx.degree_centrality(G)
        np.random.seed(42)
        for n in G.nodes():
            G.nodes[n]["centrality"] = cent[n]
            G.nodes[n]["fidelity"]   = np.random.uniform(0.1, 1.0)
            G.nodes[n]["stale_time"] = np.random.uniform(0, 100)

        G_shifted = bench_adv.sim3_label_shift(G, shift_ratio=0.3, seed=42)
        # Some attributes should be different
        diffs = sum(
            1 for n in G.nodes()
            if G.nodes[n]["fidelity"] != G_shifted.nodes[n]["fidelity"]
        )
        assert diffs > 0

    def test_cascading_faults_modifies_state(self):
        H   = self._make_hologram()
        state = {
            "hologram":      H,
            "oomphlap_bits": [1, 0, 1],
            "ssim_score":    0.95,
        }
        faulted = bench_adv.sim4_cascading_faults(state, fault_rate=1.0, seed=42)
        # At least one field should change with fault_rate=1.0
        changed = (
            not np.allclose(faulted["hologram"], state["hologram"]) or
            faulted["oomphlap_bits"] != state["oomphlap_bits"] or
            faulted["ssim_score"] != state["ssim_score"]
        )
        assert changed


class TestRunMatrixClaimRigor:
    def test_restrict_config_to_claim_disables_other_claims(self):
        run_matrix = _load_run_matrix()
        config = {
            "claims": {
                "c1_sim1_verify": {"enabled": True},
                "c2_sim2_oomphlap": {"enabled": True},
                "c3_sim3_consolicant": {"enabled": True},
                "c4_sim4_pipeline": {"enabled": True},
            }
        }

        run_matrix.restrict_config_to_claim(config, "c4")

        assert config["claims"]["c1_sim1_verify"]["enabled"] is False
        assert config["claims"]["c2_sim2_oomphlap"]["enabled"] is False
        assert config["claims"]["c3_sim3_consolicant"]["enabled"] is False
        assert config["claims"]["c4_sim4_pipeline"]["enabled"] is True

    def test_c4_reports_all_ablations_and_failure_accounting(self):
        run_matrix = _load_run_matrix()
        rows = run_matrix.run_claim_c4({"run": {"seed": 42, "trials": 6}})
        summary = rows[-1]
        trial_row = rows[0]

        assert summary["claim"] == "c4_sim4_pipeline"
        assert summary["modeled_ablation_count"] == 3
        assert summary["declared_ablation_count"] == 3
        assert summary["all_ablations_modeled"] == 1.0
        assert "uplift_vs_modeled_ablations" in summary
        assert "pipeline_failure_rate" in summary
        assert "avg_hologram_diff_count" in summary
        assert "avg_hologram_missing_count" in summary
        assert "avg_hologram_missing_to_diff_ratio" in summary
        assert "avg_hologram_severity_score" in summary
        assert "avg_hologram_geometry_score" in summary
        assert "avg_hologram_largest_cluster_share" in summary
        assert "focus_source_missing_rate" in summary
        assert "avg_hologram_focus_boundary_share" in summary
        assert "avg_hologram_focus_interior_share" in summary
        assert "avg_hologram_threshold_gap_before_recovery" in summary
        assert "avg_hologram_threshold_gap_after_recovery" in summary
        assert "avg_hologram_threshold_gap_closed_fraction" in summary
        assert "avg_failed_hologram_threshold_gap_after_recovery" in summary
        assert "threshold_crossing_recovery_rate" in summary
        assert "avg_rewrite_recovery_delta" in summary
        assert "avg_correction_interior_rewrite_fraction" in summary
        assert "avg_correction_boundary_candidate_count" in summary
        assert "avg_correction_boundary_selected_count" in summary
        assert "avg_correction_interior_candidate_count" in summary
        assert "avg_correction_interior_rewrite_coverage_fraction" in summary
        assert "avg_correction_interior_rewrite_capture_rate" in summary
        assert "avg_correction_interior_selected_count" in summary
        assert "spillover_usage_rate" in summary
        assert "avg_correction_spillover_candidate_count" in summary
        assert "avg_correction_spillover_selected_count" in summary
        assert "avg_correction_spillover_coverage_fraction" in summary
        assert "avg_correction_spillover_capture_rate" in summary
        assert "avg_correction_spillover_fraction" in summary
        assert "residual_polish_usage_rate" in summary
        assert "avg_correction_residual_candidate_count" in summary
        assert "avg_correction_residual_selected_count" in summary
        assert "avg_correction_residual_coverage_fraction" in summary
        assert "avg_correction_residual_capture_rate" in summary
        assert "avg_correction_residual_fraction" in summary
        assert "avg_total_recovery_delta" in summary
        assert "avg_spillover_recovery_delta" in summary
        assert "avg_residual_recovery_delta" in summary
        assert "avg_oomphlap_initial_bit_error_count" in summary
        assert "avg_oomphlap_final_bit_error_count" in summary
        assert "avg_oomphlap_min_threshold_distance" in summary
        assert "avg_oomphlap_retry_max_attempts" in summary
        assert "avg_oomphlap_retry_attempts_used" in summary
        assert "avg_oomphlap_retry_targeted_success_rate" in summary
        assert "oomphlap_failed_channel_in_error_indices_rate" in summary
        assert "oomphlap_retry_candidate_source_failed_channel_rate" in summary
        assert "oomphlap_retry_candidate_source_error_indices_rate" in summary
        assert "oomphlap_verify_rate" in summary
        assert "oomphlap_verify_margin_trigger_rate" in summary
        assert "oomphlap_verify_channel_failure_trigger_rate" in summary
        assert "oomphlap_retry_targeted_strategy_rate" in summary
        assert "oomphlap_retry_margin_strategy_rate" in summary
        assert "oomphlap_retry_generic_strategy_rate" in summary
        assert "oomphlap_channel_failure_stuck_low_rate" in summary
        assert "oomphlap_channel_failure_stuck_high_rate" in summary
        assert "oomphlap_channel_failure_random_rate" in summary
        assert "oomphlap_retry_attempt_rate" in summary
        assert "oomphlap_retry_success_rate_given_attempt" in summary
        assert "avg_failed_oomphlap_retry_draw_minus_success_rate" in summary
        assert "block_dropout_success_rate" in summary
        assert "block_dropout_threshold_crossing_rate" in summary
        assert "failure_count_multi_stage" in summary
        assert "uplift_vs_no_consolidate_bleach" in summary
        assert "scenario_profile" in trial_row
        assert "stress_case" in trial_row
        assert "failure_detail_full" in trial_row
        assert "hologram_diff_count" in trial_row
        assert "hologram_missing_count" in trial_row
        assert "hologram_missing_to_diff_ratio" in trial_row
        assert "hologram_severity_score" in trial_row
        assert "hologram_geometry_score" in trial_row
        assert "hologram_focus_source" in trial_row
        assert "hologram_focus_boundary_share" in trial_row
        assert "hologram_focus_interior_share" in trial_row
        assert "hologram_threshold_gap_before_recovery" in trial_row
        assert "hologram_threshold_gap_after_recovery" in trial_row
        assert "hologram_threshold_gap_closed_fraction" in trial_row
        assert "hologram_threshold_crossed_after_recovery" in trial_row
        assert "hologram_largest_cluster_share" in trial_row
        assert "correction_attempts_used" in trial_row
        assert "correction_focus_strength" in trial_row
        assert "correction_rewrite_applied" in trial_row
        assert "correction_boundary_rewrite_fraction" in trial_row
        assert "correction_interior_rewrite_fraction" in trial_row
        assert "correction_rewrite_coverage_fraction" in trial_row
        assert "correction_boundary_candidate_count" in trial_row
        assert "correction_boundary_rewrite_coverage_fraction" in trial_row
        assert "correction_boundary_selected_count" in trial_row
        assert "correction_interior_rewrite_coverage_fraction" in trial_row
        assert "correction_boundary_rewrite_capture_rate" in trial_row
        assert "correction_interior_candidate_count" in trial_row
        assert "correction_interior_rewrite_capture_rate" in trial_row
        assert "correction_interior_selected_count" in trial_row
        assert "correction_spillover_polish_applied" in trial_row
        assert "correction_spillover_candidate_count" in trial_row
        assert "correction_spillover_selected_count" in trial_row
        assert "correction_spillover_coverage_fraction" in trial_row
        assert "correction_spillover_capture_rate" in trial_row
        assert "correction_spillover_fraction" in trial_row
        assert "correction_residual_polish_applied" in trial_row
        assert "correction_residual_candidate_count" in trial_row
        assert "correction_residual_selected_count" in trial_row
        assert "correction_residual_coverage_fraction" in trial_row
        assert "correction_residual_capture_rate" in trial_row
        assert "correction_residual_fraction" in trial_row
        assert "correction_rewrite_recovery_delta" in trial_row
        assert "correction_spillover_recovery_delta" in trial_row
        assert "correction_residual_recovery_delta" in trial_row
        assert "correction_total_recovery_delta" in trial_row
        assert "correction_best_stage" in trial_row
        assert "oomphlap_channel_failure" in trial_row
        assert "oomphlap_failed_channel" in trial_row
        assert "oomphlap_threshold_drift" in trial_row
        assert "oomphlap_correlated_noise_sigma" in trial_row
        assert "oomphlap_correlated_noise_rho" in trial_row
        assert "oomphlap_initial_bit_error_count" in trial_row
        assert "oomphlap_final_bit_error_count" in trial_row
        assert "oomphlap_min_threshold_distance" in trial_row
        assert "oomphlap_verify_flag" in trial_row
        assert "oomphlap_verify_trigger_margin" in trial_row
        assert "oomphlap_verify_trigger_channel_failure" in trial_row
        assert "oomphlap_retry_strategy" in trial_row
        assert "oomphlap_retry_candidate_source" in trial_row
        assert "oomphlap_retry_max_attempts" in trial_row
        assert "oomphlap_retry_candidate_count" in trial_row
        assert "oomphlap_failed_channel_in_error_indices" in trial_row
        assert "oomphlap_retry_targeted_success_rate" in trial_row
        assert "oomphlap_retry_attempted" in trial_row
        assert "oomphlap_retry_attempts_used" in trial_row
        assert "oomphlap_retry_succeeded" in trial_row
        assert "oomphlap_retry_draw_minus_success_rate" in trial_row
        assert summary["avg_hologram_diff_count"] >= summary["avg_hologram_missing_count"]
        assert 0.0 <= summary["focus_source_missing_rate"] <= 1.0
        assert 0.0 <= summary["oomphlap_retry_success_rate_given_attempt"] <= 1.0
        assert 0.0 <= summary["avg_oomphlap_retry_targeted_success_rate"] <= 0.995

    def test_c4_stress_suite_reports_named_adversarial_metrics(self):
        run_matrix = _load_run_matrix()
        rows = run_matrix.run_claim_c4({
            "run": {"seed": 42, "trials": 8},
            "adversarial_suite": {
                "enabled": True,
                "scenarios": {
                    "sim4": [
                        "oomphlap_threshold_drift",
                        "oomphlap_correlated_channel_noise",
                        "oomphlap_single_channel_failure",
                        "cascading_faults",
                        "partial_correction_failure",
                    ]
                },
            },
        })
        summary = rows[-1]
        stress_rows = [
            row
            for row in rows[:-1]
            if row.get("scenario_profile") == "stress"
        ]

        assert summary["stress_case_count"] == 5
        assert summary["stress_trials_per_case"] >= 4
        assert "stress_full_success_rate" in summary
        assert "stress_pipeline_failure_rate" in summary
        assert "stress_uplift_vs_no_verify" in summary
        assert "stress_failure_count_partial_hologram_correction_failure" in summary
        assert "stress_failure_count_oomphlap_retry_failed" in summary
        assert "stress_threshold_drift_usage_rate" in summary
        assert "stress_correlated_noise_usage_rate" in summary
        assert "stress_cascading_fault_usage_rate" in summary
        assert "stress_partial_correction_override_rate" in summary
        assert "stress_oomphlap_threshold_drift_success_rate" in summary
        assert "stress_oomphlap_correlated_channel_noise_success_rate" in summary
        assert "stress_oomphlap_single_channel_failure_success_rate" in summary
        assert "stress_cascading_faults_success_rate" in summary
        assert "stress_partial_correction_failure_success_rate" in summary
        assert stress_rows
        assert all(row["stress_case"] != "none" for row in stress_rows)
