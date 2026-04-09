# Decision Record

## Header

- Date: 2026-04-09
- Title: Repo hardening before Phase 0-A hardware work
- Status: accepted
- Owners: Rocks, Claude, Gemini, Codex

## Decision

We will complete a repo-hardening pass before treating Phase 0-A as the primary next milestone.
Hardware-adjacent work may continue in planning form, but project framing, validation contracts, and adversarial evidence must be tightened first.

## Why We Made It

- Problem being solved: the repo's narrative and status surfaces were running ahead of the strongest evidence in the code and tests.
- Evidence used: local review found a Sim 4 perfect-reset assumption, a benchmark/spec mismatch for corrected SSIM, adversarial test failures, and inconsistent framing between `README.md`, `CLAIMS.md`, and `VALIDATION_SPEC.md`.
- Constraints: four collaborators are updating docs, tests, and plans in parallel, so evidence drift and wording drift are real risks.

## Alternatives Considered

- Option A: move directly into Phase 0-A hardware work and fix docs later
- Option B: continue simulation work only and defer all physical planning
- Option C: do a short hardening pass now, then proceed with a clearly bounded Phase 0-A analog experiment

## Risks

- Risk 1: extra process slows visible momentum in the short term.
- Risk 2: the team may overcorrect into documentation without resolving the highest-value simulation defects.

## Rollback Trigger

If the repo reaches a state where top-level framing, tests, CI, and benchmark contracts are aligned, we can treat Phase 0-A execution as the primary active milestone again.

## Follow-Up Work

- [ ] Remove or rewrite any remaining "complete" or "verified" language that outruns the claim registry
- [ ] Wire imperfect correction into Sim 4 and its benchmark matrix
- [ ] Add durable records for assumptions, failure modes, and evidence levels
- [ ] Keep the Phase 0-A analogy boundary explicit in all run sheets and reports

## Related Artifacts

- Claims: `CLAIMS.md`
- Specs: `VALIDATION_SPEC.md`, `SPECIFICATIONS.md`, `SIM_LIMITATIONS.md`
- Tests: `tests/test_adversarial.py`, `tests/test_simulations.py`
- Whiteboard note: "Codex - 2026-04-09 | Repo Review Pass"
