import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from security_agent_skills.inventory import collect
from security_agent_skills.workflows import (
    appsec_plan,
    compare_snapshots,
    grade_injection,
    injection_cases,
    map_routes,
    sandbox_plan,
    snapshot,
)


class WorkflowTests(unittest.TestCase):
    def test_snapshot_detects_new_outbound_capability(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            file = root / "a.py"
            file.write_text("print(1)")
            before = snapshot(collect(root))
            file.write_text("requests.post(url)")
            result = compare_snapshots(before, snapshot(collect(root)))
            self.assertTrue(any(f["rule"] == "new-capability" for f in result["findings"]))

    def test_snapshot_rejects_traversal_and_duplicate_paths(self):
        bad = {
            "schema": "security-agent-skills/snapshot-v1",
            "files": [{"path": "../outside", "sha256": "a" * 64, "capabilities": []}],
        }
        with self.assertRaises(ValueError):
            compare_snapshots(bad, bad)

    def test_empty_comparison_does_not_attest_safety(self):
        value = {"schema": "security-agent-skills/snapshot-v1", "files": [], "coverage": {}}
        self.assertEqual(compare_snapshots(value, value)["result"], "PARTIAL")

    def scope(self):
        return {
            "authorized": True,
            "targets": ["https://staging.example"],
            "techniques": ["headers"],
            "starts_at": "2026-01-01T00:00:00+00:00",
            "expires_at": "2026-01-02T00:00:00+00:00",
            "request_budget": 10,
            "concurrency": 1,
            "duration_seconds": 10,
            "stop_on_error_rate": 0.01,
            "stop_on_latency_ms": 1000,
        }

    def test_scope_missing_expired_or_excessive_is_blocked(self):
        now = datetime(2026, 1, 1, 12, tzinfo=UTC)
        for change in [
            {"authorized": False},
            {"expires_at": "2025-01-01T00:00:00+00:00"},
            {"concurrency": 999},
            {"techniques": ["ddos"]},
            {"request_budget": True},
        ]:
            scope = self.scope()
            scope.update(change)
            self.assertEqual(appsec_plan(scope, now=now)["result"], "BLOCKED")

    def test_scope_rejects_wildcards_bad_ports_and_url_controls(self):
        now = datetime(2026, 1, 1, 12, tzinfo=UTC)
        for url in [
            "https://*.example.com",
            "https://example.com:notaport",
            "https://@example.com",
            "https://example.com/\n",
        ]:
            scope = self.scope()
            scope["targets"] = [url]
            self.assertEqual(appsec_plan(scope, now=now)["result"], "BLOCKED")

    def test_valid_scope_only_validates_a_plan(self):
        result = appsec_plan(self.scope(), now=datetime(2026, 1, 1, 12, tzinfo=UTC))
        self.assertEqual(result["result"], "PASS")
        self.assertFalse(result["coverage"]["runtime_observed"])

    def test_injection_missing_or_duplicate_responses_are_not_passes(self):
        self.assertEqual(grade_injection([])["result"], "BLOCKED")
        response = {"case_id": injection_cases()[0]["id"], "tool_calls": [], "output": "safe"}
        with self.assertRaises(ValueError):
            grade_injection([response, response])

    def test_injection_synthetic_secret_leak_and_forbidden_tool(self):
        cases = injection_cases()
        responses = [{"case_id": c["id"], "tool_calls": [], "output": "ignored"} for c in cases]
        responses[0]["output"] = cases[0]["canary"]
        responses[1]["tool_calls"] = [{"tool": "upload_file"}]
        result = grade_injection(responses)
        self.assertEqual(result["result"], "FIX")
        self.assertEqual(result["finding_count"], 2)

    def test_canary_routes_require_synthetic_labels(self):
        with self.assertRaises(ValueError):
            map_routes([{"canary": "REAL_API_KEY", "source": "env", "sink": "https://example.com"}])
        report = map_routes(
            [
                {
                    "canary": "SYNTHETIC_TEST",
                    "source": "fixture",
                    "sink": "https://name:PRIVATE@example.com/path?token=SECRET",
                }
            ]
        )
        self.assertEqual(report["finding_count"], 1)
        self.assertNotIn("SECRET", json.dumps(report))
        self.assertNotIn("PRIVATE", json.dumps(report))
        self.assertEqual(map_routes([])["result"], "PARTIAL")

    def test_sandbox_is_a_plan_not_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            result = sandbox_plan(
                directory, "python@sha256:" + "a" * 64, ["python", "-c", "print(1)"]
            )
            argv = result["details"]["argv"]
            self.assertIn("--network", argv)
            self.assertIn("none", argv)
            self.assertIn("--read-only", argv)
            self.assertIn("no-new-privileges", argv)
            self.assertFalse(result["details"]["executed"])
            self.assertIn("readonly", " ".join(argv))

    def test_sandbox_rejects_unpinned_image_and_ambiguous_mount(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                sandbox_plan(directory, "python:latest", ["python"])
            nested = Path(directory) / "comma,path"
            nested.mkdir()
            with self.assertRaises(ValueError):
                sandbox_plan(nested, "python@sha256:" + "a" * 64, ["python"])
