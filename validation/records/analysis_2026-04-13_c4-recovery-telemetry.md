# C4 Recovery Telemetry Findings - 2026-04-13

**Run analyzed:** `results/20260413_c31d66c/`  
**Commit under test:** `c31d66c`  
**Analyzer:** Codex  
**Purpose:** Inspect the first severity-aware hologram recovery telemetry pass and rank what it says about the next defect.

---

## Executive read

The recovery-model patch did **not** improve the smoke-run top line.

- Full pipeline success rate: `0.55`
- `no_verify` success rate: `0.45`
- `no_correction_write` success rate: `0.45`
- `no_consolidate_bleach` success rate: `0.00`

That is useful.
It means the new instrumentation exposed more of the failure shape without flattering the result.

The important gain is not a better score.
It is that `C4` now tells us:

1. how often hologram correction actually fires
2. whether a second pass is being used
3. how much SSIM recovery those passes buy
4. which corruption family is still setting the ceiling

---

## What the new telemetry says

From `summary.json`:

- Average hologram damage fraction: `0.014322`
- Average hologram missing fraction: `0.000018`
- Average hologram severity score: `0.004021`
- Average correction attempts used: `0.6`
- Second-pass usage rate: `0.3`
- Average first-pass recovery delta: `0.0`
- Average second-pass recovery delta: `0.000844`
- Average total recovery delta: `0.000844`

Interpretation:

- Correction is not running on every trial, which is expected.
- When it does run, the **first pass is buying effectively nothing** at smoke-run scale.
- The small observed gain is coming almost entirely from the **second pass**.
- Even with that second pass, the average recovery gain is still tiny.

This is not evidence that the benchmark is wrong.
It is evidence that the present correction mechanism is too weak or too generic.

---

## Which corruption family still dominates

Mode-specific outcomes:

| Hologram mode | Success rate | Mean recovery delta |
|---|---:|---:|
| `block_dropout` | `0.285714` | `0.001866` |
| `distributed_dropout` | `0.500000` | `0.000638` |
| `phase_noise` | `0.857143` | `0.000000` |

Interpretation:

- `phase_noise` is mostly fine and does not need recovery to survive.
- `distributed_dropout` is mixed but not catastrophic.
- `block_dropout` remains the real cliff.

The second important nuance is that `block_dropout` does show the **largest** mean recovery delta, but its success rate is still terrible.

That means the current recovery path is nudging the right direction on localized loss, but not nearly hard enough to change the outcome envelope.

---

## What this rules out

At least for this pass, the main problem does **not** look like:

- "the severity score is too harsh"
- "the benchmark forgot to let recovery try"
- "all corruption modes are equally bad"

Why:

- The average severity score is extremely low (`0.004021`), so the rate math is not currently crushing recovery.
- Second passes are being exercised (`0.3` usage rate).
- The failure is concentrated in one mode family, not spread evenly.

So the stronger conclusion is:

> the current per-pixel probabilistic correction strategy is too weak for contiguous missing-region damage

This is a mechanism problem more than a thresholding problem.

---

## Ranked interpretation

### 1. Localized hole repair is still under-modeled

Evidence:

- `block_dropout_success_rate = 0.285714`
- `failure_count_partial_hologram_correction_failure = 5`
- first-pass recovery is effectively zero

Interpretation:

Contiguous missing information is not behaving like sparse noise.
The current correction model still treats repair too much like independent pixel restoration.

### 2. Second-pass behavior matters more than first-pass behavior

Evidence:

- `avg_first_pass_recovery_delta = 0.0`
- `avg_second_pass_recovery_delta = 0.000844`

Interpretation:

If recovery is going to matter, it currently matters only after a re-read / follow-up attempt.
That suggests the repo should treat multi-pass recovery as a first-class mechanism, not a light add-on.

### 3. Oomphlap is still the second bottleneck, not the first

Evidence:

- `failure_count_oomphlap_retry_failed = 3`
- hologram failures still outnumber oomphlap failures

Interpretation:

Oomphlap still needs work, but the next highest-value move remains localized hologram repair.

---

## Recommended next implementation pass

1. Replace pure independent-pixel repair with region-aware repair pressure.
2. Make correction probability depend on contiguous damage geometry, not just field-wide averages.
3. Track damaged-cluster size or bounding-box coverage in the trial metrics.
4. Keep the current telemetry fields so every repair change can be judged by:
   - success-rate shift
   - first-pass recovery delta
   - second-pass recovery delta
   - `block_dropout` success rate specifically

---

## Practical conclusion

This pass succeeded even though the top-line score did not move.

It converted "correction seems weak" into a tighter statement:

- the problem is primarily **localized missing-region repair**
- the current correction model is too generic
- the benchmark now has enough telemetry to measure whether the next repair model is genuinely better

That is exactly the kind of information we need if the project stance is "prove it can't work until the failures get smaller for real."
