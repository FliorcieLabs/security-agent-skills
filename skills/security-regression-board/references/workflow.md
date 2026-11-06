# Security Regression Board contract

Required fields: `schema`, `cases`. One to 100 cases, each with exactly `id`, `expected`, `baseline`, `candidate`, `baseline_status`, `candidate_status`. Case IDs are unique. Label arrays contain unique symbolic IDs, at most 100 each. Status is `complete`, `partial`, or `blocked`. A case is scored only when both statuses are complete. All other cases remain explicitly excluded, never true negatives or clean results.

Micro-averaged label metrics use TP = expected intersect observed, FP = observed minus expected, FN = expected minus observed. Precision = TP/(TP+FP), recall = TP/(TP+FN), F1 = 2TP/(2TP+FP+FN). Undefined denominators are null. There is no declared true-negative universe, accuracy metric, statistical significance test, or independently verified run. Report lost expected detections and new false positives per scored case even if aggregate F1 improves. Use identical frozen fixtures and actual captured outputs for real comparisons. Never label invented baseline outputs as another project's results.

All symbolic IDs match `[A-Za-z][A-Za-z0-9_-]{0,63}`. Reject extra fields, duplicate JSON keys, unknown schema versions, wrong types, duplicate IDs, oversized arrays, and invalid references. CLI input is a regular non-link JSON file of at most 8 MB. MCP messages have a separate 1 MB limit. JSON results use `security-agent-skills/report-v1`. All valid results remain PARTIAL and source_claims_verified is false. Input labels do not attest to runtime truth.

## Synthetic example

```json
{
  "schema": "security-agent-skills/regression-board-v1",
  "cases": [
    {
      "id": "catchTransfer",
      "expected": [
        "egress"
      ],
      "baseline": [],
      "candidate": [
        "egress"
      ],
      "baseline_status": "complete",
      "candidate_status": "complete"
    },
    {
      "id": "benignImport",
      "expected": [],
      "baseline": [
        "egress"
      ],
      "candidate": [],
      "baseline_status": "complete",
      "candidate_status": "complete"
    },
    {
      "id": "unavailableHost",
      "expected": [
        "authority"
      ],
      "baseline": [],
      "candidate": [],
      "baseline_status": "blocked",
      "candidate_status": "blocked"
    }
  ]
}
```

For MCP clients, the corresponding tool is `regression_board`, taking an object with one `record` property containing this document. It returns the same report as the CLI. No files are read by that tool.
