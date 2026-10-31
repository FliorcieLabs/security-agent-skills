---
name: security-skill-router
description: "Select a bounded set of local security skills from explicit goals and preserve unknown or deferred work."
---

# Security Skill Router

Use the supplied local JSON record for this decision. Read [the contract](references/workflow.md) before constructing inputs. Resolve symbolic evidence with the user before treating it as fact. Keep private source and raw event values out of prompts.

Run with Python 3.11+ from the installed skill directory:

```sh
python scripts/run.py /path/to/record.json
```

Replace the example path with the user's actual record. The helper never executes target code, probes services, or grants permissions. Read JSON output; Markdown summaries omit details. A valid analysis returns PARTIAL (exit 3). Invalid input returns BLOCKED (exit 2). Preserve unknowns, excluded cases, and deferred work. Report Result, Details, Validation, and Remaining with evidence references and explicit limits. Never infer universal platform compatibility or security coverage.

A portable [agent profile](references/agent.md) is included. Without Python or required execution access, inspect the record manually and label the missing executable check BLOCKED. Do not fabricate outputs.
