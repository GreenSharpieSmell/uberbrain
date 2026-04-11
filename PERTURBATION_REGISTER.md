# Perturbation Register

**Version:** 0.1  
**Status:** Draft - seeded from research capture  
**Date:** 2026-04-11  
**Owner:** Rocks D. Bear + collaborators  

**Purpose:** Maintain an explicit catalogue of anything that could perturb the
photon path, storage medium, sensor readout, timing, or interpretation of the
Uberbrain architecture.

This document exists to enforce one rule:

**Default to inclusion.**

If an effect is considered and ruled out, the dismissal should still be written
down with a reason. Silent omission is not acceptable.

This register is upstream of:
- `PHYSICAL_ASSUMPTIONS_REGISTER.md`
- `FAILURE_MODES.md`
- `VALIDATION_SPEC.md`

Promote items from this register into those documents when they become concrete
assumptions, benchmark perturbations, or named failure modes.

---

## Priority Codes

- `[P0]` Claim threat: can change interpretation of current PASS/SUGGESTS claims
- `[P1]` Near-term realism: should be modeled or benchtop-tested in Phase 0-A / 0-B
- `[P2]` Integration realism: matters once GST, quartz stack, or packaged optics exist
- `[P3]` Low-likelihood / speculative: keep a written bound or dismissal

Presence in this document does **not** imply high expected effect size.
It only means the effect has been explicitly considered.

---

## Operating Principle

When evaluating a perturbation, ask:

1. Does it affect the photon before the medium, inside the medium, or at readout?
2. Does it perturb amplitude, phase, wavelength, polarization, timing, geometry, or material state?
3. Can the current simulation suite model it directly?
4. What metric would reveal it: SSIM, BER, SNR, drift, false confidence, misregistration, or thermal budget?
5. Does it threaten an existing claim, or does it belong in a later phase?
6. If dismissed, what is the one-line reason and bound?

---

## Immediate Queue

These are the first perturbation families to wire into sims, benchtop protocols,
or explicit assumption checks:

| Priority | Family | Representative effects | Why it matters first |
|----------|--------|------------------------|----------------------|
| `[P0]` | Geometry and distance | propagation distance, standoff distance, focus depth error, beam divergence, off-axis incidence | Directly changes spot size, intensity, alignment, and reconstruction fidelity |
| `[P0]` | Thermal environment | ambient temperature drift, thermal gradients, thermal lensing, expansion/contraction | Already threatens READ/VERIFY confidence interpretation |
| `[P0]` | Ambient light field | room light, sunlight, stray reflections, backscatter | Can fake or bury sensor-side signal in Phase 0-A and later read paths |
| `[P0]` | Mechanical disturbance | vibration, shock, beam pointing jitter, stage wobble | Already adjacent to current vibration assumption and optical coherence concerns |
| `[P0]` | Readout noise | sensor noise, shot noise, dark current, clipping, ADC quantization | Can convert clean physics into false confidence or false alarms |
| `[P0]` | Laser instability | wavelength drift, power drift, coherence drift, pulse timing jitter | Threatens addressability, BER, and repeatability |
| `[P1]` | Air path contamination | dust, smoke, haze, moisture, condensation, fingerprints, film smudges | Essential for Phase 0-A realism and any open-air optical path |
| `[P1]` | Atmospheric state | pressure, altitude, humidity, turbulence, scintillation | Changes refractive index, attenuation, and beam wander |
| `[P1]` | Channel interaction | crosstalk, polarization drift, speckle, stray coupling | Directly relevant to oomphlap decode stability |
| `[P1]` | Electrical environment | EMI, PSU ripple, ground noise, clock jitter | Can masquerade as optical failure from the sensor side |

---

## Perturbation Families

### 1. Geometry, Distance, and Alignment

