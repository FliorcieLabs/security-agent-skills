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
