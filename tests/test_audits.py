import json
import tempfile
import unittest
from pathlib import Path

from security_agent_skills.audits import audit_dependencies, audit_egress, audit_exposure, audit_mcp
from security_agent_skills.inventory import collect
from security_agent_skills.reports import compact


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def write(self, name, text):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        return p

    def test_egress_never_echoes_secret_url_components(self):
        self.write(
            "client.py",
            'requests.post("https://name:PRIVATE_PASSWORD@example.com/SYNTHETIC_PRIVATE_PATH?token=PRIVATE_VALUE", data=payload)',
        )
        report = audit_egress(collect(self.root))
        text = json.dumps(report)
        self.assertTrue(report["findings"])
        self.assertNotIn("PRIVATE_PASSWORD", text)
        self.assertNotIn("PRIVATE_VALUE", text)
        self.assertNotIn("SYNTHETIC_PRIVATE_PATH", text)

    def test_skips_credentials_and_reports_incomplete_coverage(self):
        self.write(".env", "API_KEY=do-not-read")
        self.write("a.py", "print(1)")
        inventory = collect(self.root)
        self.assertEqual(len(inventory.files), 1)
        self.assertTrue(inventory.skipped)
        self.assertEqual(audit_egress(inventory)["result"], "PARTIAL")

    def test_file_budget_and_binary_are_explicit(self):
        self.write("large.py", "x" * 20)
        (self.root / "binary").write_bytes(b"\xff\x00")
        inventory = collect(self.root, max_bytes=10)
        self.assertEqual(len(inventory.skipped), 2)

    def test_does_not_follow_symlink(self):
        with tempfile.TemporaryDirectory() as outside:
            p = Path(outside) / "payload.py"
            p.write_text("PRIVATE_OUTSIDE")
            try:
                (self.root / "link.py").symlink_to(p)
            except OSError:
                self.skipTest("Host cannot create symlinks")
            inventory = collect(self.root)
            self.assertFalse(inventory.files)
            self.assertTrue(inventory.skipped)

    def test_dependency_hooks_and_mutable_sources(self):
        self.write(
            "package.json",
            json.dumps(
                {
                    "scripts": {"postinstall": "SECRET_COMMAND"},
                    "dependencies": {"example": "latest"},
                }
            ),
        )
        report = audit_dependencies(collect(self.root))
        rules = {f["rule"] for f in report["findings"]}
        self.assertIn("install-hook", rules)
        self.assertIn("unpinned-dependency", rules)
        self.assertNotIn("SECRET_COMMAND", json.dumps(report))

    def test_malformed_manifest_is_not_a_pass(self):
        self.write("package.json", "{broken")
        report = audit_dependencies(collect(self.root))
        self.assertTrue(any(f["rule"] == "invalid-manifest" for f in report["findings"]))
        self.assertNotEqual(report["result"], "PASS")

    def test_mcp_remote_and_shell_authority_without_values(self):
        self.write(
            "mcp.json",
            json.dumps(
                {
                    "mcpServers": {
                        "demo": {
                            "url": "https://host.example/private?key=SECRET",
                            "headers": {"Authorization": "PRIVATE_BEARER"},
                        },
                        "local": {"command": "bash", "args": ["-c", "SECRET_SCRIPT"]},
                    }
                }
            ),
        )
        report = audit_mcp(collect(self.root))
        rules = {f["rule"] for f in report["findings"]}
        self.assertIn("remote-mcp", rules)
        self.assertIn("shell-launch", rules)
        self.assertNotIn("PRIVATE_BEARER", json.dumps(report))
        self.assertNotIn("SECRET_SCRIPT", json.dumps(report))

    def test_exposure_is_a_review_lead(self):
        self.write("app.py", "value = eval(user_input)")
        report = audit_exposure(collect(self.root))
        self.assertEqual(report["findings"][0]["confidence"], "review-lead")

    def test_compact_retains_total_coverage_and_unknowns(self):
        self.write("app.py", "eval(x)\neval(y)\neval(z)")
        report = audit_exposure(collect(self.root))
        summary = compact(report, 1)
        self.assertEqual(summary["finding_count"], 3)
        self.assertEqual(len(summary["findings"]), 1)
        self.assertEqual(summary["omitted_findings"], 2)
        self.assertEqual(summary["coverage"], report["coverage"])
        self.assertEqual(summary["limitations"], report["limitations"])

    def test_stable_finding_identifiers(self):
        self.write("a.py", "requests.post(url)")
        self.assertEqual(audit_egress(collect(self.root)), audit_egress(collect(self.root)))

    def test_binary_reads_are_counted_even_when_not_admitted(self):
        (self.root / "binary").write_bytes(b"\xff\x00")
        inventory = collect(self.root)
        self.assertEqual(inventory.coverage()["bytes_read"], 2)
        self.assertEqual(inventory.coverage()["text_bytes_admitted"], 0)

    def test_credential_directories_are_excluded(self):
        self.write(".aws/credentials", "SYNTHETIC_PRIVATE")
        inventory = collect(self.root)
        self.assertFalse(inventory.files)
        self.assertTrue(inventory.skipped)
