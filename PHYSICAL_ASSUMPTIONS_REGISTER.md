# Physical Assumptions Register

**Version:** 0.1  
**Status:** Draft — awaiting team review  
**Date:** 2026-04-09  
**Authors:** Gemini (Google), Claude (Anthropic), Rocks D. Bear  
**Reviewers requested:** Codex (falsifiability), Claude (implementation coherence)

**Purpose:** List every material, optical, thermal, and geometric assumption of the
Uberbrain architecture. Each assumption is explicitly categorized by evidence level
to prevent confusing simulation with physical reality.

Evidence codes:
- `[LIT]` — literature-backed: supported by cited peer-reviewed sources
- `[SIM]` — simulated: demonstrated in our simulation suite
- `[EST]` — estimated: derived from first principles, not yet tested
- `[UNK]` — unknown: no current evidence; requires physical testing

Assumptions tagged `[UNK]` are the honest frontier of this architecture.
They are not weaknesses to hide — they are the experiment queue.

---

## 1. Material & Geometric Assumptions (Volumetric Quartz)

| Assumption | Description | Status | Source / Evidence |
|------------|-------------|--------|-------------------|
| 3D Quartz Transparency | Fused silica maintains >99.99% transmission at the 1030nm write wavelength at depths up to 10mm | `[LIT]` | Standard fused silica specs; `quartz_optics.py` Beer-Lambert model |
| Chromatic Dispersion | Write (1030nm) and read (532nm) lasers focus at different depths due to Sellmeier refractive index | `[SIM]` | `quartz_optics.py` Sellmeier model (Malitson 1965) |
| Rayleigh Layer Count | At NA=0.5 and 1030nm, z_R ≈ 1.9µm gives ~2000 practical layers in a 10mm disc | `[SIM]` | `quartz_optics.py` Rayleigh range; validated against reference layer-count calculation |
| Scattering & Aberration | Deep-layer reading will not be completely occluded by Rayleigh scattering from upper layers | **`[UNK]` ⚠️** | Requires Phase B physical testing; currently unproven |
| Long-Term Stability | Holographic fringes written in fused silica remain stable for 10+ years at room temperature | `[LIT]` | Wang et al. 2024 (ref [17]); standard fused silica stability data |

---

## 2. Thermal Assumptions (GST Phase-Change & Laser Energy)

| Assumption | Description | Status | Source / Evidence |
|------------|-------------|--------|-------------------|
| Athermal PIPC (Cold Write) | A 10nJ / 100fs write pulse creates a thermal bloom radius of ~1.84nm, preventing collateral melting of adjacent nodes | `[SIM]` | `quartz_optics.py` thermal_bloom_radius(); electron-phonon coupling timescale literature |
| GST Reversibility Limits | Repeated BLEACH / WRITE cycles on a single GST node will eventually cause permanent material fatigue | `[LIT]` | Standard phase-change memory literature; ≥10⁹ cycles for optimized GST |
| Thermal Accumulation | Rapid-fire write operations will not raise bulk quartz ambient temperature above GST state-transition threshold | `[EST]` | Basic thermodynamics; needs benchtop validation |
| Layer Stack Compatibility | The femtosecond write process targeting the quartz layer does not thermally damage the adjacent GST layer | **`[UNK]` ⚠️** | No current evidence; layer geometry and thermal isolation unproven |
| GST Reflectivity Stability | GST reflectivity values (amorphous: 0.38, crystalline: 0.72) remain stable under repeated read illumination below the write threshold | `[LIT]` | Rios et al. 2015 (ref [13]); used as constants in sim2 |

---

## 3. Optical & Addressing Assumptions (The Oomphlap)

