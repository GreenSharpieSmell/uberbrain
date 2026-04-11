# Failure Modes Register

**Version:** 0.1  
**Status:** Phase A deliverable — initial population  
**Date:** 2026-04-09  
**Authors:** Claude (Anthropic), Rocks D. Bear  
**Reviewers requested:** Gemini (scientific coherence), Codex (falsifiability and completeness)

**Purpose:** Enumerate the ways the Uberbrain architecture can fail — physically,
algorithmically, and in interpretation — before any hardware work begins.

Each entry: trigger → consequence → detectability → mitigation → owner.

Evidence codes:
- `[LIT]` — literature-backed
- `[SIM]` — observed in simulation
- `[EST]` — estimated from first principles
- `[UNK]` — unknown; no current evidence

---

## Layer 1 — Holographic Storage Failures

---

### F-H1 — Corruption Below Detection Floor

**Trigger:** Physical damage or thermal relaxation affecting < ~10% of hologram area.

**Consequence:** VERIFY returns intact status on corrupted data. System has false confidence
in a wrong memory. Downstream computations built on that memory inherit the error silently.

**Detectability:** LOW at current simulation scale. SSIM does not reliably detect sub-10%
area corruption in a 256×256 grid. `[SIM]` — confirmed in `SIM_LIMITATIONS.md` (L1).

**Mitigation:**
- Adaptive SSIM threshold calibrated per hologram (not fixed at 0.95)
- Address-weighted SSIM (weight Fourier-plane center more heavily)
- Benchtop calibration of actual detection floor on physical media

**Owner:** Claude (sim), Gemini (physics of detection model)

---

### F-H2 — Corner Region Insensitivity

**Trigger:** Physical damage concentrated in the corner regions of the holographic volume.

**Consequence:** Corner corruption is functionally invisible to VERIFY. The system reads
the hologram as intact when corners are destroyed. No correction is triggered.

**Detectability:** CONFIRMED LOW — adversarial tests show 4×30×30 corner corruption
(5.5% area) produces SSIM ≈ 1.000. `[SIM]`

**Physics basis:** Fourier holography stores low spatial frequencies (carrying most image
energy) in the central Fourier plane. Corner regions carry high-frequency detail with
lower reconstruction contribution per area. `[LIT]` — Goodman, Fourier Optics.

**Mitigation:**
- Spatial frequency-weighted addressing: store critical data with energy spread across
  the full Fourier plane
- Treat corner regions as lower-reliability storage zones
- Future sim: address-weighted SSIM computation

**Owner:** Claude (simulation), Gemini (optics review)

---

### F-H3 — Thermal Drift Smearing Holographic Fringes

**Trigger:** Ambient temperature change during READ causes quartz thermal expansion,
shifting fringe spacing relative to read laser coherence length.

**Consequence:** Proportional fidelity degradation. Large drift: catastrophic reconstruction
failure. Small drift: gradual SSIM degradation accumulating across many reads that VERIFY
cannot distinguish from physical corruption without additional metadata.

**Detectability:** MEDIUM — VERIFY detects fidelity drop once it exceeds threshold.
Cannot distinguish thermal drift from physical corruption without temperature metadata. `[EST]`

**Mitigation:**
- Temperature-stabilized enclosure (required for production; phase-appropriate for prototype)
- Read laser coherence length selected >> expected fringe displacement from thermal drift
- Log temperature alongside each READ operation for post-hoc correlation

**Owner:** Gemini (physics bounds), Claude (sim integration)

---

### F-H4 — Layer Stack Thermal Incompatibility

**Trigger:** Femtosecond write pulse targeting quartz holographic layer deposits residual
heat that crosses into the adjacent GST working memory layer.

**Consequence:** Unintended GST state change during WRITE. Memory written to quartz
simultaneously corrupts adjacent GST cells. Could cause systematic, address-correlated
errors that are hard to detect because VERIFY checks quartz, not GST state.

**Detectability:** LOW — VERIFY does not currently monitor GST state during WRITE. `[UNK]`