| Priority | Perturbation | Notes |
|----------|--------------|-------|
| `[P0]` | Source-to-subject distance | Controls inverse-square intensity loss, divergence, and effective spot size |
| `[P0]` | Subject-to-sensor distance | Changes magnification, blur tolerance, and reconstruction geometry |
| `[P0]` | Focus depth error | Reads/writes wrong plane or broadens addressed volume |
| `[P0]` | Beam pointing offset | Misses intended voxel or GST site |
| `[P1]` | Angle-of-incidence error | Alters reflection efficiency, interference geometry, and apparent contrast |
| `[P1]` | Packaging/mount creep | Slow alignment drift over time due to mechanical relaxation |
| `[P2]` | Layer thickness variation | Changes optical path length and thermal coupling in stack integration |

### 2. Atmosphere and Open-Path Medium

| Priority | Perturbation | Notes |
|----------|--------------|-------|
| `[P1]` | Humidity / moisture | Can shift absorption, surface wetting, and condensation risk |
| `[P1]` | Dust / particulates | Scatter, attenuate, or partially occlude the beam |
| `[P1]` | Condensation / fog | Large attenuation and diffusion; likely catastrophic in open path |
| `[P1]` | Smoke / haze / aerosols | Relevant for scattering and beam profile distortion |
| `[P1]` | Pressure / altitude | Changes refractive index of air and convective cooling conditions |
| `[P1]` | Temperature gradient in air | Produces turbulence, beam wander, and scintillation |
| `[P2]` | Gas composition / contamination | Relevant if sealed package atmosphere is engineered later |

### 3. Illumination, Radiation, and Optical Field Effects

| Priority | Perturbation | Notes |
|----------|--------------|-------|
| `[P0]` | Ambient room light | Immediate concern for camera or photodiode readout |
| `[P0]` | Stray reflections / multipath | Can create ghost signal and false structure |
| `[P1]` | Solar loading / sunlight | Adds broadband background plus heating |
| `[P1]` | Polarization drift | Can reduce read contrast or alter channel isolation |
| `[P1]` | Speckle | Coherent granular noise that can bias reconstruction metrics |
| `[P1]` | Coherence loss / phase noise | Reduces interference quality and hologram fidelity |
| `[P1]` | Scintillation | Time-varying intensity fluctuations from turbulent path |
| `[P2]` | Thermal blooming / thermal lensing | Beam self-distortion under higher power or hot local regions |
| `[P2]` | Surface scattering from contamination or roughness | Lowers useful signal and increases background |
| `[P3]` | Solar radiation / ionizing environment | Keep bounded even if negligible for bench phases |

### 4. Mechanical and Acoustic Effects

| Priority | Perturbation | Notes |
|----------|--------------|-------|
| `[P0]` | Vibration | Already known to matter for phase coherence and alignment |
| `[P1]` | Seismic activity / microseisms | Low-frequency ground motion can look like slow beam wander or mount drift |
| `[P1]` | Shock / impact | Tests robustness to sudden misalignment or transient blur |
| `[P1]` | Acoustic coupling | "Sound effects on quartz"; pressure waves can modulate path length or mounts |
| `[P1]` | Resonance / ringing | Hardware frame may amplify narrow vibration bands |
| `[P2]` | Microphonics in sensors or drivers | Converts vibration into electrical noise |
| `[P2]` | Long-term mechanical fatigue | Repeated cycling loosens optics or drifts alignment |

### 5. Sensor, Timing, and Electronics

| Priority | Perturbation | Notes |
|----------|--------------|-------|
| `[P0]` | Shot noise | Fundamental optical counting noise |
| `[P0]` | Read noise / dark current | Sensor floor may hide weak signal |
| `[P0]` | Saturation / clipping | Turns bright valid reads into misleading flat responses |
| `[P0]` | Quantization / ADC limits | Can create threshold artifacts around decision boundaries |
| `[P1]` | Timing jitter | Matters for synchronized reads, write pulses, and gated detection |
| `[P1]` | Power-supply ripple | Can modulate emitters and sensors without any optical cause |
| `[P1]` | Ambient electric fields | May bias exposed sensor electronics or poorly shielded analog paths |
| `[P1]` | Ambient magnetic fields | Relevant for drivers, supplies, shielding assumptions, and nearby inductive loads |
| `[P1]` | EMI / RFI | Electrical corruption that can be mistaken for physics-side failure |
| `[P1]` | Proximity to electrical equipment | Motors, transformers, GPUs, PSUs, fluorescent ballasts, and switching supplies can inject heat, vibration, EMI, and ground noise together |
| `[P1]` | Calibration drift | Sensor gain and offset drift move operating thresholds over time |
| `[P2]` | Rolling-shutter or sampling artifacts | Relevant if camera-based diagnostics remain in use |

