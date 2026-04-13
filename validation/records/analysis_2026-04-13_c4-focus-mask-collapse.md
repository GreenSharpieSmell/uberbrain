# C4 Focus-Mask Collapse Findings - 2026-04-13

**Run analyzed:** `results/20260413_da7a210/`  
**Commit under test:** `da7a210`  
**Analyzer:** Codex  
**Purpose:** Determine whether interior rewrite failure was caused by bad selection logic or by a collapsed focus mask upstream.

---

## Executive read

This pass found an upstream measurement defect, not just a weak selector.

The old rewrite path often derived clustered-loss geometry from a "missing pixel" mask that was far too sparse for the normalized hologram field. In the hostile block-dropout cases we care about most, that mask could collapse to a single pixel even though hundreds of hologram cells were actually damaged.

After switching geometry selection to fall back to `diff_mask` when the missing-mask support is too small, the smoke benchmark moved:

- Full pipeline success rate: `0.70` (up from `0.55`)
- Threshold-crossing recovery rate: `0.15` (up from `0.00`)
- Block-dropout success rate: `0.714286` (up from `0.285714`)
- Block-dropout threshold-crossing rate: `0.428571` (up from `0.00`)

The claim still fails honestly because `min_success_rate >= 0.9` is still unmet.

---

## What changed in the measurement

New telemetry shows why the prior interior-capture result was misleading:

- `avg_hologram_diff_count = 234.65`
- `avg_hologram_missing_count = 0.3`
- `avg_hologram_missing_to_diff_ratio = 0.000891`
- `focus_source_missing_rate = 0.0`

Interpretation:

- the missing-mask heuristic was almost never a faithful description of the damaged hologram
- the benchmark now correctly falls back to the broader diff-based mask instead of pretending a one-pixel region is the whole clustered-loss focus

This was not a "make the test easier" change.
It was a "stop measuring the wrong region" change.

---

## What the rewrite path is doing now

With the corrected focus geometry, the rewrite path is no longer starved:

- `avg_hologram_focus_boundary_share = 0.398843`
- `avg_hologram_focus_interior_share = 0.601157`
- `avg_correction_boundary_candidate_count = 12.25`
- `avg_correction_interior_candidate_count = 121.5`
- `avg_correction_boundary_selected_count = 12.25`
- `avg_correction_interior_selected_count = 121.5`
- `avg_total_recovery_delta = 0.184548`

The key takeaway is that the repair path now has real interior targets and can sometimes recover enough fidelity to cross the warning threshold. That answers the earlier uncertainty directly: the selector was not the only problem. The focus-region definition upstream was collapsing the available work.

---

## Remaining failures

Even with the better geometry, `C4` still fails:

- `min_success_rate = 0.70` vs required `0.90`
- `failure_count_oomphlap_retry_failed = 3`
- `failure_count_partial_hologram_correction_failure = 2`
- `failure_count_multi_stage = 1`

So the bottleneck has shifted.

Before this pass, the repo was mostly telling us "your hologram repair path is being asked to work on a broken focus definition."

After this pass, the repo is telling us:

- the hologram repair path is materially better
- some hard hologram cases still fail
- oomphlap retry behavior is now one of the leading remaining direct failure modes

---

## Recommended next implementation pass

1. Split the next defect pass between remaining hologram shortfalls and oomphlap retry failure.
2. Add retry telemetry for oomphlap that explains why retries miss when verify fires.
3. Keep the new focus-source and candidate-count metrics, because they protect the benchmark from drifting back into one-pixel geometry.
4. Continue tracking threshold-crossing recovery, not just partial score deltas.

---

## Bottom line

This was a real scientific correction.

The benchmark was not wrong to fail.
But it was partially failing for the wrong reason.

Now it fails for a better reason:

- the clustered-loss geometry is measured more honestly
- the rewrite path has real interior work to do
- the benchmark can show genuine threshold-crossing recovery
- and the next remaining weaknesses are much clearer
