# SOP: Change Control

This is the mandatory pre-git procedure for all meaningful repo changes.

## Rule Zero

No meaningful change may leave a local-only state without a completed change packet.

Local commits are allowed without prior signoff.
Once a branch will be pushed to a shared remote, reviewed by others, or proposed for merge, the packet becomes mandatory.

Meaningful change includes:

- code
- tests
- CI
- claims
- thresholds
- experiment protocols
- README or other high-visibility wording
- templates or SOPs

## Operating Lanes

### Exploration Lane

Use this lane for:

- local iteration
- WIP feature branches
- non-`main` pushes that are still exploratory

Rules:

- local commits are unrestricted
- before the first shared-remote push, open a change packet
- the branch must not be `main`
- signoffs may remain `PENDING`
- the packet must say what was and was not tested
- if any reviewer has already entered `BLOCK`, further shared-remote pushes must stop until the block is resolved or waived

Exploration branches are notebooks, not the lab record.

### Integration Lane

Use this lane for:

- anything proposed for merge to `main`
- any change that will be treated as adopted project position
- any C3, C4, or C5 change once it stops being draft/WIP

Rules:

- full 4/4 signoff required before merge to `main`
- no direct pushes to `main`
- claims, thresholds, benchmark interpretation, experiment protocols, and public framing must meet the stricter checks below

### Emergency Lane

Use this lane only for true exceptions defined in the exception path below.

## Gate Model

### Gate 0 — Scope Declaration

Before staging, the author must create a change packet and declare:

- change class
- files expected to change
- claims or docs affected
- risk level

### Gate 1 — Evidence Map

Before staging, the packet must say one of:

- no evidence impact
- evidence impact, with linked artifact or planned artifact

If the change affects claims, thresholds, benchmarks, or interpretation, the packet must link a claim change record or benchmark report.

### Gate 2 — Review Window

Before merge, and before any integration-lane publication, all four collaborators must have a chance to review:

- packet summary
- intended change scope
- risk classification
- evidence impact

Silence is not approval.

Each signoff must be explicit:

- PENDING
- APPROVE
- BLOCK
- WAIVE

Every BLOCK or WAIVE requires a written reason.

### Gate 3 — Exploration Push Readiness

Before a shared-remote push in exploration lane, the packet must confirm:

- branch is not `main`
- diff matches declared scope
- required tests or checks were run, or explicitly not run with reason
- docs and code are not in contradiction within the declared scope
- rollback path is stated
- packet is marked draft/WIP if signoffs are still pending
- no recorded block is being ignored

### Gate 4 — Integration Readiness

Before merge to `main`, the packet must confirm:

- diff matches declared scope
- required tests or checks were run, or explicitly not run with reason
- docs and code are not in contradiction
- top-level wording does not exceed evidence level
- rollback path is stated
- packet is complete
- all blockers are resolved or waived through exception path
- linked artifacts exist
- follow-up tasks are captured

## Mandatory Signoff Matrix

Every change packet must contain four explicit fields:

- Rocks signoff
- Claude signoff
- Gemini signoff
- Codex signoff

Required rule:

- no direct pushes to `main`
- no shared-remote push for a meaningful change without a packet
- no merge to `main` without 4/4 explicit signoff

Exploration-lane rule:

- feature-branch pushes are allowed with `PENDING` signoffs if a packet exists and no recorded `BLOCK` is being ignored

Recommended rule:

- even C0-C1 changes should still seek 4/4 signoff before merge unless clearly time-insensitive and zero-risk
- C3-C5 changes should be surfaced for review early, even while still in exploration lane

## Required Checks By Change Class

### C0

- packet
- 4 signoff fields
- no-evidence-impact statement

### C1

- packet
- wording review
- evidence-framing check

### C2

- packet
- test plan
- actual test results
- rollback note

### C3

- packet
- claim change record
- preregistration statement
- explicit reason any threshold moved

### C4

- packet
- run sheet or assumptions update
- analogy boundary statement if applicable

### C5

- packet
- top-level framing review
- evidence-level check against `CLAIMS.md`
- explicit approval from Gemini and Codex required

## Exception Path

Exceptions are allowed only for:

- credential or secret removal
- destructive bug fix needed to prevent data loss
- repo recovery after a broken push

Exception minimum:

- Human approval from Rocks
- At least one additional collaborator approval
- Exception waiver record opened immediately
- Full retroactive review within 24 hours

## Failure To Follow SOP

If a change lands without the required packet or signoff:

1. Stop further merges.
2. Open a red-team finding.
3. Reconstruct the missing packet retroactively.
4. Decide whether to keep, revert, or supersede the change.

Process debt is real debt.
