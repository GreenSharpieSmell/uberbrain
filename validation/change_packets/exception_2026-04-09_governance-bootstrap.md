# Exception Waiver

## Header

- Date: 2026-04-09
- Author: Codex
- Branch: `codex/collab-template-pack`
- Reason for exception: bootstrap publication of the signoff system itself
- Severity: medium

## Why Normal SOP Was Bypassed

The normal pre-git signoff system did not yet exist as an adopted repo standard. This change creates that system, so full four-party pre-push compliance could not be required before publishing the proposal for review.

## Immediate Risk

- Risk to repo: low; this is documentation and process scaffolding only
- Risk to data or credentials: none
- Risk to scientific integrity: low to medium; the main risk is process overhead, not claim distortion

## Minimum Approvals Obtained

- Rocks: approved by direct user instruction to push and proceed
- Additional approver: Codex

## Temporary Action Taken

- Files touched:
  - `validation/LAB_OPERATING_MODEL.md`
  - `validation/SOP_CHANGE_CONTROL.md`
  - `validation/EVIDENCE_LEVELS.md`
  - `validation/README.md`
  - `validation/change_packets/*`
  - `templates/CHANGE_PACKET_TEMPLATE.md`
  - `templates/EXCEPTION_WAIVER_TEMPLATE.md`
  - `templates/README.md`
  - `README.md`
- Commands run:
  - branch creation
  - commit
  - push to shared remote branch
- Shared-remote action:
  - push governance proposal to `origin/codex/collab-template-pack`

## Retroactive Review Due By

- Date/time: before merge of this governance package into `main`

## Final Disposition

- Keep as-is:
- Revise:
- Revert:
