# Reproducible implementation evidence

Current delivery: 26 skills, 16 Markdown agent profiles, four optional MCP tools, and 31 mapped requirements. Latest fresh-archive E2E validation and benchmark reproducibility correction is T30 below. Earlier sections retain their original counts and timings as historical evidence.

## T01 through T18 baseline

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

## T20 through T24 internal operations

Scope: five new local record helpers, five skills, five Markdown profiles, formal input shape schema, five synthetic records, CLI routing, standalone bundles, documentation, and regression coverage. No new runtime dependencies, network clients, tool dispatch, agent spawning, permissions, memory writes, or retry execution were introduced.

| Executed command or check | Outcome |
|---|---|
| python -m unittest discover -s tests -t . -v | PASS, 67 tests in 20.479 seconds. Includes 18 new tests, strict record shapes, duplicate JSON keys, authority mismatches, evidence preservation, retry contradictions, existing regressions, and all installed workflows. |
| Installed-workflow integration | PASS, 20 skills across four temporary host layouts, 80 installed bundles, isolated subprocesses outside the checkout. |
| Existing end-to-end CLI test | PASS, new operation commands run while network and subprocess calls are patched to fail if attempted. |
| python -m ruff check src scripts tests | PASS |
| python -m mypy src | PASS, 12 source modules |
| python -m black --check --workers 1 src scripts tests | PASS, 29 files |
| python scripts/build_skills.py --check | PASS, 350 generated files match canonical sources |
| python scripts/validate_skills.py | PASS, 20 skills and 10 profiles |
| python scripts/validate_specs.py | PASS, 23 mapped requirements |
| python -m build | PASS, local source distribution and wheel built, not published |
| python scripts/package_smoke.py | PASS, offline wheel install, help, egress scan, and new preflight command with authorization_granted false |
| python scripts/benchmark_reports.py | PASS, existing synthetic serialization fixture remains 267,150 to 4,335 bytes, 98.38%; no new tokenizer run or checkpoint savings measurement |
| skill-creator quick_validate.py on the five new skill folders | PASS, all five |
| Local Draft202012Validator | PASS, formal input schema, all five supplied examples, and rejection of an invalid newline-bearing identifier; optional development validator, not a runtime dependency |
| Markdown checks | PASS, 21 touched entrypoint/profile/guide files, 76 relative links and seven README navigation anchors; no em or en dashes |
| git diff --check | PASS |

The sandboxed formatter stalled and was stopped before running the same formatting command with normal process access. No code or test timeout was relaxed. The full test suite and package smoke ran with normal temporary-directory access.

The helpers validate declarations, not the truth of referenced evidence. Matching preflight and generated checkpoints remain PARTIAL. Task/handoff PASS means the named record consistency checks passed; retry PASS means a stop decision under supplied claims. All reports keep executed and authorization_granted false. Only checkpoint reports intentionally include symbolic references. No live orchestration, native agent registration, interactive model sessions, host memory integration, external effect reconciliation, or new token savings measurement was performed. Remote CI applies to the pushed commit and remains a separate PR gate.

The final documentation examples use default JSON output because operation decisions and checkpoint capsules live in details, which the existing Markdown view does not render. A direct task-plan example displayed candidate_order_positions [1, 2]; a direct checkpoint example displayed all seven mandatory references and one optional decision, with two optional decisions omitted. Its PARTIAL exit 3 is expected. Documentation and bundles were revalidated after this clarification; no runtime code changed.

## T25 CI disablement and release review

Date: October 27, 2026. Baseline fc23339 plus the correction and documentation recorded in this delivery. Remote Quality workflow 396292068 was disabled as requested; API verification returned disabled_manually. The saved workflow has workflow_dispatch only. Main review protections and the required quality-gate were inspected and retained, leaving merging blocked until an explicit maintainer policy decision.

Baseline PR run 40347602696 and push run 40347602271 failed their aggregate gates after macOS jobs were abandoned. The macOS check annotations state that no hosted runner acquired the job after multiple attempts and report macOS arm64 capacity constraints. Ubuntu/Windows tests and the quality job passed. This is not a completed macOS verification or a product assertion failure.

Review found and fixed the sandbox plan's acceptance of non-array command JSON. New tests reject strings, objects, invalid scalars/elements, and ensure CLI errors do not echo the rejected command; the existing positive case now checks exact argv preservation. The helper remains inert.

Executed after the correction: 69 tests passed in 44.407 seconds; all twenty helpers ran across four host layouts (80 bundles). Ruff passed; MyPy passed for 12 modules; Black passed for 29 files; skill validation passed for 20 skills/10 profiles; bundle check passed for 350 files; spec validation passed for 23 requirements. Source/wheel build and offline installed-package smoke passed. The existing byte benchmark reproduced 98.38% on its synthetic fixture, with no tokenizer or checkpoint savings measurement.

AST inspection covered twelve runtime modules and found no direct network/process-client imports or eval/exec/dynamic-import calls. A selected-pattern text check found no matching machine-user paths, private-key headers, or selected token literals in the reviewed files. These checks supplement source review and tests, not a complete secret scan or runtime attestation. The release assessment records incomplete platform coverage, interactive host verification, filesystem races, distribution scope, and publication prerequisites. See docs/release-readiness.md.

Verdict: public preview candidate after the correction; stable release readiness is not established. The repository is already public, but the implementation remains on integ and main still needs the required review and required-check policy resolution. No release, tag, package publication, main merge, or branch-protection relaxation occurred.

Final documentation checks: all twenty skill-creator validators passed; the updated release/branch/contributor/README documents resolved 56 local links and seven README navigation anchors, with no em or en dashes. Parsed workflow trigger inventory is workflow_dispatch only. Network filesystem and hosted-assistant behavior remain outside the no-direct-client source check.

## T26 no-CI preview preparation

Date: October 27, 2026. Version: 0.1.0a1 in pyproject.toml, canonical runtime, and all twenty bundled runtimes. Administrative API changes removed main's required_status_checks and disabled repository Actions (enabled false). Main still requires one independent approval including latest-push review and administrator enforcement, with force pushes and deletion disabled. The retained workflow file was deleted. No CI, manual pipeline, new status check, or publishing automation was introduced.

Local verification on the alpha source: 69 tests passed; the installed-workflow test exercised twenty bundles across four layouts (80 installed bundles). Ruff, MyPy (12 modules), Black (29 files), skill validation (20 skills/10 profiles), deterministic bundles (350 files), and traceability (23 requirements) passed. Version inspection matched all 21 runtime/source copies and package metadata. Source/wheel build and offline installed-wheel smoke passed at 0.1.0a1. The previous wheel was preserved under the local Git metadata directory, not published or deleted.

In this Codex desktop session, the assistant read the Egress Audit, Task Planner, and Preflight skill instructions and workflow references, installed their alpha bundles into an isolated Codex-layout project, and invoked them on synthetic inputs. Results were PARTIAL with one outbound-client lead, bounded PASS, and matching PARTIAL with authorization_granted false. No target code, additional agent/model session, or network request was executed. docs/compatibility-evidence.json records the limited host scope. Native automatic discovery, other assistant sessions, and macOS were not verified or represented as passing.

Documentation/version checks passed: 65 relative links and seven README anchors resolved; changed Markdown has no em or en dashes; no YAML workflow remains. The preview notes name the capabilities, unsupported checks, distribution differences, and incomplete coverage. This is an alpha preview, not stable or universal platform support.

Source archive inventory, SHA256SUMS, and draft-release verification are performed against the committed head and recorded with the draft release artifacts. Public publication remains dependent on independent review. The active administrator is PR #1's author, so that account cannot provide the required independent approval; no review bypass or self-approval is used.

## T27 independent security decision preview

Date: October 31, 2026. Host: Windows x64, Python 3.14.6. Version: 0.1.0a2, unpublished development preview. Owner: primary implementation agent. References: SEC-024 through SEC-028. No CI, host settings, global installs, network listener, release publication, or protected-main review policy was added or changed. The earlier 0.1.0a1 draft assets remain pinned to their source revision.

