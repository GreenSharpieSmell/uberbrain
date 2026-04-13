# C4 Adversarial Stress Envelope - 2026-04-13

**Committed smoke run:** `results/20260413_d596da6/`  
**Commit under test:** `d596da6`  
**Analyzer:** Codex  
**Purpose:** Expand `C4` beyond the now-clean baseline path by running a named adversarial stress suite against the full pipeline.

---

## Executive read

The baseline `C4` path is still clean:

- `full_success_rate = 1.0`
- `uplift_vs_no_verify = 0.55`
- standard smoke claim status = `PASS`

But the new adversarial stress suite is **not** clean, which is exactly why it was worth adding.

Across a 5-seed quick sweep with the stress suite enabled:

- mean `stress_full_success_rate = 0.876`
- min `stress_full_success_rate = 0.86`
- max `stress_full_success_rate = 0.88`
- mean `stress_uplift_vs_no_verify = 0.576`
- total stress `partial_hologram_correction_failure` count = `16`
- total stress `oomphlap_retry_failed` count = `12`

So the end-to-end system is still meaningfully better than the ablated path under adversarial pressure, but the broader envelope is no longer green.

That is progress.

---

## What changed

This pass promoted the adversarial suite from config text into actual `C4` execution.

New named stress cases now run through the full pipeline:

- `oomphlap_threshold_drift`
- `oomphlap_correlated_channel_noise`
- `oomphlap_single_channel_failure`
- `cascading_faults`
- `partial_correction_failure`

The scenario generator now supports:

- explicit threshold drift on `oomphlap` readout
- correlated channel noise
- stronger single-channel fault pressure
- cascading multi-layer degradation
- explicit partial-correction overrides on the hologram repair path

The benchmark records stress metrics separately from the standard `C4` summary so the regression gate remains legible.

---

## What held up

Some adversarial cases are already pretty strong:

- mean `stress_oomphlap_threshold_drift_success_rate` ranged from `0.8` to `1.0`
- mean `stress_oomphlap_correlated_channel_noise_success_rate` ranged from `0.8` to `1.0`
- mean `stress_oomphlap_single_channel_failure_success_rate` ranged from `0.9` to `1.0`
- `stress_partial_correction_failure_success_rate` was usually `1.0`, with one sampled `0.8`

So the system is not collapsing under every harsher condition.

---

## New bottleneck

The weakest adversarial case is now clearly `cascading_faults`.

Across the 5-seed quick sweep:

- mean `stress_cascading_faults_success_rate = 0.62`

That is substantially worse than the other named stress cases and lines up with the failure counts:

- `partial_hologram_correction_failure` still happens under compounded pressure
- `oomphlap_retry_failed` also reappears under compounded pressure

Interpretation:

- isolated perturbations are increasingly well handled
- compounded perturbations remain the real frontier

That is a much sharper failure story than “something somewhere still breaks.”

---

## Important framing

The standard `C4` pass/fail gate is still using the original baseline criteria.
The new stress metrics are not yet part of the pass/fail gate.

That is intentional for now:

- the baseline gate remains a regression check
- the stress suite is the new red-finding surface

If we decide to gate on stress metrics later, the threshold should be chosen deliberately and pre-registered before the next formal run.

---

## Practical conclusion

The repo is in a healthier state after this pass:

- the easy path is not the only path being measured anymore
- the benchmark now distinguishes standard success from adversarial robustness
- the next engineering target is much clearer: compounded pipeline stress, especially `cascading_faults`

---

## Bottom line

The project now has two useful truths at once:

- the current baseline `C4` path is strong
- the adversarial envelope still has real, repeatable failure space

That is the exact place a serious research repo should be: not flattering, but informative.
