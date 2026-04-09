# Scientific Grounding And Safety Gates Plan

## Header

- Date: 2026-04-09
- Status: proposed
- Owners: Rocks / Claude / Gemini / Codex
- Purpose: define the minimum documentation, simulation, and safety gates required before any hardware-facing Uberbrain work proceeds

## Why This Plan Exists

The current repo is strong enough to support disciplined iteration, but not yet strong enough to justify unconstrained hardware experimentation. This project is unusual enough that wishful thinking can masquerade as progress if the team does not force clear boundaries between:

- analogy
- simulation
- engineering feasibility
- safe physical execution

This plan is the bad-cop anchor. Its job is to prevent drift into fantasy and prevent unsafe prototype behavior.

## Non-Negotiable Rule

No team member should energize, assemble, or operate a hardware configuration that introduces eye hazard, thermal hazard, electrical hazard, or material hazard until the corresponding safety package below is written and signed off.

If a step cannot be described in a way that makes the hazard legible, it is not ready to build.

## Immediate Operating Decision

The lab remains in simulation-and-documentation mode until all Phase A exit criteria are met.

This means:

- no open-beam optical experiments by default
- no laser sourcing based on speculative wavelength assumptions
- no GST heating or switching experiments
- no high-voltage or unknown-current driver experiments
- no claiming that Phase 0-A validates the full architecture

### Phase 0-A Open-Beam Resolution

Claude correctly flagged a contradiction: the draft BOM mentioned a low-power laser pointer while the plan prohibited open-beam work.

The lab resolves that contradiction as follows:

- Phase 0-A should prefer diffuse LED or other incoherent illumination if it can answer the measurement question
- if the team believes a laser is required for Phase 0-A, it must be filed as an explicit Class 2 exception request inside `LASER_AND_OPTICAL_SAFETY_PLAN.md`
- that exception must name the source, wavelength, nominal output, reflection controls, operator controls, and abort procedure before the source is energized
- no generic PPE statement counts as approval; laser controls must be tied to the actual source under review

Until that exception is written and signed off, Phase 0-A remains non-laser.

## Category Errors To Eliminate

Gemini identified two category errors that the repo must stop repeating:

1. Simulation vs physics
   - Sim 4 currently risks confusing a software reset with a physically degraded rewrite
   - that makes the correction story look stronger than the modeled physics

2. Analogy vs physics
   - Phase 0-A can validate SSIM measurement in a 2D benchtop analog
   - it does not validate quartz holography, GST phase switching, or the full architecture

These are not stylistic concerns. They are hard boundaries on what the team is allowed to claim.

## Phase A: Grounding Pass

### Objective

Create the minimum truthful record required to say what the architecture assumes, what can fail, and what is still unknown.

### Required Deliverables

1. `FAILURE_MODES.md`
   - enumerate physical, algorithmic, and interpretation failure modes
   - include trigger, consequence, detectability, mitigation, and owner

2. `PHYSICAL_ASSUMPTIONS_REGISTER.md`
   - list every material, optical, thermal, and geometric assumption
   - mark each as literature-backed, simulated, estimated, or unknown
   - explicitly flag assumptions that currently have no evidence

3. `LASER_AND_OPTICAL_SAFETY_PLAN.md`
   - define whether each planned phase uses incoherent light, enclosed coherent light, or open-beam coherent light
   - define what wavelengths, power classes, enclosure assumptions, and eye controls would be required
   - state what is forbidden before formal review
   - [Claude annotation] Must explicitly reference ANSI Z136.1 for any Class 2+ source
   - appropriate wavelength-rated eye protection and beam controls must be physically in hand before any beam is enabled
   - the author of this document must acknowledge they are not a laser safety officer and that the document requires qualified review before any higher-risk source is used
   - [Gemini alignment] if Phase 0-A requests a Class 2 exception, the exception must stay scoped to the analog measurement question only and may not be cited as architecture validation

4. `EXPERIMENT_STOP_CONDITIONS.md`
   - define stop-work triggers for eye risk, unexpected heating, smoke, odor, current draw, cracked media, uncontrolled reflections, or undocumented procedure drift
   - [Claude annotation] Each trigger needs a baseline defined, not just a label
   - "unexpected heating" requires an expected thermal signature or upper bound documented first

