# Agent Context Checkpoint Keeper: record contract

Input: one existing bounded non-link JSON file, not a project directory. The CLI uses its normal 8 MB input bound. Schema: security-agent-skills/checkpoint-v1. Every shown field is required; unknown fields are rejected, including extra nested policy or task fields. JSON booleans must be true/false; booleans cannot stand in for integer budgets.

Symbolic IDs match [A-Za-z][A-Za-z0-9_-]{0,63}. Reference lists have at most 100 distinct IDs each. They are local lookup labels, not paths, URLs, raw prompts, commands, or secrets. Maintain the mapping locally outside the record. String format validation is not secret detection.

## Behavior

Required fields: objective_ref, revision_ref, constraint_refs, evidence_refs, unresolved_refs, decision_refs, next_action_ref, and max_refs (1 to 400). Constraint and evidence lists must be nonempty. Each reference occurrence costs one slot; the three scalar refs are mandatory. Mandatory lists are retained intact. Only the prefix of optional decision_refs that fits is kept. If mandatory references exceed the budget, return BLOCKED and an empty capsule instead of dropping them. A produced capsule returns PARTIAL because evidence and revision freshness are unverified. The complete optional decision list remains in the original input record. A reference count is not a token measurement.

Keep the objective, current revision, constraints, evidence, unresolved work, and next action. Map symbolic references to existing local evidence in a separate local reference index. Do not replace raw credentials with reversible encodings. Put every decision needed for correctness or authority into constraint_refs or unresolved_refs before compaction. Only optional decision references may be omitted, with an explicit count. Resolve references and compare the current revision before resuming. Do not silently write host memory or upload a checkpoint.

## Synthetic input

```json
{
  "schema": "security-agent-skills/checkpoint-v1",
  "objective_ref": "objective_01",
  "revision_ref": "revision_01",
  "constraint_refs": ["local_only", "preserve_unknowns"],
  "evidence_refs": ["test_run_01"],
  "unresolved_refs": ["review_01"],
  "decision_refs": ["decision_01", "decision_02", "decision_03"],
  "next_action_ref": "review_pending_evidence",
  "max_refs": 8
}
```

```text
python "<skill-dir>/scripts/run.py" "<record.json>" --output "<new-report.json>" --max-findings 5
```

Reports use security-agent-skills/report-v1. PASS (exit 0) means only the named record-consistency check or stop decision passed. FIX (1) identifies a declared inconsistency, BLOCKED (2) means invalid/missing input or a rejected operation candidate, and PARTIAL (3) preserves unresolved evidence or authority. No return value authorizes execution. CLI findings point to the logical record and, for task entries, one-based task positions; they are not JSON source line numbers.

Reports omit raw action payloads and freeform text. A checkpoint intentionally includes its validated symbolic references. Other operation reports contain fixed messages, counts, and derived positions. None reads the referenced evidence or observes runtime state. No automatic delegation, messages, retries, memory writes, external transfers, or configuration edits occur.
