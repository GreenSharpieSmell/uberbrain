# Uberbrain Validation Spec v0.1

**Status:** Draft for implementation  
**Author:** Codex (OpenAI), incorporated 2026-04-08  
**Audience:** builders, skeptical reviewers, external replicators  
**Goal:** Convert narrative simulation claims into falsifiable, repeatable evidence.

---

## 1) Scope and Philosophy

This spec defines **what must be measured** before strong architecture claims are made.

Core rule:
- Every claim must map to:
  1. a metric,
  2. a benchmark protocol,
  3. a baseline comparator,
  4. a pass/fail threshold,
  5. a reproducibility artifact.

No single-run "hero result" is considered proof.

Default posture:
- Treat the architecture as guilty until validated.
- Prefer finding the boundary where it fails over collecting easy passes.
- Record failure cases as first-class outputs, not embarrassing leftovers.

See `CLAIMS.md` for the claim registry mapping each claim to its current evidence level.

---

## 2) Claims Under Test

### C1 — Holographic VERIFY can reliably detect damaging corruption
- Module: `sim/sim1_holographic.py`
- Current narrative: corruption causes measurable fidelity loss.
- Validation target: robust detection quality across corruption types and locations.

### C2 — Oomphlap encoding remains useful under realistic read noise/crosstalk
- Module: `sim/sim2_oomphlap.py` (+ v2 variants)
- Current narrative: parallel channels expand state capacity.
- Validation target: quantify BER and decode stability under perturbations.

### C3 — Consolicant policy prunes low-value nodes while preserving high-value connectivity
- Module: `sim/sim3_consolicant.py`
- Current narrative: triple-filter avoids naive deletion failures.
- Validation target: quality tradeoff vs simple baselines.

### C4 — End-to-end pipeline improves net system reliability
- Module: `sim/sim4_pipeline.py`
- Current narrative: six commands behave coherently.
- Validation target: demonstrate net gain over ablations.

---

## 3) Standard Experiment Protocol

For *every* experiment:
1. Log seed(s), parameter set, git commit SHA.
2. Run at least **N=100** stochastic trials unless deterministic by design.
3. Report mean, std, median, p5/p95, and confidence interval.
4. Export machine-readable output (`.csv` + `.json`).
5. Save plots from data (no manual chart edits).

Minimum output directory layout:

```
results/
  <date>_<experiment_name>/
    config.json
    metrics.csv
    summary.json
    plots/*.png
    environment.txt
```

Run `python benchmark.py` to produce conforming output automatically.

---

## 4) Metrics and Pass/Fail Criteria

### C1: Sim1 (Holographic VERIFY)

**Required metrics:**
- SSIM detection ROC-AUC for classifying "damaging corruption"
- False negative rate (FNR) at operational threshold
- Calibration curve (predicted confidence vs observed correctness)
- Sensitivity by corruption type: block dropout, random speckle, phase jitter, blur

**Baselines:**
- MSE threshold detector
- PSNR threshold detector

**Pass criteria (v0.1):**
- ROC-AUC(SSIM detector) ≥ 0.90 on mixed corruption suite
- FNR ≤ 5% at target operating point
- SSIM detector outperforms MSE baseline on AUC by ≥ 0.03

**Current status:** SSIM detection confirmed on block dropout. ROC-AUC across mixed corruption types not yet measured. See `CLAIMS.md` H1–H5.

---

### C2: Sim2 (Oomphlap)

**Required metrics:**
- Bit Error Rate (BER) vs noise sigma
- State decode accuracy vs crosstalk coefficient
- Confusion matrix for state decoding
- Capacity-efficiency: effective bits per symbol at target BER

**Baselines:**
- Single-channel binary baseline
- Multi-channel baseline without MLC

**Pass criteria (v0.1):**
- BER ≤ 1×10⁻² at low-noise operating regime
- Graceful degradation curve (no cliff below specified sigma)
- Multi-channel configuration provides higher effective capacity than baseline at equal BER

**Current status:** BER vs sigma curve partially modeled in `sim2_v2_crosstalk.py`. Full confusion matrix and ROC not yet implemented. See `CLAIMS.md` O1–O4.

---

### C3: Sim3 (Consolicant)

**Required metrics:**
- Precision/Recall/F1 for BLEACH targeting vs synthetic ground-truth labels
- Retained-value score: weighted connectivity retained after pruning
- Regret metric: loss from mistakenly bleached high-value nodes

