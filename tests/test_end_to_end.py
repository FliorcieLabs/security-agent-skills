"""Exercise every workflow through the user-facing CLI with synthetic inputs."""

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from security_agent_skills.cli import main


class EndToEndTests(unittest.TestCase):
    def test_all_workflows_are_local_and_keep_the_report_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "package"
            target.mkdir()
            (target / "app.py").write_text("value = eval(user_input)\nrequests.post(url)")
            (target / "package.json").write_text('{"dependencies":{"demo":"latest"}}')
            (target / "mcp.json").write_text(
                '{"mcpServers":{"demo":{"url":"https://example.invalid"}}}'
            )

            def call(arguments, expected):
                out = io.StringIO()
                with contextlib.redirect_stdout(out):
                    code = main(arguments)
                self.assertEqual(code, expected, out.getvalue())
                return json.loads(out.getvalue())

            with (
                patch("socket.create_connection", side_effect=AssertionError("Unexpected network")),
                patch("subprocess.run", side_effect=AssertionError("Unexpected process execution")),
            ):
                report_path = root / "report.json"
                for command in ["egress", "dependencies", "mcp", "exposure"]:
                    args = [command, str(target)]
                    if command == "egress":
                        args += ["--output", str(report_path)]
                    value = call(args, 3)
                    self.assertEqual(value["schema"], "security-agent-skills/report-v1")
                    self.assertFalse(value["coverage"]["runtime_observed"])
                baseline = root / "baseline.json"
                candidate = root / "candidate.json"
                call(["snapshot", str(target), "--output", str(baseline)], 0)
                (target / "app.py").write_text("fetch(url)")
                call(["snapshot", str(target), "--output", str(candidate)], 0)
                call(["compare", str(baseline), str(candidate)], 3)
                scope = root / "scope.json"
                scope.write_text('{"authorized":false}')
                call(["appsec-plan", str(scope)], 2)
                cases = call(["injection-lab"], 0)
                responses = root / "responses.json"
                responses.write_text(
                    json.dumps(
                        [
                            {
                                "case_id": c["id"],
                                "tool_calls": [],
                                "output": "Ignored untrusted directions",
                            }
                            for c in cases
                        ]
                    )
                )
                call(["injection-lab", "--responses", str(responses)], 0)
                trace = root / "trace.json"
                trace.write_text(
                    '[{"canary":"SYNTHETIC_TEST","source":"fixture","sink":"https://example.invalid"}]'
                )
                call(["routes", str(trace)], 3)
                plan = call(
                    [
                        "sandbox-plan",
                        str(target),
                        "--image",
                        "python@sha256:" + "a" * 64,
                        "--command-json",
                        '["python","--version"]',
                    ],
                    3,
                )
                self.assertFalse(plan["details"]["executed"])
                archive = root / "evidence.zip"
                call(["pack", str(report_path), "--archive", str(archive)], 0)
                call(["verify", str(archive)], 0)
