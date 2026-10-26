# Requirements and traceability

| ID | Requirement | Implementation | Acceptance evidence |
|---|---|---|---|
| SEC-001 | agent-egress-audit | inventory.py, audits.py | test_audits; see ../evidence.md |
| SEC-002 | dependency-provenance-audit | audits.py | test_audits; see ../evidence.md |
| SEC-003 | mcp-authority-review | audits.py | test_audits; see ../evidence.md |
| SEC-004 | security-exposure-review | audits.py | test_audits; see ../evidence.md |
| SEC-005 | authorized-appsec-validation | plans.py | test_workflows; see ../evidence.md |
| SEC-006 | agent-package-change-sentinel | sentinel.py | test_workflows; see ../evidence.md |
| SEC-007 | prompt-injection-boundary-lab | boundaries.py | test_workflows; see ../evidence.md |
| SEC-008 | secret-route-mapper | boundaries.py | test_workflows; see ../evidence.md |
| SEC-009 | safe-install-sandbox | plans.py | test_workflows; see ../evidence.md |
| SEC-010 | security-evidence-pack | evidence.py | test_evidence; see ../evidence.md |
| SEC-011 | Portable independent bundles, four host adapters, no overwrites | scripts/install_skills.py, scripts/build_skills.py | test_portability; see ../evidence.md |
| SEC-012 | Compact consistent reports preserve unknowns and counts | reports.py, schemas/report-v1.schema.json | test_cli, scripts/benchmark_reports.py; see ../evidence.md |
| SEC-013 | instruction-boundary-audit | extended_audits.py | test_extended_audits, test_installed_workflows; see ../evidence.md |
| SEC-014 | ci-workflow-security-audit | extended_audits.py | test_extended_audits, test_installed_workflows; see ../evidence.md |
| SEC-015 | container-boundary-audit | extended_audits.py | test_extended_audits, test_installed_workflows; see ../evidence.md |
| SEC-016 | infrastructure-exposure-audit | extended_audits.py | test_extended_audits, test_installed_workflows; see ../evidence.md |
| SEC-017 | llm-data-boundary-audit | extended_audits.py | test_extended_audits, test_installed_workflows; see ../evidence.md |
| SEC-018 | Five portable Markdown agent profiles, bundled references, and usage documentation | agents/, docs/agents.md, scripts/build_skills.py | validate_skills, test_installed_workflows; see ../evidence.md |
