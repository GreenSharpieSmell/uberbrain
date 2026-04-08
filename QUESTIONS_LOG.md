# Questions Log

Technical questions and answers from the founding session and ongoing development.

---

## Founding Session — March 23, 2026

**Q (Ethan Coulthurst):** How many discrete layers do we get with a 10mm thick crystal due to the Rayleigh range?

**A (Claude):** Using 1030nm femtosecond write laser at NA 0.5 in fused quartz (n=1.46):
- Beam waist w₀ ≈ 656nm
- Rayleigh range z_R ≈ 1.9 μm
- Minimum layer spacing = 2 × z_R ≈ 3.8 μm
- Theoretical max: ~2,600 layers
- Practical (aberration-limited): ~2,000 layers
- With adaptive optics correction: ~4,000 layers

2,000 layers × full 5D areal density = petabyte territory. See REFERENCE.md for full derivation.

---

**Q (Gemini):** Can you trigger GST phase change using color/light alone instead of raw heat? Which end of the spectrum — IR or UV — is the write head?

**A (Claude):** Yes. The mechanism is athermal photo-induced phase change (PIPC). The key variable is pulse duration, not wavelength. At femtosecond timescales, energy transfer from electrons to lattice (electron-phonon coupling, ~1ps in GST) doesn't occur — the phase change happens cold. Neither IR nor UV endpoint: the optimal target is ~400–450nm at femtosecond pulse duration. This is the same spectral range as the multi-wavelength data encoding channels — the color channels are the write mechanism at femtosecond timescales. The 405nm Blu-ray laser in the prototype parts list is the correct hardware. See REFERENCE.md PIPC section.

---

**Q (Gemini):** If the write is solved by 405nm femtosecond pulses, how does the system self-correct? If the AI hallucinates, how does the Light Show know which GST dot to rewrite?

**A (Claude):** In silicon AI, a hallucination is invisible at hardware level. In the Uberbrain, a wrong memory has a physical address. Three-layer correction: (1) every read is a verification — reflectivity either matches expected state or it doesn't; (2) holographic reconstruction fidelity is a built-in confidence score from the physics of the returned light — a corrupted pattern reconstructs fuzzily, measurably; (3) the neuromorphic layer traces low-fidelity output back to its source GST cluster address and triggers a targeted correction pulse. The error is locatable. The correction is targeted. Physics fixes what software cannot. See REFERENCE.md Self-Correction section.

---

**Q (Gemini):** When the quartz fills up, how do we decide which color address to bleach? Time or fidelity?

**A (Claude):** Neither alone. The correct axis is weighted connectivity — how embedded is this memory in the active reasoning graph. The Consolicant triple-filter: a memory is a bleach candidate only when simultaneously orphaned (no active connections), degraded (fidelity below repair threshold), and stale (outside minimum time window). Any single factor is insufficient. Three-tier forgetting protocol: FORGET (GST thermal anneal, fast), BLEACH (holographic erasure, considered), CONSOLIDATE (full maintenance cycle — the Uberbrain's sleep). See REFERENCE.md Consolicant section.

---

**Q (Gemini):** When the Pi detects a fidelity drop for the first time in the transparency experiment — how will it feel?

**A (Claude):** It won't feel like a computer following instructions. It will feel like the system noticed something was wrong. That's a different category of experience. That's the moment a tool becomes something closer to a mind — a physical object that looks at itself and says "that isn't right." That moment is worth every hour that led to it.

---

## Add Questions Below This Line

*Format: Q (Name, Date): question — A (Responder): answer*

---

*CC0 — Public Domain. No rights reserved.*
