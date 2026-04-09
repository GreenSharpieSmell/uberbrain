# Uberbrain Lab Operating Model

This document defines how the four-person lab operates when making technical, scientific, and documentation changes.

The goal is simple:

- preserve scientific honesty
- preserve engineering discipline
- prevent silent drift between claims, code, tests, and framing

## Core Principle

No meaningful change should exist in only one place.

If a change affects the repo, it must be reflected in:

- code or docs
- a change packet
- explicit signoff
- the relevant evidence artifact

## Functional Roles

These roles describe responsibilities, not ego or rank.

### Rocks

- Human decision authority
- Sets project direction and approves priority shifts
- Final gate for merge-to-main and physical build spend

### Claude

- Integration and implementation lead
- Owns multi-file execution, branch hygiene, and getting changes over the finish line
- Must verify that documentation matches implemented behavior

### Gemini

- Scientific review lead
- Owns physics coherence, analogy boundaries, literature sanity, and "does this claim outrun the science?"
- Must block changes that confuse analogy, simulation, and hardware evidence

### Codex

- Validation and requirements lead
- Owns falsifiability, test expectations, claim language discipline, and SOP enforcement
- Must block changes that weaken traceability, loosen gates without preregistration, or hide failures

## Required Operating Artifacts

Every non-trivial change must have:

- a branch
- a change packet
- a signoff matrix
- linked evidence or a declared "no evidence impact" statement

Depending on change type, it may also require:

- a claim change record
- a benchmark report
- an experiment run sheet
- a decision record
- a red-team finding

## Change Classes

### C0 — Housekeeping

Examples:

- spelling fixes
- formatting
- comment cleanup with no behavioral effect

Still requires a change packet and signoff, but evidence sections may be marked "no impact."

### C1 — Process and documentation

Examples:

- new templates
- SOP changes
- handoff structure
- README wording changes

Requires wording review and evidence-framing review.

### C2 — Code, tests, and simulation behavior

Examples:

- simulation logic changes
- test changes
- CI changes
- benchmark harness changes

Requires explicit test plan and rollback note.

### C3 — Claims, thresholds, and evidence language

Examples:

- claim wording changes
- pass/fail threshold changes
- evidence label changes
- benchmark interpretation changes

Requires a claim change record and preregistration check.

### C4 — Experiment protocols and physical assumptions

Examples:

- benchtop procedure changes
- hardware BOM changes
- physical assumptions
- prototype interpretation changes

Requires an experiment run sheet or assumptions update.

### C5 — High-visibility public framing

Examples:

- top-level README claims
- pitch copy
- "verified" or "complete" language

Requires the strictest wording review. No public-facing statement may exceed the strongest current evidence level.

## Decision Cadence

Use this cadence unless urgency requires the exception path:

1. Draft locally
2. If the branch will be shared, open a change packet before the first remote push
3. Share packet summary and intended diff in the whiteboard
4. Stay in exploration lane while the branch is still WIP
5. Promote to integration lane when it targets `main` or becomes adopted project position
6. Collect four signoff decisions before merge to `main`
7. Merge only after artifacts and docs are aligned

## Working Lanes

Think of the lab as having three operating lanes.

### Exploration Lane

- local commits are free
- feature-branch pushes are allowed with a draft packet
- signoffs may remain pending
- work here is exploratory, not authoritative

### Integration Lane

- the branch is now trying to become the lab record
- claims, thresholds, experiment protocols, and public wording are no longer draft
- 4/4 signoff is required before merge to `main`

### Emergency Lane

- this is the narrow break-glass path
- use only for credentials, destructive regressions, or repo recovery
- every emergency action creates paperwork afterward

The cultural rule is simple:

feature branches are notebooks
`main` is the lab record

## Stop-The-Line Rule

Any one of the four collaborators may issue a block.

A block is not a veto forever. It is a forced pause until one of these happens:

- the objection is resolved
- the scope is reduced
- the decision is explicitly waived through the exception process

## What Success Looks Like

This operating model is working if:

- no benchmark result appears without a protocol and artifact path
- no claim wording changes without a durable record
- no README sentence outruns the claim registry
- every collaborator has a documented chance to review before git-bound publication
