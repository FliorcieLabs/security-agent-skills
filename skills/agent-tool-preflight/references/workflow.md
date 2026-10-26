# Agent Tool Preflight Reviewer: record contract

Input: one existing bounded non-link JSON file, not a project directory. The CLI uses its normal 8 MB input bound. Schema: security-agent-skills/preflight-v1. Every shown field is required; unknown fields are rejected, including extra nested policy or task fields. JSON booleans must be true/false; booleans cannot stand in for integer budgets.

Symbolic IDs match [A-Za-z][A-Za-z0-9_-]{0,63}. Reference lists have at most 100 distinct IDs each. They are local lookup labels, not paths, URLs, raw prompts, commands, or secrets. Maintain the mapping locally outside the record. String format validation is not secret detection.

## Behavior

Required nested policy fields: allowed_tools, allowed_resources, allowed_effects (read/write), external_transfer_allowed, approval_required_for_write. Required action fields: tool, resources (nonempty), effect (read/write), external_transfer, approval_recorded. Lists use exact symbolic equality with no wildcard, path, URI, inheritance, or alias interpretation. Out-of-policy tool, resource, effect, external transfer, or missing declared write approval is BLOCKED. A matching declaration is PARTIAL, authorization_granted false. Record booleans are unverified claims, not permissions or proof of actual data flow.

Determine the tool, real resource scope, read or write effect, and any external transfer using the actual tool behavior. Then compare the proposal with the existing user authorization and host policy. Do not infer a pure read from a friendly tool name or an approval from approval_recorded alone. A match is PARTIAL and grants no permission. Recheck policy freshness and actual authorization in the host. This helper does not invoke tools, bypass prompts, or make a denied action available.

## Synthetic input

```json
{
  "schema": "security-agent-skills/preflight-v1",
  "policy": {
    "allowed_tools": ["read_file"],
    "allowed_resources": ["project_source"],
    "allowed_effects": ["read"],
    "external_transfer_allowed": false,
    "approval_required_for_write": true
  },
  "action": {
    "tool": "read_file",
    "resources": ["project_source"],
    "effect": "read",
    "external_transfer": false,
    "approval_recorded": false
  }
}
```

```text
python "<skill-dir>/scripts/run.py" "<record.json>" --output "<new-report.json>" --max-findings 5
```

Reports use security-agent-skills/report-v1. PASS (exit 0) means only the named record-consistency check or stop decision passed. FIX (1) identifies a declared inconsistency, BLOCKED (2) means invalid/missing input or a rejected operation candidate, and PARTIAL (3) preserves unresolved evidence or authority. No return value authorizes execution. CLI findings point to the logical record and, for task entries, one-based task positions; they are not JSON source line numbers.

Reports omit raw action payloads and freeform text. A checkpoint intentionally includes its validated symbolic references. Other operation reports contain fixed messages, counts, and derived positions. None reads the referenced evidence or observes runtime state. No automatic delegation, messages, retries, memory writes, external transfers, or configuration edits occur.
