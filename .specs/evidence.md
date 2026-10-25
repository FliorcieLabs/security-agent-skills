# Reproducible implementation evidence

Scope: ten portable skill workflows, bounded local helpers, report contract, copy installer, standalone bundles, package, and CI definitions. Local validation host: Windows x64, Python 3.14.6. Date: October 26, 2026.

## Executed local checks

| Check | Outcome |
|---|---|
| python -m unittest discover -s tests -t . -v | 39 tests passed, including source non-execution, path/link handling, no-overwrite behavior, manifest and archive integrity, bounded summaries, scope validation, and all-workflow CLI integration. |
| python -m ruff check src scripts tests | PASS |
| python -m mypy src | PASS, 10 source modules |
| python -m black --check src scripts tests | PASS |
| python scripts/build_skills.py --check | PASS, 150 generated files match canonical sources and references |
| python scripts/validate_skills.py | PASS, ten portable name/description skill definitions |
| python scripts/validate_specs.py | PASS, 12 requirement IDs mapped |
| python -m build | Source distribution and pure Python wheel built locally, not published |
| python scripts/package_smoke.py | Offline wheel install, CLI entrypoint and static audit smoke passed |
| uv run --no-project --with tiktoken==0.14.0 python scripts/benchmark_reports.py --tokenizer cl100k_base | Synthetic report: 78,487 to 1,157 tokens, 98.53%; 267,150 to 4,335 UTF-8 bytes, 98.38% |

Local tests installed selected bundles into temporary project roots for Claude, Codex, Cursor, and Copilot, then invoked their independent helper entrypoints. Tests did not start interactive model sessions in those hosts.

## External validation

The Quality workflow defines Linux, Windows, and macOS runs on Python 3.11 and 3.14, plus lint, type, format, specification, build, and installed-wheel checks. Final remote status is recorded in the pull request and GitHub Actions checks. A configured workflow is not evidence that it ran; use the completed check for the relevant head commit.

## Limits

Static scanners emit review leads and preserve PARTIAL. No live CVE lookup, package execution, real secret collection, active penetration testing, model-provider request, packet capture, or container sandbox execution was performed. Sandbox output is a plan, and synthetic route events are supplied observations. Archive consistency is not external truth or authenticity. No universal security, interactive host compatibility, billing savings, or adoption claim is made.
