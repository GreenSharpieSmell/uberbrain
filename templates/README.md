# Collaboration Templates

This folder contains lightweight templates for coordinating work across the Uberbrain repo, the shared whiteboard, and benchmark artifacts.

Use these templates when a change needs to survive beyond chat.

## Template Pack

- `HANDOFF_TEMPLATE.md` — short worker-to-worker updates
- `DECISION_RECORD_TEMPLATE.md` — durable decisions and their rationale
- `EXPERIMENT_RUN_SHEET_TEMPLATE.md` — benchtop or simulation experiment setup plus pass/fail
- `BENCHMARK_REPORT_TEMPLATE.md` — claim-level benchmark results
- `CLAIM_CHANGE_TEMPLATE.md` — any edit to a formal claim, threshold, or evidence label
- `CHANGE_PACKET_TEMPLATE.md` — mandatory pre-git scope, evidence, and signoff packet
- `EXCEPTION_WAIVER_TEMPLATE.md` — controlled bypass for emergency changes
- `RED_TEAM_FINDING_TEMPLATE.md` — skeptical reviewer objections and mitigations

## Working Rule

Conversation happens in the whiteboard.
Source-of-truth artifacts belong in the repo.

If a change affects claims, thresholds, experiments, or project framing, capture it with one of these templates.

## Suggested Placement

- Handoffs: whiteboard first, then copy stable versions into a repo doc when needed
- Decision records: keep with validation work, for example alongside `VALIDATION_SPEC.md`
- Experiment run sheets: place next to the experiment output directory in `results/`
- Benchmark reports: place inside the matching benchmark artifact directory in `results/`
- Claim changes: store with validation and claim-related docs
- Red-team findings: keep near validation docs so objections stay visible

## Naming Suggestions

- Handoff: `handoff_YYYY-MM-DD_short-topic.md`
- Decision record: `decision_YYYY-MM-DD_short-title.md`
- Run sheet: `run_sheet_YYYY-MM-DD_short-experiment.md`
- Benchmark report: `benchmark_report_YYYY-MM-DD_short-claim.md`
- Claim change: `claim_change_YYYY-MM-DD_claim-id.md`
- Red-team finding: `red_team_YYYY-MM-DD_short-risk.md`
