# Security Skill Router contract

Required fields: `schema`, `goals`, `max_skills`. Goals are a nonempty unique symbolic ID array, at most 100. The skill cap is an integer from 1 to 24; booleans are rejected. Routing uses the closed vocabulary below and lexical selection, not model inference or risk priority. Unknown goals and skills deferred by the cap remain visible and selection_complete is false. Never silently discard deferred work when it is necessary for the user task. A complete selection is still not proof of host discovery or skill suitability.

Load only the selected SKILL.md files, then retrieve workflow references on demand. The helper does not read or install those files. Repository-relative references are logical paths; resolve them under the user's actual installed skill root. This reduces selected discovery entries, not a measured number of model tokens.

All symbolic IDs match `[A-Za-z][A-Za-z0-9_-]{0,63}`. Reject extra fields, duplicate JSON keys, unknown schema versions, wrong types, duplicate IDs, oversized arrays, and invalid references. CLI input is a regular non-link JSON file of at most 8 MB. MCP messages have a separate 1 MB limit. JSON results use `security-agent-skills/report-v1`. All valid results remain PARTIAL and source_claims_verified is false. Input labels do not attest to runtime truth.

## Goal vocabulary

| Goal | Skill |
|---|---|
| `agent_egress` | `agent-egress-audit` |
| `app_exposure` | `security-exposure-review` |
| `attack_paths` | `attack-path-rehearsal` |
| `authorized_testing` | `authorized-appsec-validation` |
| `ci_review` | `ci-workflow-security-audit` |
| `containers` | `container-boundary-audit` |
| `context_resume` | `agent-context-checkpoint` |
| `dependencies` | `dependency-provenance-audit` |
| `detection_rules` | `detection-replay-lab` |
| `evidence_archive` | `security-evidence-pack` |
| `handoff` | `agent-handoff-review` |
| `infrastructure` | `infrastructure-exposure-audit` |
| `install_plan` | `safe-install-sandbox` |
| `instruction_trust` | `instruction-boundary-audit` |
| `llm_data` | `llm-data-boundary-audit` |
| `mcp_authority` | `mcp-authority-review` |
| `package_upgrade` | `agent-package-change-sentinel` |
| `prompt_injection` | `prompt-injection-boundary-lab` |
| `regression_metrics` | `security-regression-board` |
| `retry` | `agent-retry-guard` |
| `secret_routes` | `secret-route-mapper` |
| `skill_selection` | `security-skill-router` |
| `task_graph` | `agent-task-planner` |
| `tool_proposal` | `agent-tool-preflight` |

## Synthetic example

```json
{
  "schema": "security-agent-skills/skill-route-v1",
  "goals": [
    "agent_egress",
    "instruction_trust",
    "mcp_authority"
  ],
  "max_skills": 2
}
```

For MCP clients, the corresponding tool is `skill_route`, taking an object with one `record` property containing this document. It returns the same report as the CLI. No files are read by that tool.
