# C4 Hard-Seed Robustness After Residual Polish - 2026-04-13

**Committed smoke run:** `results/20260413_f203893/`  
**Commit under test:** `f203893`  
**Analyzer:** Codex  
**Purpose:** Harden the remaining hard-seed hologram failures without loosening the `C4` benchmark.

---

## Executive read

The residual-polish pass improved the hard floor without changing the benchmark gates.

Committed smoke result:

- `full_success_rate = 1.0`
- `uplift_vs_no_verify = 0.55`
- `failure_count_partial_hologram_correction_failure = 0`
- `failure_count_oomphlap_retry_failed = 0`

Wider sweep across `5` seeds x `50` trials:

- mean `full_success_rate = 0.992`
- min `full_success_rate = 0.98`
- max `full_success_rate = 1.0`
- mean `uplift_vs_no_verify = 0.504`
- total partial hologram failures across sweep = `0`
- total `oomphlap_retry_failed` across sweep = `2`

That means the residual hard cases are no longer hologram-repair misses.
They are now concentrated in `oomphlap` retry behavior.

---

## What changed

The previous sweep showed a consistent pattern:

- the remaining hologram misses were mostly low-severity `distributed_dropout`
- `spillover_polish` was already the best correction stage in those failures
- but it still only rewrote about half of the residual damage, leaving the trial below the SSIM threshold

This pass added one more correction stage after spillover:

- `residual_polish`

It is intentionally constrained:

- it only runs if the hologram is still below threshold after first pass, rewrite, second pass, and spillover
- it targets the remaining global residual error rather than only the non-focus tail
- it logs its own usage, coverage, capture rate, score, and recovery delta

So this is not a hidden loosening of the benchmark.
It is a new modeled repair step with explicit telemetry.

---

## Why this looks honest

The new stage is not being used everywhere.

Across the 5-seed sweep:

- mean `residual_polish_usage_rate = 0.02`
- mean `avg_residual_recovery_delta = 0.006621`

That means the pass is acting like a targeted cleanup stage, not a blanket “rewrite everything until it turns green” move.

It activates rarely, but when it does, it closes the remaining hologram gap that spillover alone was leaving open.

---

## Hard-seed impact

Before this pass, the wider sweep had:

- `5` partial hologram correction failures
- `2` `oomphlap` retry failures

After this pass, the same sweep now has:

- `0` partial hologram correction failures
- `2` `oomphlap` retry failures

The hardest previously observed seed family (`126`) moved from `0.92` to `0.98`.

That is the exact kind of robustness improvement we wanted:

- the floor moved up
- the benchmark stayed strict
- the remaining failure class got simpler

---

## Practical conclusion

`C4` is now in a better falsifiability state than before:

- hologram recovery no longer appears to be the limiting factor on the sampled hard seeds
- residual failures now point much more cleanly at `oomphlap`
- future work can focus on the remaining retry misses instead of mixing optical and channel-side failure classes together

---

## Bottom line

The repo now has:

- a committed `C4` smoke pass at `1.0`
- a wider sweep averaging `0.992`
- zero sampled partial hologram correction failures in that sweep
- explicit telemetry showing that residual polish is targeted, not blanket

That is a strong robustness step, and it makes the next bottleneck much easier to see.
