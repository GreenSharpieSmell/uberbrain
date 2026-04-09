# Uberbrain — Formal Claim Registry

**Version:** 0.1  
**Status:** Simulation-validated. Benchtop validation pending.  
**Purpose:** Every claim in this repository mapped to a measurable metric, a pass criterion, and a current evidence level.

A reviewer should be able to take any claim from the documentation, find it here, and know exactly what evidence supports it and what would falsify it.

---

## How To Read This Document

**Evidence levels:**
- `LITERATURE` — supported by cited peer-reviewed papers
- `SIMULATION` — supported by code in `sim/`
- `TESTED` — covered by passing tests in `tests/`
- `BENCHTOP` — supported by physical experiment (none yet)
- `UNVERIFIED` — claimed but not yet supported by evidence

**Status:**
- `PASS` — meets criterion
- `PARTIAL` — partially supported
- `OPEN` — not yet tested

---

## Layer 1 — Holographic Storage Claims

---

### Claim H1: Holographic corruption is detectable via reconstruction fidelity

**Statement:** Corruption of ≥ 3% of a stored holographic interference pattern produces a measurable SSIM drop detectable by the VERIFY command.

**Metric:** SSIM(reconstruction_clean, reconstruction_corrupted)

**Pass criterion:** SSIM < FIDELITY_WARN (0.95) for all corruption regions ≥ 3% of hologram area

**Test:** `test_sim1_corruption_triggers_degradation_at_default_region`  
**Sim:** `sim1_holographic.py`, `sim1_v2_noise.py`

| Evidence | Result | Status |
|----------|--------|--------|
| Clean math (V0.1) | 5.5% corruption → SSIM drop of 73.9% | PASS |
| Monte Carlo N=200 (V0.2) | SSIM drop confirmed across noise distribution | PASS |
| Benchtop | Not yet performed | OPEN |

---

### Claim H2: Larger corruption causes proportionally lower fidelity

**Statement:** Fidelity degrades monotonically as corruption region size increases.

**Metric:** SSIM(10×10 corrupt) ≥ SSIM(25×25 corrupt) ≥ SSIM(40×40 corrupt)

**Pass criterion:** Monotonic SSIM decrease across at least 3 corruption sizes

**Test:** `test_sim1_larger_corruption_at_same_location_reduces_fidelity`

| Evidence | Result | Status |
|----------|--------|--------|
| Simulation | Monotonic decrease confirmed | PASS |
| Benchtop | Not yet performed | OPEN |

---

### Claim H3: Corruption address is physically locatable

**Statement:** The location of holographic corruption can be identified from the spatial pattern of reconstruction degradation.

**Metric:** Spatial correlation between known corruption mask and reconstruction error map

**Pass criterion:** Peak of error map within ±10 pixels of true corruption center

**Test:** Not yet implemented  
**Sim:** Error map generated in `sim1_holographic.py` visualization

| Evidence | Result | Status |
|----------|--------|--------|
| Visual inspection | Error map shows spatial correspondence | PARTIAL |
| Quantitative test | Not yet implemented | OPEN |

---

### Claim H4: Imperfect correction does NOT restore to SSIM = 1.000

**Statement:** Femtosecond WRITE correction leaves residual phase jitter. Corrected SSIM is 0.97–0.99, not 1.000.

**Metric:** SSIM(reconstruction_clean, reconstruction_corrected) across N=200 trials

**Pass criterion:** Mean corrected SSIM < 0.999 AND > 0.90

**Test:** Not yet in test suite  
**Sim:** `sim1_v2_noise.py` imperfect correction model

| Evidence | Result | Status |
|----------|--------|--------|
| V0.2 simulation | Corrected SSIM ≈ 0.97–0.99 | PASS |
| Benchtop | Not yet performed | OPEN |

---

### Claim H5: SSIM ceiling degrades over write cycles (endurance)

**Statement:** Each WRITE cycle reduces the maximum achievable SSIM by a small amount. After ~1,000 cycles, SSIM ceiling reaches the REPAIR threshold, making CONSOLIDATE necessary.

**Metric:** SSIM ceiling as a function of write cycle count

**Pass criterion:** SSIM ceiling crosses FIDELITY_WARN at some cycle count < MAX_WRITE_CYCLES

**Test:** Not yet in test suite  
**Sim:** `sim1_v2_noise.py` endurance model

