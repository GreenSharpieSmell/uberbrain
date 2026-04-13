# C4 Cascade Stabilization Pass - 2026-04-13

**Committed smoke run:** `results/20260413_96f30bf/`  
**Commit under test:** `96f30bf`  
**Analyzer:** Codex  
**Purpose:** Close the remaining `cascading_faults` hologram failures without loosening the benchmark.

---

## Executive read

This pass added a narrow new recovery stage for the hostile stress envelope:

- `cascade_stabilization`

It only fires after the normal repair stack has already run, only when `cascading_fault_rate > 0`, and only when the hologram is still below the fidelity threshold.

That changed the stress picture materially:

- committed smoke `full_success_rate = 1.0`
- committed smoke `stress_full_success_rate = 0.933333`
- committed smoke `stress_cascading_faults_success_rate = 1.0`
- committed smoke `stress_failure_count_partial_hologram_correction_failure = 0`
- committed smoke `stress_failure_count_oomphlap_retry_failed = 4`

So the cascade hole closed. The remaining stress failures are now mostly `oomphlap` retry failures, not optical repair failures.

---

## What changed

The previous adversarial read showed a very specific failure shape:

- local block-dropout repair was already recovering most of the damaged region
- residual polish was usually the best optical stage
- but a tiny residual tail still kept some cascade trials far below threshold

The new stage explicitly targets that tail by rewriting the highest residual diffs left after the normal repair sequence.

Telemetry was extended so the benchmark now records:

- whether `cascade_stabilization` fired
- how many residual candidates remained
- how many were rewritten
- coverage / capture fraction
- stage-specific recovery delta

This keeps the fix observable instead of silently blending it into `residual_polish`.

---

## What held up

The baseline path stayed untouched:

- smoke `full_success_rate` remained `1.0`
- ablation uplift remained `0.55`

The committed stress smoke also improved in the exact place we were targeting:

- `stress_cascading_faults_success_rate` moved to `1.0`
- `stress_failure_count_partial_hologram_correction_failure` dropped to `0`
- `stress_cascade_stabilization_usage_rate = 0.05`
- `stress_avg_cascade_recovery_delta = 0.034256`

That usage rate is low on purpose. The new stage is not carrying the baseline system; it is only stepping in on the narrow cascade tail.

---

## Wider sweep

Across a 5-seed x 50-trial quick sweep with the stress suite enabled:

- mean `full_success_rate = 1.0`
- mean `stress_full_success_rate = 0.94`
- min `stress_full_success_rate = 0.90`
- max `stress_full_success_rate = 0.966667`
- mean `stress_cascading_faults_success_rate = 0.933333`
- min `stress_cascading_faults_success_rate = 0.833333`
- max `stress_cascading_faults_success_rate = 1.0`

The failure mix from that wider sweep is now:

- `oomphlap_retry_failed = 14`
- `repair_backlog = 1`
- `verify_missed_oomphlap = 1`

That is a much healthier frontier than the previous mixed optical-plus-oomphlap failure surface.

---

## Practical conclusion

This pass did what it needed to do:

- it did not flatter the baseline
- it did close the targeted `cascading_faults` hologram gap
- it shifted the remaining adversarial red toward `oomphlap`

That means the next engineering target is clearer again:

- stress-harden `oomphlap` retry under threshold drift and correlated channel noise
- then revisit the one remaining graph-side `repair_backlog` outlier

---

## Bottom line

`cascading_faults` is no longer the sharpest remaining failure surface.

The repo now has a better adversarial story:

- optical cascade recovery is materially stronger
- the remaining stress envelope is mostly `oomphlap`
- the benchmark got more specific, not softer
