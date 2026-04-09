# Uberbrain — Engineering Specifications

**Version:** 0.2  
**Status:** Simulation-derived targets — awaiting benchtop validation  
**Authors:** Rocks D. Bear, Claude (Anthropic), Gemini (Google), informed by Codex (OpenAI) critique

---

## Purpose

This document defines falsifiable engineering Key Performance Indicators (KPIs) for the Uberbrain architecture. These are not aspirational targets — they are specific, measurable numbers that a working implementation must achieve. If a physical prototype fails to meet these numbers, the architecture must be revised.

This document is the answer to: *"Is this validated?"* The honest answer is: not yet. This is what validation looks like.

---

## Technology Readiness Level

| Current State | TRL |
|--------------|-----|
| Individual components demonstrated in literature | TRL 2 |
| Mathematical simulations of integrated architecture | TRL 2-3 |
| Digital twin with noise modeling and BER curves | TRL 3 |
| **Target: Benchtop experiment matching sim prediction** | **TRL 4** |
| Physical prototype (shoebox) | TRL 4-5 |
| Integrated oomphlap array demonstration | TRL 5-6 |
| Contact lens form factor | TRL 8-9 |

---

## Layer 1 — Holographic Storage (READ / VERIFY / BLEACH)

### Storage Medium: Fused Quartz (5D Optical)

| KPI | Target | Basis | Status |
|-----|--------|-------|--------|
| Areal density | ≥ 1 TB/cm² | Wang et al. 2024 (ref [17]) | Literature demonstrated |
| Layer count (10mm disc) | ≥ 2,000 | Rayleigh range reference calculation | Simulation verified |
| Data retention | ≥ 10 years @ 85°C | Fused quartz stability | Literature demonstrated |
| Read non-destructive | Yes — read power below write threshold | Physical property | By design |
| BLEACH energy | < 1 µJ per voxel | Estimated from fs laser params | Unverified |

### VERIFY Command (Fidelity Scoring)

| KPI | Target | Basis | Status |
|-----|--------|-------|--------|
| Intact detection threshold | SSIM ≥ 0.95 | Sim 1 V0.1 | Simulation |
| Corruption detection rate | > 99.9% for ≥ 3% hologram damage | Sim 1 V0.1 | Simulation |
| False positive rate (intact flagged as degraded) | < 0.1% | Sim 1 V0.2 Monte Carlo | Simulation |
| SSIM floor under full noise stack | ≥ 0.85 (clean reads) | Sim 1 V0.2 Monte Carlo | Simulation |
| Correction restored SSIM | 0.97–0.99 (NOT 1.000) | Sim 1 V0.2 imperfect correction | Simulation |

### READ/WRITE Optical Parameters

| KPI | Target | Basis | Status |
|-----|--------|-------|--------|
| Write wavelength | 400–450 nm | PIPC electronic coupling | Literature (athermal regime) |
| Write pulse duration | < 1 ps (femtosecond) | Electron-phonon coupling timescale | Literature |
| Write pulse energy | < 10 nJ per voxel | GST switching energy estimates | Unverified |
| Read wavelength | 532 nm (isolated from write) | Wavelength separation | By design |
| Read power | < 1% of write threshold | Non-destructive read requirement | By design |
| Spatial resolution | ≥ Rayleigh limit (~400 nm) | Diffraction physics | Sim verified |

---

## Layer 2 — GST Working Memory (WRITE / READ / FORGET)

### Phase-Change Material Performance

| KPI | Target | Basis | Status |
|-----|--------|-------|--------|
| Binary state separation | ΔR ≥ 0.30 (amorphous vs crystalline) | GST material constants | Literature demonstrated |
| Decision threshold margin | ≥ 0.10 from each state | Sim 2 V0.2 eye diagram | Simulation |
| GST reflectivity drift (thermal) | σ ≤ 0.02 per read | Sim 2 V0.2 noise model | Simulation |
| Write endurance | ≥ 10⁹ cycles before BLEACH required | GST literature (optimized GST) | Literature — unverified for this config |
| FORGET pulse energy | < 1 nJ (thermal anneal) | IR pulse energy estimates | Unverified |
| FORGET latency | < 10 ns | Thermal relaxation timescale | Unverified |

### Oomphlap Encoding (Multi-Wavelength)

| KPI | Target | Basis | Status |
|-----|--------|-------|--------|
| Binary state space (3-channel) | 8 states (2³) | Sim 2 V0.1 | Simulation — all correct |
| MLC state space (3-channel, 4-level) | 64 states (4³) | Sim 2 V0.1 | Simulation |
| BER target (conservative) | < 1×10⁻⁶ | Industry standard for storage | Falsifiable |
| BER target (hard) | < 1×10⁻⁹ | High-reliability standard | Falsifiable |
| Required SNR for BER < 10⁻⁶ | Sim-derived (see sim2_v2_crosstalk.py) | Sim 2 V0.2 | Simulation |
| Max tolerable channel crosstalk | Sim-derived (see sim2_v2_crosstalk.py) | Sim 2 V0.2 | Simulation |
| Read latency per oomphlap | < 1 ns | Photonic detection timescale | Unverified |

