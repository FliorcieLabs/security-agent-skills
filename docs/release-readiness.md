# Release readiness assessment

Date: October 27, 2026. Scope: twenty skills, ten Markdown agent profiles, shared local helpers, CLI, standalone bundles, copy installer, schemas, documentation, and package build. Baseline: 3b22cc0, followed by no-CI preview preparation at version 0.1.0a1. Earlier verification counts below retain their recorded source scope; current checks are recorded under T26 in .specs/evidence.md.

## Decision

The implementation is a public preview candidate after the correction below. The bounded helpers pass the executed local checks. A stable release or a claim of universal interactive compatibility is not supported by the current evidence.

The repository is already public. The implementation remains on integ; main still contains the initial repository contents. A preview is prepared for independent review. Required CI checks have been removed, repository Actions is disabled, and no workflow remains. Publishing from main is blocked only by the independent review, not by a pipeline requirement. No approval is fabricated or bypassed.

## What is ready for preview use

| Component | Executed evidence | Public description |
|---|---|---|
| Nine static security audits | Source review, scanner boundary regressions, output privacy, bounded reads, and installed subprocess checks | Local review leads with explicit PARTIAL coverage, not a safety verdict |
| Five internal-operation skills | Task graph, handoff authority, checkpoint retention, preflight boundaries, retry-state and invalid-input regressions | Validators for declared records, not agent execution or permission enforcement |
| Snapshot comparison and evidence archive helpers | Content-change, path, archive inventory, hash, no-overwrite, and reproducibility regressions | Local content consistency, not authenticity or external truth |
| AppSec and sandbox plan helpers | Scope checks, digest-pinned inert argv, strict argument-array validation, and non-execution regressions | Plan validation and generation, not active testing or sandbox execution |
| Injection lab and synthetic route helper | Supplied response grading, missing evidence, synthetic canary, and output privacy regressions | Synthetic evidence interpretation, not a live model evaluation or network capture |
| Twenty standalone bundles | 350 generated files match canonical sources; twenty helpers exercised across four temporary host layouts, 80 installed bundles | Portable helper execution with Python 3.11+, independent of checkout location |
| Ten agent profiles | Catalog, frontmatter, references, and bundled profile parity validation | Markdown role instructions, not universal native agent registration |

The groups above account for all twenty skills. Tests of directory layouts do not establish interactive skill discovery or decision quality inside Claude Code, Codex, Cursor, Copilot, or another assistant.

## Correction made during this review

The sandbox plan generator accepted a string or object instead of the required command argument array. Python iteration could turn a string into individual command arguments or an object into its keys. The helper never executed that plan, so this was an input-contract defect in inert output, not evidence of command execution.

The generator now requires a nonempty list of nonempty strings without NUL characters. Regressions cover scalar/object/invalid-element rejection, preserved valid argv, CLI BLOCKED status, and omission of the rejected command value from error output. All bundles were regenerated from the corrected source.

## Verification after the correction

Local host: Windows, Python 3.14.6.

| Check | Outcome |
|---|---|
| python -m unittest discover -s tests -t . -v | PASS, 69 tests in 44.407 seconds, including all twenty installed workflows |
| python -m ruff check src scripts tests | PASS |
| python -m mypy src | PASS, 12 source modules |
| python -m black --check --workers 1 src scripts tests | PASS, 29 files |
| python scripts/validate_skills.py | PASS, 20 skills and 10 profiles |
| python scripts/build_skills.py --check | PASS, 350 generated files |
| python scripts/validate_specs.py | PASS, 23 mapped requirements |
| python -m build | PASS, source distribution and wheel built locally |
| python scripts/package_smoke.py | PASS, offline wheel installation, CLI, egress scan, and preflight |
| python scripts/benchmark_reports.py | Existing byte fixture reproduced 98.38% serialization reduction; no new token measurement |