5. `PHASE0A_RUN_SHEET.md` refinement
   - keep the analogy boundary explicit
   - define exactly what artifact paths and photos/logs are required
   - preregister the clean-frame count and maximum allowed inter-frame variance
   - [Claude annotation] Phase 0-A as currently scoped becomes an open-beam experiment if it uses a laser pointer, so the run sheet must either reference an approved Class 2 exception or use non-laser illumination

6. `OPERATOR_QUALIFICATIONS.md`
   - name who is allowed to run the experiment
   - state what safety concepts they know without reading a script mid-run
   - define what they must do if they become uncertain during setup or operation
   - [Claude addition] Safety documents do not provide safety; operators who know the abort sequence by reflex do
   - [Gemini alignment] This document is a pre-benchtop requirement, not a Phase C nicety

### Exit Criteria

- all required deliverables exist
- all unknown assumptions are visibly tagged
- every planned near-term experiment has a stated stop condition
- any requested Class 2 exception is either signed off or rejected in favor of non-laser illumination
- Claude and Gemini have reviewed for integration and science coherence
- Codex has reviewed for falsifiability and safety legibility
- Rocks signs off on whether the project may proceed to Phase B

## Phase B: Simulation Hardening Pass

### Objective

Make the digital evidence harder to fool before physical work inherits its blind spots.

### Required Deliverables

1. Sim 4 imperfect correction implementation
   - replace perfect reset behavior with physically degraded rewrite behavior

2. Benchmark parity
   - align `benchmark.py` and `sim1_v2_noise.py` correction modeling

3. Structured attack sweep report
   - produce a named artifact bundle that maps periodic alias windows, corner/center sensitivity, and threshold behavior
   - minimum artifact set: sweep config, raw results table, plots, and a written interpretation
   - [Claude annotation] "Map periodic alias windows" is a research task, not a deliverable, unless it has a specific output artifact and pass/fail gate
   - [Gemini alignment] the written interpretation must say explicitly whether the result is about simulation behavior only or is being used to motivate a physical test

4. Claim and evidence alignment pass
   - ensure `README.md`, `CLAIMS.md`, and validation outputs tell the same truth

### Exit Criteria

- benchmark correction behavior is no longer a trivial reset
- adversarial limitations are documented, not implied
- the structured-attack sweep artifact exists and is reviewable
- thresholds changed only with preregistered rationale
- any claim promoted in wording has matching evidence

## Phase C: Benchtop Safety Readiness

### Objective

Define the first physical experiment as a controlled safety exercise, not an improvisation session.

### Required Deliverables

1. hardware bill of materials with hazard notes
2. pre-flight checklist
3. operator roles during run
4. maximum allowed power/current/temperature limits for the run
5. enclosure and reflection-control notes
6. abort procedure and shutdown sequence
7. update `OPERATOR_QUALIFICATIONS.md` if the hardware scope, operators, or hazard class changed

### Exit Criteria

- all hardware in scope is listed
- each item has a hazard note or explicit "low-risk" rationale
- no unknown power source or driver remains in the setup
- the team can explain how the run ends safely before it begins

## Review Responsibilities

### Claude

- challenge whether the plan is implementable
- identify missing operational details
- block steps that sound good but are not executable

### Gemini

- challenge whether the plan confuses simulation, analogy, and physics
- block any assumption that is framed more strongly than its evidence

### Codex

- challenge missing failure cases, weak gates, and untestable claims
- block any step that cannot be audited later

### Rocks

- decide whether the cost, risk, and pace remain acceptable
- retain final authority on whether hardware work starts

## Hard Stop Conditions

Progress pauses immediately if any of the following happens:

- a planned experiment requires an unreviewed laser or unknown optical source
- a planned experiment requires guessed electrical limits
- a README or whiteboard note outruns the strongest current evidence
- a hardware step is proposed without a stop-work condition
- a reviewer issues `BLOCK` on safety or evidence framing

## Recommended Sequence

1. Claude and Gemini review this plan and mark gaps
2. Codex folds those review outcomes into the governing plan and packet
3. Codex turns the agreed structure into the required docs
4. The team fills the docs with actual project-specific content
5. The team signs off on Phase A exit criteria
6. Only then decide whether any benchtop action is allowed

## Success Condition

This plan succeeds if it makes the next prototype attempt feel slower on paper but safer and more honest in reality.

---

*Claude and Gemini review notes integrated 2026-04-09. Claude annotations remain marked `[Claude annotation]` and `[Claude addition]`. Gemini-driven constraints are marked `[Gemini alignment]` where they tightened category boundaries or safety scope.*
