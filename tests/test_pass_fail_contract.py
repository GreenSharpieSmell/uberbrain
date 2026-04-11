"""
tests/test_pass_fail_contract.py
=================================
Tests for the pass/fail evaluation contract.

Verifies that evaluate_pass_fail() behaves exactly as Codex specified:
- Parses every gate from YAML config
- Compares measured metric to threshold using configured operator
- Emits per-gate PASS/FAIL + reason
- Emits overall claim status and global run status
- Matches required summary.json schema

License: CC0 — Public Domain
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(ROOT / "sim" / "benchmarks"))

import bench_metrics


# ─────────────────────────────────────────────────────────────────────────────
# Test evaluate_gate (atomic unit)
# ─────────────────────────────────────────────────────────────────────────────

class TestEvaluateGate:
    """Unit tests for the atomic gate evaluation function."""

    def test_gte_pass(self):
        assert bench_metrics.evaluate_gate(0.95, ">=", 0.90) is True

    def test_gte_fail(self):
        assert bench_metrics.evaluate_gate(0.85, ">=", 0.90) is False

    def test_gte_exact(self):
        assert bench_metrics.evaluate_gate(0.90, ">=", 0.90) is True

    def test_lte_pass(self):
        assert bench_metrics.evaluate_gate(0.03, "<=", 0.05) is True

    def test_lte_fail(self):
        assert bench_metrics.evaluate_gate(0.06, "<=", 0.05) is False

    def test_lte_exact(self):
        assert bench_metrics.evaluate_gate(0.05, "<=", 0.05) is True

    def test_gt_strict_pass(self):
        assert bench_metrics.evaluate_gate(0.91, ">", 0.90) is True

    def test_gt_strict_fail_at_boundary(self):
        assert bench_metrics.evaluate_gate(0.90, ">", 0.90) is False

    def test_lt_strict(self):
        assert bench_metrics.evaluate_gate(0.04, "<", 0.05) is True
        assert bench_metrics.evaluate_gate(0.05, "<", 0.05) is False

    def test_invalid_operator_raises(self):
        with pytest.raises(ValueError):
            bench_metrics.evaluate_gate(0.5, "~~", 0.5)


# ─────────────────────────────────────────────────────────────────────────────
# Pass/fail contract tests (via simulate evaluate_pass_fail logic)
# ─────────────────────────────────────────────────────────────────────────────

def _build_config(gates: dict) -> dict:
    """Helper: build minimal config with one claim and given gates."""
    return {
        "claims": {
            "c1_test": {
                "enabled": True,
                "pass_fail": {
                    name: {"op": rule["op"], "value": rule["value"]}
                    for name, rule in gates.items()
                }
            }
        }
    }


def _build_summary(metrics: dict) -> dict:
    return {
        "run_id":  "test_run_001",
        "metrics": {"c1_test": metrics}
    }


def _evaluate(gates: dict, measured: dict) -> dict:
    """Run evaluate_pass_fail with synthetic config and summary."""
    sys.path.insert(0, str(ROOT / "sim" / "benchmarks"))
    # Import run_matrix evaluate_pass_fail
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "run_matrix",
        ROOT / "sim" / "benchmarks" / "run_matrix.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    config  = _build_config(gates)
    summary = _build_summary(measured)
    return mod.evaluate_pass_fail(config, summary)


class TestPassFailContract:

    def test_all_gates_pass_overall_pass(self):
        result = _evaluate(
            gates={"roc_auc": {"op": ">=", "value": 0.90},
                   "fnr":     {"op": "<=", "value": 0.05}},
            measured={"roc_auc": 0.95, "fnr": 0.03}
        )
        assert result["overall_status"] == "PASS"

    def test_one_gate_fails_overall_fail(self):
        result = _evaluate(
            gates={"roc_auc": {"op": ">=", "value": 0.90},
                   "fnr":     {"op": "<=", "value": 0.05}},
            measured={"roc_auc": 0.95, "fnr": 0.08}  # fnr fails
        )
        assert result["overall_status"] == "FAIL"

    def test_all_gates_fail_overall_fail(self):
        result = _evaluate(
            gates={"roc_auc": {"op": ">=", "value": 0.90},
                   "fnr":     {"op": "<=", "value": 0.05}},
            measured={"roc_auc": 0.80, "fnr": 0.10}
        )
        assert result["overall_status"] == "FAIL"

    def test_per_gate_status_in_result(self):
        result = _evaluate(
            gates={"roc_auc": {"op": ">=", "value": 0.90}},
            measured={"roc_auc": 0.95}
        )
        gates = result["claims"]["c1_test"]["gates"]
        assert "roc_auc" in gates
        assert gates["roc_auc"]["status"] == "PASS"

    def test_failing_gate_has_fail_status(self):
        result = _evaluate(
            gates={"roc_auc": {"op": ">=", "value": 0.90}},
            measured={"roc_auc": 0.80}
        )
        gates = result["claims"]["c1_test"]["gates"]
        assert gates["roc_auc"]["status"] == "FAIL"

    def test_gate_includes_reason_string(self):
        result = _evaluate(
            gates={"roc_auc": {"op": ">=", "value": 0.90}},
            measured={"roc_auc": 0.95}
        )
        gate = result["claims"]["c1_test"]["gates"]["roc_auc"]
        assert isinstance(gate["reason"], str)
        assert len(gate["reason"]) > 0

    def test_gate_includes_measured_value(self):
        result = _evaluate(
            gates={"roc_auc": {"op": ">=", "value": 0.90}},
            measured={"roc_auc": 0.95}
        )
        gate = result["claims"]["c1_test"]["gates"]["roc_auc"]
        assert abs(gate["measured"] - 0.95) < 1e-9

    def test_missing_metric_is_fail_not_skip(self):
        result = _evaluate(
            gates={"roc_auc":      {"op": ">=", "value": 0.90},
                   "missing_metric": {"op": ">=", "value": 0.50}},
            measured={"roc_auc": 0.95}  # missing_metric not in measured
        )
        gates = result["claims"]["c1_test"]["gates"]
        assert gates["missing_metric"]["status"] == "FAIL"
        assert result["claims"]["c1_test"]["status"] == "FAIL"
        assert result["overall_status"] == "FAIL"

    def test_all_missing_metrics_fail_claim(self):
        result = _evaluate(
            gates={"roc_auc": {"op": ">=", "value": 0.90}},
            measured={}
        )
        gate = result["claims"]["c1_test"]["gates"]["roc_auc"]
        assert gate["status"] == "FAIL"
        assert gate["measured"] is None
        assert result["claims"]["c1_test"]["status"] == "FAIL"
        assert result["overall_status"] == "FAIL"

    def test_summary_json_schema_matches_codex_spec(self):
        """
        Verify the output matches Codex's required schema:
        {
          "run_id": "...",
          "git_sha": "...",
          "claims": {
            "c1_test": {
              "metrics": {...},
              "gates": {...},
              "status": "PASS" | "FAIL"
            }
          },
          "overall_status": "PASS" | "FAIL"
        }
        """
        result = _evaluate(
            gates={"roc_auc": {"op": ">=", "value": 0.90}},
            measured={"roc_auc": 0.95}
        )

        assert "run_id"         in result
        assert "git_sha"        in result
        assert "claims"         in result
        assert "overall_status" in result
        assert result["overall_status"] in ("PASS", "FAIL")

        claim = result["claims"]["c1_test"]
        assert "metrics" in claim
        assert "gates"   in claim
        assert "status"  in claim
        assert claim["status"] in ("PASS", "FAIL")

        gate = claim["gates"]["roc_auc"]
        assert "status"    in gate
        assert "reason"    in gate
        assert "measured"  in gate
        assert "threshold" in gate
        assert "op"        in gate

    def test_disabled_claim_not_evaluated(self):
        sys.path.insert(0, str(ROOT / "sim" / "benchmarks"))
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "run_matrix2",
            ROOT / "sim" / "benchmarks" / "run_matrix.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        config = {
            "claims": {
                "c1_disabled": {
                    "enabled": False,
                    "pass_fail": {"roc_auc": {"op": ">=", "value": 0.90}}
                }
            }
        }
        summary = {"run_id": "test", "metrics": {"c1_disabled": {"roc_auc": 0.50}}}
        result  = mod.evaluate_pass_fail(config, summary)

        # Disabled claims should not appear in results
        assert "c1_disabled" not in result.get("claims", {})
        # Overall should still pass (no enabled claims failed)
        assert result["overall_status"] == "PASS"