---

## Layer 3 — Consolicant (CONSOLIDATE / BLEACH)

### Triple-Filter Parameters

| KPI | Target | Basis | Status |
|-----|--------|-------|--------|
| Staleness threshold | Configurable (default: 60 time units) | Sim 3 | Simulation |
| Fidelity threshold | SSIM < 0.50 (BLEACH) / < 0.95 (REPAIR) | Sim 3 | Simulation |
| Connectivity threshold | Degree centrality < 0.02 | Sim 3 | Simulation |
| False BLEACH rate (connected nodes erased) | 0.00% — architectural guarantee | Sim 3 verification | Simulation |
| CONSOLIDATE cycle time | < 1% of active operation time | Not yet modeled | Unverified |

### Endurance Integration

| KPI | Target | Basis | Status |
|-----|--------|-------|--------|
| SSIM ceiling after 1,000 write cycles | ≥ 0.94 | Sim 1 V0.2 endurance model | Simulation |
| Write cycles before REPAIR threshold | Sim-derived | Sim 1 V0.2 endurance model | Simulation |
| Write cycles before BLEACH threshold | Sim-derived | Sim 1 V0.2 endurance model | Simulation |

---

## System-Level KPIs

### Energy Efficiency

| KPI | Target | Comparison | Status |
|-----|--------|------------|--------|
| Energy per READ operation | < 1 pJ | DRAM: ~100 fJ / Flash: ~10 nJ | Unverified |
| Energy per WRITE operation | < 10 nJ | Flash WRITE: ~10 nJ | Unverified |
| Energy per VERIFY operation | < 0.1 pJ (passive optical) | No active compute needed | Theoretical |
| Idle power (quartz storage) | ~0 W (passive) | HDD: ~5W / SSD: ~2W | Physical property |
| Thermal dissipation | < 1 mW per cm² (athermal WRITE) | GPU: ~300W | Theoretical |

### Data Transfer

| KPI | Target | Basis | Status |
|-----|--------|-------|--------|
| LiFi I/O bandwidth | ≥ 1 Gbps | Commercial LiFi (Tsonev 2014) | Literature |
| Oomphlap read throughput | Sim-derived | Pending Sim 4 integration | Unverified |

---

## Falsification Criteria

The following results would require significant architectural revision:

1. **BER floor** — if BER cannot reach < 10⁻⁶ at any achievable SNR with the 3-channel oomphlap, the encoding architecture requires redesign (more channels, wider wavelength separation, or different decision algorithm).

2. **Correction ceiling** — if corrected SSIM cannot consistently exceed 0.90 after imperfect recrystallization, the femtosecond WRITE correction loop is insufficient and alternative correction strategies are needed.

3. **Crosstalk limit** — if physical bandpass filters cannot achieve < 10% channel crosstalk at the required SNR, the LiFi I/O wavelength must be redesigned to avoid overlap with storage channels.

4. **Endurance failure** — if GST cells degrade to BLEACH threshold in < 10⁶ write cycles, the material or pulse parameters require optimization before the neuromorphic learning model is viable.

5. **Integration incompatibility** — if the holographic quartz write process thermally damages adjacent GST layer, the layer stack geometry must be revised.

---

## The Benchtop Experiment

The minimum experiment that closes the gap between TRL 3 and TRL 4:

**Prediction from Sim 1:** A Raspberry Pi camera measuring fidelity of a printed test pattern will detect a statistically significant SSIM drop when a region of the pattern is corrupted with a marker.

**Required result:** Measured SSIM drop ≥ X% (where X is predicted by sim1_holographic.py with equivalent corruption fraction) within 2 standard deviations of the Monte Carlo mean from sim1_v2_noise.py.

**Materials:** Raspberry Pi 4, Pi Camera Module 3, printed test pattern on transparency, dry-erase marker.

**Cost:** ~$0 (assumes existing Pi hardware).

**What it proves:** The mathematical model maps to physical reality. The simulation predictions are experimentally falsifiable.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 0.1 | 2026-03-23 | Initial architecture specification |
| 0.2 | 2026-04-08 | Falsifiable KPIs added, noise models referenced, TRL assessment, benchtop experiment defined |

---

*CC0 — Public Domain. No rights reserved.*  
*"Concept + simulation hypothesis, not engineering-ready architecture." — Codex, 2026-04-08*  
*"Demonstrate one benchtop experiment that matches a simulation prediction." — Codex, 2026-04-08*
