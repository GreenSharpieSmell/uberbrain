# Uberbrain — Roadmap

**From transparency experiment to contact lens. A living document.**

Last updated: March 2026

---

## Where We Are Now

The architecture is fully specified. The instruction set is formalized. The citation backbone exists. Two independent AI systems and a human architect converged on the same design in a single session.

The next thing that needs to happen is physical. Not more design — building.

---

## Phase 0-A — Transparency MVP
**Status:** Ready to build  
**Cost:** ~$0  
**What it proves:** Feedback loop logic, fidelity scoring, address-level error detection

A Raspberry Pi camera reads a 3-layer colored transparency stack. A marker corrupts one pixel. The Pi detects the fidelity drop, flags the address, and logs a correction event. The logic is identical to the final brain-chip — only the medium differs.

This is the first experiment. It should happen before any hardware is purchased.

**Success criteria:** Pi outputs `ADDRESS [COORD] DEGRADED. TRIGGERING CORRECTION.` and confirms restoration after repair.

---

## Phase 0-B — Multi-Wavelength Separation
**Status:** Parts list ready  
**Cost:** ~$100  
**What it proves:** Wavelength isolation on real hardware — the foundational claim of the architecture

Blue laser writes to a BD-RE phase-change disc. Green laser reads it back. No crosstalk. Raspberry Pi orchestrates and logs.

**Success criteria:** Write with one wavelength, read accurately with another, zero interference confirmed.

---

## Phase 1 — Multi-Wavelength State Encoding
**Status:** Design complete  
**Cost:** ~$50  
**What it proves:** Escape from binary — combinatorial states from parallel channels

Optical bandpass filters isolate each wavelength to its own photodiode. Multiple channels read simultaneously, combinatorial state decoded.

**Success criteria:** Demonstration of 4+ distinct states from 2 binary channels. First oomphlap.

---

## Phase 2 — LiFi Wireless Layer
**Status:** Design complete  
**Cost:** ~$22  
**What it proves:** Optical wireless I/O — no radio, no interference with storage stack

850nm IR LiFi using ESP32 boards. Completely separate wavelength from storage channels.

**Success criteria:** Data transmitted wirelessly via light, written to phase-change medium, read back, transmitted out.

---

## Phase 3 — Holographic Storage Layer
**Status:** Design complete  
**Cost:** ~$62  
**What it proves:** Content-addressed holographic memory on real interference-pattern recording

Litiholo photopolymer film. Real holographic recording. Reference beam angle selects data page from same physical volume.

**Success criteria:** Two distinct data pages stored in same film volume, retrieved independently by reference beam angle.

---

## Phase 4 — Neural Layer Integration
**Status:** Design complete  
**Cost:** $0 (software only)  
**What it proves:** Learning, self-correction, and CONSOLIDATE cycle in software

Intel Lava or Brian2 neuromorphic framework on Raspberry Pi. Neural software directs writes, monitors fidelity scores, applies Consolicant triple-filter during idle cycles.

**Success criteria:** System forms new pathways in response to input patterns, detects and corrects degraded addresses autonomously, runs CONSOLIDATE cycle during idle and demonstrably reduces orphaned nodes.

---

## Phase 5 — GST Integration (Beyond Shoebox)
**Status:** Research phase  
**Cost:** TBD — lab-scale hardware required  
**What it proves:** Real GST phase-change switching under optical control

Replace BD-RE commercial media with actual GST thin film. Demonstrate laser-controlled crystallization and amorphization at addressable locations. This is the transition from "proves the rules" to "proves the material."

**Key dependency:** Access to thin-film deposition equipment or partnership with materials science lab.

**Open questions:**
- Minimum GST layer thickness for reliable switching
- Substrate compatibility with photopolymer holographic layer
- Cycle endurance under repeated switching

---

