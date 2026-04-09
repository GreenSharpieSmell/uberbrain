# Evidence Levels

This document defines the language ceiling for Uberbrain claims.

If a sentence exceeds the allowed language for its evidence level, it must be rewritten or blocked.

## Level 0 — Hypothesis

Meaning:

- idea
- intuition
- literature extrapolation
- architectural proposal without validating benchmark evidence

Allowed language:

- hypothesizes
- proposes
- suggests as a possible architecture
- may enable
- is designed to

Blocked language:

- proves
- verifies
- demonstrates in hardware
- complete
- ready

## Level 1 — Suggestive Simulation

Meaning:

- one or more simulations show a signal
- limited tests may pass
- adversarial coverage is incomplete or mixed
- no hardware validation yet

Allowed language:

- suggests
- indicates
- is consistent with
- simulation demonstrates a narrow effect
- simulation supports further testing

Blocked language:

- solved
- validated architecture
- digital twin complete
- fully verified

## Level 2 — Demonstrated Narrow Claim

Meaning:

- preregistered benchmark criteria met
- artifacts saved
- failure cases documented
- claim is narrow and explicitly bounded

Allowed language:

- demonstrates this specific claim
- passes the defined benchmark
- reproducibly meets the stated threshold

Blocked language:

- proves the whole architecture
- engineering-ready
- production-ready

## Level 3 — Benchtop Validated Narrow Claim

Meaning:

- physical experiment reproduces a targeted prediction
- setup, thresholds, and artifacts are documented
- analogy boundaries are explicit

Allowed language:

- benchtop validation suggests
- physically demonstrates this narrow behavior
- matches the targeted prediction under the stated conditions

Blocked language:

- validates unrelated layers of the stack
- validates quartz/GST behavior unless directly tested

## Level 4 — System Validation

Meaning:

- multiple linked claims hold together under repeated testing
- ablations are beaten
- failures are known and bounded
- simulation and benchtop evidence align

Allowed language:

- system-level evidence supports
- validated within the tested operating envelope

Blocked language:

- universal proof
- production deployment claims

## Current Ceiling For This Repo

Current default ceiling:

- Level 1 for architecture-wide statements
- Level 2 only for narrow, well-bounded benchmark claims
- Level 3 only after a specific benchtop result exists

Until stronger evidence exists, the safe default phrase remains:

"Concept plus simulation hypothesis, not engineering-ready architecture."