### 6. Materials, Surfaces, and Aging

| Priority | Perturbation | Notes |
|----------|--------------|-------|
| `[P1]` | Surface dust / fingerprints / smudges | Especially relevant for Phase 0-A analog experiments |
| `[P1]` | Coating contamination | Lowers transmission or changes reflection characteristics |
| `[P2]` | GST fatigue / endurance loss | Already a known later-stage issue |
| `[P2]` | Diode aging | Output power and wavelength drift over life |
| `[P2]` | Photodiode degradation | Responsivity drift changes thresholds |
| `[P2]` | Filter bandpass drift | Degrades channel isolation over time |
| `[P2]` | Quartz defect growth / color center formation | Radiation or repeated exposure may alter transparency |
| `[P2]` | Adhesive outgassing / yellowing | Packaging material can become an optical contaminant |

### 7. System and Model Artifacts

| Priority | Perturbation | Notes |
|----------|--------------|-------|
| `[P0]` | Threshold miscalibration | Can manufacture false PASS / FAIL outcomes |
| `[P0]` | Address misregistration | System writes or reads the wrong physical site while appearing successful |
| `[P0]` | Limited metric sensitivity | Example: SSIM blind spots already seen in corner corruption scenarios |
| `[P1]` | Dataset or pattern bias | Fidelity metric may work only on friendly test patterns |
| `[P1]` | Simulator under-modeling | Missing physics can overstate confidence |
| `[P1]` | Control-loop latency | System may detect corruption too slowly for correction to matter |
| `[P2]` | Cross-layer verification gaps | Quartz may look valid while GST or sensor chain is wrong |

### 8. Exotic / Speculative Effects

These should not dominate near-term work, but they should be explicitly
considered and either bounded or dismissed.

| Priority | Perturbation | Default handling |
|----------|--------------|------------------|
| `[P2]` | Ambient planetary background noise | Use as an umbrella bucket for geomagnetic variation, Schumann-band background, and site-level environmental drift that is real but usually low amplitude |
| `[P3]` | Cosmic rays / high-energy particles | Bound expected upset rate for sensor and material exposure |
| `[P3]` | Solar storms / radiation spikes | Note as environment-specific unless deployment demands it |
| `[P3]` | Relativistic effects | Usually dismiss for bench-scale stationary systems; document bound |
| `[P3]` | Gravitational waves | Expected dismissal unless path length / sensitivity ever enters relevant regime |
| `[P3]` | Neutrinos | Expected dismissal; document negligible interaction cross-section |
| `[P3]` | Axions / dark photons | Expected dismissal unless architecture becomes a detector by design |
| `[P3]` | Tachyons | Keep as explicit considered-and-dismissed item unless a real mechanism is proposed |

---

## Promotion Rules

Move an item out of this register when one of these becomes true:

- It changes a claim in `CLAIMS.md`
- It becomes an explicit assumption in `PHYSICAL_ASSUMPTIONS_REGISTER.md`
- It gets a named entry in `FAILURE_MODES.md`
- It receives a benchmark or benchtop protocol in `VALIDATION_SPEC.md`

---

## Current Research Stance

The working standard is:

- Test the realistic effects first
- Keep the weird effects on the page
- Write down dismissals instead of silently skipping them
- Treat completeness as scientific integrity, not theatrics

---

*CC0 - Public Domain.*
