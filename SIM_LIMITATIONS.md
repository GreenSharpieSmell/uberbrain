# Uberbrain — Simulation Limitations

**Version:** 0.1  
**Status:** Living document — updated as limitations are discovered  
**Purpose:** Honest catalogue of what the simulations do NOT prove.

Per Codex's VALIDATION_SPEC.md: failures must be documented, not hidden.
Per Gemini's review: the digital twin is verified *within these bounds*.

---

## L1 — Small Holographic Corruption Below VERIFY Detection Floor

**Discovered by:** Codex repo review, 2026-04-09  
**Confirmed by:** adversarial test failures (TestStructuredCorruption)

**Observation:** Corruption covering < ~10% of the hologram area does not reliably drop SSIM below the FIDELITY_WARN threshold (0.95) in the current simulation. The VERIFY command may miss small damage sites.

**Root cause:** The simulation uses 2D FFT holography at 256×256 resolution. Small corruptions (< ~6% area) distribute their energy so broadly in the Fourier reconstruction that the per-pixel error is below SSIM detection sensitivity.

**What this means:**
- SSIM ROC AUC = 1.0 remains valid — perfect separation IS achievable
- The detection threshold must be calibrated, not fixed at 0.95
- Real holographic systems use adaptive thresholds based on noise floor

**What this does NOT mean:**
- It does not mean small corruptions are undetectable in principle
- Real holographic systems have higher spatial resolution and lower noise floors
- At physical scale (sub-micron voxels), the equivalent corruption fraction would trigger detection

**Impact on claims:** H1 (PASS with caveat), H3 (OPEN — spatial localization not yet quantified)

**Mitigation path:** The benchtop transparency experiment (Phase 0-A) will establish the empirical detection floor for physical media.

---

## L2 — Corner Regions Have Lower Detection Sensitivity

**Discovered by:** adversarial test failures (TestStructuredCorruption::test_corner_corruption_detected)

**Observation:** Corruption isolated to the four corners of the hologram remains weakly visible even at large coverage. In the current adversarial suite, four 60×60 corner erasures (~22% coverage) still produce SSIM ≈ 1.000, while an equal-area central erasure of the same total damaged pixels drops SSIM to ~0.037.

**Root cause:** Fourier holography spreads spatial frequency energy non-uniformly. Low spatial frequencies (containing most image energy) are concentrated in the central region of the Fourier plane. Corner regions carry high-frequency detail that contributes less to overall SSIM.

**What this means:**
- Not all hologram regions contribute equally to reconstruction fidelity
- Equal-area corner damage is dramatically less detectable than equal-area center damage
- A physical damage site in a corner region requires much larger area to trigger VERIFY
- Adaptive addressing (weighting corner regions more heavily) could compensate

**Impact on claims:** H1 (PASS with caveat), H3 (OPEN)

**Mitigation path:** Address-weighted SSIM computation (future sim update). Benchtop experiment will measure corner vs center sensitivity empirically.

---

## L7 — Periodic Grid Corruption Can Alias With FFT Structure

**Discovered by:** Codex repo review follow-up, 2026-04-09

**Observation:** Some regular grid attacks preserve SSIM above the VERIFY threshold even at high coverage. In the current adversarial suite, a periodic 6×6 patch grid on a 12-pixel stride changes ~24.2% of the hologram yet still yields SSIM ≈ 0.970, while matched random corruption of the exact same changed-pixel count drops SSIM to ~0.191.

**Root cause:** The attack pattern can align with the discrete Fourier structure strongly enough that removed energy aliases into a reconstruction that still looks globally similar under vanilla SSIM.

**What this means:**
- Detection is not monotone in damaged area for all structured attacks
- Some periodic patterns are more dangerous than random damage of the same size
- The current VERIFY metric is vulnerable to adversarially regular corruption layouts

**Impact on claims:** H1 (PASS with caveat), H3 (OPEN)

**Mitigation path:** Sweep structured attack families systematically, add address-weighted fidelity metrics, and test phase-offset or jittered grid attacks rather than only area-matched corruption.

---

## L3 — Sim 4 Correction Is a Perfect Reset

**Discovered by:** Codex repo review, 2026-04-09  

**Observation:** In `sim4_pipeline.py` and `run_matrix.py`, the correction WRITE is modeled as restoring the clean hologram directly. This means the ablation comparison (pipeline vs no-correction) shows zero uplift at simulation scale.

**Root cause:** The sim uses `holo_corrected = holo_clean.copy() + small_noise` — a near-perfect software reset rather than a physically constrained write/read correction loop.