The reference repository at 54a798831d2266a3ca61ce68a7acb80b81160d57 was downloaded for static review. All 4,532 tracked files were inventoried, 4,531 UTF-8 text files scanned, and 1,103 Python files parsed with no syntax errors. The single binary image was not semantically analyzed. Deeper selected source review and excluded checks are recorded in docs/research/reference-review.md and JSON; a SHA-256 inventory identifies all reviewed files. No third-party skill content was imported or executed. Network/process lexical indicators are review leads, not maliciousness or complete data-flow conclusions.

Implementation: assurance.py owns graph BFS and edge-removal counterfactuals, exact-match fixture replay, paired metrics with explicit exclusions, and capped closed-vocabulary routing. assurance_contracts.py exposes shape contracts. mcp_stdio.py exposes only the same four record functions via bounded newline-delimited JSON-RPC; CLI and MCP results are tested for equality. Examples, profiles, workflow references, source-to-bundle manifests, preview notes, README, and compatibility boundaries are updated.

| Command or check | Actual result |
|---|---|
| python -m unittest discover -s tests -t . -v | PASS, 97 tests in 26.065 seconds, including 96 installed bundles (24 skills across four layouts) |
| python -m ruff check src scripts tests | PASS |
| python -m mypy src | PASS, 15 source modules |
| python -m black --check --workers 1 src scripts tests | PASS |
| python scripts/build_skills.py --check | PASS, 494 generated files |
| python scripts/validate_skills.py | PASS, 24 skills and 14 profiles |
| python scripts/validate_specs.py | PASS, 28 requirements |
| python -m build | PASS, 0.1.0a2 source distribution and wheel |
| python scripts/package_smoke.py | PASS, offline wheel install, CLI help, egress, preflight, installed MCP executable initialization/list/four calls from outside the checkout |
| python scripts/benchmark_assurance.py | PASS, eight synthetic cases, toy baseline TP2/FP3/FN0, exact replay TP1/FP0/FN1; lower recall retained visibly |

Benchmark fixture SHA-256: c9faa3e648f12be9bd99dfbb1d220e1aa507b5a38d13a4e526129668adf0a653. No reference implementation, model, API, live target, or assistant benchmark was executed. Selected entrypoint bytes are measured separately from tokens and billing.

Verification limits: no native automatic discovery, Claude/Cursor/Copilot session, current macOS run, hosted MCP integration, live attack, external advisory match, complete semantic graph extraction, or operational detection coverage was established. All four valid record analyses remain PARTIAL. MCP reports are deliberately returned to the invoking host, whose provider data handling is outside this helper's boundary.

Additional T27 checks: 91 Markdown files and 146 relative links resolved; no em/en dash punctuation found in that documentation scope. The formal assurance JSON Schema and four examples validated with Draft202012Validator (authoring-time dependency only). AST import classification across 15 runtime modules found standard-library imports only and no direct network/process client imports. urllib.parse is present for URL parsing and is not a network client. This inspection is not complete semantic data-flow verification. Local benchmark JSON is recorded in docs/assurance-benchmark.json. Actions remained enabled=false and main required_status_checks=null; the independent review count remained one.

Final T27 protocol review added support for standard object-valued MCP request metadata, which is ignored for analysis and cannot grant authority. Malformed metadata is rejected. All 24 skills passed skill-creator quick_validate. Final format check covered 36 source/test/script files. The rebuilt 0.1.0a2 wheel passed offline installation and the installed MCP executable smoke after that correction.

## T28 attributed offline adaptations

Date: October 31, 2026. Host: Windows, Python 3.14.6. Version: 0.1.0a3 development preview. Owner: primary implementation agent. Scope: SEC-029 email-header-triage and SEC-030 http-header-snapshot-review. Imported selected reviewed pure helpers at pinned upstream revision 54a798831d2266a3ca61ce68a7acb80b81160d57, retaining Apache-2.0 license, copyright 2026 mukul975, upstream author metadata mahipal, source hashes, and modification notices. Original project files remain MIT. No license obligations were concealed through renaming.

