"""Behavioral boundaries for offline internal agent operation records."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from security_agent_skills.cli import read_json
from security_agent_skills.internal_operations import OPERATIONS

ROOT = Path(__file__).resolve().parents[1]


def example(command):
    return json.loads((ROOT / "examples/internal-operations" / f"{command}.json").read_text())


class InternalOperationTests(unittest.TestCase):
    def test_operation_reader_rejects_duplicate_keys_at_any_depth(self):
        with tempfile.TemporaryDirectory() as directory:
            record = Path(directory) / "record.json"
            for content in [
                '{"schema":"one","schema":"two"}',
                '{"policy":{"allow":false,"allow":true}}',
            ]:
                record.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_json(str(record), unique_keys=True)

    def test_examples_keep_the_report_contract_and_never_execute_or_authorize(self):
        for command, operation in OPERATIONS.items():
            with self.subTest(command=command):
                value = example(command)
                before = copy.deepcopy(value)
                report = operation(value)
                self.assertEqual(report["schema"], "security-agent-skills/report-v1")
                self.assertFalse(report["details"]["executed"])
                self.assertFalse(report["details"]["authorization_granted"])
                self.assertFalse(report["coverage"]["source_claims_verified"])
                self.assertEqual(value, before)

    def test_task_graph_returns_positions_in_dependency_order(self):
        doc = example("task-plan")
        doc["tasks"].reverse()
        report = OPERATIONS["task-plan"](doc)
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["details"]["candidate_order_positions"], [2, 1])

    def test_task_cycles_unknown_dependencies_and_duplicate_ids(self):
        doc = example("task-plan")
        doc["tasks"][0]["depends_on"] = ["verify"]
        report = OPERATIONS["task-plan"](doc)
        self.assertEqual(report["result"], "FIX")
        self.assertEqual(report["details"]["candidate_order_positions"], [])
        doc["tasks"][0]["depends_on"] = ["missing"]
        self.assertIn(
            "unknown-task-dependency", {f["rule"] for f in OPERATIONS["task-plan"](doc)["findings"]}
        )
        doc["tasks"][0]["id"] = "verify"
        with self.assertRaises(ValueError):
            OPERATIONS["task-plan"](doc)

    def test_task_ownership_evidence_and_step_budget_are_checked(self):
        doc = example("task-plan")
        doc["tasks"][1]["write_resources"] = doc["tasks"][0]["write_resources"][:]
        doc["tasks"][1]["evidence_required"] = False
        doc["max_total_steps"] = 1
        rules = {f["rule"] for f in OPERATIONS["task-plan"](doc)["findings"]}
        self.assertEqual(rules, {"shared-write-owner", "missing-task-evidence", "task-step-budget"})

    def test_handoff_prevents_authority_expansion_and_false_completion(self):
        doc = example("handoff")
        self.assertEqual(OPERATIONS["handoff"](doc)["result"], "PASS")
        doc["delegated_permissions"].append("publish_package")
        doc["status"] = "complete"
        report = OPERATIONS["handoff"](doc)
        self.assertEqual(
            {f["rule"] for f in report["findings"]},
            {"handoff-authority-expansion", "handoff-unresolved-completion"},
        )
        self.assertNotIn("publish_package", json.dumps(report))

    def test_handoff_requires_distinct_agents_acceptance_and_evidence(self):
        doc = example("handoff")
        doc.update(target_agent=doc["source_agent"], acceptance_refs=[], evidence_refs=[])
        self.assertEqual(OPERATIONS["handoff"](doc)["finding_count"], 3)

    def test_checkpoint_preserves_mandatory_refs_and_counts_omissions(self):
        doc = example("checkpoint")
        report = OPERATIONS["checkpoint"](doc)
        self.assertEqual(report["result"], "PARTIAL")
        capsule = report["details"]["capsule"]
        for name in ["constraint_refs", "evidence_refs", "unresolved_refs"]:
            self.assertEqual(capsule[name], doc[name])
        self.assertEqual(capsule["decision_refs"], ["decision_01"])
        self.assertEqual(report["details"]["decision_refs_omitted"], 2)

    def test_checkpoint_blocks_instead_of_dropping_critical_context(self):
        for change in [{"max_refs": 1}, {"constraint_refs": []}, {"evidence_refs": []}]:
            with self.subTest(change=change):
                doc = example("checkpoint")
                doc.update(change)
                report = OPERATIONS["checkpoint"](doc)
                self.assertEqual(report["result"], "BLOCKED")
                self.assertEqual(report["details"]["capsule"], {})

    def test_preflight_allowlists_do_not_grant_authorization(self):
        report = OPERATIONS["preflight"](example("preflight"))
        self.assertEqual(report["result"], "PARTIAL")
        self.assertTrue(report["details"]["declared_policy_match"])
        self.assertFalse(report["details"]["authorization_granted"])

    def test_preflight_denies_each_authority_boundary(self):
        for key, value, rule in [
            ("tool", "upload_file", "preflight-tool"),
            ("resources", ["outside_scope"], "preflight-resource"),
            ("effect", "write", "preflight-effect"),
            ("external_transfer", True, "preflight-external-transfer"),
        ]:
            with self.subTest(key=key):
                doc = example("preflight")
                doc["action"][key] = value
                report = OPERATIONS["preflight"](doc)
                self.assertEqual(report["result"], "BLOCKED")
                self.assertIn(rule, {f["rule"] for f in report["findings"]})
        doc = example("preflight")
        doc["policy"]["allowed_effects"].append("write")
        doc["action"]["effect"] = "write"
        self.assertIn(
            "preflight-write-approval",
            {f["rule"] for f in OPERATIONS["preflight"](doc)["findings"]},
        )
        doc["action"]["approval_recorded"] = True
        self.assertEqual(OPERATIONS["preflight"](doc)["result"], "PARTIAL")

    def test_unknown_write_requires_reconciliation(self):
        doc = example("retry")
        report = OPERATIONS["retry"](doc)
        self.assertEqual(report["result"], "BLOCKED")
        self.assertEqual(report["details"]["next_action"], "reconcile_ambiguous_write")
        doc["reconciliation"] = "inconclusive"
        self.assertEqual(OPERATIONS["retry"](doc)["result"], "BLOCKED")
        doc["reconciliation"] = "effect_absent"
        self.assertEqual(OPERATIONS["retry"](doc)["result"], "PARTIAL")

    def test_retry_success_or_effect_present_stops_without_retry(self):
        for change in [{"outcome": "succeeded"}, {"reconciliation": "effect_present"}]:
            doc = example("retry")
            doc.update(change)
            report = OPERATIONS["retry"](doc)
            self.assertEqual(report["result"], "PASS")
            self.assertEqual(report["details"]["next_action"], "stop_without_retry")

    def test_retry_budget_read_candidate_and_contradiction(self):
        doc = example("retry")
        doc["max_attempts"] = 1
        self.assertEqual(
            OPERATIONS["retry"](doc)["details"]["next_action"], "stop_budget_exhausted"
        )
        doc.update(effect="read", max_attempts=3)
        self.assertEqual(OPERATIONS["retry"](doc)["result"], "PARTIAL")
        doc["attempts"] = 0
        with self.assertRaises(ValueError):
            OPERATIONS["retry"](doc)

    def test_handoff_blocked_status_needs_a_blocker_reference(self):
        doc = example("handoff")
        doc.update(status="blocked", unresolved_refs=[])
        self.assertEqual(OPERATIONS["handoff"](doc)["result"], "FIX")

    def test_retry_contradictions_and_initial_attempt(self):
        for change in [
            {"effect": "read", "reconciliation": "effect_present"},
            {"outcome": "succeeded", "reconciliation": "effect_absent"},
            {"outcome": "failed_no_effect", "reconciliation": "effect_present"},
            {"outcome": "failed_no_effect", "reconciliation": "inconclusive"},
        ]:
            doc = example("retry")
            doc.update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                OPERATIONS["retry"](doc)
        doc = example("retry")
        doc.update(outcome="not_started", attempts=0)
        self.assertEqual(OPERATIONS["retry"](doc)["result"], "PARTIAL")

    def test_strict_record_shapes_reject_nested_and_unbounded_content(self):
        mutations = [None, [], {}, {"schema": "unrecognized"}]
        for command, operation in OPERATIONS.items():
            for mutation in mutations:
                with (
                    self.subTest(command=command, mutation=mutation),
                    self.assertRaises(ValueError),
                ):
                    operation(mutation)
            doc = example(command)
            doc["hidden_prompt"] = "PRIVATE_SYNTHETIC_VALUE"
            with self.assertRaises(ValueError):
                operation(doc)
        for value in [True, "5", -1, 1001]:
            doc = example("task-plan")
            doc["max_total_steps"] = value
            with self.assertRaises(ValueError):
                OPERATIONS["task-plan"](doc)
        for refs in [
            ["duplicate", "duplicate"],
            ["x"] * 101,
            ["../outside"],
            ["https://example.invalid"],
            ["line\nbreak"],
        ]:
            doc = example("checkpoint")
            doc["decision_refs"] = refs
            with self.assertRaises(ValueError):
                OPERATIONS["checkpoint"](doc)

    def test_cli_blocks_bad_records_without_echoing_content_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, output = root / "input.json", root / "report.json"
            for command in OPERATIONS:
                doc = example(command)
                doc["PRIVATE_SYNTHETIC_FIELD"] = "PRIVATE_SYNTHETIC_VALUE"
                source.write_text(json.dumps(doc), encoding="utf-8")
                result = subprocess.run(
                    [sys.executable, str(ROOT / "scripts/security_check.py"), command, str(source)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("PRIVATE_SYNTHETIC", result.stdout + result.stderr)
            source.write_text(json.dumps(example("checkpoint")), encoding="utf-8")
            output.write_text("existing", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/security_check.py"),
                    "checkpoint",
                    str(source),
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            self.assertEqual(result.returncode, 2)
            self.assertEqual(output.read_text(), "existing")
