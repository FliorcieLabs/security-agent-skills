---
name: mail-auth-review
description: "Review supplied email authentication claims and sender/reply-to differences with concise output; no DNS or sender verification."
---

# Mail Auth Review

Review a bounded local header record. Read the [contract](references/workflow.md) when constructing input. Python 3.11+ is required.

```sh
python scripts/run.py /path/to/record.json
```

Default: brief JSON, at most three leads, total/omitted counts, observations, and explicit uncertainty. Use `--view full --max-findings 20` for the complete console report. `--output new-report.json` always saves full evidence and refuses overwrite. Preserve PARTIAL (exit 3); invalid records return BLOCKED (exit 2). Never describe supplied header claims as verified security.

For a combined email/web record, run `python scripts/run.py header-review /path/to/combined.json`. Missing input stays visible. Load only the routed skill and requested references. In replies: result, key leads, next decision, unresolved scope. Do not repeat the input or raw values. If findings are omitted, inspect full evidence before deciding.

Selected helpers are adapted under Apache-2.0. Original authorship, revision, and changes are in THIRD_PARTY_NOTICES.md and third-party-provenance.json; both licenses are bundled. [Portable role](references/agent.md).
