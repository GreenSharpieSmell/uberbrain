# Uberbrain — Architecture Specification

Detailed technical specification for the Solid-State Optical Brain.

---

## Design Principles

1. **Light as the universal primitive** — signal, storage, write head, read head, verification, correction, and wireless transmission are all optical
2. **No Von Neumann split** — compute and memory unified in the same physical medium
3. **Physics-based verification** — correctness is a property of light, not a software assertion
4. **Passive persistence** — stored state requires no power to maintain
5. **Structural learning** — the system learns by forming and pruning pathways, not by updating fixed parameters
6. **Open architecture** — CC0, no restrictions, anyone can build it

---

## Layer Specification

### Layer 0 — Wireless I/O (LiFi)
- **Protocol:** Light Fidelity — optical wireless, no radio frequency
- **Wavelength:** 850nm IR (isolated from all storage wavelengths)
- **Hardware:** ESP32 with IR LED emitter/receiver pair
- **Prototype:** Phase 2 build

### Layer 1 — Neuromorphic Compute
- **Function:** Orchestrates all read/write/verify/correct operations. Maintains usage graph for Consolicant filtering. Runs CONSOLIDATE cycles during idle.
- **Prototype:** Intel Lava or Brian2 on Raspberry Pi
- **Final form:** Dedicated photonic logic array

### Layer 2 — Multi-Wavelength Laser Array
- **405nm (blue-violet):** Primary write + encode channel. Femtosecond pulses for athermal PIPC. Continuous wave for read at low power.
- **532nm (green):** Secondary read channel. Holographic reference beam.
- **650nm (red):** Tertiary encode channel.
- **Long IR:** FORGET command — thermal anneal of GST working memory.
- **850nm IR:** LiFi wireless I/O (Layer 0).
- **Prototype:** Salvaged USB Blu-ray drive (contains 405nm, 650nm, 780nm natively)

### Layer 3 — GST Working Memory Array
- **Material:** Germanium Antimony Telluride (GST) or commercial analog AgInSbTe
- **Unit:** Oomphlap — a cluster of spatially-adjacent GST sites, one per wavelength channel, read simultaneously
- **Write mechanism (prototype):** Thermal pulse — nanosecond timescale
- **Write mechanism (final):** Athermal PIPC — femtosecond pulse, ~405nm, near-zero heat
- **MLC extension:** Partial crystallization for 2–4 states per site independent of channel encoding
- **FORGET mechanism:** Long IR thermal anneal to amorphous baseline

### Layer 4 — Holographic Quartz Volume
- **Material:** Fused quartz (SiO₂), optical grade
- **Encoding:** 5D — X, Y, Z position + polarization orientation + birefringence intensity
- **Capacity:** ~360TB per 120mm × 10mm disc at current demonstrated density
- **Layers:** ~2,000 practical / ~4,000 with adaptive optics (Rayleigh-limited, see REFERENCE.md)
- **Persistence:** Billions of years at room temperature. No power required.
- **Self-verification:** Reconstruction fidelity is a direct physical property of returned light — corrupted patterns reconstruct measurably below full amplitude
- **BLEACH mechanism:** Sustained high-power pulse melts nanogratings back to smooth transparent state
- **Prototype:** Litiholo photopolymer holographic film (Phase 3)

### Layer 5 — Photodiode Read Array
- **Function:** Receives reflected/reconstructed light from Layers 3 and 4
- **Outputs:** (a) digital state value per GST channel, (b) reconstruction fidelity score per holographic read
- **Wavelength isolation:** Optical bandpass filters ensure each photodiode receives only its designated wavelength
- **Fidelity scoring:** Amplitude of reconstructed holographic wavefront relative to expected — physics-derived confidence score, not a trained heuristic

---

## The Oomphlap (Minimum Addressable Unit)

The oomphlap is the fundamental data unit of the Uberbrain — the minimum cluster that can be addressed, read, and written as a single operation.

A standard 3-channel oomphlap consists of:
- One GST site for 405nm (blue) channel
- One GST site for 532nm (green) channel  
- One GST site for 650nm (red) channel
- One holographic address in the quartz volume indexing this cluster
- One entry in the neuromorphic usage graph

Reading an oomphlap: all three channels illuminated simultaneously, all three photodiodes read simultaneously, combined state decoded, fidelity score computed.

Writing an oomphlap: neuromorphic layer specifies target state, laser array fires appropriate channel combination, re-read confirms write.

---

## Addressing Model

GST working memory: **location-addressed** — X/Y coordinates on the GST layer surface.

Holographic quartz: **content-addressed** — reference beam angle + wavelength selects the data page. No coordinate lookup. The medium reconstructs the matching pattern from any partial match.

Neuromorphic layer maintains a bridge index — mapping between GST working memory addresses and their corresponding holographic content addresses in long-term storage.

---

## Consolicant Filter Implementation

The neuromorphic layer maintains a usage graph updated on every READ operation:

```
node: holographic_address
  last_accessed: timestamp
  fidelity_history: [float]  // rolling window
  connection_weights: {address: float}  // edges to co-activated nodes
```

During CONSOLIDATE cycle:

```
for each node in usage_graph:
  orphaned = max(connection_weights.values()) < CONNECTIVITY_THRESHOLD
  degraded = mean(fidelity_history[-N:]) < FIDELITY_THRESHOLD
  stale = (now - last_accessed) > STALENESS_WINDOW
  
  if orphaned AND degraded AND stale:
    queue_for_bleach(node.holographic_address)
  elif degraded AND NOT stale:
    queue_for_repair(node.holographic_address)
```

All three thresholds are configurable parameters. Default values are an open research question — biological analogs suggest staleness window should scale with connection weight (important memories tolerate longer dormancy).

---

## Key Differences From Biological Brains

| Property | Biological Brain | Uberbrain |
|----------|-----------------|-----------|
| Signal speed | 1–120 m/s (electrochemical) | ~0.67c (photonic) |
| Heat | ~20W (glucose combustion) | Near-zero (athermal PIPC) |
| Rewiring speed | Hours–days (protein synthesis) | Nanoseconds (laser pulse) |
| Memory durability | Degrades and distorts | Holographic reconstruction — lossless |
| Hardwired overrides | Amygdala has admin privileges | No inherited evolutionary baggage |
| Introspection | Limited, distorted | Full fidelity read of own state |
| Multitasking | Serialized attention (prefrontal bottleneck) | Genuinely parallel wavelength channels |
| Self-correction | Slow, imprecise, emotional | Physics-derived confidence score, targeted correction |

---

*CC0 — Public Domain. No rights reserved. Build it.*
