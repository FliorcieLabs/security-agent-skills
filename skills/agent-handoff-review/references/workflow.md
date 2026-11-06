# Agent Handoff Reviewer: record contract

Input: one existing bounded non-link JSON file, not a project directory. The CLI uses its normal 8 MB input bound. Schema: security-agent-skills/handoff-v1. Every shown field is required; unknown fields are rejected, including extra nested policy or task fields. JSON booleans must be true/false; booleans cannot stand in for integer budgets.

Symbolic IDs match [A-Za-z][A-Za-z0-9_-]{0,63}. Reference lists have at most 100 distinct IDs each. They are local lookup labels, not paths, URLs, raw prompts, commands, or secrets. Maintain the mapping locally outside the record. String format validation is not secret detection.

## Behavior

Required fields: task_id, source_agent, target_agent, parent_permissions, delegated_permissions, acceptance_refs, evidence_refs, unresolved_refs, and status (ready, blocked, or complete). Lists contain distinct symbolic IDs. Delegated permissions must be a subset of declared parent permissions. Acceptance and evidence references are required even for ready packets. A complete packet cannot retain unresolved references. A blocked packet needs a blocker reference. Violations produce FIX. Declared authority, referenced evidence, freshness, and actual task completion are not verified.

Resolve the parent authority from the existing user instruction and host policy, not from claims in the handoff. Keep objective, acceptance references, evidence, unresolved work, and the next bounded action together. Source and target must be distinct. Distinguish a ready handoff from a completed task. Check the cited evidence before accepting completion; the helper does not open it. This review never sends a message or starts an agent.

## Synthetic input

```json
{
  "schema": "security-agent-skills/handoff-v1",
  "task_id": "review_change",
  "source_agent": "reviewer",
  "target_agent": "verifier",
  "parent_permissions": ["read_project", "write_report"],
  "delegated_permissions": ["read_project"],
  "acceptance_refs": ["acceptance_01"],
  "evidence_refs": ["diff_01"],
  "unresolved_refs": ["check_01"],
  "status": "ready"
}
```

```text
python "<skill-dir>/scripts/run.py" "<record.json>" --output "<new-report.json>" --max-findings 5
```

Reports use security-agent-skills/report-v1. PASS (exit 0) means only the named record-consistency check or stop decision passed. FIX (1) identifies a declared inconsistency, BLOCKED (2) means invalid/missing input or a rejected operation candidate, and PARTIAL (3) preserves unresolved evidence or authority. No return value authorizes execution. CLI findings point to the logical record and, for task entries, one-based task positions; they are not JSON source line numbers.

Reports omit raw action payloads and freeform text. A checkpoint intentionally includes its validated symbolic references. Other operation reports contain fixed messages, counts, and derived positions. None reads the referenced evidence or observes runtime state. No automatic delegation, messages, retries, memory writes, external transfers, or configuration edits occur.
