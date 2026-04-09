"""
sim/benchmarks/metrics.py
=========================
Uberbrain Benchmark — Statistical Metrics

All metrics return scalars or simple structures.
Every function handles edge cases (empty input, degenerate distributions).

License: CC0 — Public Domain
"""

from __future__ import annotations

import math
from typing import Iterable


def mean(values: Iterable[float]) -> float:
    """Arithmetic mean. Returns 0.0 for empty input."""
    v = list(values)
    return sum(v) / len(v) if v else 0.0


def std(values: Iterable[float]) -> float:
    """Sample standard deviation (ddof=1). Returns 0.0 for < 2 values."""
    v = list(values)
    if len(v) < 2:
        return 0.0
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def percentile(values: Iterable[float], p: float) -> float:
    """
    p-th percentile via linear interpolation (matches numpy default).
    p in [0, 100].
    """
    v = sorted(values)
    if not v:
        return 0.0
    if len(v) == 1:
        return v[0]
    idx   = (p / 100) * (len(v) - 1)
    lo    = int(idx)
    hi    = min(lo + 1, len(v) - 1)
    frac  = idx - lo
    return v[lo] + frac * (v[hi] - v[lo])


def confidence_interval(
    values: Iterable[float], confidence: float = 0.95
) -> tuple[float, float]:
    """
    Bootstrap-free CI using normal approximation.
    Returns (lower, upper).

    For small N or non-normal distributions, use percentile CI instead.
    """
    v = list(values)
    if not v:
        return (0.0, 0.0)
    m = mean(v)
    s = std(v)
    n = len(v)

    # z-scores for common confidence levels
    z_table = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}
    z = z_table.get(confidence, 1.960)

    margin = z * s / math.sqrt(n) if n > 1 else 0.0
    return (m - margin, m + margin)


def roc_auc(y_true: list[int], y_score: list[float]) -> float:
    """
    Area Under the ROC Curve via trapezoidal rule.
    y_true: binary labels (0 or 1).
    y_score: continuous scores (higher = more likely positive).
    Returns AUC in [0, 1]. Returns 0.5 for degenerate input.
    """
    if len(y_true) != len(y_score) or not y_true:
        return 0.5
    if len(set(y_true)) < 2:
        return 0.5  # Only one class present

    # Sort by descending score
    pairs = sorted(zip(y_score, y_true), reverse=True)

    n_pos = sum(y_true)
    n_neg = len(y_true) - n_pos
    if n_pos == 0 or n_neg == 0:
        return 0.5

    tp = fp = 0
    prev_tp = prev_fp = 0
    auc = 0.0
    prev_score = None

    for score, label in pairs:
        if score != prev_score and prev_score is not None:
            # Trapezoidal contribution
            auc += (fp - prev_fp) * (tp + prev_tp) / 2
            prev_tp = tp
            prev_fp = fp
        if label == 1:
            tp += 1
        else:
            fp += 1
        prev_score = score

    auc += (fp - prev_fp) * (tp + prev_tp) / 2
    return auc / (n_pos * n_neg)


def expected_calibration_error(
    y_true: list[int], y_score: list[float], bins: int = 10
) -> float:
    """
    Expected Calibration Error (ECE).
    Measures how well predicted probabilities match actual frequencies.
    Lower is better. Perfect calibration = 0.0.
    """
    if not y_true or not y_score:
        return 0.0

    n      = len(y_true)
    bin_edges = [i / bins for i in range(bins + 1)]
    ece    = 0.0

    for b in range(bins):
        lo, hi = bin_edges[b], bin_edges[b + 1]
        # Include upper bound in last bin
        if b == bins - 1:
            indices = [i for i, s in enumerate(y_score) if lo <= s <= hi]
        else:
            indices = [i for i, s in enumerate(y_score) if lo <= s < hi]

        if not indices:
            continue

        bin_conf = mean([y_score[i] for i in indices])
        bin_acc  = mean([y_true[i]  for i in indices])
        ece     += (len(indices) / n) * abs(bin_conf - bin_acc)

    return ece


def false_negative_rate(y_true: list[int], y_pred: list[int]) -> float:
    """
    FNR = FN / (FN + TP).
    Returns 0.0 if no positive ground truth labels.
    """
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    return fn / (fn + tp) if (fn + tp) > 0 else 0.0


def precision_recall_f1(
    y_true: list[int], y_pred: list[int]
) -> tuple[float, float, float]:
    """Returns (precision, recall, f1)."""
    tp = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)
    fp = sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1)
    fn = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0)

    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec  = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1   = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    return prec, rec, f1


def bit_error_rate(y_true: list[int], y_pred: list[int]) -> float:
    """BER = number of bit errors / total bits."""
    if not y_true:
        return 0.0
    errors = sum(1 for t, p in zip(y_true, y_pred) if t != p)
    return errors / len(y_true)


def evaluate_gate(value: float, op: str, threshold: float) -> bool:
    """
    Evaluate a single pass/fail gate.
    op: one of ">", ">=", "<", "<=", "==", "!="
    """
    ops = {
        ">":  lambda v, t: v > t,
        ">=": lambda v, t: v >= t,
        "<":  lambda v, t: v < t,
        "<=": lambda v, t: v <= t,
        "==": lambda v, t: abs(v - t) < 1e-9,
        "!=": lambda v, t: abs(v - t) >= 1e-9,
    }
    if op not in ops:
        raise ValueError(f"Unknown operator: {op}")
    return ops[op](value, threshold)
