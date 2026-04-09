# Uberbrain — Simulations

**Digital twins of the Uberbrain instruction set.**

Each simulation is a self-contained Python script proving one architectural layer using real mathematics. No hardware required. No special equipment. The physics is the test.

---

## Quick Start

```bash
pip install -r requirements.txt
python sim1_holographic.py
```

---

## Simulation Map

| Script | Commands Demonstrated | Key Proof |
|--------|----------------------|-----------|
| `sim1_holographic.py` | READ, VERIFY | 5.5% hologram corruption → 73.9% fidelity drop. Address is locatable. |
| `sim2_oomphlap.py` | READ, WRITE | Multi-wavelength encoding escapes binary. N channels = 2^N base states. |
| `sim3_consolicant.py` | FORGET, BLEACH, CONSOLIDATE | Orphaned + degraded + stale = bleach candidate. Active nodes protected. |
| `sim4_pipeline.py` | All six commands | Full pipeline: encode → store → corrupt → detect → correct → forget. |

---

## Sim 1 — Holographic Fidelity Scoring

**File:** `sim1_holographic.py`  
**Commands:** READ, VERIFY  
**Libraries:** NumPy, Matplotlib, scikit-image

### What It Proves

The loudest objection to the Uberbrain architecture was: *"you could never read it back successfully."*

Sim 1 disproves this with Fourier optics.

A data pattern is encoded as a holographic interference pattern using 2D FFT. The pattern is then physically corrupted (a region zeroed out, simulating bit-rot, thermal drift, or physical damage). The hologram is reconstructed via inverse FFT. The reconstruction fidelity is measured using SSIM (Structural Similarity Index).

**Key result:** 5.5% corruption of the hologram produces a 73.9% reconstruction fidelity drop. The system detects this. The corrupted address is known and targetable for correction.

### The Math

```
Object beam:   O = FFT2(data)
Reference beam: R = plane wave (constant phase)
Hologram:      H = |O + R|^2    ← stored in quartz
Reconstruction: R = |IFFT2(H)|  ← READ command output
Fidelity:      SSIM(R_clean, R_corrupted)  ← VERIFY command output
```

### Why SSIM Is The Right Metric

SSIM measures structural similarity — how much the perceptual content matches, not just pixel-by-pixel difference. In the Uberbrain context, SSIM maps directly to "how much of the stored information is recoverable." A score near 1.0 means full recovery. A score near 0.0 means unrecoverable.

Critically: this score is derived from the physics of the reconstruction. It is not a trained heuristic. You cannot fake a sharp reconstruction from a corrupted interference pattern. The SSIM value is what the light produces, not what a model predicts.

### Output

Running `sim1_holographic.py` produces:

- `uberbrain_sim1_output.png` — 2×3 figure:
  - Row 1: Stored hologram (clean / corrupted / difference)
  - Row 2: Reconstruction (clean baseline / degraded / error map)
  - VERIFY status banner
- Console VERIFY report with SSIM score, MSE, fidelity drop %, and corruption address

---

## Sim 2 — Multi-Wavelength State Encoding (oomphlap)

**File:** `sim2_oomphlap.py`  
**Commands:** READ, WRITE  
**Libraries:** NumPy, Matplotlib  
**Status:** In development — contributions welcome

### What It Proves

Binary encodes 2 states per position. The oomphlap (minimum addressable Uberbrain unit) uses N wavelength channels simultaneously, each encoding a binary GST state, producing 2^N combined states per cluster.

3 channels → 8 states. Add MLC partial crystallization → 4 states per channel → 64 states per cluster. Add intensity gradations and polarization → thousands of states per position.

This demonstrates escape from binary using only real phase-change material physics.

---

## Sim 3 — Consolicant Filter (CONSOLIDATE Cycle)

**File:** `sim3_consolicant.py`  
**Commands:** FORGET, BLEACH, CONSOLIDATE  
**Libraries:** NetworkX, NumPy, Matplotlib  
**Status:** In development — Gemini (Google) contributing

### What It Proves

The Consolicant triple-filter correctly identifies bleach candidates from a live memory graph. A node is queued for BLEACH only when simultaneously:
- **Orphaned** — connection weight to active nodes below threshold
- **Degraded** — fidelity history below repair threshold  
- **Stale** — not accessed within time window

Connected, healthy nodes are protected regardless of age. This is the Uberbrain's sleep cycle — structural refinement during idle time.

---

## Sim 4 — Full Pipeline Integration

**File:** `sim4_pipeline.py`  
**Commands:** All six (READ, VERIFY, WRITE, FORGET, BLEACH, CONSOLIDATE)  
**Status:** Pending Sim 1-3 completion

### What It Proves

The complete six-command instruction set executes as a coherent system. Data flows from input → oomphlap encoding → holographic storage → corruption → fidelity detection → targeted correction → Consolicant garbage collection.

---

## Contributing

These simulations are CC0 — public domain. Fork, extend, improve.

If you run Sim 1 and get results, open a Discussion with your SSIM scores and system specs. If you build Sim 2 or Sim 3, open a pull request.

The goal is experimental validation, not just documentation.

---

## Mathematical Grounding

The physics used in these simulations is textbook:

- **Fourier holography:** Goodman, J.W. (2005). *Introduction to Fourier Optics.* Roberts & Company.
- **SSIM metric:** Wang, Z., et al. (2004). Image quality assessment: from error visibility to structural similarity. *IEEE Transactions on Image Processing.*
- **GST phase-change:** See CITATIONS.md refs [13–15] for optical neuromorphic GST literature.
- **Holographic storage:** See CITATIONS.md refs [16–18] for volumetric storage literature.

---

*CC0 — Public Domain. No rights reserved.*  
*"You stopped throwing away the light. That's the whole thing."*