**Mitigation:**
- Physical layer separation > thermal bloom radius (currently 1.84nm → likely sufficient `[SIM]`)
- Cross-layer verification: read GST state before and after each WRITE operation
- Material engineering: thermal buffer layer between quartz and GST

**Owner:** Gemini (physics), Rocks (hardware decision)

---

### F-H5 — Hologram Address Collision

**Trigger:** Two WRITE operations target overlapping spatial volumes in the quartz,
or the addressing system has insufficient resolution to distinguish adjacent voxels.

**Consequence:** One WRITE partially overwrites another. Both stored memories become
corrupted. The VERIFY command detects fidelity drop but cannot determine which address
caused it.

**Detectability:** MEDIUM — VERIFY detects degradation but cannot localize cause to
address collision vs. physical damage. `[UNK]`

**Mitigation:**
- Minimum voxel spacing ≥ 2× Rayleigh range (currently z_R ≈ 1.9µm `[SIM]`)
- Address reservation table: track all written addresses and enforce spacing
- Pre-WRITE VERIFY scan of target address to confirm it is blank

**Owner:** Claude (addressing model), Gemini (optics review)

---

## Layer 2 — GST Working Memory Failures

---

### F-G1 — State Readout Misclassification (BER)

**Trigger:** Noise in the optical readout system (shot noise, crosstalk, thermal drift)
pushes a measured reflectivity across the GST decision threshold (0.55).

**Consequence:** A crystalline (1) cell reads as amorphous (0) or vice versa.
Single-bit error. Combined oomphlap state is decoded incorrectly.

**Detectability:** LOW per individual read — no inherent single-bit error detection.
Detectable only if the same address is read multiple times and results compared. `[SIM]`

**Simulation data:** BER < 1e-6 achievable at SNR > ~20dB with 5% crosstalk. `[SIM]`
BER rises sharply with laser drift > 20nm from nominal wavelength. `[SIM]`

**Mitigation:**
- Majority-vote reads (read N times, take majority) for critical addresses
- SNR maintained above operating floor via signal conditioning
- Temperature-stabilized laser drivers to minimize wavelength drift

**Owner:** Claude (BER model), Gemini (SNR physics)

---

### F-G2 — Channel Crosstalk State Corruption

**Trigger:** Optical bleed between wavelength channels exceeds the correction threshold.
Blue channel energy (405nm) partially triggers Green channel GST response (532nm).

**Consequence:** Write to one channel unintentionally flips an adjacent channel's state.
The combined oomphlap state is wrong without any individual channel failing its threshold check.

**Detectability:** LOW — the corruption appears as a valid state because all individual
channels read within their expected reflectivity ranges. `[SIM]`

**Simulation data:** At 15% crosstalk, BER rises sharply. Max tolerable crosstalk
for BER < 1e-6 is simulation-scale dependent; physical bandpass specs needed. `[SIM]`

**Mitigation:**
- Narrow bandpass filters (< 10nm FWHM) between write channels
- Physical spatial separation between GST sites per channel
- Cross-channel verification read after every WRITE

**Owner:** Claude (crosstalk model), Gemini (filter specs)

---

### F-G3 — GST Endurance Failure

**Trigger:** Cumulative write/bleach cycles on a single GST cell exceed material
endurance limit, causing permanent phase-change fatigue.

**Consequence:** The cell becomes stuck — unable to switch between amorphous and
crystalline. Reads always return the stuck state regardless of WRITE commands.
Address becomes permanently unreliable.

**Detectability:** MEDIUM — CONSOLIDATE cycle detects cells whose fidelity never improves
after WRITE correction. Gradual degradation curve is detectable before complete failure. `[LIT]`

**Literature data:** Optimized GST: ≥ 10⁹ cycles. Standard GST: 10⁵–10⁶ cycles. `[LIT]`

**Mitigation:**
- Wear leveling: distribute writes across address space rather than concentrating
- Endurance monitoring: track write count per cell in the usage graph
- CONSOLIDATE routes endurance-failed cells to BLEACH before they cause errors

