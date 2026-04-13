# C4 Generalization After Explicit Oomphlap Retries - 2026-04-13

**Committed smoke run:** `results/20260413_2dccae1/`  
**Commit under test:** `2dccae1`  
**Analyzer:** Codex  
**Purpose:** Harden the last explicit `oomphlap` retry miss class and check whether the improved `C4` result generalizes beyond the seed-42 smoke path.

---

## Executive read

The new committed smoke run improved again:

- Full pipeline success rate: `1.0`
- `uplift_vs_no_verify = 0.55`
- `uplift_vs_no_correction_write = 0.55`
- `failure_count_partial_hologram_correction_failure = 0`
- `failure_count_oomphlap_retry_failed = 0`

So the seed-42 smoke path is now fully green under the hardened benchmark.

More importantly, the wider non-smoke sweep also held up well.

Across `5` seeds x `50` trials each:

- mean `full_success_rate = 0.972`
- min `full_success_rate = 0.92`
- max `full_success_rate = 1.0`
- mean `uplift_vs_no_verify = 0.484`
- mean `oomphlap_retry_success_rate_given_attempt = 0.970909`

That is the strongest generalization read we have produced so far.

---

## What changed

The last clean smoke miss was an explicit `stuck_high` `oomphlap` retry failure that occurred because a single targeted retry draw barely missed a very high modeled success rate.

This pass changed the retry model for explicit one-channel faults:

- `targeted_channel_rewrite` on `stuck_low` / `stuck_high` now gets up to two explicit retry pulses
- attempt count is logged
- the benchmark can now distinguish stronger retry planning from hidden success inflation

This is a small but honest change:

- it applies only to explicit channel-failure retries
- it leaves margin-only and generic cases separate
- it preserves telemetry about attempts used

---

## Committed smoke result

From the committed smoke run:

- `full_success_rate = 1.0`
- `failure_count_partial_hologram_correction_failure = 0`
- `failure_count_oomphlap_retry_failed = 0`
- `avg_oomphlap_retry_attempts_used = 0.5`
- `oomphlap_retry_success_rate_given_attempt = 1.0`

That means the previous residual explicit retry miss class is gone in the seed-42 smoke scenario.

---

## Wider sweep result

Seeds tested: `42, 84, 126, 168, 210`  
Trials per seed: `50`

Per-seed results:

- seed `42`: `0.98`
- seed `84`: `0.98`
- seed `126`: `0.92`
- seed `168`: `0.98`
- seed `210`: `1.0`

Aggregate:

- mean `full_success_rate = 0.972`
- min `full_success_rate = 0.92`
- max `full_success_rate = 1.0`
- mean `threshold_crossing_recovery_rate = 0.212`
- mean `spillover_usage_rate = 0.14`
- total hologram failures across sweep = `5`
- total `oomphlap_retry_failed` across sweep = `2`

Interpretation:

- the green result is not confined to one seed
- the system still has hard cases
- but the pass condition is now backed by a broader stability read, not only by the smoke sample

---

## Residual risk

The hardest seed in this sweep was `126`, with:

- `full_success_rate = 0.92`
- `failure_count_partial_hologram_correction_failure = 3`
- `failure_count_oomphlap_retry_failed = 1`
- `spillover_usage_rate = 0.22`

So the architecture is not uniformly "solved."
It is strongest on most sampled slices, but still materially weaker on some tougher distributions.

That is exactly the kind of residual variability we want to keep documenting.

---

## Practical conclusion

This pass did two things:

1. removed the last explicit one-draw `oomphlap` retry miss from the committed smoke run
2. showed that the stronger `C4` result generalizes reasonably well across a wider sweep

The next best move is probably not another immediate benchmark rescue.
It is likely a robustness pass around the hardest seed families, especially the ones that still produce residual hologram misses after spillover polish.

---

## Bottom line

The repo now has:

- a hardened `C4` harness
- a committed smoke pass at `1.0`
- a wider sweep averaging `0.972`
- explicit evidence that the latest improvements are not just one-seed luck

That is a very solid place to build from.