Full upstream workflows were not imported. Excluded acquisition, DNS, subprocess, HTTP clients, attachments, writes, raw reports, grading, and CLI paths. Email output preserves contradictory supplied claims without validating sender identity. HTTP output checks only a narrow header subset and does not implement CSP or cookies. Both adapters suppress raw values and return PARTIAL. The four-tool MCP interface is unchanged. Bundles and wheel/source distributions include both licenses, the notice, and source provenance.

| Command/check | Actual outcome |
|---|---|
| python -m unittest discover -s tests -t . -v | PASS, 108 tests in 34.259 seconds, including 26 skills across four layouts, 104 installed bundles |
| python -m unittest tests.test_header_records -v | PASS, 11 focused tests after strengthening the file-access guard |
| python -m ruff check src scripts tests | PASS |
| python -m mypy src | PASS, 18 modules |
| python -m black --check --workers 1 src scripts tests | PASS, 40 files |
| python scripts/build_skills.py --check | PASS, 692 generated files, including license/notice/provenance in all bundles |
| python scripts/validate_skills.py | PASS, 26 skills, 16 profiles |
| python scripts/validate_specs.py | PASS, 30 requirements |
| python -m build | PASS, 0.1.0a3 wheel and source distribution |
| python scripts/package_smoke.py | PASS, offline installed CLI, both adapted commands, existing MCP roundtrip, and packaged license/notice/provenance assertions |
| skill-creator quick_validate | PASS, all 26 skills |
| Source/license hash comparison | PASS, both adapted source and license files match pinned provenance; no upstream NOTICE* file found |

Documentation check covered 101 Markdown files and 170 relative links with no broken targets or em/en dash punctuation. Source and per-bundle tests retain original attribution. README's prior wholly-original/MIT-only wording was corrected and historical research claims were labeled as T27 scope. docs/adapted-skills.md explains direct reuse, omissions, input contracts, and why other candidates were not imported.

Remaining: no new live endpoint, sender cryptography, native assistant recognition, hosted MCP integration, macOS execution, comprehensive header grammar, or competitor benchmark was verified. No global install or host config was changed. CI and publication remain disabled/unchanged under existing policy. The earlier draft release is untouched.

Build environment note: an optional `python -m build --no-isolation` attempt could not import setuptools.build_meta from the host interpreter. The required standard isolated `python -m build` succeeded without adding global build dependencies; its installed-wheel smoke passed. This was a build-environment limitation, not a passed no-isolation check.

## T29 compact header-review workflow

Date: October 31, 2026. Host: Windows Python 3.14.6. Version: 0.1.0a4 development preview. Owner: primary implementation agent. SEC-029 through SEC-031. Renamed email-header-triage to mail-auth-review and http-header-snapshot-review to web-header-review. Existing CLI command names and individual record schemas remain compatible. Routing goals map to the new names; installed copies are not automatically renamed or overwritten. Attribution and both licenses remain unchanged.

Added header-review to combine either or both strict records. Missing scope is explicit and both-null input is rejected. Both renamed standalone launchers support this command. Brief header presentation uses its own schema and defaults to three findings, retaining total/omitted counts, stable IDs, all observations, coverage, no-action flags, and unresolved source claims. --view full restores full console presentation; --output always saves unabridged report-v1 evidence to a new file. All other command defaults and the four-tool MCP surface remain unchanged.

