# Bounded delivery tasks

Owner: repository maintainer implementation through professional-coder. Status before implementation: READY. Invariant: no source execution, external transfer, silent overwrites, or missing coverage represented as a clean result.

| Task | Requirement | Component | Acceptance command |
|---|---|---|---|
| T01 | SEC-001 | inventory, report schema, egress leads | python -m unittest tests.test_audits -v |
| T02 | SEC-002 | dependency and hook inspection | python -m unittest tests.test_audits -v |
| T03 | SEC-003 | MCP authority inspection | python -m unittest tests.test_audits -v |
| T04 | SEC-004 | local exposure review | python -m unittest tests.test_audits -v |
| T05 | SEC-005 | authorization scope validation | python -m unittest tests.test_workflows -v |
| T06 | SEC-006 | local content snapshot comparisons | python -m unittest tests.test_workflows -v |
| T07 | SEC-007 | offline injection cases and response grading | python -m unittest tests.test_workflows -v |
| T08 | SEC-008 | synthetic canary route interpretation | python -m unittest tests.test_workflows -v |
| T09 | SEC-009 | restricted container plan generation | python -m unittest tests.test_workflows -v |
| T10 | SEC-010 | reproducible report archive and verification | python -m unittest tests.test_evidence -v |
| T11 | SEC-011 | portable standalone skill bundles and installer | python -m unittest tests.test_portability -v |
| T12 | SEC-012 | bounded summaries and size benchmark | python scripts/benchmark_reports.py |

Implementation records and final validation belong in evidence.md and 01-requirements/traceability.md. Commands are run from the repository root. The task status is updated only after executable evidence exists.

Local delivery status: T01 through T12 verified by the executable evidence in evidence.md. External CI is a separate gate attached to the pushed head revision.

## Expansion tasks

Owner: primary implementation agent. Status before implementation: READY. Keep local-only analysis and explicit incomplete coverage. Each scanner owns one review boundary and emits fixed messages and source locations, never source values. Shared integration owns CLI routing, bundles, and the catalog.

| Task | Requirement | Component | Acceptance command |
|---|---|---|---|
| T13 | SEC-013 | instruction-boundary-audit | python -m unittest tests.test_extended_audits -v |
| T14 | SEC-014 | ci-workflow-security-audit | python -m unittest tests.test_extended_audits -v |
| T15 | SEC-015 | container-boundary-audit | python -m unittest tests.test_extended_audits -v |
| T16 | SEC-016 | infrastructure-exposure-audit | python -m unittest tests.test_extended_audits -v |
| T17 | SEC-017 | llm-data-boundary-audit | python -m unittest tests.test_extended_audits -v |
| T18 | SEC-018 | five portable agent profiles and Markdown guide | python scripts/validate_skills.py |

Acceptance also requires subprocess execution of all fifteen installed helpers in all four host directory layouts, no overwrites, source-to-bundle parity, and existing quality checks. Native interactive recognition on every AI platform is not an acceptance claim.

Local expansion status: T13 through T18 verified by the 49-test suite, skill validation, deterministic bundles, lint/type/format checks, and package smoke evidence. Remote checks apply to the pushed head and are reported in the PR.

## README presentation

T19, SEC-018. Owner: primary implementation agent. Status: READY. Scope: README navigation, original security artwork, and an animated CLI example. Invariant: the example uses synthetic inputs, shows actual helper results and incomplete coverage, and makes no new security or platform claims. Acceptance: relative Markdown links and media decode; demonstration output matches a fresh CLI run; all existing tests and bundle validators pass. Record executed evidence in evidence.md.

Local T19 status: VERIFIED by the README presentation checks in evidence.md. Remote checks apply to the pushed head.

## Internal agent operations

Owner: primary implementation agent. Status before implementation: READY. Invariant: validate bounded local records without executing actions, changing host permissions, delegating agents, or representing declared records as runtime truth. Every helper keeps the report contract and source-verification limits visible.

| Task | Requirement | Component | Acceptance command |
|---|---|---|---|
| T20 | SEC-019 | agent-task-planner: dependency graph, ownership, step budget | python -m unittest tests.test_internal_operations -v |
| T21 | SEC-020 | agent-handoff-review: authority subset and completion evidence | python -m unittest tests.test_internal_operations -v |
| T22 | SEC-021 | agent-context-checkpoint: bounded references with mandatory context preserved | python -m unittest tests.test_internal_operations -v |
| T23 | SEC-022 | agent-tool-preflight: declared policy comparison without a permission grant | python -m unittest tests.test_internal_operations -v |
| T24 | SEC-023 | agent-retry-guard: stop conditions and ambiguous-write reconciliation | python -m unittest tests.test_internal_operations -v |

Integration acceptance: all twenty installed helpers run outside the checkout in all four host layouts; source-to-bundle parity, strict input boundaries, output privacy, existing tests and quality gates pass. Update README, compatibility, capability limits, profile guide, traceability, and reproducible evidence. No interactive host recognition or actual agent execution is claimed.

Local T20 through T24 status: VERIFIED by 67 passing tests, 80 installed bundles, 350 generated files, shape/skill/spec validation, quality checks, package build, offline wheel smoke, and documentation checks in evidence.md. Remote checks apply to the pushed head.

## CI disablement and release readiness

T25, SEC-009 and SEC-018. Owner: primary implementation agent. Status before implementation: READY. Disable the Quality workflow remotely and remove automatic push/PR triggers from its saved definition. Preserve branch protection, tests, validators, and manual verification commands. Correct the sandbox plan's argument-array validation with regression coverage. Review source, installation boundaries, public claims, distribution, and available verification evidence before recommending a release tier. Do not publish a release, tag, merge, or remove required main checks as part of this review.

Acceptance: remote workflow state disabled_manually, saved workflow has workflow_dispatch only, full test and quality checks pass, deterministic bundles validate, package build and offline smoke pass, and release assessment names any unresolved prerequisites. Record evidence and update README, branch policy, and contributor instructions.

Local T25 status: VERIFIED by the 69-test suite, 80 installed bundles, bundle/skill/spec validation, lint/type/format checks, source/wheel build, offline smoke, source review, and recorded remote settings. Release verdict remains a preview candidate with publication prerequisites in docs/release-readiness.md; stable readiness is not established.

## No-CI preview preparation

T26, SEC-011 and SEC-018. Owner: primary implementation agent. Status before implementation: READY. Remove required CI checks from main, disable repository Actions, and delete the retained workflow. Preserve independent review, administrator enforcement, linear history, conversation resolution, and restrictions on force pushes/deletion. Prepare version 0.1.0a1 as a preview with documented compatibility limits and a full-kit source archive. Validate explicit skill use in this Codex session without launching other agents or claiming automatic discovery. Do not fabricate macOS or unavailable host sessions. Stage a draft prerelease; publish only after the existing independent review is satisfied. Acceptance: local tests, bundle parity, version consistency, package smoke, source archive inventory/checksums, documented host evidence, remote settings, and a reviewable draft.

T26 local implementation and verification: PASS, with 69 tests, 80 installed bundles, three representative explicit Codex workflows, aligned alpha versions, build/smoke checks, and no configured workflow or required status check. Committed-head archive/checksum and draft staging results are recorded with the release artifacts. Independent review remains the public-publication prerequisite.
