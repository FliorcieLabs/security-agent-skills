# Reproducible implementation evidence

Scope: fifteen portable skill workflows, five Markdown agent profiles, bounded local helpers, report contract, copy installer, standalone bundles, package, and CI definitions. Local validation host: Windows x64, Python 3.14.6. Date: October 26, 2026.

## Executed local checks

| Check | Outcome |
|---|---|
| python -m unittest discover -s tests -t . -v | 49 tests passed in 31.061 seconds, including source non-execution, path/link handling, output privacy, no-overwrite behavior, archive integrity, bounded summaries, scope validation, and installed-workflow integration. |
| python -m ruff check src scripts tests | PASS |
| python -m mypy src | PASS, 11 source modules |
| python -m black --check --workers 1 src scripts tests | PASS, 27 files |
| python scripts/build_skills.py --check | PASS, 245 generated files match canonical sources and references |
| python scripts/validate_skills.py | PASS, fifteen portable skill definitions and five bundled agent profiles |
| python scripts/validate_specs.py | PASS, 18 requirement IDs mapped |
| python -m build | Source distribution and pure Python wheel built locally, not published |
| python scripts/package_smoke.py | Offline wheel install, CLI entrypoint and static audit smoke passed |
| uv run --no-project --with tiktoken==0.14.0 python scripts/benchmark_reports.py --tokenizer cl100k_base | Synthetic report: 78,487 to 1,157 tokens, 98.53%; 267,150 to 4,335 UTF-8 bytes, 98.38% |

The installed-workflow regression installs all fifteen bundles into all four temporary host layouts (60 installed bundles), then invokes each helper as an isolated subprocess from outside the checkout with synthetic fixtures. It also checks no-overwrite behavior, snapshot comparison, injection response grading, and archive verification. Tests did not start interactive model sessions in those hosts.

An initial local installed-helper run hit a 30-second process timeout while an unrelated sandboxed formatter process was stalled. After stopping that process, the focused test passed in 25.317 seconds and the complete 49-test suite passed in 31.061 seconds. The subprocess timeout was not relaxed. Sandbox fixture-directory access errors were addressed by running the same commands with normal temporary-directory access, not by changing product behavior.

All five new SKILL.md files passed the skill-creator quick validator. The report serialization fixture remains unchanged: a fresh byte-only benchmark reproduced 267,150 to 4,335 UTF-8 bytes (98.38%). The optional tokenizer measurement in the table is the previously recorded result in docs/report-benchmark.json, not a new tokenizer run.

## External validation

The first macOS runs exposed an ambiguous test sentinel: `/private` was both the synthetic URL path and the host's temporary-directory prefix. The fixture now uses `SYNTHETIC_PRIVATE_PATH` and still checks the entire report for leaked credentials, query values, and URL path content. No runtime behavior changed.

The Quality workflow defines Linux, Windows, and macOS runs on Python 3.11 and 3.14, plus lint, type, format, specification, build, and installed-wheel checks. Final remote status is recorded in the pull request and GitHub Actions checks. A configured workflow is not evidence that it ran; use the completed check for the relevant head commit.

## Limits

Static scanners emit review leads and preserve PARTIAL. No live CVE lookup, package execution, real secret collection, active penetration testing, model-provider request, packet capture, or container sandbox execution was performed. Sandbox output is a plan, and synthetic route events are supplied observations. Archive consistency is not external truth or authenticity. No universal security, interactive host compatibility, billing savings, or adoption claim is made.