| Executed check | Outcome |
|---|---|
| python -m unittest discover -s tests -t . -v | PASS, 117 tests in 34.522 seconds; 104 installed bundles plus eight combined-review calls through the two renamed bundles across four layouts |
| python -m ruff check src scripts tests | PASS |
| python -m mypy src | PASS, 18 runtime modules |
| python -m black --check --workers 1 src scripts tests | PASS, 42 files |
| python scripts/build_skills.py --check | PASS, 692 generated files |
| python scripts/validate_skills.py | PASS, 26 skills and 16 profiles |
| python scripts/validate_specs.py | PASS, 31 requirements |
| python -m build | PASS, 0.1.0a4 sdist and wheel |
| python scripts/package_smoke.py | PASS, offline installed individual/combined brief commands, existing MCP checks, and license inventory |
| python scripts/benchmark_header_output.py | PASS, standard-library byte benchmark on three fixed synthetic records |
| Isolated tokenizer run of benchmark_header_output.py --tokenizer cl100k_base | PASS, tiktoken 0.14.0, local token counts recorded in docs/header-output-benchmark.json |
| skill-creator quick_validate | PASS, all 26 skills |
| Draft202012Validator for header-brief-v1 | PASS, 12 case/cap combinations |
| Documentation links | PASS, 103 Markdown files and 179 relative links; no em/en dash punctuation in that scope |

Measured minified JSON, including terminating newline: mail full 356 tokens to brief 237 (33.43% reduction, zero omissions); web 383 to 264 (31.07%, zero omissions); combined 634 to all-findings brief 461 (27.29%, zero omissions), or default brief 355 (44.01%, three of six findings omitted explicitly). Full/brief observations and coverage are regression-tested for equality. This is serialization on synthetic inputs, not a real-project/model-quality, latency, provider-billing, or universal tokenizer claim. The tokenizer is installed only in an ignored authoring virtual environment; shipped runtime dependencies remain empty. No project records were sent to a model.

Remaining: no new native assistant discovery/session, hosted MCP integration, macOS execution, complete security coverage, or billing measurement. No global skills, host permissions, CI settings, release/tag/package publication, or main review policy were changed.

## T30 fresh-archive E2E and reproducibility correction

Date: October 31, 2026. Owner: primary implementation agent. Package version remains 0.1.0a4; runtime semantics are unchanged. Base commit: 6905ba5b2156ae4fab6dc88c030b18886a85a3e5. Tested candidate source tree: 78064d38a5b41ec0a97455a99aaa8a0033c38a59. Candidate archive SHA-256: 7c131bc33cf386d0e1dd8b8b9ebf3a0a82732565911ffc85bc22ee324337ad10. This snapshot includes the fix and regression below; subsequent verification-record updates change documentation only.

E2E-001 found that saved benchmark fixture hashes changed under LF/CRLF conversion in a clean Git archive, although token counts and savings matched. Fixed hashing to use canonical parsed JSON (sorted keys, compact separators, ASCII escapes, UTF-8), documented the basis, regenerated recorded hashes, and added a regression that tolerates newline/key-order changes but detects changed input values. E2E-002 corrected a stale fixed helper count in CONTRIBUTING.md.

| Final fresh-source suite | Result |
|---|---|
| Python 3.11.15, python -m unittest discover -s tests -t . -v | PASS, 118 tests in 31.633 seconds |
| Python 3.12.13, same suite | PASS, 118 tests in 32.523 seconds |
| Python 3.13.14, same suite | PASS, 118 tests in 32.092 seconds |
| Python 3.14.6, same suite | PASS, 118 tests in 34.176 seconds |

Total: 472 final test executions. Each runtime exercised all 26 catalog skills in four temporary host layouts (104 catalog bundles per runtime), plus eight combined-header calls. Pinned requirements-dev.txt installed in a fresh authoring environment. Python downloads were isolated to the temporary test directory without PATH or Windows registry registration.

Fresh Ruff, MyPy (18 modules), Black (43 files), deterministic bundle check (692 files), 26-skill/16-profile validation, 31-requirement validation, wheel/sdist build, and offline installed CLI/MCP/license smoke all passed. Both saved benchmarks reproduced exactly from the fixed candidate archive, including canonical fixture identities; token counts and reduction percentages did not change.

