# Host compatibility

All fifteen skills use the common name/description YAML frontmatter subset and a self-contained Python 3.11+ helper. There are no vendor-specific tool permission grants, plugin hooks, MCP dependencies, absolute machine paths, or repository-location imports inside a built bundle.

The installer uses native discovery roots. Current source references:

- [Claude Code skills](https://code.claude.com/docs/en/skills): project and personal .claude/skills roots.
- [Codex skills](https://learn.chatgpt.com/docs/build-skills): project and personal .agents/skills roots.
- [Cursor skills](https://cursor.com/help/customization/skills): project and personal .cursor/skills roots, with compatibility roots also supported.
- [GitHub Copilot CLI skills](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference): project .github/skills and personal .copilot/skills roots. Copilot surfaces and rollout versions can differ; check that your IDE or CLI supports agent skills.

Format checks, temporary project installs for all four hosts, and standalone helper execution are automated. Interactive Claude, Cursor, Copilot, and Codex model sessions are not part of those tests. Recognition in an older client, personal-to-cloud synchronization, and model decision quality are not established by a filesystem install test. Use the host's skill picker or restart its discovery process if it has cached the old list. The installer does not force a reload.

The five new Markdown agent profiles can be read as ordinary instructions on other AI platforms. They are also bundled in the matching skills at references/agent.md. This is text portability, not universal native registration. Assistants with no local tools can review supplied excerpts and preserve partial coverage; helper execution needs a terminal and Python. See agents.md.
