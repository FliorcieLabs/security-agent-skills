# Security Agent Skills

![Security Agent Skills: a circuit-node shield on a dark navy background](docs/assets/security/security-banner.png)

**Review the risk. Rehearse the boundary. Check whether the fix holds.**

[![MIT and Apache-2.0](https://img.shields.io/badge/license-MIT%20%2B%20Apache--2.0-blue.svg)](THIRD_PARTY_NOTICES.md)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](pyproject.toml)

Forty-one local skills and thirty-one portable agent profiles for security review and internal agent operations. Inspect unfamiliar AI tooling, review project boundaries, plan bounded tasks, prepare handoffs, checkpoint context, and review tool or retry proposals before execution.

**No API key. No runtime Python dependencies. No telemetry. No source upload.** Analysis helpers read bounded local inputs without importing or executing reviewed code.

**Release status: 0.1.0a4 development preview.** The earlier 0.1.0a1 draft remains pinned to its earlier source revision; these additions are not a published release. GitHub Actions is disabled, workflow files are removed, and no CI check is required to merge. Verification is local; independent review remains required. See the [development preview notes](docs/releases/0.1.0a4.md) and [release assessment](docs/release-readiness.md) for tested scope and limits.

[Quick start](#start-with-one-folder) | [Demo](#see-a-local-review) | [Security skills](#choose-the-security-question) | [Additional domains](#additional-security-domains) | [Agent operations](#internal-agent-operations) | [Install](#install-for-your-assistant) | [31 agents](#portable-agent-profiles) | [Limits](#privacy-and-limits) | [Contribute](CONTRIBUTING.md)

Use it before installing an unfamiliar agent package, granting an MCP server access, accepting a dependency change, or sharing a security finding. Start with one question and one skill. Review the referenced source before deciding what to allow or fix.

## Start with one folder

The implementation is on `integ` while its protected-main pull request is under review:

```sh
git clone --branch integ https://github.com/FliorcieLabs/security-agent-skills.git
cd security-agent-skills
python scripts/security_check.py egress ../my-project --format markdown --max-findings 5
```

Replace `../my-project` with an existing project folder. Python 3.11+ is required; use `python3` or `py -3` if that is your interpreter command. Static scans return **exit 3, PARTIAL**, including when they find no indicators. This is an intentional evidence status, not a crashed command.

## See a local review

![Animated synthetic egress review: inspect inert text, find three review leads, show two with one omitted, report one skipped file, and retain PARTIAL coverage](docs/assets/security/security-demo.gif)

**Synthetic inputs, actual CLI results.** This rendered summary shows the egress helper inspecting inert source-like text. It finds sensitive input access, a network client call, and a process execution boundary. The console is limited to two findings; the full report retains all three. A synthetic `.env` file is skipped. No fixture code runs and no outbound request is made.

Prefer a still image? [Open the PNG sample](docs/assets/security/security-demo.png). Read the [text walkthrough](docs/assets/security/README.md), [compact JSON](docs/assets/security/demo-compact.json), or [full JSON](docs/assets/security/demo-report.json). The demo is a presentation of one local scan, not a recording of an AI assistant or a confirmed attack.

### Pick a review path

| Your task | Start here | Follow with |
|---|---|---|
| Adopt a new skill or agent | Agent Egress Audit | Instruction Boundary Audit and Dependency Provenance Audit |
| Grant an MCP server access | MCP Authority Review | Agent Egress Audit for the server package |
| Review a deployment change | CI Workflow Security Audit | Container Boundary Audit or Infrastructure Exposure Audit |
| Check AI data settings | LLM Data Boundary Audit | Trace the flagged endpoint or capture setting in the source |
| Review a package upgrade | Agent Package Change Sentinel | A focused audit of the changed files |

Each path narrows the next decision. It does not combine the results into a safety score.

## Additional security domains

Fifteen evidence-guided workflows add the following domains. Each includes a portable Markdown agent profile and an optional declared-evidence consistency helper. These are review workflows, not automatic vulnerability scanners. No new MCP tools or CI pipelines are installed.

| Skill | Review boundary |
|---|---|
| [Agent Memory Integrity Review](skills/agent-memory-integrity-review/SKILL.md) | Review persistent agent memory for poisoning and cross-scope reuse. |
| [MCP Tool Drift Sentinel](skills/mcp-tool-drift-sentinel/SKILL.md) | Compare MCP versions for changes to tool authority and contracts. |
| [Agent Approval Binding Review](skills/agent-approval-binding-review/SKILL.md) | Review approval binding to exact actions, arguments, targets, and validity windows. |
| [Tenant Isolation Review](skills/tenant-isolation-review/SKILL.md) | Review tenant boundaries in queries, storage, caches, and workers. |
| [Webhook Trust Review](skills/webhook-trust-review/SKILL.md) | Review webhook signatures, replay controls, and duplicate processing. |
| [Archive and Path Boundary Review](skills/archive-path-boundary-review/SKILL.md) | Review archive extraction for traversal, links, collisions, and resource exhaustion. |
| [CI Identity and OIDC Review](skills/ci-identity-oidc-review/SKILL.md) | Review supplied CI cloud trust and token permissions without enabling a pipeline. |
| [Sensitive Logging Review](skills/sensitive-logging-review/SKILL.md) | Review logs, traces, exceptions, and transcripts for sensitive data capture. |
| [Race and Replay Review](skills/race-replay-review/SKILL.md) | Review concurrent state changes, duplicate actions, and ambiguous effects. |
| [OAuth Integration Review](skills/oauth-integration-review/SKILL.md) | Review redirects, account linking, authorization callbacks, and token lifecycle. |
| [Browser Agent Boundary Review](skills/browser-agent-boundary-review/SKILL.md) | Review untrusted pages influencing browser agents and authenticated actions. |
| [RAG Access Boundary Review](skills/rag-access-boundary-review/SKILL.md) | Review document permissions across retrieval, indexing, citations, and caches. |
| [Cryptographic Usage Review](skills/cryptographic-usage-review/SKILL.md) | Review cryptographic API misuse, randomness, nonce handling, and key lifecycle. |
| [Security Fix Verification](skills/security-fix-verification/SKILL.md) | Verify security patches against original failures, variants, and legitimate behavior. |
| [Data Deletion Propagation Review](skills/data-deletion-propagation-review/SKILL.md) | Review deletion through primary stores, caches, indexes, exports, and retained copies. |

```sh
python scripts/security_check.py domain-review examples/domain-reviews/agent-approval-binding-review.json --max-findings 3
```

The synthetic example reports five unresolved checks and exits 3. Evidence references are never opened or verified. [Contracts and limits](docs/domain-reviews.md).

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

## Rehearse a boundary and test the evidence

Four independent additions connect security review to a concrete next decision:

| Skill | Try it when | CLI command |
|---|---|---|
| [Attack Path Rehearsal](skills/attack-path-rehearsal) | You need declared entry-to-asset paths and the effect of removing one edge, including alternate routes | `attack-path` |
| [Detection Replay Lab](skills/detection-replay-lab) | You want to test exact field predicates against labeled events before trusting a detection | `detection-replay` |
| [Security Regression Board](skills/security-regression-board) | You need paired baseline/candidate metrics without hiding lost detections or incomplete cases | `regression-board` |
| [Security Skill Router](skills/security-skill-router) | You want to load a few explicit goal matches and preserve deferred work | `skill-route` |

```sh
python scripts/security_check.py attack-path examples/assurance/attack-path.json
python scripts/security_check.py detection-replay examples/assurance/detection-replay.json
python scripts/benchmark_assurance.py
```

The graph example retains an unknown edge. The replay example exposes a missed detection after a field rename. Valid analyses return PARTIAL, exit 3. The benchmark reports synthetic precision, recall, per-case regressions, and selected entrypoint bytes. It does not measure another repository, live attacks, model tokens, or real-world coverage. [Examples, contracts, and measured limits](docs/assurance-workflows.md).

An optional [local stdio MCP server](docs/mcp.md) exposes these same four record operations. It accepts structured records and emits results to the invoking host, with no arbitrary file reads, shell tool, or independent network client. Markdown profiles, Python helpers, and MCP are separate access paths. Use only the path your AI platform supports.

We reviewed the complete tracked inventory of a widely adopted security skill library and manually examined selected workflows. [Research, source revision, adoption signals, ten prioritized areas, and reasons for deferred imports](docs/research/reference-review.md). The four decision workflows were independently authored. Two later offline adaptations retain selected upstream helper functions with explicit attribution and Apache-2.0 licensing. No head-to-head superiority claim is made.

## Attributed offline adaptations

| Local skill | Upstream skill | Available behavior |
|---|---|---|
| [Mail Auth Review](skills/mail-auth-review) | analyzing-email-headers-for-phishing-investigation | Supplied header claims and sender/reply-to differences, without DNS or attachments |
| [Web Header Review](skills/web-header-review) | performing-security-headers-audit | Supplied HSTS, nosniff, referrer-policy presence, and identification headers, without HTTP requests |

```sh
python scripts/security_check.py email-headers examples/adapted-headers/email-headers.json
python scripts/security_check.py http-headers examples/adapted-headers/http-headers.json
```

Both return PARTIAL, exit 3, with brief output by default. These reuse selected reviewed pure functions, not the full upstream scripts. Names describe their narrower offline scope. Original authorship, pinned revision, changes, and Apache-2.0 terms remain explicit. [Third-party notices](THIRD_PARTY_NOTICES.md) and [adaptation limits](docs/adapted-skills.md). Original project code remains MIT; distributed bundles contain both licenses.

### One compact header-review workflow

Use the routed skill for one header type, or review both in one local record:

```sh
python scripts/security_check.py header-review examples/adapted-headers/header-review.json --output header-evidence.json
python scripts/security_check.py header-review examples/adapted-headers/header-review.json --view full --max-findings 20
```

The first command displays at most three leads and saves every finding to a new evidence file. Both views retain PARTIAL, key observations, coverage, per-part counts, and missing scopes. Stable IDs connect follow-up questions to full evidence. Brief reports use a distinct schema; use the saved full report with Security Evidence Pack.

On three fixed synthetic fixtures, `cl100k_base` output tokens fell **33.43% for mail** and **31.07% for web**, with every finding visible. Combined output fell **27.29% with every finding visible**, or **44.01% with the default three-finding cap and explicit omissions**. These measure local serialization, not actual host billing, latency, or model quality. [Workflow and reproducible measurements](docs/header-review-workflow.md).

## Internal agent operations

These five skills help an assistant manage its work with explicit scope, evidence, and stop conditions. Their helpers validate supplied JSON records locally. They do not provide a background agent runtime or invoke tools on your behalf.

| Skill | Internal operation | CLI command |
|---|---|---|
| [Agent Task Planner](skills/agent-task-planner) | Checks a task dependency graph, write ownership, evidence requirements, and step caps. | `task-plan` |
| [Agent Handoff Review](skills/agent-handoff-review) | Checks permission subsets, acceptance references, evidence, and completion claims. | `handoff` |
| [Agent Context Checkpoint](skills/agent-context-checkpoint) | Builds a reference-only capsule while retaining constraints, evidence, revision, unresolved work, and next action. | `checkpoint` |
| [Agent Tool Preflight](skills/agent-tool-preflight) | Compares a proposed tool action with declared tools, resources, effects, transfer policy, and approval requirements. | `preflight` |
| [Agent Retry Guard](skills/agent-retry-guard) | Stops after success or a recorded effect, bounds attempts, and requires reconciliation for unknown write outcomes. | `retry` |

Try the supplied synthetic records:

```sh
python scripts/security_check.py task-plan examples/internal-operations/task-plan.json
python scripts/security_check.py checkpoint examples/internal-operations/checkpoint.json --max-findings 5
python scripts/security_check.py preflight examples/internal-operations/preflight.json
python scripts/security_check.py retry examples/internal-operations/retry.json
```

The task-plan example passes its declared consistency checks. Checkpoint and matching preflight return PARTIAL (exit 3). The retry example deliberately returns BLOCKED (exit 2): it describes a write with an unknown outcome. Neither result executes an action or grants authority.

Example request:

> Use Agent Context Checkpoint to prepare a resume packet for this task. Preserve the current revision, user constraints, evidence references, unresolved work, and next action. Keep optional history out of the packet and report any omissions. Do not write host memory or upload the checkpoint.

Use symbolic local references instead of raw prompts, credentials, payloads, or entire transcripts. Resolve those references and verify freshness before resuming. The reference budget is not a token count. [Operation contracts and examples](docs/internal-operations.md).

## Install for your assistant

Preview one skill for an existing project, then apply the plan:

```sh
python scripts/install_skills.py --agent codex --project ../my-project --skill instruction-boundary-audit
python scripts/install_skills.py --agent codex --project ../my-project --skill instruction-boundary-audit --apply
```

Choose `claude`, `codex`, `cursor`, `copilot`, or `all`. Omit `--skill` to select all forty-one. Replace `--project ../my-project` with `--global` for personal discovery across projects. Existing destinations are refused, never silently upgraded or overwritten.

| Assistant | Project skills | Personal skills |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Cursor | `.cursor/skills/` | `~/.cursor/skills/` |
| GitHub Copilot on supported surfaces | `.github/skills/` | `~/.copilot/skills/` |

Each bundle includes its own helper and can run from another folder without this checkout. The installer does not enable hooks, grant permissions, install dependencies, edit project instructions, or force a reload. A failed copy may leave its new folder for inspection. Older clients and cloud sessions can have different discovery rules. [Compatibility details](docs/compatibility.md).

## Portable agent profiles

- [Instruction Boundary Auditor](agents/instruction-boundary-audit.md)
- [CI Workflow Security Reviewer](agents/ci-workflow-security-audit.md)
- [Container Boundary Reviewer](agents/container-boundary-audit.md)
- [Infrastructure Exposure Reviewer](agents/infrastructure-exposure-audit.md)
- [LLM Data Boundary Reviewer](agents/llm-data-boundary-audit.md)
- [Agent Task Planner](agents/agent-task-planner.md)
- [Agent Handoff Reviewer](agents/agent-handoff-review.md)
- [Agent Context Checkpoint Keeper](agents/agent-context-checkpoint.md)
- [Agent Tool Preflight Reviewer](agents/agent-tool-preflight.md)
- [Agent Retry Guard](agents/agent-retry-guard.md)
- [Attack Path Rehearsal Reviewer](agents/attack-path-rehearsal.md)
- [Detection Replay Reviewer](agents/detection-replay-lab.md)
- [Security Regression Reviewer](agents/security-regression-board.md)
- [Security Skill Selection Reviewer](agents/security-skill-router.md)
- [Mail Auth Review Reviewer](agents/mail-auth-review.md)
- [Web Header Reviewer](agents/web-header-review.md)

Attach a profile or load its text into an assistant that accepts Markdown instructions. Each matching installed skill carries its profile in `references/agent.md`. These are portable instructions, not universal native agent registrations. Without filesystem access, an assistant can review supplied excerpts and report partial coverage. Running helpers requires terminal access and Python. [Agent usage](docs/agents.md).

Example request:

> Use the CI Workflow Security Reviewer on this project's GitHub Actions workflows. Keep analysis local. Report file and line evidence, effective-authority questions, and the smallest fixes. Preserve unknowns and list the commands actually run.

Pass the project root to the `ci` helper so `.github/workflows` retains its expected relative path. In Codex, explicitly invoke `$ci-workflow-security-audit`; in Claude Code, use `/ci-workflow-security-audit`. Other hosts can use their skill picker or a natural-language request.

## Spend context on decisions

```sh
python scripts/security_check.py llm-data ../my-project --max-findings 5 --output llm-review.json
```

The console shows up to five findings plus the total count, omitted count, coverage, and limitations. The new `llm-review.json` file keeps the complete report. Keep output outside the target when comparing snapshots.

Deterministic local work, one relevant skill, references opened on demand, and focused source review reduce repeated context. Stable finding IDs let follow-ups refer to saved evidence instead of replaying the whole report.

The [synthetic benchmark](docs/report-benchmark.md) measured **78,487 to 1,157 `cl100k_base` tokens**, a **98.53% reduction** when compacting a 1,000-finding fixture to twenty visible findings. This measures serialization, not real-project savings, model quality, or billing. Full evidence remains available separately.

Keep a follow-up small: pass the saved report, relevant finding IDs, and the source lines needed to resolve them. Raise `--max-findings` when a decision needs more evidence. An omitted finding remains unresolved until reviewed.

## One result contract

Every report uses [`security-agent-skills/report-v1`](schemas/report-v1.schema.json), retaining workflow, scope, findings, coverage, limitations, and details. Findings have stable IDs, rule names, source locations, and confidence. Lexical matches are review leads, not confirmed vulnerabilities.

| Exit | Result | Meaning |
|---|---|---|
| `0` | PASS or generated data | The named bounded check passed, or inert fixture/snapshot data was generated. |
| `1` | FIX | Supplied evidence fails a bounded check. |
| `2` | BLOCKED | Required input, access, schema, or a new output path is missing. |
| `3` | PARTIAL | Evidence is incomplete or the operation is static. |

Agent profiles use Result, Findings, Coverage, Validation, and Remaining. Passing package tests does not turn a partially inspected target into a safe target.

For example, the [demo's compact report](docs/assets/security/demo-compact.json) keeps `finding_count: 3`, `omitted_findings: 1`, and `runtime_observed: false` together. A short report still tells the reviewer what remains unseen.

## Privacy and limits

- Analysis helpers make no network requests and execute no reviewed code. Explicit development commands can download public build or test dependencies.
- Inventory excludes links, reparse points, hardlinks, credential filenames, binaries, dependency folders, unreadable files, and over-budget inputs. Coverage records skips.
- Static findings omit source excerpts and configuration values. Reports still include scope paths and filenames. Evidence export omits scope paths and freeform details and applies best-effort pattern scrubbing. Inspect artifacts before sharing.
- New audits are lexical, line-based checks. They do not evaluate complete YAML/HCL semantics, templates, inherited permissions, provider defaults, or runtime data flows. Quoted examples and negations can produce leads.
- AppSec validation checks declared scope without making requests. Injection grading consumes supplied records. Route mapping consumes synthetic events. Sandbox generation does not launch Docker. Evidence hashes establish local consistency, not authenticity or external truth.
- Internal-operation records are declarations. Helpers do not open evidence references, verify their freshness, resolve resource aliases, or observe actual tool effects. A matching preflight is PARTIAL and never grants host permission. Checkpoints contain reference IDs that may themselves be sensitive; review before sharing.
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

Tests cover scanner boundaries, source non-execution, output privacy, incomplete coverage, no-overwrite installation, archive integrity, and installed-helper subprocesses across all four directory layouts. No CI pipeline is configured or required. Representative explicitly loaded workflows were exercised in this Codex session on Windows; automatic discovery, other assistants, and the latest macOS runtime remain unverified. See [compatibility evidence](docs/compatibility.md).

See [CONTRIBUTING.md](CONTRIBUTING.md) for lint, types, formatting, build, and installed-wheel checks, [SECURITY.md](SECURITY.md) for vulnerability reporting, and [.specs](.specs/README.md) for requirements and evidence.

Documentation artwork and demo sources live in [docs/assets/security](docs/assets/security/README.md). They are local assets, so the README does not depend on a third-party GIF host. The optional Pillow renderer is for documentation authors only; it is not a runtime dependency.

`integ` is the development branch. `main` remains protected, including for administrators, and requires independent review. The required CI check has been removed. No release or merge is automatic. See [branch policy](docs/branch-policy.md).

Original Fliorcie-authored code is MIT licensed. Two adapted helper modules retain Apache-2.0 licensing and original attribution. Standalone bundles carry both licenses and [third-party notices](THIRD_PARTY_NOTICES.md). [Portfolio estimates](docs/portfolio.md) are hypotheses, not promises of adoption.
