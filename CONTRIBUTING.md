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

Keep SKILL.md focused and short. Put mode-specific inputs in references/workflow.md. Do not force implicit activation, read entire projects into context, grant tool permissions, or add telemetry. Every claimed runtime check needs reproducible evidence. Host documentation support is different from interactive client verification.

Run package checks without publishing. Do not add release automation, tags, or package publishing without explicit maintainer authorization. See .specs for requirement IDs and traceability.
