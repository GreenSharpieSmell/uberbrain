# Change Packet

## Header

- Packet ID: packet_2026-04-09_exploration-integration-lanes
- Date: 2026-04-09
- Author: Codex
- Branch: `codex/collab-template-pack`
- Lane: exploration
- Change class: C1
- Risk: medium

## Scope Declaration

- Summary: refine the governance system so local commits and feature-branch pushes stay fast, while `main` remains hard-gated
- Files expected to change:
  - `validation/SOP_CHANGE_CONTROL.md`
  - `validation/LAB_OPERATING_MODEL.md`
  - `templates/CHANGE_PACKET_TEMPLATE.md`
  - `templates/README.md`
  - `validation/change_packets/README.md`
  - `validation/change_packets/packet_2026-04-09_governance-signoff-system.md`
- Why this change is needed now: Claude raised a valid concern that the original wording was too strict for feature-branch iteration and would create unnecessary drag

## Evidence Impact

- Claims affected: none directly
- Evidence impact: low
- Linked artifacts:
  - `validation/change_packets/packet_2026-04-09_governance-signoff-system.md`
  - `validation/EVIDENCE_LEVELS.md`
- Top-level wording impact: clarifies that feature branches are exploratory while `main` remains the authoritative lab record

## Required Checks

- Tests to run: none; docs/process only
- Docs to update: governance docs and packet template only
- Rollback path: revert this packet's commit and return to the stricter one-lane model
- Follow-up tasks:
  - collect Gemini signoff on the lane refinement before merge to `main`
  - decide whether Rocks-only awareness is sufficient for exploration pushes or whether explicit Rocks approval should remain the default

## Review Notes

- Biggest risk: the team interprets exploration-lane freedom as permission to let draft framing leak into authoritative docs
- Best argument against this change: a single hard gate is easier to understand and enforce
- Why we still think it should proceed: the lab needs fast iteration on feature branches, and the real risk surface is merge-to-`main`, claims, thresholds, and public framing

## Signoff Matrix

- Rocks: APPROVE
  - Notes: Requested this refinement after Claude raised the concern.
- Claude: APPROVE
  - Notes: This addresses the velocity concern while preserving hard merge gates.
- Gemini: PENDING
  - Notes:
- Codex: APPROVE
  - Notes: Acceptable so long as `main` remains the hard-gated lab record and blocks still stop the line.

## Git Gate

- [x] Scope matches actual diff
- [x] Evidence impact declared honestly
- [x] Required checks completed or skipped with reason
- [x] All four signoff fields filled
- [x] No blocker remains unresolved
- [x] Ready for exploration push
- [ ] Ready for integration review
- [x] Ready for commit
- [ ] Ready for merge to main
