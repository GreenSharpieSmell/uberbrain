# C4 Threshold-Crossing Update - 2026-04-13

**Run analyzed:** `results/20260413_838d9b3/`  
**Commit under test:** `838d9b3`  
**Analyzer:** Codex  
**Purpose:** Measure whether the new contiguous-region rewrite turns partial hologram recovery into actual threshold-crossing recovery.

---

## Executive read

The top-line result stayed unchanged:

- Full pipeline success rate: `0.55`
- `no_verify` success rate: `0.45`
- `no_correction_write` success rate: `0.45`
- `no_consolidate_bleach` success rate: `0.00`

But the benchmark can now answer a more specific question:

> does recovery actually push damaged holograms back across the fidelity threshold?

In this smoke run, the answer is still:

- `threshold_crossing_recovery_rate = 0.0`

That is important because it tells us the latest rewrite path improves the reconstruction, but not enough to convert failing hologram cases into passing ones.

---

## What the new telemetry says

Recovery metrics from `838d9b3`:

- `avg_first_pass_recovery_delta = 0.017169`
- `avg_rewrite_recovery_delta = 0.042964`
- `avg_second_pass_recovery_delta = 0.007712`
- `avg_total_recovery_delta = 0.067845`
- `rewrite_usage_rate = 0.3`
- `avg_correction_rewrite_fraction = 0.336853`
- `avg_correction_rewrite_coverage_fraction = 0.000725`

Interpretation:

- The contiguous rewrite is now the **largest** single source of measured recovery.
- The second pass still contributes, but less than the rewrite itself.
- Recovery is no longer dominated by small probabilistic nudges.

So this pass successfully changed the internal mechanism.
It just did not move the trials far enough to reach the success threshold.

---

## What stayed red

The failure picture remains:

- `failure_count_partial_hologram_correction_failure = 5`
- `failure_count_oomphlap_retry_failed = 3`
- `failure_count_multi_stage = 1`

And by perturbation family:

- `block_dropout_success_rate = 0.285714`
- `block_dropout_threshold_crossing_rate = 0.0`
- `distributed_dropout_success_rate = 0.500000`
- `distributed_dropout_threshold_crossing_rate = 0.0`
- `phase_noise_success_rate = 0.857143`
- `phase_noise_threshold_crossing_rate = 0.0`

Interpretation:

- The new rewrite path helps damaged holograms recover partially.
- It still does not salvage a single failed hologram all the way back to fidelity health in the smoke run.
- `block_dropout` remains the leading defect.

---

## Practical conclusion

This is another useful red result.

The repo can now say:

1. region-aware repair is real
2. contiguous rewrite is doing measurable work
3. the missing piece is no longer "do repairs help?"
4. the missing piece is "how do we turn partial geometric recovery into threshold-crossing recovery?"

That is a narrower and more actionable defect statement than before.

---

## Recommended next implementation pass

1. Measure boundary and interior recovery separately.
2. Add a stronger interior rewrite step for contiguous holes instead of rewriting only a narrow core.
3. Track "distance to threshold after recovery" so the benchmark can tell near-miss recovery from hopeless recovery.
4. Keep `block_dropout_threshold_crossing_rate` as the leading metric until it moves above zero.

---

## Bottom line

The benchmark is still red for the right reason.

The architecture is no longer failing because recovery is absent.
It is failing because recovery is still not strong enough to produce threshold-crossing salvage under clustered loss.
