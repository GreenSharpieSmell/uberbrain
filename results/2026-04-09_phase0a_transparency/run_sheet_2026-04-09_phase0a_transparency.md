# Experiment Run Sheet

## Header

- Date: 2026-04-09
- Operator: TBD
- Experiment name: Phase 0-A transparency analog
- Related claim(s): Sim 1 / VERIFY-style corruption detection only
- Related simulation or protocol: `sim/sim1_holographic.py`

## Goal

Validate that a 2D optical capture pipeline can detect and roughly localize controlled corruption in a physical transparency analog using the same SSIM-style logic as Sim 1.

## Non-Goals

This experiment does not validate:

- 3D quartz volumetric storage
- GST phase switching
- multi-wavelength addressing
- femtosecond WRITE physics
- full Uberbrain feasibility

## Setup

- Hardware:
  - Camera: TBD
  - Light source: TBD
  - Transparency medium: TBD
  - Mount geometry: TBD
- Software/script version: TBD
- Fixed parameters:
  - Exposure settings: TBD
  - Distance camera->medium: TBD
  - Distance light->medium: TBD
  - Ambient light condition: TBD
- Environment conditions: TBD

## Predeclared Thresholds

- Primary threshold: SSIM warn threshold = TBD before data capture
- Secondary threshold: clean-vs-clean floor = TBD before data capture
- Localization tolerance: overlap or center-error tolerance = TBD before data capture

## Procedure

1. Freeze the setup and record hardware, geometry, and camera settings.
2. Capture at least 10 clean baseline frames with identical settings.
3. Apply one controlled corruption event and log intended location and approximate size.
4. Capture at least 10 post-corruption frames with no retuning.
5. Run the analysis script using the predeclared thresholds.
6. Save raw artifacts, output plots, and a short summary in this result folder.
7. Repeat the full clean -> corrupt -> measure cycle at least 3 times.

## Artifacts

- Raw files: `results/2026-04-09_phase0a_transparency/raw/`
- Config or parameter file: `results/2026-04-09_phase0a_transparency/config.json`
- Output plots: `results/2026-04-09_phase0a_transparency/plots/`
- Notes path: `results/2026-04-09_phase0a_transparency/notes.md`

## Results

- Primary metric: corrupted-vs-clean SSIM relative to predeclared warn threshold
- Secondary metric: clean-vs-clean stability and rough localization quality
- Expected outcome: clean frames remain above threshold; corrupted frames fall below threshold; damaged region is approximately localizable
- Actual outcome: TBD

## Pass / Fail

- Result: TBD
- Reason: TBD

## Pass Conditions

- Clean and corrupted captures are separable without post-hoc threshold tuning
- The damaged area is approximately localizable
- The result repeats across runs
- The final writeup states the analogy boundary explicitly

## Fail Conditions

- Lighting drift or camera auto-adjustment dominates the signal
- The threshold only works after retrospective tuning
- Damage location cannot be approximately recovered
- The team is tempted to describe the result as quartz/GST validation

## Analogy Boundary

This is a 2D optical analog experiment only. A passing result demonstrates physical SSIM-style corruption detection in an analog medium, not quartz holography, GST switching, or the full Uberbrain stack.

## Next Action

- Owner: TBD
- Action: collect hardware details, predeclare thresholds, and create the matching analysis script and config file before the first capture run