**Baselines:**
- Age-only deletion
- Fidelity-only deletion
- Random deletion with equal prune budget

**Pass criteria (v0.1):**
- F1 ≥ 0.80 on labeled synthetic tasks
- Regret ≤ 50% of best naive baseline
- Retained-value score ≥ naive baselines under equal prune ratio

**Current status:** Age-only and fidelity-only baselines compared in `benchmark.py`. F1 and regret metrics not yet computed. See `CLAIMS.md` C1–C4.

---

### C4: Sim4 (Pipeline)

**Required metrics:**
- End-to-end task success rate before vs after correction + consolidation
- Net reliability uplift from full pipeline over ablations:
  - No VERIFY
  - No correction WRITE
  - No CONSOLIDATE/BLEACH
- Cost metrics: runtime, operation count, memory overhead

**Pass criteria (v0.1):**
- Full pipeline outperforms each ablation on primary reliability metric
- No single module contributes negative net effect at target operating point

**Current status:** Pipeline demonstrated in `sim4_pipeline.py`. Ablation comparison not yet implemented.

---

## 5) Adversarial Test Suite (Must-Have)

Add an adversarial suite that intentionally attacks assumptions:

- **Sim1:** Structured perturbations that minimally change global SSIM but break key features
- **Sim2:** Drifting thresholds, correlated channel noise, asymmetric channel failure
- **Sim3:** Non-scale-free graphs, distribution shift, adversarial stale/fidelity labels
- **Sim4:** Cascading fault scenarios and partial correction failure

Any claim must include both **standard** and **adversarial** performance to be considered validated.

See `CLAIMS.md` A1–A2 for current adversarial claim status (all OPEN).

---

## 6) Reproducibility and Governance

Required for each benchmark release:
- Fixed dependency versions (see `sim/requirements.txt`)
- Deterministic seed list committed to repo
- CI job executes smoke benchmark subset on PRs (see `.github/workflows/ci.yml`)
- Full benchmark runs produce immutable artifact bundles

**Change control:**
- Any metric/threshold change requires a changelog entry with rationale
- Do not retroactively change thresholds to fit outcomes
- All threshold changes must be pre-registered before running the experiment they affect

---

## 7) Reporting Template

Every benchmark report must include:
1. Claim being tested
2. Protocol and parameter ranges
3. Baselines used
4. Results table (mean/std/CI)
5. Failures and edge cases
6. Whether pass criteria were met
7. Next actions

**Use explicit language levels:**
- **Demonstrates:** passed benchmark criteria
- **Suggests:** signal present but criteria not fully met
- **Hypothesizes:** no benchmark evidence yet

Current repo language level: **Hypothesizes → Suggests** (simulations pass; hardware unvalidated)

---

## 8) 30-Day Execution Plan

**Week 1 (current):**
- ✓ Build benchmark harness + unified results schema (`benchmark.py`)
- ✓ Add Sim1/2 noise and crosstalk sweeps (V0.2 sims)
- ✓ Formal claim registry (`CLAIMS.md`)
- → Add ROC-AUC measurement to Sim1

**Week 2:**
- Implement baseline comparators and ROC/BER tooling
- Add Sim3 labeled synthetic tasks and baseline policies
- Compute F1/regret metrics for Consolicant

**Week 3:**
- Add adversarial suites and ablations
- Lock pass/fail thresholds in config
- Run Sim4 ablation comparison

**Week 4:**
- Run full benchmark matrix
- Publish first validation report with raw artifacts
- Run transparency experiment (Phase 0-A, see `PROTOTYPE.md`)

---

## 9) Exit Criteria for "Serious" Claims

You can make strong claims when **all** are true:
1. Predefined pass criteria met on standard suite
2. Competitive performance on adversarial suite
3. Results reproducible across machines/reruns
4. Full pipeline beats ablations
5. Failures are documented, not hidden

**Until then, frame work as promising simulation research.**

Current honest framing: *"Concept + simulation hypothesis, not engineering-ready architecture."*

That framing is in `SPECIFICATIONS.md`. Keep it there until exit criteria are met.

---

## 10) What This Document Is Not

This spec does not:
- Claim the architecture works in hardware
- Assert the simulations prove physical feasibility
- Substitute for peer review

It defines what evidence would be required to make those claims. Building that evidence is the work.

---

*Validation Spec authored by Codex (OpenAI), 2026-04-08*  
*Incorporated into Uberbrain repository under CC0 — Public Domain*  
*"Until then, frame work as promising simulation research." — Codex*
