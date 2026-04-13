# C4 Spillover Polish Pass - 2026-04-13

**Run analyzed:** `results/20260413_6fd4fc7/`  
**Commit under test:** `6fd4fc7`  
**Analyzer:** Codex  
**Purpose:** Add a final spillover-polish stage for hard hologram residuals after focus-region recovery is already complete.

---

## Executive read

This pass flipped `C4` to green in the smoke benchmark.

- Full pipeline success rate: `0.95`
- `uplift_vs_no_verify = 0.5`
- `uplift_vs_no_correction_write = 0.5`
- Overall `c4_sim4_pipeline` status: `PASS`

That means the benchmark is now passing honestly under the stricter failure-first harness that previously drove the score down to `0.55`.

---

## What changed

The residual analysis from the previous pass showed something important:

- the remaining hard hologram failures were no longer failing inside the focus region
- the focus region was already repaired
- the residual gap lived entirely in non-focus spillover structure

So this pass added a final `spillover_polish` stage:

- only after the earlier recovery stages had already run
- only when fidelity was still below threshold
- only on the residual non-focus error field
- targeting the highest-magnitude remaining residuals rather than doing a blind full rewrite

This was enough to close the last hard hologram misses in the smoke sample.

---

## What the benchmark says now

New key metrics:

- `full_success_rate = 0.95`
- `threshold_crossing_recovery_rate = 0.3`
- `spillover_usage_rate = 0.15`
- `avg_correction_spillover_candidate_count = 8.5`
- `avg_correction_spillover_selected_count = 4.25`
- `avg_correction_spillover_fraction = 0.058172`
- `avg_spillover_recovery_delta = 0.068634`

Interpretation:

- the new stage is not firing everywhere
- when it does fire, it acts on a small residual set
- that small cleanup step is enough to erase the remaining hologram failure class in this smoke run

---

## Failure split after the change

Counts:

- `failure_count_partial_hologram_correction_failure = 0`
- `failure_count_oomphlap_retry_failed = 1`
- `failure_count_multi_stage = 0`
- `avg_failed_hologram_threshold_gap_after_recovery = 0.0`

That is the cleanest result we have had so far.

There is only one failing smoke-trial left, and it is not hologram-related:

- trial `14`
- `failure_reason_full = oomphlap_retry_failed`
- `channel_failure = stuck_high`
- `retry_strategy = targeted_channel_rewrite`
- `retry_attempted = 1`
- `retry_succeeded = 0`
- `hologram_gap_after = 0.0`

So the current residual risk is now concentrated almost entirely in a single `oomphlap` retry miss type.

---

## Why this pass matters

This was not a return to soft or flattering benchmarking.

The benchmark still:

- fails missing evidence
- requires all declared ablations to be modeled
- compares against disabled verification/correction baselines
- records explicit failure reasons

The green result came after the benchmark was hardened, not before.

That makes this pass much more valuable than an early easy `PASS`.

---

## Practical conclusion

The repo now has a strong new baseline:

- hardened `C4` harness
- honest failure accounting
- channel-aware `oomphlap` retry
- residual spillover hologram cleanup
- smoke-pass at `0.95`

The next best move is probably a much narrower one:

1. attack the remaining `stuck_high` `oomphlap` retry miss type
2. run a wider non-smoke sweep to see whether the `0.95` smoke pass generalizes
3. keep watching whether spillover polish stays sparse and justified instead of becoming a hidden crutch

---

## Bottom line

This is the first real `C4` pass under the failure-first benchmark.

And the reason it passed is legible:

- focus recovery got strong enough
- `oomphlap` retry got smarter
- the last hard hologram misses were really spillover residuals
- a constrained spillover cleanup stage removed that failure class

That is exactly the kind of evidence trail we wanted this repo to produce.
