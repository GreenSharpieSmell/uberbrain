# Change Packet

## Header

- Packet ID: packet_2026-04-09_governance-signoff-system
- Date: 2026-04-09
- Author: Codex
- Branch: `codex/collab-template-pack`
- Lane: integration
- Change class: C1 / C5
- Risk: high

## Scope Declaration

- Summary: add a formal operating model, evidence-language ceiling, change-control SOP, and mandatory pre-git packet templates
- Files expected to change:
  - `validation/LAB_OPERATING_MODEL.md`
  - `validation/SOP_CHANGE_CONTROL.md`
  - `validation/EVIDENCE_LEVELS.md`
  - `validation/change_packets/README.md`
  - `templates/CHANGE_PACKET_TEMPLATE.md`
  - `templates/EXCEPTION_WAIVER_TEMPLATE.md`
  - `templates/README.md`
- Why this change is needed now: the repo is now being changed by four collaborators in parallel, and the team explicitly requested a stringent pre-git signoff system

## Evidence Impact

- Claims affected: no direct claim text change
- Evidence impact: medium
- Linked artifacts:
  - `validation/records/decision_2026-04-09_repo-hardening-before-hardware.md`
  - `validation/records/red_team_2026-04-09_evidence-framing-gap.md`
- Top-level wording impact: future high-visibility wording will be constrained by the new evidence-level policy

## Required Checks

- Tests to run: none; docs/process only
- Docs to update: optional root README navigation if the team wants higher visibility later
- Rollback path: remove the governance docs and templates if the team finds the system too heavy
- Follow-up tasks:
  - collect signoff from all four collaborators
  - decide effective date for mandatory enforcement
  - decide whether all pushes or only mainline merges require unanimous signoff

## Review Notes

- Biggest risk: process becomes so strict that it slows harmless work
- Best argument against this change: the lab is still small and can rely on the shared whiteboard plus normal git review
- Why we still think it should proceed: the project already experienced evidence-framing drift and parallel-agent coordination issues; formal control is now justified

## Signoff Matrix

- Rocks: APPROVED
  - Notes: As the human in the middle, this is going to be required for me to be able to keep track of all changes and what is happening with the project.
- Claude: APPROVE
  - Notes: Full agreement on EVIDENCE_LEVELS, LAB_OPERATING_MODEL, templates, and records. One recommended scope clarification was to loosen feature-branch push rules while keeping hard merge gates for `main`. That follow-up is captured in `packet_2026-04-09_exploration-integration-lanes.md`.
- Gemini: APPROVE
  - Notes: Formally approves the governance packet and collab-template-pack, including the validation workflows, honest reporting standards, and decentralized multi-model lab structure.
- Codex: APPROVE
  - Notes: Strongly recommended; this is the minimum structure needed to keep claims, tests, framing, and experiments aligned.

## Git Gate

- [x] Scope matches actual diff
- [x] Evidence impact declared honestly
- [x] Required checks completed or skipped with reason
- [x] All four signoff fields filled
- [x] No blocker remains unresolved
- [ ] Ready for exploration push
- [x] Ready for integration review
- [x] Ready for commit
- [x] Ready for merge to main
