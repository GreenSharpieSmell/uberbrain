# C4 Oomphlap And Hologram Gap Telemetry - 2026-04-13

**Run analyzed:** `results/20260413_cc8d9e3/`  
**Commit under test:** `cc8d9e3`  
**Analyzer:** Codex  
**Purpose:** Separate the remaining hologram shortfall from the `oomphlap` retry bottleneck and make both failure modes measurable.

---

## Executive read

The top line did not move in this pass:

- Full pipeline success rate: `0.70`
- `no_verify` success rate: `0.45`
- `no_correction_write` success rate: `0.45`
- `no_consolidate_bleach` success rate: `0.00`

That is fine. This pass was about removing ambiguity, not chasing a prettier number.

The new telemetry says two things clearly:

1. `oomphlap` is now one of the cleanest remaining bottlenecks.
2. The remaining direct hologram failures are fewer, but when they happen they are still not "almost fixed."

---

## Oomphlap read

The retry path is now measurable instead of opaque:

- `avg_oomphlap_initial_bit_error_count = 0.45`
- `avg_oomphlap_final_bit_error_count = 0.2`
- `oomphlap_verify_rate = 0.9`
- `oomphlap_verify_margin_trigger_rate = 0.1`
- `oomphlap_verify_channel_failure_trigger_rate = 0.85`
- `oomphlap_retry_attempt_rate = 0.45`
- `oomphlap_retry_success_rate_given_attempt = 0.555556`
- `avg_failed_oomphlap_retry_draw_minus_success_rate = 0.181292`

Interpretation:

- verify is firing on most hostile runs
- it is usually firing because of explicit channel-failure signatures, not because values are merely near the threshold
- once retry is attempted, it still fails almost half the time

The important structural clue is that this is not mostly a "borderline analog ambiguity" problem.
It is mostly a "known channel failure is detected, but the retry path is still too weak" problem.

---

## Hologram read

The recovery-gap telemetry sharpens the remaining hologram story:

- `avg_hologram_threshold_gap_before_recovery = 0.238285`
- `avg_hologram_threshold_gap_after_recovery = 0.061237`
- `avg_hologram_threshold_gap_closed_fraction = 0.223325`
- `avg_failed_hologram_threshold_gap_after_recovery = 0.408243`

Interpretation:

- the recovery path is closing part of the threshold deficit on average
- but the remaining direct hologram failures are still substantial misses, not tiny near-misses

The failed trial details reinforce that:

- direct hologram failures in this smoke run still had post-recovery gaps around `0.28` to `0.64`
- pure `oomphlap` failures often had `hologram_threshold_gap_after_recovery = 0.0`

So the repo is now saying:

- some hologram failures are still hard failures
- but several total pipeline failures are no longer hologram-limited at all

---

## Failure split in this smoke run

Counts:

- `failure_count_partial_hologram_correction_failure = 2`
- `failure_count_oomphlap_retry_failed = 3`
- `failure_count_multi_stage = 1`

Among the failing rows:

- three failures were pure `oomphlap_retry_failed` with no residual hologram gap
- one failure was mixed: `partial_hologram_correction_failure,oomphlap_retry_failed`
- two were direct hologram failures only

That means the next best move is no longer ambiguous.

---

## Practical conclusion

The next redesign target should be `oomphlap` first, specifically:

1. Make retry behavior channel-failure-aware instead of treating all retries like generic uncertainty.
2. Separate stuck-low/high recovery from random-channel recovery.
3. Keep the new retry-gap telemetry so any improvement has to show up as observed retry success, not a narrative.

The hologram path still matters, but its remaining failures now look like a smaller set of harder cases rather than the dominant broad bottleneck.

---

## Bottom line

This pass successfully split the remaining red into two different classes:

- `oomphlap` failures: frequent, explicit, and likely the best next optimization target
- hologram failures: fewer, but still materially far from threshold when they happen

That is a much better place to design from than "C4 still fails for assorted reasons."
