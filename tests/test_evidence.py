import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from security_agent_skills.evidence import pack_reports, verify_pack
from security_agent_skills.reports import report


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        self.source = self.root / "report.json"
        self.source.write_text(
            json.dumps(
                report(
                    "test",
                    "PRIVATE_LOCAL_PATH",
                    [],
                    {},
                    ["static only"],
                    details={"command": "PRIVATE_COMMAND"},
                )
            )
        )

    def test_reproducible_export_omits_machine_scope_and_command(self):
        a = self.root / "a.zip"
        b = self.root / "b.zip"
        pack_reports([self.source], a)
        pack_reports([self.source], b)
        self.assertEqual(a.read_bytes(), b.read_bytes())
        self.assertEqual(verify_pack(a)["result"], "PASS")
        with zipfile.ZipFile(a) as z:
            text = z.read("reports/0000.json").decode()
        self.assertNotIn("PRIVATE_LOCAL_PATH", text)
        self.assertNotIn("PRIVATE_COMMAND", text)

    def test_never_overwrites_export(self):
        target = self.root / "existing.zip"
        target.write_bytes(b"keep")
        with self.assertRaises(FileExistsError):
            pack_reports([self.source], target)
        self.assertEqual(target.read_bytes(), b"keep")

    def test_rejects_arbitrary_source_files(self):
        self.source.write_text('{"password":"PRIVATE"}')
        with self.assertRaises(ValueError):
            pack_reports([self.source], self.root / "bad.zip")

    def test_tampering_extra_entries_and_traversal_are_rejected(self):
        good = self.root / "good.zip"
        pack_reports([self.source], good)
        with zipfile.ZipFile(good) as original:
            files = {n: original.read(n) for n in original.namelist()}
        for name, payload in [
            ("reports/0000.json", b"tampered"),
            ("../escape", b"extra"),
            ("unexpected", b"extra"),
        ]:
            target = self.root / (str(len(name)) + name.replace("/", "_") + ".zip")
            modified = dict(files)
            modified[name] = payload
            with zipfile.ZipFile(target, "w") as z:
                for n, raw in modified.items():
                    z.writestr(n, raw)
            with self.assertRaises(ValueError):
                verify_pack(target)
