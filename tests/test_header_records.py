"""Attributed adaptations keep offline and output-privacy boundaries."""

import copy
import json
import unittest
from pathlib import Path
from unittest.mock import patch

from security_agent_skills.header_records import HEADER_RECORDS, email_headers, http_headers

ROOT = Path(__file__).resolve().parents[1]


def example(command):
    return json.loads((ROOT / "examples/adapted-headers" / (command + ".json")).read_text())


class HeaderRecordTests(unittest.TestCase):
    def test_email_claims_and_reply_mismatch_without_values(self):
        result = email_headers(example("email-headers"))
        self.assertEqual(result["finding_count"], 3)
        self.assertEqual(result["details"]["claimed_results"]["spf"], ["fail"])
        self.assertTrue(result["details"]["from_reply_to_mismatch"])
        self.assertNotIn("example.invalid", json.dumps(result))
        self.assertFalse(result["details"]["claims_authoritative"])

    def test_email_missing_claims_are_unknown_and_conflicts_remain(self):
        doc = {
            "schema": "security-agent-skills/email-headers-v1",
            "headers": "From: a@example.invalid\n",
        }
        self.assertEqual(email_headers(doc)["details"]["claimed_results"]["dkim"], ["unknown"])
        doc["headers"] += (
            "Authentication-Results: receiver; spf=fail\n"
            "Authentication-Results: untrusted; spf=pass\n"
        )
        value = email_headers(doc)
        self.assertEqual(value["details"]["claimed_results"]["spf"], ["fail", "pass"])
        self.assertEqual(value["finding_count"], 1)

    def test_email_rejects_bodies_duplicate_identities_and_bad_shapes(self):
        for text in (
            "From: a@example.invalid\n\nprivate body",
            "From: a@example.invalid\nFrom: b@example.invalid",
            "Subject: missing sender",
            "From: a@example.invalid\rBad: x",
            "\x00",
            "From: a@example.invalid\n" + "X: a\n" * 100,
            "a" * 65537,
        ):
            with self.subTest(text_length=len(text)):
                with self.assertRaises(ValueError):
                    email_headers(
                        {"schema": "security-agent-skills/email-headers-v1", "headers": text}
                    )

    def test_http_example_does_not_expose_server_value(self):
        result = http_headers(example("http-headers"))
        self.assertEqual(result["finding_count"], 3)
        self.assertNotIn("Synthetic-Server", json.dumps(result))
        self.assertEqual(result["details"]["identification_header_count"], 1)

    def test_http_hsts_case_ows_and_invalid_age(self):
        doc = example("http-headers")
        doc["headers"][0] = {
            "name": "STRICT-TRANSPORT-SECURITY",
            "value": "MAX-AGE = 31536000; includeSubDomains",
        }
        result = http_headers(doc)
        self.assertNotIn("HTTP-HSTS-AGE-UNKNOWN", [f["rule"] for f in result["findings"]])
        self.assertNotIn("HTTP-HSTS-AGE-REVIEW", [f["rule"] for f in result["findings"]])
        for text in ("max-age=garbage", "x-max-age=31536000", "max-age=" + "9" * 100):
            doc["headers"][0]["value"] = text
            result = http_headers(doc)
            self.assertIn("HTTP-HSTS-AGE-UNKNOWN", [f["rule"] for f in result["findings"]])

    def test_http_valid_subset_is_still_partial_and_transport_is_not_verified(self):
        doc = {
            "schema": "security-agent-skills/http-headers-v1",
            "secure_transport": True,
            "headers": [
                {"name": "Strict-Transport-Security", "value": "max-age=31536000"},
                {"name": "X-Content-Type-Options", "value": "nosniff"},
                {"name": "Referrer-Policy", "value": "no-referrer"},
            ],
        }
        result = http_headers(doc)
        self.assertEqual(result["finding_count"], 0)
        self.assertEqual(result["result"], "PARTIAL")
        doc["secure_transport"] = False
        self.assertTrue(http_headers(doc)["details"]["hsts_not_evaluated"])

    def test_http_wrong_nosniff_and_duplicate_headers_are_not_clean(self):
        doc = example("http-headers")
        doc["headers"][1]["value"] = "invalid"
        self.assertIn("HTTP-NOSNIFF-REVIEW", [f["rule"] for f in http_headers(doc)["findings"]])
        doc["headers"].append({"name": "SERVER", "value": "other"})
        with self.assertRaises(ValueError):
            http_headers(doc)

    def test_http_rejects_control_characters_non_strings_and_overflow(self):
        for key, bad in (
            ("value", "private\r\ninjected"),
            ("name", "bad/name"),
            ("value", {}),
            ("value", "x" * 4097),
        ):
            doc = example("http-headers")
            doc["headers"][0][key] = bad
            with self.assertRaises(ValueError):
                http_headers(doc)
        for value in ("true", 1, None):
            doc = example("http-headers")
            doc["secure_transport"] = value
            with self.assertRaises(ValueError):
                http_headers(doc)

    def test_record_fields_versions_and_non_objects_rejected(self):
        for command, operation in HEADER_RECORDS.items():
            for value in (
                [],
                None,
                True,
                {**example(command), "extra": "private"},
                {**example(command), "schema": "unknown"},
            ):
                with self.assertRaises(ValueError):
                    operation(value)

    def test_adapters_are_deterministic_no_network_process_or_file_writes(self):
        samples = {command: example(command) for command in HEADER_RECORDS}
        with (
            patch("socket.socket", side_effect=AssertionError("network")),
            patch("subprocess.run", side_effect=AssertionError("process")),
            patch("builtins.open", side_effect=AssertionError("file access")),
            patch("pathlib.Path.open", side_effect=AssertionError("path access")),
        ):
            for command, operation in HEADER_RECORDS.items():
                doc = samples[command]
                original = copy.deepcopy(doc)
                first = operation(doc)
                self.assertEqual(first, operation(doc))
                self.assertEqual(original, doc)
                self.assertFalse(first["coverage"]["runtime_observed"])

    def test_every_bundle_retains_attribution_licenses_and_source_provenance(self):
        catalog = json.loads((ROOT / "catalog.json").read_text())
        provenance = json.loads((ROOT / "third-party-provenance.json").read_text())
        self.assertEqual(len(provenance["adaptations"]), 2)
        for item in provenance["adaptations"]:
            text = (ROOT / item["adapted_module"]).read_text()
            self.assertIn("SPDX-License-Identifier: Apache-2.0", text)
            self.assertIn("Copyright 2026 mukul975", text)
            self.assertIn("Modified by Fliorcie Labs", text)
        for entry in catalog:
            base = ROOT / "skills" / entry["name"]
            for relative in (
                "LICENSES/Apache-2.0.txt",
                "THIRD_PARTY_NOTICES.md",
                "third-party-provenance.json",
            ):
                self.assertEqual(
                    (base / relative).read_bytes(),
                    (ROOT / relative).read_bytes().replace(b"\r\n", b"\n"),
                )
