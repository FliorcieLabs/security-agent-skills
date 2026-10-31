# Agent Retry Guard: record contract

Input: one existing bounded non-link JSON file, not a project directory. The CLI uses its normal 8 MB input bound. Schema: security-agent-skills/retry-v1. Every shown field is required; unknown fields are rejected, including extra nested policy or task fields. JSON booleans must be true/false; booleans cannot stand in for integer budgets.

Symbolic IDs match [A-Za-z][A-Za-z0-9_-]{0,63}. Reference lists have at most 100 distinct IDs each. They are local lookup labels, not paths, URLs, raw prompts, commands, or secrets. Maintain the mapping locally outside the record. String format validation is not secret detection.

## Behavior

Required fields: effect (read/write), outcome (not_started/succeeded/failed_no_effect/unknown), attempts (0 to 100), max_attempts (1 to 100), and reconciliation (not_checked/effect_absent/effect_present/inconclusive). not_started requires zero attempts; other outcomes require a positive count. Effect reconciliation is defined only for writes. Contradictory outcome and reconciliation claims are BLOCKED. Success or effect_present returns a bounded PASS stop decision. An exhausted budget is BLOCKED. An unknown write is BLOCKED until effect_absent is declared; remaining candidates are PARTIAL and still require evidence and host policy review. The helper never records attempts, sleeps, schedules, or enforces a live retry policy.

Classify the actual effect and outcome from evidence. A timed-out write is unknown until reconciled; transport failure does not establish no effect. Stop after success or a confirmed effect. Keep the attempt budget, existing idempotency design, and stop conditions in the surrounding task. Do not treat an idempotency key as proof that a write did not occur. The helper returns a review decision only, never a retry. Check evidence freshness before relying on a supplied reconciliation claim.

## Synthetic input

```json
{
  "schema": "security-agent-skills/retry-v1",
  "effect": "write",
  "outcome": "unknown",
  "attempts": 1,
  "max_attempts": 3,
  "reconciliation": "not_checked"
}
```

```text
python "<skill-dir>/scripts/run.py" "<record.json>" --output "<new-report.json>" --max-findings 5
```

Reports use security-agent-skills/report-v1. PASS (exit 0) means only the named record-consistency check or stop decision passed. FIX (1) identifies a declared inconsistency, BLOCKED (2) means invalid/missing input or a rejected operation candidate, and PARTIAL (3) preserves unresolved evidence or authority. No return value authorizes execution. CLI findings point to the logical record and, for task entries, one-based task positions; they are not JSON source line numbers.

Reports omit raw action payloads and freeform text. A checkpoint intentionally includes its validated symbolic references. Other operation reports contain fixed messages, counts, and derived positions. None reads the referenced evidence or observes runtime state. No automatic delegation, messages, retries, memory writes, external transfers, or configuration edits occur.
