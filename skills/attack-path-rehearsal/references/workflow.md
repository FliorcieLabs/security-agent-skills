# Attack Path Rehearsal contract

Required fields: `schema`, `nodes`, `entries`, `assets`, `edges`. The first three lists after schema contain unique symbolic IDs, at most 100 each, and must be nonempty. Entries and assets must reference nodes. At most 200 edges, each with exactly `id`, `from`, `to`, `state`, `evidence`. Edge IDs must be unique; endpoints must exist. State is `open`, `blocked`, or `unknown`. Evidence is a unique ID array, at most 100. An open edge without evidence is treated as unknown for reachability. Evidence identifiers are not verified.

The helper returns one deterministic shortest route per asset, separating declared-open routes, routes requiring evidence, and absence of a declared route. It evaluates removing each edge in the declared-open graph and lists assets that become unreachable, accounting for alternate paths. These are single-edge counterfactuals, not a complete minimal-cut solver, exploit validation, or a cost-based remediation ranking. Entry assets can be reachable by a zero-edge route. Cycles are permitted and traversal terminates. Limits: 100 nodes, 200 edges, bounded breadth-first searches.

All symbolic IDs match `[A-Za-z][A-Za-z0-9_-]{0,63}`. Reject extra fields, duplicate JSON keys, unknown schema versions, wrong types, duplicate IDs, oversized arrays, and invalid references. CLI input is a regular non-link JSON file of at most 8 MB. MCP messages have a separate 1 MB limit. JSON results use `security-agent-skills/report-v1`. All valid results remain PARTIAL and source_claims_verified is false. Input labels do not attest to runtime truth.

## Synthetic example

```json
{
  "schema": "security-agent-skills/attack-path-v1",
  "nodes": [
    "entry",
    "agent",
    "vault"
  ],
  "entries": [
    "entry"
  ],
  "assets": [
    "vault"
  ],
  "edges": [
    {
      "id": "retrieval",
      "from": "entry",
      "to": "agent",
      "state": "open",
      "evidence": [
        "reviewA"
      ]
    },
    {
      "id": "readVault",
      "from": "agent",
      "to": "vault",
      "state": "unknown",
      "evidence": []
    }
  ]
}
```

For MCP clients, the corresponding tool is `attack_path`, taking an object with one `record` property containing this document. It returns the same report as the CLI. No files are read by that tool.
