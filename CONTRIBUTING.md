# Contributing

Work from integ and propose a reviewed pull request to main. Keep one semantic change per commit when practical. Never weaken security checks just to make a fixture pass.

Use Python 3.11+ and an isolated environment. Runtime code must use the standard library. Optional development tools are pinned in requirements-dev.txt.

```sh
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -t . -v
python -m ruff check src scripts tests
python -m mypy src
python -m black --check src scripts tests
python scripts/build_skills.py
python scripts/build_skills.py --check
python scripts/validate_skills.py
python scripts/validate_specs.py
python -m build
python scripts/package_smoke.py
```

Modify src/security_agent_skills, then regenerate the skill copies with build_skills.py. Do not patch generated helper copies individually. A canonical change must produce the same bytes in every bundle. Include regression tests for permission, path, secret handling, incomplete coverage, archive integrity, and output contract changes.

Catalog entries define the installed skill inventory. An optional agent field names a canonical Markdown profile under agents/. The builder includes that profile as references/agent.md in its skill bundle and hashes it with the other files. Update the catalog, requirement traceability, selection limits, and installed-workflow fixtures when adding a skill. The installed-workflow test executes all twenty helpers in all four host directory layouts using synthetic inputs and isolated subprocesses.

Internal-operation contracts live in internal_operations.py, schemas/internal-operations-v1.schema.json, and the five standalone workflow references. Keep synthetic examples in examples/internal-operations aligned with those contracts. Reject invalid or ambiguous input without echoing it. Preserve the distinction between record consistency, actual authority, evidence truth, and runtime execution. Never turn a matching preflight into a host permission grant or an unknown write into an automatic retry.

Keep SKILL.md focused and short. Put mode-specific inputs in references/workflow.md. Do not force implicit activation, read entire projects into context, grant tool permissions, or add telemetry. Every claimed runtime check needs reproducible evidence. Host documentation support is different from interactive client verification.

Run package checks without publishing. Do not add release automation, tags, or package publishing without explicit maintainer authorization. See .specs for requirement IDs and traceability.
