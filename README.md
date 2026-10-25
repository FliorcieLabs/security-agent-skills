# Security Agent Skills

**Review what your agent can read, run, and send before you trust it.**

[![Quality](https://github.com/FliorcieLabs/security-agent-skills/actions/workflows/quality.yml/badge.svg)](https://github.com/FliorcieLabs/security-agent-skills/actions/workflows/quality.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](pyproject.toml)

Ten local security workflows for **Claude Code, Codex, Cursor, and GitHub Copilot**. Inspect agent packages, review MCP authority, compare upgrades, and export compact evidence. Use any project folder as input. No API key, hosted backend, telemetry, or runtime Python dependencies.

```text
Agent package or project folder
            |
      Local bounded helper
            |
   Compact report + full local evidence
```

## Try a local review

```sh
git clone https://github.com/FliorcieLabs/security-agent-skills.git
cd security-agent-skills
python scripts/security_check.py egress . --format markdown
```

Python 3.11+ is required. Use `python3` or `py -3` if that is your interpreter command. The helper never imports or executes target code. Static audits return exit code **3, PARTIAL**, including when no indicators are found. This preserves the difference between an inspected source pattern and a verified runtime fact.

## The ten skills

| Skill | What you get today |
|---|---|
| [Agent Egress Audit](skills/agent-egress-audit) | File and line references for outbound clients, sensitive sources, tracking indicators, and process boundaries. |
| [Dependency Provenance Audit](skills/dependency-provenance-audit) | Local manifest, lockfile, lifecycle-hook, mutable-source, and integrity review leads. No online CVE lookup. |
| [MCP Authority Review](skills/mcp-authority-review) | Remote endpoint, shell launch, credential configuration, and tool-allowlist review leads. |
| [Security Exposure Review](skills/security-exposure-review) | Potential evaluation, deserialization, broad-listener, debug, and shell boundaries to investigate. |
| [Authorized AppSec Validation](skills/authorized-appsec-validation) | Validation of declared authorization, exact targets, time window, budgets, and stop thresholds. No active attacks. |
| [Agent Package Change Sentinel](skills/agent-package-change-sentinel) | Local content snapshots and diffs for new files, changed hashes, and new capability indicators. |
| [Prompt Injection Boundary Lab](skills/prompt-injection-boundary-lab) | Five offline synthetic cases and grading of supplied structured response records. No model calls. |
| [Secret Route Mapper](skills/secret-route-mapper) | Classification of supplied synthetic canary route events. No real credentials or packet capture. |
| [Safe Install Sandbox](skills/safe-install-sandbox) | A digest-pinned, network-disabled Docker execution plan. It does not launch Docker or attest isolation. |
| [Security Evidence Pack](skills/security-evidence-pack) | Reproducible ZIPs of suite reports and exact-member/hash verification. No arbitrary project archive. |

Read [capabilities and limits](docs/capabilities.md) before treating a result as a security decision. These workflows provide review leads and scoped checks, not a universal malware detector or a safety certification.

## Install for your assistant

The same `SKILL.md` format and bundled helper work in each supported host. Each bundle is self-contained. No reference back to this checkout or developer machine is needed.

Preview installation into a project, then apply the reviewed plan:

```sh
python scripts/install_skills.py --agent codex --project .
python scripts/install_skills.py --agent codex --project . --apply
```

Choose `claude`, `codex`, `cursor`, `copilot`, or `all`. Choose a different existing folder with `--project`. Install just one skill with `--skill agent-egress-audit`. For personal skills across projects, replace `--project .` with `--global`.

| Host | Project destination | Personal destination |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| GitHub Copilot CLI / supported IDE skill discovery | `.github/skills/` | `~/.copilot/skills/` |

The installer previews by default, refuses links in destination paths, and never overwrites an existing skill. It does not enable hooks, change tool permissions, edit agent instructions, install dependencies, or restart a host. A failed copy may leave its new folder for inspection. Older assistant versions and cloud sessions may have different discovery rules. See [host compatibility](docs/compatibility.md).

Then ask your assistant:

> Use agent-egress-audit to review this package. Keep it local, show coverage, and preserve unknowns.

For Codex you can explicitly invoke `$agent-egress-audit`; Claude Code supports `/agent-egress-audit`. Other hosts can discover skills through their skill selector or a natural-language request. No skill bypasses the host's permission model.

## Compact by default, complete when needed

```sh
python scripts/security_check.py egress . --max-findings 5 --output review.json
```

The console keeps five findings and reports the full count, omitted count, coverage, and limitations. `review.json` contains the full report and must be a new file. Source excerpts, command bodies, header values, and URL queries are not copied into static review findings. Keep output outside the inspected folder when you need stable snapshots.

Token-conscious operation comes from doing deterministic work locally, loading only one relevant skill, following references on demand, and reading only the source lines needed to resolve a lead. See the [reproducible benchmark](docs/report-benchmark.md) for measured serialization and optional tokenizer counts. Synthetic savings are not promises about model billing or every project.

## One output contract

Every review report uses `security-agent-skills/report-v1`:

```json
{"result":"PARTIAL","finding_count":0,"findings":[],"coverage":{"runtime_observed":false},"limitations":["Static inspection does not establish safety."]}
```

This is an abbreviated example; [the schema](schemas/report-v1.schema.json) defines the complete document. Stable finding IDs support follow-up work without replaying the whole report. Repeated leads at one source location carry an occurrence count.

| Exit | Meaning |
|---|---|
| `0` | The named check passed, or inert fixture/snapshot data was generated. |
| `1` | Supplied evidence contains a bounded check failure (`FIX`). |
| `2` | Missing prerequisites, invalid input, denied access, or an output collision (`BLOCKED`). |
| `3` | Evidence is partial or the operation is static (`PARTIAL`). |

## Safety and privacy

- Analysis helpers make no network calls and execute no reviewed code. Sandbox generation emits an inert command array only.
- Links, reparse points, hardlinks, credential filenames, binary files, excluded dependency folders, unreadable inputs, and byte/entry limits appear in coverage. They are not silently treated as clean.
- Credential filenames are excluded by default. Evidence export also omits scope paths and freeform details and applies best-effort pattern scrubbing. Inspect any artifact before sharing it.
- Prompt injection cases use synthetic canaries. Route records are supplied observations, not independently captured events.
- Container plans require a reviewed image, a disposable environment, synthetic inputs, an isolated Docker daemon, and an external watchdog before an operator executes them.
- No DDoS, amplification, credential attack, automatic publishing, or hidden external upload behavior is included.

## Develop and verify

```sh
python -m unittest discover -s tests -t . -v
python scripts/build_skills.py --check
python scripts/validate_skills.py
python scripts/validate_specs.py
python scripts/benchmark_reports.py
```

Install `requirements-dev.txt` only when you need Ruff, MyPy, Black, or package builds. Runtime helpers need none of them. See [CONTRIBUTING.md](CONTRIBUTING.md) for build and review commands, [SECURITY.md](SECURITY.md) for reporting vulnerabilities, and [the delivery specification](.specs/README.md) for traceability.

`integ` is the development branch. `main` is protected and changes arrive through reviewed pull requests and required CI. Packages are not automatically published.

MIT licensed by Fliorcie Labs. Inspired by the problem of deciding what to trust in third-party agent packages; this repository does not bundle those third-party projects. Adoption estimates in [the portfolio](docs/portfolio.md) are subjective hypotheses, not evidence of popularity or guarantees of virality.
