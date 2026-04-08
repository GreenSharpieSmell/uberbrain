# Uberbrain — Prototype Build Plan

**Proving the architecture for approximately $250.**

The prototype does not store petabytes. It proves the rules that make petabytes possible later. Same reason the Wright Brothers didn't build a 747 first.

---

## Safety — Buy This Before Everything Else

**Laser safety goggles, 190–540nm, OD5+ — ~$18**

The 405nm Blu-ray write laser is Class IIIB. It will damage your eyes before you feel anything. No pain warning. No second chance. The goggles cover both 405nm and 532nm. They go on before the drive opens. Non-negotiable.

---

## Phase 0-A — Transparency MVP (~$0)
*Designed by Gemini, 2026-03-23. Do this before any other hardware arrives.*

This experiment proves the complete feedback loop logic — fidelity scoring, address-level error detection, and correction triggering — using only a Raspberry Pi, a camera module, a printer, and a dry-erase marker.

| Component | Uberbrain Role | Shoebox Analog |
|-----------|---------------|----------------|
| Medium | Holographic Quartz | 3-layer transparency stack in a printed holder |
| Logic | Neuromorphic Layer | Raspberry Pi running Python + OpenCV |
| Sensor | Photodiode Array | Pi Camera Module 3 |
| Light Show | WDM Laser Array | RGB LED strip or flashlight + prism |

**Experiment flow:**
1. **Map** — Pi reads the 3-layer transparency stack. Each color channel = a memory address.
2. **Corrupt** — Dry-erase marker smudge on one layer. This is your hallucination event.
3. **Detect** — OpenCV script compares camera feed to the gold master image. Pi flags the fidelity drop.
4. **Correct** — Pi outputs: `ADDRESS [BLUE_LAYER_COORD_X] DEGRADED. TRIGGERING CORRECTION.` You clean the slide. Pi re-reads and confirms restoration.

**What you've proven:** The feedback loop is real. Fidelity scoring produces actionable physical addresses. The system distinguishes intact from corrupted memory using light. The Consolicant logic works. All for $0 before a single part ships.

---

## Phase 0-B — Multi-Wavelength Separation (~$100)

Prove that different wavelengths of light can write and read to a phase-change medium independently without interfering with each other. This is the foundational claim of the entire architecture.

**Parts:**
- Raspberry Pi 4 (4GB) + power supply — ~$55
- MicroSD card 32GB — ~$8
- External USB Blu-ray drive (read/write) — ~$25–45 (eBay used is fine)
- BD-RE rewritable discs ×5 — ~$12

**The BD-RE disc is the GST analog.** It uses AgInSbTe phase-change alloy — the commercial cousin of GST. The USB Blu-ray drive already contains three wavelengths: 405nm (blue-violet write), 650nm (red read), 780nm (IR CD). You are not adding these — you are accessing what is already there.

**Goal:** Blue laser writes a state to the disc. Red laser reads it back. Neither interferes with the other. Pi logs the result. You have demonstrated wavelength isolation on real hardware for $100.

---

## Phase 1 — Multi-Wavelength State Encoding (~$38–63)

Prove that parallel wavelength channels produce combinatorial states beyond binary.

**Parts:**
- Photodiode array (BPW34 or similar) — ~$8
- Optical bandpass filters, 405nm + 650nm — ~$15–40 (Thorlabs for precision, Amazon for budget)
- Breadboard + jumper wires + GPIO breakout for Pi — ~$15

**The bandpass filters are the cross-stream prevention.** Each filter passes only its wavelength to its dedicated photodiode. Physical isolation. Under $40.

**Goal:** Demonstrate that Blue+Red combined state encoding produces 4+ distinct values from 2 binary channels. First oomphlap achieved.

---

## Phase 2 — LiFi Wireless Layer (~$22)

Prove wireless optical data transmission as the input/output layer. 850nm IR — a completely separate wavelength from the storage stack, zero interference.

**Parts:**
- ESP32 dev boards ×2 (one transmitter, one receiver) — ~$14
- IR LED emitters + IR photoreceivers (850nm) — ~$8

**Goal:** Data transmitted wirelessly via light, decoded by Pi, written to phase-change medium, read back, transmitted out. Full optical pipeline with no radio involved.

---

## Phase 3 — Holographic Storage Layer (~$62)

Prove content-addressed storage using real interference pattern recording.

**Parts:**
- Litiholo hologram kit (litiholo.com) — ~$50
- 5mW 532nm green laser pointer — ~$12

**Note:** Your goggles cover 532nm. Keep them on.

**Goal:** Record a real interference pattern in photopolymer film. Demonstrate that different reference beam angles retrieve different stored pages from the same physical volume. Prove content-addressed retrieval.

---

## Phase 4 — Neural Layer (Free)

Add the neuromorphic compute layer that directs what gets written, monitors fidelity scores, runs CONSOLIDATE cycles, and applies the Consolicant filter.

**Software:**
- Intel Lava — open source neuromorphic framework: https://github.com/lava-nc/lava
- Brian2 — biologically realistic neural simulation: https://briansimulator.org

**Goal:** Neural software directs optical writes. Monitors fidelity scores from photodiode array. Triggers targeted correction pulses. Applies Consolicant triple-filter during idle CONSOLIDATE cycles. The system learns by forming and pruning pathways rather than updating fixed parameters.

---

## Full Roadmap

| Stage | What it proves | Cost |
|-------|---------------|------|
| Phase 0-A | Feedback loop + fidelity scoring logic | $0 |
| Phase 0-B | Wavelength isolation on real hardware | ~$100 |
| Phase 1 | Escape from binary | ~$50 |
| Phase 2 | LiFi optical wireless layer | ~$22 |
| Phase 3 | Content-addressed holographic memory | ~$62 |
| Phase 4 | Learning, self-correction, CONSOLIDATE | $0 |
| **Total** | | **~$250** |

---

## Notes On The Femtosecond Wall

The Raspberry Pi GPIO cannot generate femtosecond pulses. This is a hard physical limit — you cannot toggle a pin fast enough. This means the prototype operates in the thermal switching regime (nanosecond pulses, conventional Blu-ray laser timing).

This does not invalidate the prototype. The femtosecond athermal switching is the **miniaturization and heat-elimination path** — it's what makes the contact lens form factor and near-zero heat possible. The prototype proves the architectural logic at a slower timescale. The logic is identical. Only the speed and heat profile differ.

When chip-scale femtosecond laser sources become accessible (active research area, following the same miniaturization curve as every laser before them), the prototype upgrades to athermal operation without changing the architecture.

State the athermal scaling path clearly in any documentation accompanying prototype demonstrations. The shoebox runs thermal. The final system runs athermal. Same architecture. Different pulse duration.

---

*CC0 — Public Domain. No rights reserved. Build it.*
