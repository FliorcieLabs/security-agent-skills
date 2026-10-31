# Host compatibility

All twenty-six skills use the common name/description YAML frontmatter subset and a self-contained Python 3.11+ helper. There are no vendor-specific tool permission grants, plugin hooks, MCP dependencies, absolute machine paths, or repository-location imports inside a built bundle.

The installer uses native discovery roots. Current source references:

- [Claude Code skills](https://code.claude.com/docs/en/skills): project and personal .claude/skills roots.
- [Codex skills](https://learn.chatgpt.com/docs/build-skills): project and personal .agents/skills roots.
- [Cursor skills](https://cursor.com/help/customization/skills): project and personal .cursor/skills roots, with compatibility roots also supported.
- [GitHub Copilot CLI skills](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference): project .github/skills and personal .copilot/skills roots. Copilot surfaces and rollout versions can differ; check that your IDE or CLI supports agent skills.

Format checks, temporary project installs for all four hosts, and standalone helper execution run through local test commands, not a CI pipeline. Recognition in an older client, personal-to-cloud synchronization, and model decision quality are not established by a filesystem install test. Use the host's skill picker or restart its discovery process if it has cached the old list. The installer does not force a reload.

The sixteen Markdown agent profiles can be read as ordinary instructions on other AI platforms. They are also bundled in the matching skills at references/agent.md. This is text portability, not universal native registration. Assistants with no local tools can review supplied excerpts and preserve partial coverage; helper execution needs a terminal and Python. See agents.md.

Internal operations use explicit local JSON records. They do not assume a host-specific orchestration, delegation, memory, or retry API. Directory-layout tests exercise all twenty-six helpers in all four supported installation layouts; they do not start interactive model sessions or prove host decision quality. See [operation contracts](internal-operations.md).

## Recorded host evidence

On October 27, 2026, this Codex desktop session explicitly loaded the Egress Audit, Task Planner, and Tool Preflight instructions and invoked installed helpers on synthetic local inputs. Egress returned PARTIAL with one outbound-client lead; Task Planner returned bounded PASS; matching Preflight returned PARTIAL and authorization_granted false. The local fixture was not executed and no additional model sessions were launched. [Recorded results](compatibility-evidence.json).

| Surface | Verified | Not verified |
|---|---|---|
| Current Codex desktop session on Windows | Explicit Markdown loading and helper invocation for three representative skills | Native automatic discovery, all twenty-six decision workflows, other Codex surfaces |
| Claude Code | Temporary directory layout and isolated helper execution | Real assistant session and automatic discovery; CLI unavailable in this environment |
| Cursor | Temporary directory layout and isolated helper execution | Real assistant session and automatic discovery; CLI unavailable in this environment |
| Copilot | Temporary directory layout and isolated helper execution | Real assistant session and automatic discovery |
| macOS | Historical older-scope test evidence only | Latest full skill set and preview revision; this Windows host cannot establish macOS execution |

These are preview support limits. There is no claim of universal native agent support or complete platform validation. The unavailable checks are not replaced with a passing status, and no hosted CI is required to use or release a preview with these limits disclosed.

## Development preview additions

Version 0.1.0a2 adds four record-analysis workflows and four Markdown roles. Local CLI and isolated installed-layout execution are tested; the earlier three explicit Codex workflows remain historical 0.1.0a1 evidence. No new Claude, Cursor, Copilot, macOS, or automatic-discovery result is implied. The optional stdio MCP interface is tested through a protocol subprocess; real host registration and assistant tool selection remain unverified. [MCP setup and boundaries](mcp.md).

Version 0.1.0a3 adds two attributed offline header adaptations with portable Markdown profiles and retained Apache-2.0 notices. Their helpers accept local records and perform no independent external requests. They are not additional MCP tools. [Scope and provenance](adapted-skills.md).
