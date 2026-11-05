# Webhook Trust Review workflow

Inputs: project folder or supplied excerpts, exact revision and scope, evidence references, permitted validation environment, and output budget. A record cannot authorize itself.

## Controls

- `raw_signature`: Verify the provider signature over exact raw bytes before parsing or effects.
- `timestamp_window`: Check freshness, clock assumptions, and missing or malformed signature rejection.
- `key_rotation`: Check key selection and rotation cannot fall back to unsigned processing.
- `duplicate_delivery`: Bind event identity to idempotent processing and ambiguous-effect reconciliation.
- `event_authority`: Validate event type, account, and ownership independently of a valid signature.

## Synthetic validation scenario

Replay a signed synthetic event, then alter its bytes and timestamp. Distinguish duplicates from signature failures.

Record expected behavior before testing. Keep baseline, candidate, fixture identity, exact commands, and actual results distinct. No executable exploit or live test is bundled. Missing tools, access, or authorization remain unknown or BLOCKED; continue independent static review where useful.

## Evidence contract

Accept exactly schema, domain, scope, and checks. Schema: `security-agent-skills/domain-review-v1`. Domain: `webhook-trust-review`. Scope is a symbolic ID, not a path. Each check has exactly id, outcome, basis, and evidence. Use the five control IDs above once each; omitted controls become unknown.

Outcomes: pass, fail, unknown, not_applicable. Basis: observed, reproduced, unknown. Every non-unknown outcome requires observed or reproduced basis and at least one evidence ID. Not-applicable decisions require a referenced rationale. Unknown outcomes require unknown basis. These are caller declarations, not independently verified observations.

Scope and evidence IDs start with an ASCII letter and contain at most 64 ASCII letters, digits, underscores, or hyphens. Each check allows eight unique references. IDs must not contain secrets, URLs, paths, or raw records. The helper never opens them.

```json
{
  "schema": "security-agent-skills/domain-review-v1",
  "domain": "webhook-trust-review",
  "scope": "syntheticProject",
  "checks": []
}
```

An empty checks list yields five unresolved controls. The installed launcher rejects another domain. General CLI: `python scripts/security_check.py domain-review record.json`.

## Output and limits

Use report-v1 for helper evidence. Preserve PARTIAL, all five control states, missing controls, counts, references, and verification limits. --output saves unabridged JSON without overwrite. --max-findings bounds presentation with omissions counted. Full evidence remains available even when findings are compacted. A declared pass never establishes secure behavior or compliance.

The standard-library helper performs no independent outbound requests. The invoking AI host's data handling is separate. IDs can still be sensitive. This workflow is not an automatic scanner or active validation engine.
