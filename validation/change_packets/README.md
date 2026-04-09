# Change Packets

This folder holds the mandatory pre-git control packets for meaningful repo changes.

Use one packet per branch-sized change.

## Naming

- `packet_YYYY-MM-DD_short-topic.md`

## Minimum Rule

Before a meaningful change is pushed to a shared remote or proposed for merge, the packet should describe:

- scope
- evidence impact
- required checks
- review risk
- signoff status for Rocks, Claude, Gemini, and Codex

## Lane Rule

- exploration lane packets may be pushed with `PENDING` signoffs
- integration lane packets must be fully signed before merge to `main`

## Status Convention

- `PENDING` — review not complete
- `APPROVE` — reviewed and accepted
- `BLOCK` — reviewed and stopped
- `WAIVE` — reviewer did not approve, but formally waives direct review for this change
