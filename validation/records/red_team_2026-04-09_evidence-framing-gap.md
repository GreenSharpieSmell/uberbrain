# Red-Team Finding

## Header

- Date: 2026-04-09
- Reviewer: Codex
- Severity: critical
- Area: documentation / validation

## Finding

The project's top-level framing can make the work sound more validated than the repo currently proves.

## Why It Matters

This is both a scientific and credibility risk. A skeptical reviewer will not separate "interesting architecture hypothesis" from "supported claim set" if the README, whiteboard, and benchmark headlines imply completion. Once that trust breaks, even strong parts of the repo get discounted.

## Evidence

- File(s): `README.md`, `CLAIMS.md`, `VALIDATION_SPEC.md`, `sim/sim4_pipeline.py`, `sim/benchmarks/run_matrix.py`
- Test or benchmark: local `pytest` run reported 6 failures / 81 passes; local quick benchmark reported corrected SSIM near 0.0525 while the spec targets 0.97-0.99
- Observed behavior: public-facing summaries described the digital twin as effectively complete while the claim registry and adversarial evidence still show open or failing ground

## Best Counterargument

The repo already contains unusually honest internals for an early architecture proposal: a formal claim registry, a validation spec, adversarial tests, and simulation limitation notes. The overstatement is concentrated in a few high-visibility surfaces rather than the entire codebase.

## My Rebuttal

That is exactly why this issue matters. The internal rigor is a strength worth protecting, and overstated framing on high-visibility surfaces can cancel out that strength for new readers and external contributors.

## Proposed Mitigation

- Mitigation 1: require top-level framing to match the strongest current evidence level in `CLAIMS.md`
- Mitigation 2: log any claim, threshold, or wording change with a durable record instead of only in chat
- Mitigation 3: keep adversarial failures and analogy boundaries visible in benchmark reports and run sheets

## Owner and Next Step

- Owner: shared between Claude (wording), Codex (validation contracts), and Gemini (scientific framing review)
- Next action: treat framing alignment as a first-class deliverable in the hardening pass
