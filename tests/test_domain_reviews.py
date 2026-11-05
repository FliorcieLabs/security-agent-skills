"""Evidence consistency is not independent security verification."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from security_agent_skills.domain_reviews import CONTROLS, review_domain
from tests.test_portability import ROOT


def record(domain=None):
    return {
        "schema": "security-agent-skills/domain-review-v1",
        "domain": domain or next(iter(CONTROLS)),
        "scope": "fixtureProject",
        "checks": [],
    }


class DomainReviewTests(unittest.TestCase):
    def test_all_examples_preserve_missing_checks_and_unknowns(self):
        for domain in CONTROLS:
            doc = json.loads((ROOT / "examples/domain-reviews" / (domain + ".json")).read_text())
            before = copy.deepcopy(doc)
            value = review_domain(doc)
            self.assertEqual(value["result"], "PARTIAL")
            self.assertEqual(value["details"]["counts"]["unknown"], 5)
            self.assertEqual(value["finding_count"], 5)
            self.assertEqual(doc, before)
            self.assertEqual(value, review_domain(doc))
            self.assertFalse(value["coverage"]["source_claims_verified"])
            self.assertFalse(value["details"]["executed"])
            self.assertFalse(value["details"]["authorization_granted"])

    def test_declared_passes_never_become_a_verified_pass(self):
        doc = record()
        doc["checks"] = [
            {"id": key, "outcome": "pass", "basis": "reproduced", "evidence": ["testEvidence"]}
            for key in CONTROLS[doc["domain"]]
        ]
        value = review_domain(doc)
        self.assertEqual(value["result"], "PARTIAL")
        self.assertEqual(value["finding_count"], 0)
        self.assertEqual(value["details"]["counts"]["pass"], 5)
        self.assertFalse(value["coverage"]["runtime_observed"])

    def test_failed_and_not_applicable_controls_retain_evidence(self):
        doc = record()
        ids = list(CONTROLS[doc["domain"]])
        doc["checks"] = [
            {"id": ids[0], "outcome": "fail", "basis": "observed", "evidence": ["caseB", "caseA"]},
            {
                "id": ids[1],
                "outcome": "not_applicable",
                "basis": "observed",
                "evidence": ["rationale"],
            },
        ]
        value = review_domain(doc)
        self.assertEqual(value["details"]["checks"][0]["evidence"], ["caseA", "caseB"])
        self.assertEqual(
            value["details"]["counts"], {"pass": 0, "fail": 1, "unknown": 3, "not_applicable": 1}
        )
        self.assertEqual(value["finding_count"], 4)

    def test_strict_record_shapes_types_budgets_and_control_identity(self):
        doc = record()
        invalid = [
            None,
            [],
            True,
            {**doc, "extra": True},
            {**doc, "schema": "other"},
            {**doc, "domain": []},
            {**doc, "scope": "../private"},
            {**doc, "checks": {}},
        ]
        valid = {
            "id": next(iter(CONTROLS[doc["domain"]])),
            "outcome": "pass",
            "basis": "observed",
            "evidence": ["caseA"],
        }
        for change in (
            {"id": "unknown"},
            {"id": []},
            {"outcome": True},
            {"basis": []},
            {"evidence": []},
            {"evidence": ["../private"]},
            {"evidence": ["caseA"] * 2},
            {"evidence": ["case" + str(i) for i in range(9)]},
            {"outcome": "unknown"},
            {"basis": "unknown"},
            {"outcome": "not_applicable", "evidence": []},
            {"extra": True},
        ):
            invalid.append({**doc, "checks": [{**valid, **change}]})
        invalid += [{**doc, "checks": [valid, valid]}, {**doc, "checks": [valid] * 6}]
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                review_domain(value)

    def test_cli_full_export_omissions_collision_and_error_privacy(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            source, output = folder / "record.json", folder / "full.json"
            source.write_text(json.dumps(record()))
            command = [
                sys.executable,
                str(ROOT / "scripts/security_check.py"),
                "domain-review",
                str(source),
                "--max-findings",
                "2",
                "--output",
                str(output),
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 3, result.stderr)
            shown = json.loads(result.stdout)
            full = json.loads(output.read_text())
            self.assertEqual(shown["omitted_findings"], 3)
            self.assertEqual(len(full["findings"]), 5)
            self.assertEqual(shown["details"], full["details"])
            previous = output.read_bytes()
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertEqual(previous, output.read_bytes())
            source.write_text('{"schema":"PRIVATE_MARKER","schema":"other"}')
            result = subprocess.run(command[:-4], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("PRIVATE_MARKER", result.stdout + result.stderr)

    def test_standalone_domain_binding_cannot_be_overridden(self):
        domains = list(CONTROLS)
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    str(ROOT / "skills" / domains[0] / "scripts/run.py"),
                    str(ROOT / "examples/domain-reviews" / (domains[1] + ".json")),
                    "--domain",
                    domains[1],
                ],
                cwd=directory,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["result"], "BLOCKED")
