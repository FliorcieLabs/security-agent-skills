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

## T19 README presentation checks

Scope: README navigation and review paths, original PNG banner, a five-frame animated example, static PNG alternative, text walkthrough, normalized JSON examples, and an optional documentation renderer. Product helpers and skill bundles are unchanged. The decorative banner was generated using a visual prompt only; its exact prompt is in docs/assets/security/README.md. This documentation asset generation is separate from analysis CLI behavior.

- `python docs/assets/security/render_demo.py`: PASS. Actual egress CLI invocation on inert synthetic text returned PARTIAL, exit 3, three expected rules, two console findings, and one omitted finding. Coverage shows one text file read, one credential filename excluded, and runtime_observed false. The renderer asserts these values. Only the temporary scope path is normalized in committed reports. Fixture and report text use LF line endings.
- `python -m unittest discover -s tests -t . -v`: PASS, 49 tests in 14.705 seconds.
- `python scripts/validate_skills.py`: PASS, 15 skills and 5 agent profiles.
- `python scripts/build_skills.py --check`: PASS, 245 generated files unchanged.
- `python scripts/validate_specs.py`: PASS, 18 requirements mapped.
- `python -m ruff check docs/assets/security/render_demo.py` and `python -m black --check --workers 1 docs/assets/security/render_demo.py`: PASS.
- README and media-guide relative links: 48 file/directory targets resolved. Navigation anchors match README headings. New Markdown contains no em or en dashes.
- Pillow decode and verification: banner 2172 x 724, static demo 1120 x 650, GIF 1120 x 650 with five frames and 15,600 ms loop duration. All five frames were visually inspected. The GIF is a rendered summary, not a screen recording. Static and text alternatives are linked.
- `git diff --check`: PASS. No runtime dependency, installer change, new skill, package publication, or protected-main merge is part of T19.

The first renderer attempt could not create a fixture subdirectory in the restricted sandbox's temporary directory. The same renderer succeeded with normal temporary-directory access. No filesystem permission workaround was added to the project.