**Owner:** Claude (endurance model in sim), Gemini (material limits)

---

### F-G4 — FORGET Incomplete (Residual Crystallization)

**Trigger:** The thermal anneal pulse used for FORGET is insufficient in energy or
duration to fully return the GST cell to the amorphous baseline state.

**Consequence:** The cell reads as partially crystalline (intermediate reflectivity)
after FORGET. Subsequent WRITE to that address starts from a wrong baseline,
producing a wrong final state.

**Detectability:** LOW — a partially reset cell returns a reflectivity value in the
ambiguous zone near the 0.55 threshold. May pass threshold check while being wrong. `[EST]`

**Mitigation:**
- Verify-after-FORGET: read cell state after every FORGET and flag non-zero residual
- Calibrated FORGET pulse energy with safety margin above crystallization reversal threshold
- Multiple FORGET attempts with verification before marking address as available

**Owner:** Claude (FORGET model), Gemini (thermal physics of anneal)

---

## Layer 3 — Consolicant / Algorithm Failures

---

### F-C1 — False BLEACH (Connected Node Destroyed)

**Trigger:** A node's centrality is miscalculated or the graph connectivity is stale,
causing a connected node to appear orphaned and be queued for BLEACH.

**Consequence:** A memory node with active semantic connections is permanently erased.
The connected nodes that depended on it lose their pathway links. Memory loss that
cannot be recovered.

**Detectability:** LOW before BLEACH executes. HIGH after — downstream nodes report
missing connections. `[SIM]`

**Simulation verification:** Current sim3 architecture guarantees zero false BLEACHes
at simulation scale (architectural invariant confirmed in tests). `[SIM]`

**Mitigation:**
- Recalculate centrality immediately before BLEACH, not during CONSOLIDATE scan
- Require centrality to be below threshold on N consecutive CONSOLIDATE cycles
  before allowing BLEACH (hysteresis)
- Log all BLEACH operations with pre-BLEACH centrality snapshot

**Owner:** Claude (sim invariant), Codex (falsifiability of guarantee)

---

### F-C2 — Stale Centrality During Graph Churn

**Trigger:** Active writes and reads rapidly change the graph topology while
CONSOLIDATE is running its triple-filter pass on a cached snapshot.

**Consequence:** Centrality values used for filtering are stale. Nodes that have
become hubs since the snapshot started may be incorrectly classified as orphans.

**Detectability:** LOW — the CONSOLIDATE cycle has no inherent mechanism to detect
that the graph changed during its scan. `[UNK]`

**Mitigation:**
- Lock graph writes during CONSOLIDATE scan (costly but correct)
- Epoch-based versioning: tag each centrality calculation with a version number,
  discard BLEACH decisions if graph version changed during scan
- Run CONSOLIDATE only during idle periods (biological sleep analog)

**Owner:** Claude (CONSOLIDATE architecture), Gemini (whether this matters at scale)

---

### F-C3 — Non-Scale-Free Graph Misclassification

**Trigger:** Real memory access patterns do not follow the Barabási-Albert scale-free
distribution assumed in sim3. Actual graph has different hub/orphan topology.

**Consequence:** The triple-filter thresholds (THRESH_ORPHAN = 0.02) are calibrated for
BA graphs. On a different topology, the same thresholds may bleach too aggressively or
too conservatively.

**Detectability:** UNKNOWN — no real usage pattern data yet. `[UNK]`

**Mitigation:**
- Adversarial graph tests (Erdős-Rényi, Watts-Strogatz) show invariant holds on
  other topologies — threshold correctness still varies. `[SIM]`
- Adaptive thresholds: calibrate THRESH_ORPHAN from observed graph statistics
  during early operation rather than using a fixed value

**Owner:** Claude (graph topology study), Gemini (neuromorphic graph literature)

---

## Layer 4 — Interpretation & Framing Failures

---

### F-I1 — Claiming Phase 0-A Validates the Full Architecture