| Evidence | Result | Status |
|----------|--------|--------|
| V0.2 endurance model | Degradation curve generated | SIMULATION |
| Literature (GST endurance) | ≥ 10⁹ cycles for optimized GST | LITERATURE |
| Benchtop | Not yet performed | OPEN |

---

## Layer 2 — Oomphlap Encoding Claims

---

### Claim O1: Multi-wavelength encoding produces 2^N states from N binary channels

**Statement:** Three binary GST channels read simultaneously produce 8 distinct addressable states — not 1.

**Metric:** Number of unique (written, read_back) pairs over full truth table

**Pass criterion:** All 2³ = 8 states correctly written and read back without collision

**Test:** `test_sim2_truth_table_all_binary_states_round_trip_correct`  
**Sim:** `sim2_oomphlap.py`

| Evidence | Result | Status |
|----------|--------|--------|
| Clean math (V0.1) | All 8 states correct ✓ | PASS |
| Benchtop | Not yet performed | OPEN |

---

### Claim O2: State decoding degrades gracefully under noise

**Statement:** At low noise (σ=0.01), error rate < 0.1%. At high noise (σ=0.08), error rate increases detectably. System is not noise-immune.

**Metric:** State error rate across 1,500 trials per noise level

**Pass criterion:** error_rate(σ=0.01) < 0.001 AND error_rate(σ=0.08) > error_rate(σ=0.01)

**Test:** `test_sim2_noise_causes_nonzero_error_at_high_sigma`

| Evidence | Result | Status |
|----------|--------|--------|
| Simulation | Both criteria met | PASS |
| BER vs SNR curve | Generated in sim2_v2_crosstalk.py | SIMULATION |
| Benchtop | Not yet performed | OPEN |

---

### Claim O3: BER target < 1×10⁻⁶ achievable at feasible SNR

**Statement:** The oomphlap can achieve Bit Error Rate < 10⁻⁶ at a Signal-to-Noise Ratio achievable with real optical hardware.

**Metric:** BER vs SNR curve from Monte Carlo (N=10,000 trials per point)

**Pass criterion:** BER < 10⁻⁶ at SNR ≤ 30 dB (achievable with photodiodes)

**Test:** Not yet in test suite  
**Sim:** `sim2_v2_crosstalk.py`

| Evidence | Result | Status |
|----------|--------|--------|
| V0.2 BER curve | SNR requirement identified | SIMULATION |
| Crosstalk tolerance | Max tolerable crosstalk identified | SIMULATION |
| Benchtop | Not yet performed | OPEN |

---

### Claim O4: MLC partial crystallization extends state space to 4^N

**Statement:** Four crystallization levels per GST cell extend 3-channel state space from 8 to 64 states.

**Metric:** Number of unique MLC states addressable without collision

**Pass criterion:** 4³ = 64 distinct states, each correctly written and read

**Test:** Partial — MLC write/read tested but not full 64-state truth table  
**Sim:** `sim2_oomphlap.py`

| Evidence | Result | Status |
|----------|--------|--------|
| Simulation | 6 MLC combos demonstrated | PARTIAL |
| Full 64-state truth table | Not yet tested | OPEN |

---

## Layer 3 — Consolicant Claims

---

### Claim C1: Triple-filter correctly partitions all nodes

**Statement:** Every node in the memory graph is classified as exactly one of: BLEACH, REPAIR, or PROTECTED. No node is unclassified.

**Metric:** len(bleach) + len(repair) + len(protected) == NUM_NODES

**Pass criterion:** Exact partition, no remainder

**Test:** `test_sim3_consolidation_partitions_every_node_and_bleach_rule_holds`

| Evidence | Result | Status |
|----------|--------|--------|
| Simulation | Partition verified | PASS |

---

### Claim C2: No connected node is ever bleached (architectural guarantee)

**Statement:** A node with degree centrality ≥ THRESH_ORPHAN (0.02) is never queued for BLEACH, regardless of fidelity or staleness.

**Metric:** max(centrality[n] for n in bleach_targets)

**Pass criterion:** max centrality < THRESH_ORPHAN for all BLEACH targets

**Test:** `test_sim3_consolidation_partitions_every_node_and_bleach_rule_holds` (includes assertion)  
**Sim:** `sim3_consolicant.py` main() verification

| Evidence | Result | Status |
|----------|--------|--------|
| Simulation | Assertion verified | PASS |

---

### Claim C3: Pure time-based deletion is inferior to triple-filter