AST inspection of the twelve runtime modules found standard-library imports only, no direct network/process client imports, and no eval, exec, or dynamic import calls. The runtime code was also reviewed for reads, writes, declared authority, unknown outcomes, and report handling. A selected-pattern text check found no matching machine-user paths, private-key headers, or selected token literals in the reviewed source/docs/examples. These bounded checks are not a complete secret or data-flow audit. The existing CLI end-to-end test makes attempted network/process calls fail and exercises the operation helpers.

All twenty skills also passed the skill-creator frontmatter/scaffold validator. The updated README, contributor guide, branch policy, and this report resolved 56 local links and seven README navigation anchors. The retained workflow parsed with workflow_dispatch as its only trigger.

On the pre-correction baseline fc23339, remote Ubuntu and Windows jobs for Python 3.11 and 3.14 and the quality job passed. The two macOS jobs never acquired hosted runners. GitHub reported runner capacity constraints and abandoned the matrix; the aggregate quality gate correctly failed. This was not a passing macOS run and is not a failed product test assertion. The latest correction has fresh Windows-local verification, not a completed new multi-OS matrix.

## CI state

GitHub Actions is disabled at the repository level, the retained workflow file has been deleted, and main's required_status_checks is absent. There is no automatic or manual pipeline prerequisite. The earlier disabled workflow may remain in GitHub's historical workflow list; historical failed runs are not rewritten as passing.

The [branch policy](branch-policy.md) retains independent review and administrator enforcement. The active administrator is also the PR author and cannot provide independent approval. The [contributor guide](../CONTRIBUTING.md) retains the local verification commands. With no CI, each release needs recorded verification for its actual source revision; this report does not cover later changes.

## Preview host check

Three representative skills were explicitly loaded and invoked in the current Codex desktop session on Windows using synthetic inputs. The recorded egress result was PARTIAL, Task Planner was bounded PASS, and matching Preflight was PARTIAL without granting authority. This validates that explicit workflow for these examples, not native automatic discovery or all client surfaces. See [compatibility evidence](compatibility.md). Other assistant CLIs and macOS execution were unavailable; their limits are disclosed in the [preview notes](releases/0.1.0a1.md).

## Distribution scope

The full skill kit is the repository checkout or a complete GitHub source archive: it contains catalog.json, skills/, agents/, schemas/, and scripts/install_skills.py. The installer previews changes and refuses existing destinations. It does not grant permissions, start services, register native agents, or reload a host.

The Python wheel installs the analysis CLI and its runtime modules. It does not install all twenty skill folders or the repository copy installer. The Python source distribution is also a CLI distribution, not a substitute for the full repository kit. Do not advertise pip installation as installing the entire skill catalog.

The repository and each standalone bundle include the MIT license. No third-party project ZIPs or unrelated demo GIFs are shipped by this kit. The banner's generation prompt and the original synthetic demo source are documented in [media provenance](assets/security/README.md). No legal certification or independent license audit is implied.

## Remaining before release

1. Obtain the required independent review before merging the implementation into main. No CI check is required. Do not remove review controls or fabricate approval.
2. Publish the prepared 0.1.0a1 only as a preview/prerelease after review. Package and bundled runtime versions are aligned; draft preparation is not public release publication.
3. State the actual verification scope in release notes. For a stable cross-platform claim, complete the missing macOS checks on the release revision and verify representative interactive sessions in the supported assistants.
4. Retain the known capability boundaries: incomplete static coverage, best-effort export scrubbing, unverified evidence references, no runtime egress capture, no executed sandbox, and no permission enforcement. Work from a trusted, stable checkout; installer planning and filesystem reads do not provide atomic protection against every concurrent filesystem replacement.

Using a hosted assistant can send the prompts or excerpts a user supplies to that provider under the host's own data handling. The toolkit's local helpers make no such provider requests; this review does not verify the host's behavior. Select local input and output paths: the operating system can perform network filesystem access for UNC paths or mapped shares even without a Python network client. No public release, package upload, tag, protected-main merge, or independent external security assessment was performed.
