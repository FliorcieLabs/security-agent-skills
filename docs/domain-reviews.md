# Domain review workflows

Fifteen domain skills provide platform-neutral Markdown instructions, portable role profiles, and optional Python 3.11+ evidence-record validation. Existing installer adapters support Claude, Codex, Cursor, and Copilot directory layouts. Other hosts can load Markdown manually. Native discovery and real assistant behavior remain host-dependent and unverified for these additions.

## Installation

Preview from the repository root, then apply if intended:

```sh
python scripts/install_skills.py --agent all --project /path/to/project --skill agent-approval-binding-review
python scripts/install_skills.py --agent all --project /path/to/project --skill agent-approval-binding-review --apply
```

Repeat --skill for a selection or omit it for the full catalog. Existing destinations are never overwritten. This does not register native subagents, grant permissions, enable CI, or add MCP tools.

## Evidence and output

Read the selected skill's workflow for its five controls and synthetic scenario. Review actual project artifacts with available tools and existing authorization. Each example under examples/domain-reviews starts with no supplied checks, so all five controls remain unknown.

The helper accepts schema, domain, symbolic scope, and checks. Each check contains id, outcome, basis, and up to eight symbolic evidence references. Non-unknown outcomes require evidence and an observed or reproduced declaration. Not-applicable decisions require a rationale reference. Unknown outcomes require unknown basis. Missing controls become unknown. Shape, duplicate, domain, and consistency errors return BLOCKED, exit 2.

References are not opened. The helper neither inspects the project nor independently verifies supplied claims, test results, authorization, or exploitability. Every valid result remains PARTIAL, exit 3, even with all declared passes. No security score is produced.

--max-findings bounds console findings with omissions counted. --output new-report.json saves all findings and control states and refuses overwrite. Preserve full evidence locally before compacting replies. Initially return up to three priority findings, counts, evidence IDs, actual validation results, and unresolved scope. No measured model-token or billing improvement is asserted.

## Boundaries

These workflows are not automatic scanners, exploitation engines, or complete security coverage. Active tests require explicit authorization and bounded disposable targets. Missing access or execution is not a passed test. Standard-library helpers perform no independent network requests; the invoking host's provider policies remain separate. Evidence IDs may still be sensitive. Existing four MCP tools are unchanged. CI is neither required nor enabled.