**Statement:** Age-only deletion incorrectly destroys old-but-connected nodes that triple-filter protects.

**Metric:** |nodes_age_deletes ∩ protected_by_triple_filter|

**Pass criterion:** At least 1 node that age-only would delete that triple-filter correctly protects

**Test:** Not yet implemented — **BASELINE COMPARISON NEEDED**  
**Sim:** Not yet implemented

| Evidence | Result | Status |
|----------|--------|--------|
| Theoretical argument | Documented in REFERENCE.md | PARTIAL |
| Empirical comparison | Not yet implemented | OPEN |

---

### Claim C4: Pure fidelity-based deletion is inferior to triple-filter

**Statement:** Fidelity-only deletion incorrectly destroys degraded-but-connected nodes that triple-filter correctly routes to REPAIR.

**Metric:** |nodes_fidelity_deletes ∩ repair_by_triple_filter|

**Pass criterion:** At least 1 node that fidelity-only would delete that triple-filter correctly repairs

**Test:** Not yet implemented — **BASELINE COMPARISON NEEDED**

| Evidence | Result | Status |
|----------|--------|--------|
| Theoretical argument | Documented in REFERENCE.md | PARTIAL |
| Empirical comparison | Not yet implemented | OPEN |

---

## Adversarial Claims

---

### Claim A1: SSIM cannot be fooled by structured corruption

**Statement:** Corruption that is geometrically structured (e.g. regular grid pattern) is detected as reliably as random corruption of equivalent area.

**Metric:** SSIM drop for structured vs random corruption of equal area

**Pass criterion:** SSIM drop for structured corruption ≥ 80% of SSIM drop for random corruption

**Test:** Not yet implemented — **ADVERSARIAL TEST NEEDED**

| Evidence | Result | Status |
|----------|--------|--------|
| Simulation | Not yet tested | OPEN |

---

### Claim A2: Consolicant is robust to non-Barabási graph distributions

**Statement:** The triple-filter policy produces valid partitions on random graphs that do not follow the Barabási-Albert scale-free distribution.

**Metric:** Partition validity on Erdős-Rényi and Watts-Strogatz graphs

**Pass criterion:** len(bleach)+len(repair)+len(protected)==N AND no connected node in bleach

**Test:** Not yet implemented — **ADVERSARIAL TEST NEEDED**

| Evidence | Result | Status |
|----------|--------|--------|
| Simulation | Only Barabási-Albert tested | PARTIAL |

---

## Open Claims (unverified)

These claims appear in the documentation but have no simulation or literature support yet:

| Claim | Location | What's needed |
|-------|----------|---------------|
| Contact lens form factor achievable | README, ROADMAP | Hardware miniaturization roadmap |
| Near-zero heat from athermal PIPC | REFERENCE.md | Benchtop fs laser experiment |
| 360TB per disc achievable | README | Already in literature (ref [17]) — LITERATURE |
| LiFi I/O at ≥ 1 Gbps | SPECIFICATIONS | Already in literature (ref [30]) — LITERATURE |
| Energy per READ < 1 pJ | SPECIFICATIONS | Not yet modeled |
| CONSOLIDATE cycle time < 1% | SPECIFICATIONS | Not yet modeled |

---

## Claim Summary

| Layer | Total claims | PASS | PARTIAL | OPEN |
|-------|-------------|------|---------|------|
| Holographic (H) | 5 | 3 | 1 | 3 |
| Oomphlap (O) | 4 | 2 | 1 | 3 |
| Consolicant (C) | 4 | 2 | 1 | 3 |
| Adversarial (A) | 2 | 0 | 0 | 2 |
| **Total** | **15** | **7** | **3** | **11** |

**7/15 claims have passing simulation evidence. 11 open items define the next phase of work.**

---

## Next Priority Tests

In order of impact:

1. **C3, C4** — baseline comparison: age-only vs fidelity-only vs triple-filter (proves the Consolicant is better than simpler alternatives)
2. **H3** — quantitative corruption localization test (spatial accuracy of VERIFY)
3. **A2** — Consolicant on non-Barabási graphs (adversarial robustness)
4. **O4** — full 64-state MLC truth table
5. **A1** — structured corruption adversarial test
6. **H4, H5** — endurance model tests

---

*CC0 — Public Domain. No rights reserved.*  
*"Turn each narrative claim into a measurable statement." — Codex, 2026-04-08*