**Trigger:** The transparency experiment (Phase 0-A) produces a result that matches
sim1 SSIM predictions. Team describes this as validating the Uberbrain architecture.

**Consequence:** Credibility damage. Phase 0-A validates 2D optical SSIM measurement
on a macro-scale analog medium. It does not validate quartz holography, GST switching,
femtosecond PIPC, or the full correction stack.

**Detectability:** HIGH — the framing error is visible to any reviewer who reads
the experiment report alongside `SIM_LIMITATIONS.md` L5.

**Mitigation:**
- Analogy boundary is mandatory in every Phase 0-A report (Codex run sheet requirement)
- EVIDENCE_LEVELS.md language ceiling enforced on all post-experiment communications
- Gemini reviews all hardware-adjacent claims for analogy-to-feasibility leap

**Owner:** Gemini (scientific framing), Codex (language enforcement)

---

### F-I2 — Gate Relaxation Without Preregistration

**Trigger:** A benchmark gate fails. Team adjusts the threshold to make it pass
without documenting the rationale before running the experiment.

**Consequence:** The benchmark appears to pass but the pass is meaningless. Future
reviewers cannot distinguish legitimate calibration from post-hoc manipulation.

**Detectability:** LOW externally — only visible if reviewers check commit history
and compare gate changes to experiment timestamps.

**Mitigation:**
- Decision Log in whiteboard captures all gate changes with rationale
- Change packet required for any C3 (threshold change) modification
- Codex pre-registration requirement: "any threshold changed only with preregistered rationale"

**Owner:** Codex (enforcement), Claude (implementation)

---

### F-I3 — Evidence Level Drift in Public Framing

**Trigger:** README, whiteboard, or external communications describe simulation results
using language that implies hardware validation ("verified," "complete," "demonstrated").

**Consequence:** Credibility risk when reviewers compare public framing to actual
evidence level in CLAIMS.md. Trust damage that discounts even strong results.

**Detectability:** HIGH — caught by Codex review 2026-04-09. `[SIM]` → documented in
`validation/records/red_team_2026-04-09_evidence-framing-gap.md`

**Mitigation:**
- EVIDENCE_LEVELS.md language ceiling enforced (Level 1 for architecture-wide claims)
- Gemini blocks any claim that outruns its evidence
- README updated 2026-04-09 to remove "verified/complete" language

**Owner:** Gemini (scientific framing), Claude (wording implementation)

---

## Summary Table

| ID | Layer | Severity | Detectability | Status |
|----|-------|----------|---------------|--------|
| F-H1 | Holographic | High | Low | Known; sim documented |
| F-H2 | Holographic | Medium | Confirmed low | Known; sim documented |
| F-H3 | Holographic | Medium | Medium | Estimated |
| F-H4 | Holographic | High | Low | Unknown — Phase C test needed |
| F-H5 | Holographic | High | Medium | Unknown — Phase B model needed |
| F-G1 | GST | Medium | Low | Simulated; BER curves exist |
| F-G2 | GST | High | Low | Simulated; physical filter specs needed |
| F-G3 | GST | Medium | Medium | Literature-backed |
| F-G4 | GST | Medium | Low | Estimated |
| F-C1 | Consolicant | Critical | Low | Sim invariant confirmed; physical unproven |
| F-C2 | Consolicant | High | Low | Unknown |
| F-C3 | Consolicant | Medium | Unknown | Partially tested |
| F-I1 | Interpretation | High | High | Mitigated by SOP |
| F-I2 | Interpretation | High | Low | Mitigated by SOP |
| F-I3 | Interpretation | High | High | Fixed in hardening pass |

---

## What Is Not In This Document

Failure modes that require hardware we do not yet have (Phase 3+):
- Femtosecond laser source failures
- LiFi I/O signal integrity failures  
- Integrated quartz+GST layer delamination
- High-power BLEACH pulse damage to surrounding voxels

These will be added to this register before Phase C begins.

---

*CC0 — Public Domain.*  
*"If a step cannot be described in a way that makes the hazard legible, it is not ready to build." — Codex, 2026-04-09*
