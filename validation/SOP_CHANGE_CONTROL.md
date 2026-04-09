# SOP: Change Control

This is the mandatory pre-git procedure for all meaningful repo changes.

## Rule Zero

No commit or push for a meaningful change without a completed change packet.

Meaningful change includes:

- code
- tests
- CI
- claims
- thresholds
- experiment protocols
- README or other high-visibility wording
- templates or SOPs

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

Before commit, all four collaborators must have a chance to review:

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

### Gate 3 — Git Readiness

Before commit and push, the packet must confirm:

- diff matches declared scope
- required tests or checks were run, or explicitly not run with reason
- docs and code are not in contradiction
- top-level wording does not exceed evidence level
- rollback path is stated

### Gate 4 — Merge Readiness

Before merge to `main`, confirm:

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

- no shared-remote push for C2-C5 changes without 4/4 explicit signoff
- no merge to `main` without 4/4 explicit signoff

Recommended rule:

- even C0-C1 changes should still seek 4/4 signoff unless clearly time-insensitive and zero-risk

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