| Assumption | Description | Status | Source / Evidence |
|------------|-------------|--------|-------------------|
| WDM Crosstalk Envelope | Spectral bleed between Blue/Green/Red read sensors remains below 5%, allowing the correction layer to recover the state | `[SIM]` | `sim2_oomphlap.py`; `sim2_v2_crosstalk.py` BER curves |
| Phase Coherence Under Vibration | Mechanical vibration below ~25nm allows acceptable SSIM reconstruction (>0.95 threshold) | `[SIM]` | `tests/test_adversarial.py` T1 vibration sweep; threshold empirically determined |
| Perfect 3D Targeting | The optical system can address a specific microscopic GST node in 3D space without hitting nodes directly in front of or behind it | **`[UNK]` ⚠️** | Zero current evidence; requires complex non-linear optics or spatially selective femtosecond focusing to prove |
| Wavelength Isolation | Bandpass filters provide sufficient channel isolation that Blue write pulse does not trigger Green or Red GST sites | `[EST]` | Standard optical filter specs; not tested in our configuration |
| Photodiode Array Response | Photodiode array can read all three channels simultaneously within one read cycle without temporal crosstalk | `[EST]` | Standard photodiode specs; not modeled in current sims |
| GST Reflectivity Wavelength Rolloff | Away from optimal wavelength, GST contrast decreases as Gaussian with σ ≈ 30nm | `[EST]` | `tests/test_adversarial.py` chromatic jitter model; not independently verified |

---

## 4. Phase 0-A Assumptions (Transparency Analogy Experiment)

| Assumption | Description | Status | Source / Evidence |
|------------|-------------|--------|-------------------|
| 2D SSIM Translation | A Raspberry Pi camera can detect a physical marker smudge on a 2D transparency using the same SSIM drop logic modeled in sim1 | `[EST]` | OpenCV standard capability; untested in our configuration |
| Analogy Boundary | Success in Phase 0-A proves spatial noise detection in 2D macro-optics only. Provides zero validation of 3D quartz writing, GST switching, or femtosecond PIPC | `[LIT]` | Codex review 2026-04-09; Phase A protocol |
| LED Adequacy | A diffuse LED (not laser) provides sufficient coherence for SSIM-style fidelity measurement in the transparency experiment | `[EST]` | Follows from Phase 0-A defaulting to non-laser per safety gate plan |
| Camera Stability | Ambient lighting changes and camera auto-adjustment will not dominate the signal over corruption-induced SSIM drops | `[EST]` | Addressable via controlled lighting; not yet tested |
| Grid Pattern Detectability | A printed grid pattern on transparency will show measurable SSIM degradation when physically marked | `[EST]` | Supported by sim1 results at equivalent corruption fractions; not yet physically tested |

---

## 5. System-Level Assumptions

| Assumption | Description | Status | Source / Evidence |
|------------|-------------|--------|-------------------|
| Physical Address Uniqueness | Each holographic storage location has a unique, stable physical address that can be consistently targeted for WRITE and BLEACH | `[EST]` | Implied by holographic storage architecture; not independently demonstrated |
| VERIFY Independence | The fidelity scoring mechanism (SSIM of reconstruction) is independent of the data content stored — it responds to corruption, not to data pattern | `[SIM]` | sim1 uses varied test patterns; limited pattern diversity tested |
| Consolicant Graph Validity | Real neuromorphic memory access patterns follow a Barabási-Albert scale-free topology that the Consolicant is designed for | **`[UNK]` ⚠️** | Assumed in sim3; real usage patterns not measured |
| LiFi I/O Integration | LiFi wireless input/output can be integrated with the holographic and GST layers without wavelength interference | `[LIT]` | Tsonev 2014 (ref [30]); integration architecture unspecified |
| Energy Per Operation | READ < 1pJ, WRITE < 10nJ, FORGET < 1nJ per operation | `[EST]` | Estimated from component literature; not modeled or measured |

---

## Summary: Unknown Assumptions

These are the honest frontier. Each `[UNK]` is a Phase B or Phase C experiment target:

| ID | Assumption | Phase to address |
|----|------------|-----------------|
| UNK-1 | Deep-layer scattering / aberration | Phase B simulation, Phase C benchtop |
| UNK-2 | Layer stack thermal compatibility (quartz ↔ GST) | Phase C benchtop |
| UNK-3 | Perfect 3D targeting / spatial selectivity | Phase C benchtop (requires fs optics) |
| UNK-4 | Real usage graph topology (Barabási vs actual) | Phase B simulation study |

---

## What This Document Is Not

This register does not claim the architecture is broken because of unknown assumptions.
Every new architecture has unknown assumptions. The value of this document is making
them visible so they can be addressed in the right order.

**Do not proceed to hardware experiments that depend on an `[UNK]` assumption
without first converting it to `[EST]` or `[SIM]` through benchtop or simulation work.**

---

*CC0 — Public Domain.*  
*"List every assumption. Tag the unknown ones. That's the experiment queue." — Gemini, 2026-04-09*
