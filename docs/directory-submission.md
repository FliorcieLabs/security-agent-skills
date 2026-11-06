# AgenticSkills submission kit

Checked November 6, 2026 against the [skill form](https://agenticskills.io/submit), [MCP form](https://agenticskills.io/submit?type=mcp), and [inclusion criteria](https://agenticskills.io/methodology).

## What to submit

The form requests source links and metadata, not a ZIP upload or branch deployment. Keep main public and use the repository as the canonical source.

The methodology recognizes individual skill paths in monorepos. For distinct listings, submit individual skill names using the same repository and identify each skill path. The published instructions do not promise automatic import of all 41 skills or confirm acceptance of subdirectory URLs in the repository field. Ask directory staff about batch intake before submitting 41 entries. A collection submission does not establish that every skill will be indexed.

Use the separate MCP form for the optional server. It is one server with four tools. The checked forms do not document a separate agent-profile submission route. Profiles are companion Markdown instructions, not independent executable agents.

## Initial skill listing

| Field | Suggested value |
|---|---|
| Skill Name | agent-egress-audit |
| GitHub Repository URL | https://github.com/FliorcieLabs/security-agent-skills |
| Short Description | Review local agent packages for outbound data-flow indicators, sensitive input access, and execution boundaries. Compact reports preserve evidence, skipped scope, and unknowns. |
| Tags | security, agent-skills, egress, local-first, supply-chain |
| Author Name | Maintainer public identity associated with the repository |
| Email | Maintainer-controlled contact address |
| Category | Closest security category available in the actual form |

Source: [Agent Egress Audit](../skills/agent-egress-audit/SKILL.md). If staff accept a collection listing, use Security Agent Skills and describe it as a preview collection of 41 local security and agent-operation workflows. Other strong focused candidates are MCP Authority Review, Agent Package Change Sentinel, and Security Fix Verification.

## MCP listing

| Field | Suggested value |
|---|---|
| MCP Server Name | Security Agent Skills: Local Security Records |
| Repository or MCP URL | https://github.com/FliorcieLabs/security-agent-skills |
| Short Description | Local stdio MCP server for declared attack paths, detection replay, regression comparisons, and focused skill routing. Four bounded record tools preserve coverage and unknowns. |
| Tags | security, mcp, stdio, detection, evidence |
| Client Compatibility | State stdio support and tested scope; do not mark every client as live-tested |

Supporting documentation: [server setup](mcp.md), [compatibility](compatibility.md), and [preview assessment](release-readiness.md). Enter author and contact details yourself. Do not submit private findings, credentials, or local evidence reports.

## Claims and verification

The current code has 41 skills, 31 profiles, and four MCP tools. T31 records 124 passing tests on each of Windows Python 3.11.15 and 3.14.6, including 164 installed bundles per suite. Earlier T30 evidence includes an independent MCP SDK client check. See [.specs/evidence.md](../.specs/evidence.md).

These are recorded checks, not proof of universal assistant compatibility. Latest Linux/macOS execution, all native assistant sessions, and automatic discovery remain unverified. Fifteen domain helpers check declared records; they do not scan projects or verify evidence references. Preserve the preview label and bounded capability descriptions.

Listing is selective. Acceptance, ranking, and popularity are not guaranteed. Preparing this kit does not submit a form or publish a release.
