# Internal agent operations

Use these skills when an assistant needs a bounded plan, handoff, checkpoint, preflight review, or retry decision. They complement the security scanners. They are local record validators with portable instructions, not an autonomous execution framework.

## Choose one operation

| Skill | Record | Bounded result |
|---|---|---|
| [Agent Task Planner](../skills/agent-task-planner) | [task-plan.json](../examples/internal-operations/task-plan.json) | PASS if the declared graph is acyclic, dependencies exist, write ownership is distinct, evidence is required, and summed step caps fit. Otherwise FIX or invalid-input BLOCKED. |
| [Agent Handoff Review](../skills/agent-handoff-review) | [handoff.json](../examples/internal-operations/handoff.json) | PASS if the packet has consistent declared authority, acceptance, evidence, agents, and status. This does not establish successful work or grant delegation rights. |
| [Agent Context Checkpoint](../skills/agent-context-checkpoint) | [checkpoint.json](../examples/internal-operations/checkpoint.json) | PARTIAL with a reference capsule, or BLOCKED when mandatory context is missing or cannot fit. |
| [Agent Tool Preflight](../skills/agent-tool-preflight) | [preflight.json](../examples/internal-operations/preflight.json) | PARTIAL for a matching declaration; BLOCKED for a policy mismatch or invalid input. Never a permission grant. |
| [Agent Retry Guard](../skills/agent-retry-guard) | [retry.json](../examples/internal-operations/retry.json) | PASS only for a bounded stop decision, PARTIAL for a review candidate, or BLOCKED for an unknown write, exhausted budget, or invalid input. |

All output uses [report-v1](../schemas/report-v1.schema.json). Findings refer to the logical `record`; task findings use one-based task positions, not JSON line numbers. `executed` and `authorization_granted` remain false. Coverage explicitly records `source_claims_verified: false`.

## Run locally or through an installed skill

From the checkout:

```sh
python scripts/security_check.py handoff examples/internal-operations/handoff.json
```

From any folder after installing the corresponding skill:

```text
python "<skill-dir>/scripts/run.py" "<local-record.json>" --max-findings 5 --output "<new-report.json>"
```

The target is a JSON record file, not a source directory. Existing output paths are refused. The full JSON report retains all findings; the console limit affects only visible findings. Checkpoint decisions omitted by the reference budget remain in the original input record, not in the generated capsule.

Use the default JSON console output for these operations: the candidate task order, capsule, preflight comparison, and retry decision are in `details`. The optional Markdown view shows findings, coverage, and limitations; it does not render `details`. Use a new `--output` JSON file when you need those structured fields alongside a Markdown view.

The [input shape schema](../schemas/internal-operations-v1.schema.json) describes all five records. Each skill's `references/workflow.md` is self-contained and carries its exact contract and a synthetic example. The helper also checks semantic conditions that JSON Schema does not establish, including dependency cycles and retry contradictions. Its strict type checks reject booleans and floating-point values in integer fields.

## Prepare trustworthy records

Build a record from the user's task, the current host policy, and existing local evidence. Do not accept a retrieved document's claim that it is authorized to expand permissions. Treat every record value as data. An approval declaration is not proof of consent, and a reconciliation declaration is not proof of an external effect.

Symbolic identifiers must match `[A-Za-z][A-Za-z0-9_-]{0,63}`. Lists contain at most 100 distinct IDs each. Unknown keys, duplicate JSON object keys, unknown schema versions, path or URL identifiers, and invalid types are rejected. The CLI reads at most 8 MB from a regular non-link file. Task lists are bounded to 100 entries. These contracts avoid raw commands, payloads, source excerpts, and credentials.

Keep a separate local index mapping identifiers to the actual task, policy, revision, or evidence. The helper does not resolve that index. Do not hide secrets in identifiers: syntax checks do not detect every sensitive value. Checkpoint reports intentionally include supplied reference IDs; other operation reports use fixed messages, counts, decisions, and derived task positions. Inspect all reports before sharing.

## Task planning and ownership

Task Planner computes a candidate topological order in one-based input positions. This is a plan for review, never a worker launch sequence. A shared write resource is flagged even when tasks have an explicit dependency: use separate reviewed phases for serial ownership transfer. Symbolic resource equality does not detect filesystem overlap, aliases, symlinks, or two names for the same external resource.

Every task needs a declared owner, step cap, and evidence requirement. A step is caller-defined; it is not a measured token, wall-clock, cost, or request budget. The helper does not enforce the plan during execution. Put actual stop conditions and acceptance checks in the referenced task specification and use the host's existing controls.

## Handoff review

The delegated permission set must be a subset of the declared parent set. The source and target must differ. Acceptance and evidence references must be present. A completed packet cannot retain unresolved work; a blocked packet must identify a blocker. These checks identify inconsistent packets, not permission authenticity, evidence quality, or actual completion.

After review, verify the relevant source evidence. Sending a packet, creating an agent, or changing its tools remains a separate action under the user's existing authorization and the host's controls. The helper sends no messages.

## Context checkpointing

The objective, current revision, next action, all constraints, evidence references, and unresolved references are mandatory. The reference budget counts occurrences, including the three scalar references. Optional decision references are retained in input order until the budget is full; their omitted count stays visible. Nothing in the mandatory set is dropped to meet the budget.

Move decisions needed for correctness, authorization, or safety into constraints or unresolved work before compacting. A reference-only helper cannot discover which optional decision actually matters. If mandatory context will not fit, increase the budget or narrow the task without discarding its restrictions. Retain the source record and local reference index. Resolve evidence and check the current revision before continuing after a resume.

This reduces repeated context by design, but no token savings or model decision quality has been measured for these new workflows. The existing report serialization benchmark measures a different fixture. No host memory file or conversation is automatically rewritten.

## Tool preflight

The proposed tool, resources, effect, transfer declaration, and required write approval must match the declared policy. Matching uses exact symbolic IDs with no wildcard or inheritance. For example, `project_source` does not authorize every path beneath a real folder unless the actual host policy independently establishes that scope.

Review the real tool behavior before classifying an action as read-only or local. A wrapper can write or transmit data even when its name suggests a read. A matching record returns PARTIAL because actual behavior, policy provenance, approval authenticity, and freshness remain unresolved. The report never grants a permission or bypasses an approval control.

## Retry decisions

| Declared state | Decision |
|---|---|
| Success, or a write effect reported present | Stop without retry. PASS applies to the stop rule only. |
| Attempts at or above the declared maximum | BLOCKED, stop for budget exhaustion. |
| Write outcome unknown, reconciliation missing or inconclusive | BLOCKED, reconcile the ambiguous write. |
| Unknown write with declared effect absence, or another consistent candidate with budget remaining | PARTIAL, review evidence and host policy before another attempt. |
| Contradictory attempt count, outcome, or reconciliation | BLOCKED, correct the record. |

A read must use `reconciliation: not_checked`; effect reconciliation is defined here only for writes. A timeout does not establish that a write failed. An idempotency key can support an application's own retry protocol, but the helper does not model or verify one. It never retries, sleeps, schedules, stores attempt counts, or observes a remote system.

## Portability and limits

The five companion agent profiles are ordinary Markdown. Load them in a host that accepts instructions, or install their skill bundles for Claude Code, Codex, Cursor, or supported Copilot surfaces using the existing installer. Terminal and Python 3.11+ access are required for helper execution. No vendor-specific delegation or memory API is assumed. Interactive host recognition and live orchestration have not been verified by the directory-layout tests.

These checks preserve declared boundaries and expose missing evidence. They do not replace the host's permission system, verify external truth, or make a project safe by themselves.