An independent MCP SDK 2.3.0 client tested the offline-installed wheel outside the source tree. Initialization negotiated protocol 2025-11-25. Ping, discovery of four tools, input-schema validation, all four tool calls with CLI-equivalent reports, progress metadata, invalid records, and unknown-tool rejection passed. Temporary harness imports and field accesses were adapted to the installed SDK's Python API before the successful run. This was a protocol client test, not a real assistant session.

A separate installed user journey passed for both renamed header bundles across four host layouts: preview made no writes, repeat install was refused, full export retained all six leads while brief output showed two and declared four omissions, report schemas validated, raw synthetic header values stayed absent, existing outputs were preserved, evidence ZIPs were byte-reproducible, brief JSON was rejected as a full report, and an unexpected ZIP member was rejected.

Documentation/contract checks passed for all 140 committed Markdown files, 187 relative links, four schema definitions, 33 schema/example cases, 26 bundle inventories/hashes, 18 standard-library-only runtime modules, no eval/exec/dynamic-import calls in that AST scope, and zero wheel runtime dependencies. All three README media files decoded, including five GIF frames; the synthetic demo reproduced its committed finding IDs/messages and omission counts. These are bounded checks, not complete source-to-sink analysis or a security certification.

Remaining: Linux and macOS execution, native automatic discovery, real Claude/Cursor/Copilot sessions, hosted-client integration, model quality, and complete security coverage remain unverified. Copilot's detected executable is only an uninstalled-CLI shim. WSL is not installed and Docker is unavailable. GitHub Actions remained disabled, required status checks remained absent, and one independent PR approval remained required. No CI, release/tag/package publication, global skills, or host permissions were changed. The existing local header-evidence.json was preserved. Detailed logs, the tested archive, harnesses, and machine-readable results were saved under the original checkout's ignored security-reports folder.

## T31: Fifteen security domain workflows, November 5, 2026

Result: PASS for local implementation and verification. Added fifteen original evidence-guided skills and portable profiles, strict domain-review input schema and helper, examples, closed-goal routing, standalone domain binding, and compact-output guidance. Catalog: 41 skills, 31 profiles, four MCP tools. New helpers do not scan projects, open evidence references, execute attacks, or verify supplied claims. Missing controls remain unknown; valid analyses remain PARTIAL.

Verification:

- `python -m unittest discover -s tests -t . -v`: 124 tests on Python 3.14.6 (65.828 seconds), and the same command using the explicit managed Python 3.11.15 interpreter (53.022 seconds). Both PASS, 248 executions total. Each suite installs and runs all 41 bundles across four layouts (164 installs), plus all 60 new domain-mismatch rejection cases.
- `python scripts/validate_skills.py`: 41 skills, 31 profiles. `python scripts/validate_specs.py`: 32 requirements. `python scripts/build_skills.py --check`: 1138 generated files. All PASS.
- Authoring environment: Ruff check PASS, MyPy 19 modules PASS, Black check 45 files PASS. Runtime dependencies remain empty.
- `python -m build --outdir <temporary-build-root>/dist`: sdist and wheel PASS with isolated build dependencies. An initial --no-isolation attempt could not import setuptools in the authoring environment; no product failure was concealed. Retried with normal isolated build successfully.
- Copied the current package_smoke.py and examples into the isolated build root containing exactly one wheel, preserving historical dist artifacts. `python <temporary-build-root>/scripts/package_smoke.py`: offline install and CLI, all fifteen new domain examples, headers, and four MCP tools PASS outside the checkout.
- Draft202012Validator: new schema plus 105 positive/negative record cases PASS. Relative Markdown check: 237 links PASS before these evidence additions. Assurance and cl100k_base header benchmark dictionaries match recorded JSON exactly. The assurance document-selection denominator now uses 41 entrypoints; no new token savings claim.
- GitHub settings read: Actions disabled; required status checks null; one approving main review remains required. No pipeline or protection changes.

Historical T30 verification is retained in validation-t30.json. These additions were not rerun on Python 3.12/3.13, Linux, macOS, or native interactive assistant sessions. Directory layouts and offline helper execution do not establish universal host behavior. No public release, tag, package publication, or protected-main merge was performed.
