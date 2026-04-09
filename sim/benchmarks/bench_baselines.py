"""
sim/benchmarks/baselines.py
===========================
Uberbrain Benchmark — Baseline Comparison Policies

These are the "naive" alternatives that the Uberbrain architecture
must demonstrably outperform. Without baselines, claims are self-referential.

Baselines implemented:
  sim1_mse_detector      — simple MSE threshold (no SSIM, no fidelity model)
  sim1_psnr_detector     — PSNR threshold detector
  sim3_age_only_policy   — delete oldest nodes regardless of connectivity
  sim3_fidelity_only_policy — delete lowest-fidelity nodes regardless of connectivity
  sim3_random_policy     — random deletion (lower bound)

License: CC0 — Public Domain
"""

from __future__ import annotations

import math
import random as _random

import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# SIM 1 BASELINES — corruption detection
# ─────────────────────────────────────────────────────────────────────────────

def sim1_mse_detector(
    clean: np.ndarray,
    test: np.ndarray,
    threshold: float = 0.005
) -> int:
    """
    Detect corruption using Mean Squared Error.

    Baseline: no Fourier optics, no SSIM, just pixel-level MSE.
    Returns 1 (DEGRADED) if MSE > threshold, else 0 (INTACT).

    This is the simplest possible detector. SSIM must outperform it
    on ROC AUC to justify the more complex fidelity model.
    """
    mse = float(np.mean((clean.astype(float) - test.astype(float)) ** 2))
    return 1 if mse > threshold else 0


def sim1_psnr_detector(
    clean: np.ndarray,
    test: np.ndarray,
    threshold_db: float = 30.0
) -> int:
    """
    Detect corruption using Peak Signal-to-Noise Ratio.

    Returns 1 (DEGRADED) if PSNR < threshold_db, else 0 (INTACT).
    PSNR = 10 * log10(MAX^2 / MSE). Lower PSNR = more degradation.

    Baseline: classical image quality metric with no physics model.
    """
    mse = float(np.mean((clean.astype(float) - test.astype(float)) ** 2))
    if mse < 1e-12:
        return 0  # Perfect reconstruction
    max_val = 1.0  # Normalized images
    psnr    = 10 * math.log10(max_val ** 2 / mse)
    return 1 if psnr < threshold_db else 0


def sim1_random_detector(seed: int = 42) -> int:
    """
    Random detector — lower bound baseline.
    Should be beaten by any real detector. AUC ≈ 0.5.
    """
    rng = _random.Random(seed)
    return rng.randint(0, 1)


# ─────────────────────────────────────────────────────────────────────────────
# SIM 3 BASELINES — memory garbage collection policies
# ─────────────────────────────────────────────────────────────────────────────

def sim3_age_only_policy(graph, budget: int) -> list[int]:
    """
    Age-only deletion: remove the `budget` stalest nodes.

    This is the naive baseline. It ignores connectivity and fidelity,
    which means it will destroy old-but-vital hub memories.

    The triple-filter must demonstrate lower regret than this policy.
    """
    nodes_by_age = sorted(
        graph.nodes(),
        key=lambda n: graph.nodes[n].get("stale_time", 0),
        reverse=True   # Most stale first
    )
    return nodes_by_age[:budget]


def sim3_fidelity_only_policy(graph, budget: int) -> list[int]:
    """
    Fidelity-only deletion: remove the `budget` lowest-fidelity nodes.

    This ignores connectivity and staleness. It will destroy
    degraded-but-connected nodes that should be repaired, not bleached.

    The triple-filter must demonstrate lower regret than this policy.
    """
    nodes_by_fidelity = sorted(
        graph.nodes(),
        key=lambda n: graph.nodes[n].get("fidelity", 1.0)
        # Lowest fidelity first
    )
    return nodes_by_fidelity[:budget]


def sim3_random_policy(graph, budget: int, seed: int = 42) -> list[int]:
    """
    Random deletion: remove `budget` randomly chosen nodes.

    Lower bound baseline. The triple-filter must outperform random
    deletion on retained_value_score.
    """
    rng   = _random.Random(seed)
    nodes = list(graph.nodes())
    rng.shuffle(nodes)
    return nodes[:budget]


def sim3_compute_regret(
    graph,
    deleted_nodes: list[int],
    connectivity_weight: float = 1.0,
    fidelity_weight: float = 0.5
) -> float:
    """
    Compute regret for a deletion policy.

    Regret = sum over deleted nodes of:
      (centrality * connectivity_weight + fidelity * fidelity_weight)

    Higher centrality or fidelity in deleted nodes = more regret.
    Triple-filter should minimize regret by only deleting truly expendable nodes.
    """
    regret = 0.0
    for node in deleted_nodes:
        data        = graph.nodes[node]
        centrality  = data.get("centrality", 0.0)
        fidelity    = data.get("fidelity",   0.5)
        regret     += centrality * connectivity_weight + fidelity * fidelity_weight
    return regret


def sim3_compute_retained_value(
    graph,
    retained_nodes: list[int]
) -> float:
    """
    Compute value of retained nodes.

    Value = sum over retained nodes of (centrality * fidelity).
    High centrality + high fidelity = high value memory retained.
    """
    value = 0.0
    for node in retained_nodes:
        data = graph.nodes[node]
        value += data.get("centrality", 0.0) * data.get("fidelity", 0.5)
    return value
