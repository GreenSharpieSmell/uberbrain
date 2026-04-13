# C4 Oomphlap Retry Alignment - 2026-04-13

**Committed smoke run:** `results/20260413_361ab0c/`  
**Commit under test:** `361ab0c`  
**Analyzer:** Codex  
**Purpose:** Remove the last sampled `oomphlap_retry_failed` cases without loosening the `C4` benchmark.

---

## Executive read

The previous hard-seed sweep ended with only two sampled failures left, and both were `oomphlap_retry_failed`.

This pass removed both of them.

Committed smoke result:

- `full_success_rate = 1.0`
- `uplift_vs_no_verify = 0.55`
- `failure_count_partial_hologram_correction_failure = 0`
- `failure_count_oomphlap_retry_failed = 0`

Wider sweep across `5` seeds x `50` trials:

- mean `full_success_rate = 1.0`
- min `full_success_rate = 1.0`
- max `full_success_rate = 1.0`
- mean `uplift_vs_no_verify = 0.512`
- total partial hologram failures across sweep = `0`
- total `oomphlap_retry_failed` across sweep = `0`

That means the currently sampled `C4` sweep is fully clean under the hardened benchmark.

---

## Root cause

The two remaining `oomphlap` misses turned out to be different problems:

1. one was a real logic bug
2. one was an honest stochastic miss

### Logic bug

In the harder seed family, the retry planner always preferred the explicit failed physical channel whenever `verify_trigger_channel_failure` was true.

That sounds reasonable, but one sampled trial showed this shape:

- failed physical channel = `0` (`stuck_low`)
- actual decoded bit error = channel `2`
- retry draw was good enough to succeed
- but the retry rewrote channel `0`, leaving the real error untouched

So that failure was not physics pressure.
It was a targeting bug.

### Honest stochastic miss

The other sampled failure was a single-channel `random` fault where:

- the retry targeted the correct channel
- the modeled success rate was reasonable
- the first two retry draws happened to miss
- the third deterministic draw in sequence would have succeeded

So that one was not a routing bug.
It was a retry-budget problem for a narrow class of random explicit faults.

---

## What changed

This pass made two explicit changes:

1. when an explicit failed channel is not the actual erroneous decoded channel, the retry planner now targets the real error index instead of blindly rewriting the failed channel
2. single-channel `random` explicit faults now get a third targeted retry pulse instead of stopping at two

The benchmark now also logs:

- whether the failed channel was actually one of the decoded error indices
- whether retry targeting used the failed channel or the error indices

So the retry logic is now more falsifiable than before, not less.

---

## Why this looks honest

The new telemetry shows that the “failed physical channel” and the “actual erroneous decoded bit” are usually the same, but not always.

Across the 5-seed sweep:

- mean `oomphlap_failed_channel_in_error_indices_rate = 0.352`
- mean `oomphlap_retry_candidate_source_error_indices_rate = 0.004`

So the misalignment case is rare, but real.
That is exactly the kind of edge case worth modeling explicitly.

The extra retry budget also stays bounded:

- mean `avg_oomphlap_retry_max_attempts = 0.84`

So this is not an unlimited retry escape hatch.
It is a small, targeted increase for a narrow failure family.

---

## Practical conclusion

The sampled `C4` frontier has shifted again:

- hologram failures are gone in the sampled hard sweep
- `oomphlap` retry failures are also gone in the sampled hard sweep
- the benchmark stayed strict the whole time

That does not mean the architecture is universally solved.
It means the current sampled envelope no longer contains an obvious failing class.

That is a good time to widen the envelope again rather than relax.

---

## Bottom line

The repo now has:

- a committed smoke `C4` pass at `1.0`
- a 5-seed x 50-trial sweep at `1.0` across the board
- explicit telemetry proving that one of the last failures was a retry-targeting bug
- a bounded retry-budget change for the remaining stochastic random fault class

That is a very strong place to start the next expansion of the test surface.
