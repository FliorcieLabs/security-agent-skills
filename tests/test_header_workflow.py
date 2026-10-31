"""Compact presentation must preserve evidence, counts, and uncertainty."""

import copy
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from security_agent_skills.cli import main
from security_agent_skills.header_records import (
    BRIEF_SCHEMA,
    brief_header_markdown,
    brief_header_report,
    header_review,
)
from tests.test_header_records import ROOT, example


class HeaderWorkflowTests(unittest.TestCase):
    def call(self, arguments):
        output = io.StringIO()
        with redirect_stdout(output):
            code = main(arguments)
        return code, output.getvalue()

    def test_combined_review_preserves_both_parts_and_ids(self):
        value = header_review(example("header-review"))
        self.assertEqual(value["finding_count"], 6)
        self.assertEqual(value["details"]["finding_counts"], {"email": 3, "http": 3})
        self.assertEqual(value["details"]["not_supplied"], [])
        self.assertEqual(value["result"], "PARTIAL")

    def test_one_scope_missing_stays_visible_and_empty_scope_is_blocked(self):
        doc = example("header-review")
        doc["email"] = None
        value = header_review(doc)
        self.assertEqual(value["details"]["not_supplied"], ["email"])
        self.assertEqual(value["result"], "PARTIAL")
        doc["http"] = None
        with self.assertRaises(ValueError):
            header_review(doc)

    def test_invalid_combined_child_fields_or_schema_are_rejected(self):
        for change in ({"email": True}, {"schema": "unknown"}, {"extra": "private"}):
            doc = {**example("header-review"), **change}
            with self.assertRaises(ValueError):
                header_review(doc)

    def test_brief_keeps_all_observations_counts_and_unknowns_without_mutation(self):
        full = header_review(example("header-review"))
        original = copy.deepcopy(full)
        brief = brief_header_report(full, 2)
        self.assertEqual(brief["schema"], BRIEF_SCHEMA)
        self.assertEqual(brief["finding_count"], 6)
        self.assertEqual(brief["omitted_findings"], 4)
        self.assertEqual(brief["coverage"], full["coverage"])
        self.assertEqual(brief["details"], full["details"])
        self.assertEqual(
            [f["id"] for f in brief["findings"]], [f["id"] for f in full["findings"][:2]]
        )
        self.assertEqual(full, original)
        brief["details"]["not_supplied"].append("private")
        self.assertEqual(full, original)

    def test_zero_cap_preserves_count_and_negative_cap_is_invalid(self):
        full = header_review(example("header-review"))
        brief = brief_header_report(full, 0)
        self.assertEqual(brief["findings"], [])
        self.assertEqual(brief["omitted_findings"], 6)
        with self.assertRaises(ValueError):
            brief_header_report(full, -1)

    def test_default_brief_full_view_and_unabridged_export_agree(self):
        record = ROOT / "examples/adapted-headers/header-review.json"
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "full.json"
            code, text = self.call(["header-review", str(record), "--output", str(output)])
            self.assertEqual(code, 3)
            brief, full = json.loads(text), json.loads(output.read_text())
            self.assertEqual(brief["schema"], BRIEF_SCHEMA)
            self.assertEqual(len(brief["findings"]), 3)
            self.assertEqual(brief["omitted_findings"], 3)
            self.assertEqual(len(full["findings"]), 6)
            self.assertEqual(full["schema"], "security-agent-skills/report-v1")
            code, text = self.call(
                ["header-review", str(record), "--view", "full", "--max-findings", "20"]
            )
            self.assertEqual(code, 3)
            shown = json.loads(text)
            self.assertEqual(shown["details"], full["details"])
            self.assertEqual(shown["findings"], full["findings"])
            before = output.read_bytes()
            code, text = self.call(["header-review", str(record), "--output", str(output)])
            self.assertEqual(code, 2)
            self.assertEqual(output.read_bytes(), before)

    def test_individual_header_commands_use_brief_without_api_name_changes(self):
        for command in ("email-headers", "http-headers"):
            code, text = self.call(
                [command, str(ROOT / "examples/adapted-headers" / (command + ".json"))]
            )
            self.assertEqual(code, 3)
            self.assertEqual(json.loads(text)["schema"], BRIEF_SCHEMA)

    def test_markdown_contains_claims_missing_scopes_omissions_and_limits(self):
        doc = example("header-review")
        doc["http"] = None
        brief = brief_header_report(header_review(doc), 1)
        text = brief_header_markdown(brief)
        self.assertIn("omitted: 2", text)
        self.assertIn('"not_supplied":["http"]', text)
        self.assertIn('"claims_authoritative":false', text)
        self.assertIn("unverified", text)
        self.assertNotIn("example.invalid", text)

    def test_serialized_brief_is_smaller_even_with_every_finding_visible(self):
        full = header_review(example("header-review"))
        brief = brief_header_report(full, 100)

        def encode(value):
            return json.dumps(value, sort_keys=True, separators=(",", ":"))

        self.assertLess(len(encode(brief)), len(encode(full)))
        self.assertEqual(brief["omitted_findings"], 0)
