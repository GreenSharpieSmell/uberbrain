# C4 Boundary vs Interior Rewrite Telemetry - 2026-04-13

**Run analyzed:** `results/20260413_db51e1e/`  
**Commit under test:** `db51e1e`  
**Analyzer:** Codex  
**Purpose:** Separate clustered-damage boundary behavior from interior behavior and see whether the stronger interior rewrite is actually engaging.

---

## Executive read

The top line is unchanged again:

- Full pipeline success rate: `0.55`
- `no_verify` success rate: `0.45`
- `no_correction_write` success rate: `0.45`
- `no_consolidate_bleach` success rate: `0.00`

But the new telemetry closes another ambiguity.

The damage geometry now says the largest clustered-loss regions are not all boundary:

- `avg_hologram_focus_boundary_share = 0.640544`
- `avg_hologram_focus_interior_share = 0.359456`

So there is now a meaningful "interior" region in the accounting.

The key negative result is:

- `avg_correction_interior_rewrite_capture_rate = 0.0`
- `avg_correction_boundary_rewrite_capture_rate = 0.2`

Meaning:

> the rewrite policy is still not capturing any interior rewrite candidates in this smoke run, even after switching to bbox-based interior accounting

That is a sharper statement than we had before.

---

## What this tells us

### 1. The failure is not just "no interior region exists"

That was the open question before this pass.

Now we know:

- the bbox model exposes a real interior share
- but the actual rewrite still lands on boundary candidates only

So the next issue is not accounting.
It is the relationship between:

- the stored-field damage pattern
- the rewrite candidate definition
- the recovery mechanism itself

### 2. Recovery is still real, but still sub-threshold

Current recovery metrics:

- `avg_first_pass_recovery_delta = 0.017169`
- `avg_rewrite_recovery_delta = 0.042964`
- `avg_second_pass_recovery_delta = 0.007712`
- `avg_total_recovery_delta = 0.067845`
- `threshold_crossing_recovery_rate = 0.0`

So the repair path is still doing meaningful work.
It is just not doing it in a way that creates interior salvage or threshold-crossing rescue.

### 3. `block_dropout` remains the lead defect

- `block_dropout_success_rate = 0.285714`
- `block_dropout_recovery_delta = 0.115199`
- `block_dropout_threshold_crossing_rate = 0.0`

Interpretation:

`block_dropout` is still where the architecture breaks first.
The current rewrite path improves the damaged field, but still fails to restore enough structure for fidelity recovery.

---

## Practical conclusion

This pass successfully answered a design question:

- the interior accounting works
- the interior recovery still does not

That means the next model change should probably stop thinking in terms of "rewrite a subset of damaged pixels" and move toward:

- a region-level reconstruction move
- or a neighborhood interpolation / infill step
- or a reconstruction-space correction rather than only a hologram-space correction

Because at this point the repo has pretty good evidence that local rewrite targeting alone is not enough.

---

## Recommended next implementation pass

1. Add a region-level infill or interpolation step for clustered loss.
2. Measure whether interior recovery is absent because there are no interior diff candidates or because selection logic still rejects them.
3. Track reconstruction-space error inside the cluster bbox, not only hologram-space rewrite coverage.
4. Keep `block_dropout_threshold_crossing_rate` and `avg_correction_interior_rewrite_capture_rate` as lead metrics for this defect.

---

## Bottom line

This is useful red again.

The benchmark is now telling us:

- the cluster has an interior
- the rewrite still misses it
- partial recovery exists
- threshold-crossing recovery still does not

That is exactly the kind of narrowing we want before the next redesign step.
