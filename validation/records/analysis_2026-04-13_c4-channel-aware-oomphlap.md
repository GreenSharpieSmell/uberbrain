# C4 Channel-Aware Oomphlap Retry Findings - 2026-04-13

**Run analyzed:** `results/20260413_2a461db/`  
**Commit under test:** `2a461db`  
**Analyzer:** Codex  
**Purpose:** Replace generic oomphlap retry behavior with channel-aware retry planning and measure whether that shifts the real `C4` bottleneck.

---

## Executive read

This pass produced a real benchmark gain:

- Full pipeline success rate: `0.80` (up from `0.70`)
- `uplift_vs_no_verify = 0.35` (up from `0.25`)
- `uplift_vs_no_correction_write = 0.35` (up from `0.25`)

The claim still fails honestly because `min_success_rate >= 0.9` is still unmet.

But the failure split changed in a very useful way:

- `failure_count_partial_hologram_correction_failure = 3`
- `failure_count_oomphlap_retry_failed = 1`
- `failure_count_multi_stage = 0`

So the retry redesign worked well enough to move `oomphlap` out of the lead bottleneck position.

---

## What changed

The old retry path treated all oomphlap failures like one generic probabilistic retry.

This pass made retry behavior channel-aware:

- explicit `stuck_low` / `stuck_high` / `random` faults now use `targeted_channel_rewrite`
- margin-only ambiguity can use `margin_guard_rewrite`
- retry now targets the affected channel set instead of treating recovery like a blind global rewrite

The new telemetry shows that behavior is actually being exercised:

- `oomphlap_retry_targeted_strategy_rate = 0.4`
- `oomphlap_retry_margin_strategy_rate = 0.05`
- `avg_oomphlap_retry_targeted_success_rate = 0.393233`
- `oomphlap_retry_success_rate_given_attempt = 0.888889`

That last number is the most important one.

Under this smoke run, once retry actually fired, it succeeded on nearly 89% of attempts.

---

## What moved and what did not

### Oomphlap improved materially

Before this pass, direct oomphlap retry failure count in the smoke run was `3`.

Now it is `1`.

And the only remaining pure oomphlap failure in this smoke run was:

- trial `14`
- `channel_failure = stuck_high`
- `retry_strategy = targeted_channel_rewrite`
- `retry_targeted_success_rate = 0.953394`
- hologram gap after recovery = `0.0`

That means the remaining oomphlap miss was no longer a structural detection problem.
It was essentially a bad-luck miss against a very strong targeted retry.

### Hologram is now the dominant bottleneck again

The three remaining failing trials were:

- block-dropout hologram failure with successful targeted oomphlap retry
- block-dropout hologram failure with no oomphlap error to correct
- distributed-dropout hologram failure with successful targeted oomphlap retry

Their post-recovery hologram gaps were still substantial:

- `0.64168`
- `0.300545`
- `0.282505`

And the aggregate metric stayed harsh:

- `avg_failed_hologram_threshold_gap_after_recovery = 0.408243`

So the repo is now saying something much cleaner:

- oomphlap retry is no longer the main broad bottleneck
- the remaining red is mostly hard hologram recovery

---

## Practical conclusion

This pass successfully removed a major source of ambiguity.

The next best move is now very likely to go back to the hologram side and attack the hard residual misses directly:

1. isolate the remaining high-gap `block_dropout` cases
2. understand why the current repair path still leaves `0.28` to `0.64` threshold gaps
3. design the next reconstruction move for those hard failures specifically

Oomphlap is still worth monitoring, but it no longer looks like the first thing to optimize next.

---

## Bottom line

The channel-aware retry redesign did what we hoped:

- it improved `C4`
- it widened the uplift over disabled verification and correction
- it cut direct oomphlap retry failures down to one smoke-trial miss
- and it handed the bottleneck back to the remaining hard hologram failures

That is a clean scientific win even without crossing the `0.9` gate yet.
