# C4 Failure-First Findings — 2026-04-13

**Run analyzed:** `results/20260413_3cc8f78/`  
**Commit under test:** `3cc8f78`  
**Analyzer:** Codex  
**Purpose:** Turn the first failure-first `C4` benchmark into a ranked defect picture.

---

## Executive read

The headline change is not that the architecture "got worse."
The benchmark got less flattering and more truthful.

`C4` now models all three declared ablations and runs the full pipeline against the
same hostile scenario as each ablation. Under that stricter setup:

- Full pipeline success rate: `0.55`
- `no_verify` success rate: `0.45`
- `no_correction_write` success rate: `0.45`
- `no_consolidate_bleach` success rate: `0.00`

Interpretation:

1. `CONSOLIDATE/BLEACH` is decisively load-bearing.
2. The present ceiling on the full pipeline is **not** graph maintenance.
3. The dominant current losses are in **hologram correction** and **oomphlap retry/recovery**.

---

## What failed most often

Observed full-pipeline failure reasons across 20 smoke trials:

| Failure reason | Count | Notes |
|---|---:|---|
| `partial_hologram_correction_failure` | 5 | Primary observed weakness |
| `oomphlap_retry_failed` | 3 | Secondary observed weakness |
| `multi_stage_failure` | 1 | Combined hologram + oomphlap failure |

There were:

- 11 successful trials
- 9 failed trials

So the current `0.55` success rate is mostly explained by two concrete defects,
not by vague "pipeline complexity."

---

## Which perturbations are hurting us

Success/failure split by hologram perturbation family:

| Perturbation family | Trials | Success | Fail | Mean `ssim_pipeline` |
|---|---:|---:|---:|---:|
| `block_dropout` | 7 | 2 | 5 | `0.324` |
| `distributed_dropout` | 6 | 3 | 3 | `0.833` |
| `phase_noise` | 7 | 6 | 1 | `1.000` |

Interpretation:

- `phase_noise` is mostly surviving in the current model.
- `block_dropout` is the real cliff.
- `distributed_dropout` is mixed, and its failures skew toward oomphlap retry.

This suggests the immediate problem is not "all corruption."
It is specifically **localized missing-information repair**.

---

## What the ablations prove

### 1. `no_consolidate_bleach` proves graph maintenance is essential

`no_consolidate_bleach` dropped to `0.00` success rate.

Failure reasons on that ablation:

- `graph_maintenance_disabled`: 11
- `multi_stage_failure`: 9

Meaning:

- The graph layer is not cosmetic.
- If maintenance is removed, the pipeline collapses even when hologram and
  oomphlap behavior are otherwise favorable.

### 2. `no_verify` and `no_correction_write` each drop from `0.55` to `0.45`

This is smaller than the consolidation effect, but still real.

Implication:

- `VERIFY` currently matters only insofar as it can trigger a useful corrective act.
- The present correction path is helping, but only modestly.
- The verify/correct pair is underpowered relative to the corruption families being sampled.

---

## Ranked defect list

### Priority 1 — Hologram correction under localized damage

Evidence:

- 5 direct failures
- 1 additional multi-stage failure containing hologram failure
- 4 of the 5 direct failures happened under `block_dropout`

Interpretation:

The current correction model is too weak when information is sharply removed from
one region. In practical terms, the pipeline does not yet know how to recover from
"hole punched in the stored structure" conditions.

Recommended next move:

- Make correction success conditional on corruption family and severity instead of
  one broad random recovery rate.
- Add a second-pass correction attempt and track whether re-read actually improves.
- Record recovery delta, not just final pass/fail.

### Priority 2 — Oomphlap retry / read recovery

Evidence:

- 3 direct failures
- concentrated in `distributed_dropout` plus one `phase_noise` case

Interpretation:

The recovery path for channel decoding is not robust enough once the read sits near
the threshold or one channel goes bad. This is likely a retry policy / verification
margin problem before it is a "new physics" problem.

Recommended next move:

- Split "verify detected a bad read" from "retry successfully repaired state."
- Add retry count, retry margin, and fallback read strategy to the metrics.
- Test whether majority-vote or repeated-read logic improves this more than a single retry.

### Priority 3 — Multi-stage interaction

Evidence:

- only 1 direct multi-stage failure in this smoke run

Interpretation:

This is real, but not yet the dominant bottleneck.
It should be monitored, not chased first.

---

## Practical conclusion

The repo is finally telling us something actionable:

- The pipeline is not failing "everywhere."
- It is failing in a **ranked order**.
- The first repairs should target:
  1. localized hologram correction
  2. oomphlap retry/recovery
  3. only then broader multi-stage coordination

That is exactly the value of the failure-first posture.

---

## Recommended next implementation pass

1. Enrich `sim4` trial logging with:
   - correction attempt count
   - pre/post recovery delta
   - retry trigger cause
   - retry success/failure reason
2. Make hologram correction severity-aware:
   - distinguish block dropout from distributed damage
   - let recovery probability degrade with missing-area fraction
3. Add oomphlap repeated-read / majority-vote ablation:
   - compare single retry vs repeated read under the same scenario
4. Re-run `C4` smoke and full matrix after those changes.

---

**Bottom line:** the new red is useful red. The benchmark is now telling us where
the architecture breaks first, which is more valuable than the old green ever was.
