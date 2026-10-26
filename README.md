# Security Agent Skills

**Know what an AI agent can read, run, and send.**

[![Quality](https://github.com/FliorcieLabs/security-agent-skills/actions/workflows/quality.yml/badge.svg?branch=integ)](https://github.com/FliorcieLabs/security-agent-skills/actions/workflows/quality.yml?query=branch%3Ainteg)
[![MIT license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](pyproject.toml)

Fifteen local security skills and five portable agent profiles for reviewing AI tooling and the projects it touches. Inspect unfamiliar skills, review MCP authority, compare upgrades, or check CI, containers, infrastructure, and LLM data settings before granting access.

**No API key. No runtime Python dependencies. No telemetry. No source upload.** Analysis helpers read bounded local inputs without importing or executing reviewed code.

## Start with one folder

The implementation is on `integ` while its protected-main pull request is under review:

```sh
git clone --branch integ https://github.com/FliorcieLabs/security-agent-skills.git
cd security-agent-skills
python scripts/security_check.py egress ../my-project --format markdown --max-findings 5
```

Replace `../my-project` with an existing project folder. Python 3.11+ is required; use `python3` or `py -3` if that is your interpreter command. Static scans return **exit 3, PARTIAL**, including when they find no indicators. This is an intentional evidence status, not a crashed command.

```text
Local project or agent package
             |
     Bounded static helper
             |
 Fixed review leads + visible coverage
             |
 Human or AI reviews relevant source lines
```

## Choose the security question

| Skill | What it reviews or produces | CLI command |
|---|---|---|
| [Agent Egress Audit](skills/agent-egress-audit) | Outbound clients, tracking indicators, sensitive input access, and execution boundaries. | `egress` |
| [Dependency Provenance Audit](skills/dependency-provenance-audit) | Local manifests, lockfiles, lifecycle hooks, mutable sources, and integrity records. | `dependencies` |
| [MCP Authority Review](skills/mcp-authority-review) | Endpoints, shell launch authority, credential configuration, and tool restrictions. | `mcp` |
| [Security Exposure Review](skills/security-exposure-review) | Evaluation, deserialization, debug, listener, and shell review leads. | `exposure` |
| [Authorized AppSec Validation](skills/authorized-appsec-validation) | A declared authorization document, exact targets, time window, budgets, and stop conditions. | `appsec-plan` |
| [Agent Package Change Sentinel](skills/agent-package-change-sentinel) | Local content snapshots and diffs for changed files and new capability indicators. | `snapshot`, `compare` |
| [Prompt Injection Boundary Lab](skills/prompt-injection-boundary-lab) | Five synthetic boundary cases and grading of supplied response records. | `injection-lab` |
| [Secret Route Mapper](skills/secret-route-mapper) | Supplied synthetic canary route events. No credential collection or packet capture. | `routes` |
| [Safe Install Sandbox](skills/safe-install-sandbox) | An inert, digest-pinned Docker execution plan with restricted authority. | `sandbox-plan` |
| [Security Evidence Pack](skills/security-evidence-pack) | Reproducible report ZIPs and exact-member/hash verification. | `pack`, `verify` |
| [Instruction Boundary Audit](skills/instruction-boundary-audit) | Agent instruction overrides, approval bypass language, concealed transfers, and invisible text. | `instructions` |
| [CI Workflow Security Audit](skills/ci-workflow-security-audit) | GitHub Actions references, triggers, permissions, inherited secrets, runner selection, and event expressions. | `ci` |
| [Container Boundary Audit](skills/container-boundary-audit) | Explicit root users, privileged containers, host namespaces, daemon sockets, escalation settings, and remote ADD sources. | `containers` |
| [Infrastructure Exposure Audit](skills/infrastructure-exposure-audit) | Literal Terraform HCL world ranges, wildcard policy scope, public storage, encryption, and validation settings. | `iac` |
| [LLM Data Boundary Audit](skills/llm-data-boundary-audit) | Explicit content capture, disabled scrubbing, remote code trust, configured endpoints, and TLS bypasses. | `llm-data` |

Use a directory as the target for each static command. Read the skill's workflow reference for structured inputs to the other commands. [Capabilities and limits](docs/capabilities.md) describe what each helper can establish.

## Install for your assistant

Preview one skill for an existing project, then apply the plan:

```sh
python scripts/install_skills.py --agent codex --project ../my-project --skill instruction-boundary-audit
python scripts/install_skills.py --agent codex --project ../my-project --skill instruction-boundary-audit --apply
```

Choose `claude`, `codex`, `cursor`, `copilot`, or `all`. Omit `--skill` to select all fifteen. Replace `--project ../my-project` with `--global` for personal discovery across projects. Existing destinations are refused, never silently upgraded or overwritten.

| Assistant | Project skills | Personal skills |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| GitHub Copilot on supported surfaces | `.github/skills/` | `~/.copilot/skills/` |

Each bundle includes its own helper and can run from another folder without this checkout. The installer does not enable hooks, grant permissions, install dependencies, edit project instructions, or force a reload. A failed copy may leave its new folder for inspection. Older clients and cloud sessions can have different discovery rules. [Compatibility details](docs/compatibility.md).

## Five portable security agents

- [Instruction Boundary Auditor](agents/instruction-boundary-audit.md)
- [CI Workflow Security Reviewer](agents/ci-workflow-security-audit.md)
- [Container Boundary Reviewer](agents/container-boundary-audit.md)
- [Infrastructure Exposure Reviewer](agents/infrastructure-exposure-audit.md)
- [LLM Data Boundary Reviewer](agents/llm-data-boundary-audit.md)

Attach a profile or load its text into an assistant that accepts Markdown instructions. Each new installed skill also carries its profile in `references/agent.md`. These are portable instructions, not universal native agent registrations. Without filesystem access, an assistant can review supplied excerpts and report partial coverage. Running helpers requires terminal access and Python. [Agent usage](docs/agents.md).

Example request:

> Use the CI Workflow Security Reviewer on this project's GitHub Actions workflows. Keep analysis local. Report file and line evidence, effective-authority questions, and the smallest fixes. Preserve unknowns and list the commands actually run.

Pass the project root to the `ci` helper so `.github/workflows` retains its expected relative path. In Codex, explicitly invoke `$ci-workflow-security-audit`; in Claude Code, use `/ci-workflow-security-audit`. Other hosts can use their skill picker or a natural-language request.

## Spend context on decisions

```sh
python scripts/security_check.py llm-data ../my-project --max-findings 5 --output llm-review.json
```

The console shows five findings plus the total count, omitted count, coverage, and limitations. The new `llm-review.json` file keeps the complete report. Keep output outside the target when comparing snapshots.

Deterministic local work, one relevant skill, references opened on demand, and focused source review reduce repeated context. Stable finding IDs let follow-ups refer to saved evidence instead of replaying the whole report.

The [synthetic benchmark](docs/report-benchmark.md) measured **78,487 to 1,157 `cl100k_base` tokens**, a **98.53% reduction** when compacting a 1,000-finding fixture to twenty visible findings. This measures serialization, not real-project savings, model quality, or billing. Full evidence remains available separately.

## One result contract

Every report uses [`security-agent-skills/report-v1`](schemas/report-v1.schema.json), retaining workflow, scope, findings, coverage, limitations, and details. Findings have stable IDs, rule names, source locations, and confidence. Lexical matches are review leads, not confirmed vulnerabilities.

| Exit | Result | Meaning |
|---|---|---|
| `0` | PASS or generated data | The named bounded check passed, or inert fixture/snapshot data was generated. |
| `1` | FIX | Supplied evidence fails a bounded check. |
| `2` | BLOCKED | Required input, access, schema, or a new output path is missing. |
| `3` | PARTIAL | Evidence is incomplete or the operation is static. |

Agent profiles use Result, Findings, Coverage, Validation, and Remaining. Passing package tests does not turn a partially inspected target into a safe target.

## Privacy and limits

- Analysis helpers make no network requests and execute no reviewed code. Explicit development commands can download public build or test dependencies.
- Inventory excludes links, reparse points, hardlinks, credential filenames, binaries, dependency folders, unreadable files, and over-budget inputs. Coverage records skips.
- Static findings omit source excerpts and configuration values. Reports still include scope paths and filenames. Evidence export omits scope paths and freeform details and applies best-effort pattern scrubbing. Inspect artifacts before sharing.
- New audits are lexical, line-based checks. They do not evaluate complete YAML/HCL semantics, templates, inherited permissions, provider defaults, or runtime data flows. Quoted examples and negations can produce leads.
- AppSec validation checks declared scope without making requests. Injection grading consumes supplied records. Route mapping consumes synthetic events. Sandbox generation does not launch Docker. Evidence hashes establish local consistency, not authenticity or external truth.
- No helper proves absence of malware, certifies compliance, or grants permission for active tests. No DDoS executor, hidden telemetry, or automatic package publishing is included.

## Develop and verify

Runtime helpers use Python 3.11+ standard library only. Optional development tools are pinned in `requirements-dev.txt`.

```sh
python -m unittest discover -s tests -t . -v
python scripts/build_skills.py --check
python scripts/validate_skills.py
python scripts/validate_specs.py
python scripts/benchmark_reports.py
```

Tests cover scanner boundaries, source non-execution, output privacy, incomplete coverage, no-overwrite installation, archive integrity, and installed-helper subprocesses across all four directory layouts. CI runs Python 3.11 and 3.14 on Linux, Windows, and macOS. These tests do not establish interactive recognition or decision quality inside every AI product.

See [CONTRIBUTING.md](CONTRIBUTING.md) for lint, types, formatting, build, and installed-wheel checks, [SECURITY.md](SECURITY.md) for vulnerability reporting, and [.specs](.specs/README.md) for requirements and evidence.

`integ` is the development branch. `main` requires review and passing CI, including for administrators. No release or merge is automatic.

MIT licensed by Fliorcie Labs. This project ships original workflows and helpers, not copies of third-party agent projects. [Portfolio estimates](docs/portfolio.md) are hypotheses, not promises of adoption.