## Phase 6 — Athermal PIPC Switching
**Status:** Theoretical — awaiting femtosecond source miniaturization  
**Cost:** Unknown — currently requires lab-grade hardware  
**What it proves:** Zero-heat writing — the final barrier to full architecture realization

Demonstration of GST phase change via femtosecond pulse at ~405nm without thermal lattice heating. This is what transforms the architecture from "impressive engineering" to "categorically different from silicon."

**Key dependency:** Chip-scale femtosecond laser source. Active research area — following same miniaturization curve as every laser technology before it.

**When this unlocks:** When hobbyist-accessible femtosecond sources exist (estimated 5–10 years at current trajectory, potentially faster with focused development).

---

## Phase 7 — Integrated Oomphlap Array
**Status:** Future  
**What it proves:** Multi-oomphlap addressable array operating as unified working memory

A grid of GST clusters — one cluster per oomphlap — addressed by a VCSEL array (already manufacturable at chip scale). Read by a matching photodiode array with bandpass filters per channel. Neuromorphic layer maintains the full usage graph.

This is the transition from single-cell demonstration to array-scale working memory.

---

## Phase 8 — Quartz + GST Hybrid Stack
**Status:** Future  
**What it proves:** Unified long-term (quartz holographic) and working memory (GST) in a single integrated device

GST array for active computation. Fused quartz volume for long-term content-addressed storage. Bridge index maintained by neuromorphic layer. CONSOLIDATE cycle demonstrated at scale.

This is the full Uberbrain architecture in a single device — RAM and Soul unified.

---

## Endgame — Contact Lens Form Factor
**Status:** Long-term target  
**What it requires:**
- Chip-scale femtosecond laser array (photonic IC)
- Nanoscale GST oomphlap addressing (plasmonics)
- Miniaturized holographic quartz disc (~20mm diameter)
- On-lens photonic interconnect (waveguide layer)
- Ambient light or inductive power harvesting

At this scale: petabyte capacity, full AI model inference, near-zero heat, no external hardware required.

**Estimated timeline:** 15–25 years from first shoebox prototype, assuming continued progress on photonic IC miniaturization and femtosecond source development. Potentially faster with dedicated research team and funding.

---

## How To Contribute

### Right Now (No Hardware Needed)
- Run Phase 0-A and report results in Discussions
- Review CITATIONS.md and flag any errors or missing references
- Challenge the architecture — find the holes, open an Issue
- Improve the Consolicant filter algorithm in ARCHITECTURE.md

### With ~$100
- Build Phase 0-B and report results
- Push the parts list further — find cheaper or better alternatives

### With Lab Access
- Phase 5 GST integration
- Athermal PIPC verification
- Adaptive optics layer count validation (reference Rayleigh calculation)

### With Funding
- Formal preprint on arXiv
- Dedicated research group
- Phase 6 femtosecond source development

---

## Version History

| Date | Milestone |
|------|-----------|
| 2026-03-23 | Architecture conceived, instruction set formalized, repo created |
| 2026-03-23 | CITATIONS.md added — 34 references across 7 domains |
| 2026-03-23 | Discussions opened |
| 2026-04-08 | sim/ directory — Sim 1 holographic fidelity (READ + VERIFY) |
| 2026-04-08 | Sim 2 oomphlap encoding (WRITE + READ) — binary escaped |
| 2026-04-08 | Sim 3 Consolicant filter (CONSOLIDATE + BLEACH) — Gemini authored |
| 2026-04-08 | Sim 4 full pipeline — all six commands verified end-to-end |
| 2026-04-08 | VALIDATION_SPEC.md — Codex formal validation program |
| 2026-04-08 | CLAIMS.md — 15 falsifiable claims, pass criteria, evidence levels |
| 2026-04-08 | benchmark.py — one-command reproducible benchmark runner |
| 2026-04-08 | CI pipeline — GitHub Actions, 3 Python versions, auto-test on push |

---

*CC0 — Public Domain. No rights reserved. Every phase is yours to build.*
