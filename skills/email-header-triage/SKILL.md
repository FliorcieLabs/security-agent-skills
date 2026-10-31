---
name: email-header-triage
description: "Review a supplied email header block for claimed SPF/DKIM/DMARC results and From/Reply-To differences without DNS, attachment processing, or sender verification."
---

# Email Header Triage

Adapted helper provenance: analyzing-email-headers-for-phishing-investigation from mukul975/Anthropic-Cybersecurity-Skills at revision 54a798831d2266a3ca61ce68a7acb80b81160d57. Copyright 2026 mukul975; upstream skill author metadata mahipal. Selected runtime portions remain Apache-2.0. Fliorcie Labs added this bounded offline adapter and workflow on October 31, 2026. See THIRD_PARTY_NOTICES.md and LICENSES/Apache-2.0.txt in this bundle. No affiliation or endorsement is implied.

Read [the input contract and synthetic example](references/workflow.md). Analyze a supplied local header record only. Keep real message addresses, tokens, cookies, and private header values out of hosted prompts. The helper does not acquire evidence or perform live verification.

```sh
python scripts/run.py /path/to/header-record.json
```

Replace the example path with the actual record. Python 3.11+ is required. Valid analysis returns PARTIAL (exit 3), including zero leads. Invalid input returns BLOCKED (exit 2). Read JSON details; the Markdown summary omits them. Preserve unknowns and avoid sender-authentication, application-safety, or compliance claims. Report Result, Details, Validation, and Remaining.

The [portable role](references/agent.md) grants no tools and requires no native subagent API. Without local execution, label the missing executable check BLOCKED and distinguish manual review from helper results.