**What this means:**
- The C4 pipeline claim (uplift ≥ 0.0) is trivially satisfied
- The ablation does not demonstrate meaningful correction value
- `sim1_v2_noise.py` correctly models imperfect correction (SSIM 0.97–0.99) but this is not wired into the pipeline benchmark

**Impact on claims:** C4 (PASS under permissive gate — not yet a strong demonstration)

**Mitigation path:** Wire sim1_v2_noise imperfect correction model into sim4 and run_matrix C4 runner. This is the next engineering task after repo hardening.

---

## L4 — Benchmark.py Corrected SSIM Inconsistency

**Discovered by:** Codex repo review, 2026-04-09

**Observation:** Running `benchmark.py --quick` reports 7/7 PASS but shows corrected SSIM ≈ 0.052, not the 0.97–0.99 target in SPECIFICATIONS.md.

**Root cause:** `benchmark.py` uses a simple Gaussian noise model for correction, not the V0.2 imperfect recrystallization model from `sim1_v2_noise.py`. The two scripts model correction differently.

**What this means:**
- `benchmark.py` and `sim1_v2_noise.py` give inconsistent corrected SSIM values
- The 0.97–0.99 target in SPECIFICATIONS.md reflects the V0.2 noise model
- `benchmark.py` needs to be updated to use the same noise model

**Impact on claims:** H4 (PARTIAL — corrected SSIM target not met in benchmark.py)

**Mitigation path:** Update benchmark.py correction model to match sim1_v2_noise.py.

---

## L5 — Phase 0-A Is an Analogy Experiment

**Discovered by:** Codex repo review; Gemini architectural response, 2026-04-09

**Observation:** The Phase 0-A transparency experiment validates SSIM measurement of 2D optical noise through a physical medium. It does NOT validate:
- 3D quartz holographic storage
- GST phase-change material switching
- Femtosecond athermal PIPC
- The full READ → VERIFY → WRITE correction stack

**What this means:**
- Phase 0-A proves the measurement methodology works physically
- Phase 0-A does NOT validate the Uberbrain architecture specifically
- Successful Phase 0-A = TRL 4 for the SSIM measurement method only

**Impact on claims:** All claims remain at simulation evidence level after Phase 0-A

**Mitigation path:** Phases 1–3 address GST, holographic film, and wavelength isolation respectively. Each phase validates specific architectural claims.

---

## L6 — Sim 3 Uses Barabási-Albert Graph Only

**Observation:** The Consolicant Sim 3 generates memory graphs exclusively using the Barabási-Albert preferential attachment model. Real neuromorphic memory graphs may follow different topologies.

**What this means:**
- Triple-filter correctness is proven on scale-free graphs
- Adversarial tests (Erdős-Rényi, Watts-Strogatz) show it holds on other topologies
- But real usage graphs were not measured

**Impact on claims:** C1, C2 (PASS with caveat)

**Mitigation path:** Adversarial graph topology tests are in `tests/test_adversarial.py`. All pass. Consider adding real-world-derived graph samples in future work.

---

## Summary Table

| ID | Limitation | Severity | Claims Affected | Mitigation |
|----|------------|----------|-----------------|------------|
| L1 | Small corruption below detection floor | Medium | H1, H3 | Benchtop calibration |
| L2 | Corner regions lower sensitivity | Low | H1, H3 | Address-weighted SSIM |
| L3 | Sim 4 correction is perfect reset | Medium | C4 | Wire V0.2 noise model |
| L4 | benchmark.py SSIM inconsistency | Medium | H4 | Update correction model |
| L5 | Phase 0-A is analogy only | High | All | Phases 1–3 |
| L6 | Sim 3 uses one graph model | Low | C1, C2 | Adversarial tests added |
| L7 | Periodic grid alias window | Medium | H1, H3 | Structured-attack sweeps |

---

## What Is NOT a Limitation

These concerns have been raised and investigated:

- **"5.5% corruption → 73.9% fidelity drop"** is valid — this is the default corruption size (60×60px). Limitation L1 only applies to smaller patches.
- **Gate threshold relaxations** are documented in the Decision Log in the shared whiteboard and are defensible — see Gemini's architectural review 2026-04-09.
- **Thermal bloom radius 1.84nm** correctly validates athermal PIPC — this is a strength, not a limitation.

---

*CC0 — Public Domain. Limitations documented honestly per Codex VALIDATION_SPEC.md.*  
*"Failures must be documented, not hidden."*
