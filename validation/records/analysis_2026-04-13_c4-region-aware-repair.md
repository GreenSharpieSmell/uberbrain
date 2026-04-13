# C4 Region-Aware Repair Pass - 2026-04-13

**Run analyzed:** `results/20260413_d1cbb75/`  
**Commit under test:** `d1cbb75`  
**Analyzer:** Codex  
**Purpose:** Evaluate whether region-aware hologram repair changes the failure shape more usefully than the previous per-pixel-only correction path.

---

## Executive read

The headline stayed the same:

- Full pipeline success rate: `0.55`
- `no_verify` success rate: `0.45`
- `no_correction_write` success rate: `0.45`
- `no_consolidate_bleach` success rate: `0.00`

But the recovery behavior changed a lot.

The region-aware pass did **not** raise the smoke-run pass rate yet, but it did turn hologram correction from "basically no measured recovery" into a path that produces visible partial restoration under the same hostile scenarios.

That matters because it tells us the mechanism change is real even though the benchmark gate is still red.

---

## What changed in the telemetry

Current run (`d1cbb75`):

- `avg_first_pass_recovery_delta = 0.017169`
- `avg_second_pass_recovery_delta = 0.049896`
- `avg_total_recovery_delta = 0.067065`
- `block_dropout_recovery_delta = 0.112720`
- `distributed_dropout_recovery_delta = 0.092044`

Earlier recovery-telemetry baseline (`c31d66c`):

- `avg_first_pass_recovery_delta = 0.0`
- `avg_second_pass_recovery_delta = 0.000844`
- `avg_total_recovery_delta = 0.000844`
- `block_dropout_recovery_delta = 0.001866`
- `distributed_dropout_recovery_delta = 0.000638`

Interpretation:

- First-pass recovery is no longer dead.
- Second-pass recovery is now substantial instead of negligible.
- `block_dropout` is still the hardest mode, but the new correction path is now doing measurable work inside that mode.

So the repair model is no longer "telemetry with no actual motion."
It is now "real partial recovery that still fails to clear the success bar often enough."

---

## What stayed stubborn

The failure counts did not materially change:

- `failure_count_partial_hologram_correction_failure = 5`
- `failure_count_oomphlap_retry_failed = 3`
- `failure_count_multi_stage = 1`

And the mode split remains:

- `block_dropout_success_rate = 0.285714`
- `distributed_dropout_success_rate = 0.500000`
- `phase_noise_success_rate = 0.857143`

Interpretation:

- Region-aware repair improved recovery quality.
- It did **not** yet improve end-state success frequency.
- The missing-information cases are still usually recovering only partway.

That means the next bottleneck is no longer "does the repair attempt matter at all?"
We now know it does.

The next bottleneck is:

> how to convert partial geometric recovery into threshold-crossing recovery

---

## Why this is still a good result

This pass reduced uncertainty in a useful way.

Before this change, the repo could say:

- hologram repair is weak

After this change, the repo can say something more precise:

- region-aware repair produces meaningful partial SSIM recovery
- the current gain is still insufficient to flip most failing `block_dropout` cases into success
- the next iteration should target stronger region rewrite, not generic probability tuning

That is a better scientific position than "we tried something and the top line stayed red."

---

## Geometry signals now available

The benchmark now records geometry information for every `C4` trial:

- `avg_hologram_geometry_score = 0.687263`
- `avg_hologram_damage_cluster_count = 17.45`
- `avg_hologram_largest_cluster_share = 0.667372`
- `avg_hologram_largest_cluster_bbox_fraction = 0.008176`
- `avg_hologram_largest_cluster_fill_ratio = 0.746936`
- `avg_correction_focus_strength = 0.368891`

These are useful because they let us ask:

- did recovery improve because damage was easier?
- or because the repair mechanism got better for clustered loss?

With this pass, the answer is now measurable instead of hand-wavy.

---

## Recommended next implementation pass

1. Add a true region rewrite step for contiguous holes instead of only boosted per-pixel restoration.
2. Distinguish boundary recovery from interior recovery explicitly in the metrics.
3. Add a "threshold crossing after recovery" counter so the benchmark can tell partial improvement from full salvage.
4. Keep `block_dropout_success_rate` as the leading score for this defect until it moves.

---

## Practical conclusion

This pass is a win even with the same `0.55` top line.

It tells us:

- the new repair mechanism is doing real work
- the present ceiling is not "repair has no effect"
- the next missing piece is stronger contiguous-region reconstruction

That is exactly the kind of update a failure-first repo should want: the red stayed honest, but the mechanism underneath it got more legible.
