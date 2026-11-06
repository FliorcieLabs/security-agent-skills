import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from security_agent_skills.cli import main
from security_agent_skills.reports import finding, report


class CliTests(unittest.TestCase):
    def call(self, args):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            code = main(args)
        return code, json.loads(stream.getvalue())

    def test_partial_exit_full_output_and_bounded_console(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "target"
            target.mkdir()
            (target / "app.py").write_text("eval(a)\neval(b)")
            output = Path(directory) / "evidence.json"
            code, value = self.call(
                ["exposure", str(target), "--max-findings", "1", "--output", str(output)]
            )
            self.assertEqual(code, 3)
            self.assertEqual(value["finding_count"], 2)
            self.assertEqual(value["omitted_findings"], 1)
            self.assertEqual(len(json.loads(output.read_text())["findings"]), 2)
            code, _ = self.call(["exposure", str(target), "--output", str(output)])
            self.assertEqual(code, 2)

    def test_errors_do_not_echo_untrusted_input(self):
        code, value = self.call(["routes", "PRIVATE_TOKEN_NOT_A_FILE"])
        self.assertEqual(code, 2)
        self.assertNotIn("PRIVATE_TOKEN_NOT_A_FILE", json.dumps(value))

    def test_duplicate_leads_keep_unique_ids_and_occurrences(self):
        lead = finding("same", "a.py", 1, "Inspect")
        value = report("test", "synthetic", [lead, lead], {}, [])
        self.assertEqual(value["finding_count"], 1)
        self.assertEqual(value["findings"][0]["occurrences"], 2)

    def test_invalid_json_does_not_echo_credential_text(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "invalid.json"
            source.write_text("{PRIVATE_CREDENTIAL:")
            code, value = self.call(["routes", str(source)])
            self.assertEqual(code, 2)
            self.assertNotIn("PRIVATE_CREDENTIAL", json.dumps(value))

    def test_static_review_does_not_execute_target_code(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            marker = root / "executed"
            (root / "payload.py").write_text(
                "from pathlib import Path\nPath(" + repr(str(marker)) + ").write_text('bad')"
            )
            code, value = self.call(["egress", str(root)])
            self.assertEqual(code, 3)
            self.assertFalse(marker.exists())

    def test_markdown_escapes_terminal_control_characters_in_paths(self):
        from security_agent_skills.reports import markdown

        value = report(
            "test", "synthetic", [finding("review", "\x1b[31m`file.py", 1, "Inspect")], {}, []
        )
        rendered = markdown(value)
        self.assertNotIn("\x1b", rendered)
        self.assertIn("\\x1b", rendered)
