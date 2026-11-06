# Detection Replay Lab contract

Required fields: `schema`, `rules`, `events`. One to 32 rules, each with exactly `id`, `equals`. One to 100 events, each with exactly `id`, `fields`, `expected`. Rule IDs and event IDs are unique within their own lists. Expected IDs must reference declared rules. `equals` and `fields` contain 1 to 16 symbolic field names with string values of at most 256 characters. Match uses case-sensitive equality of every predicate field. Missing fields do not match. No regex, eval, code, YAML, SIEM query execution, Sigma translation, timestamp window, or correlation support.

Outputs contain only symbolic event/rule IDs, not field names or values. Metrics count event/rule labels with micro-averaged precision, recall, and F1. Undefined denominators are JSON null. Labels are declarations and may be wrong. The schema-drift fixture deliberately misses one expected detection. Synthetic fixtures do not establish operational recall.

All symbolic IDs match `[A-Za-z][A-Za-z0-9_-]{0,63}`. Reject extra fields, duplicate JSON keys, unknown schema versions, wrong types, duplicate IDs, oversized arrays, and invalid references. CLI input is a regular non-link JSON file of at most 8 MB. MCP messages have a separate 1 MB limit. JSON results use `security-agent-skills/report-v1`. All valid results remain PARTIAL and source_claims_verified is false. Input labels do not attest to runtime truth.

## Synthetic example

```json
{
  "schema": "security-agent-skills/detection-replay-v1",
  "rules": [
    {
      "id": "unapprovedWrite",
      "equals": {
        "effect": "write",
        "approved": "false"
      }
    }
  ],
  "events": [
    {
      "id": "deniedWrite",
      "fields": {
        "effect": "write",
        "approved": "false"
      },
      "expected": [
        "unapprovedWrite"
      ]
    },
    {
      "id": "safeRead",
      "fields": {
        "effect": "read",
        "approved": "false"
      },
      "expected": []
    },
    {
      "id": "schemaDrift",
      "fields": {
        "effect": "write",
        "approval": "false"
      },
      "expected": [
        "unapprovedWrite"
      ]
    }
  ]
}
```

For MCP clients, the corresponding tool is `detection_replay`, taking an object with one `record` property containing this document. It returns the same report as the CLI. No files are read by that tool.
