import io
import json
import os
import subprocess
import sys
import unittest

from security_agent_skills.assurance import ASSURANCE
from security_agent_skills.mcp_stdio import MAX_MESSAGE_BYTES, Session, serve
from tests.test_assurance import ROOT, example


def request(method, params=None, identity=1):
    return {"jsonrpc": "2.0", "id": identity, "method": method, "params": params or {}}


def initialize(session):
    value = session.handle(
        request(
            "initialize",
            {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "test", "version": "1"},
            },
        )
    )
    session.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
    return value


class McpStdioTests(unittest.TestCase):
    def test_request_metadata_is_accepted_without_affecting_record_authority(self):
        session = Session()
        initialize(session)
        value = session.handle(request("tools/list", {"_meta": {"progressToken": "fixture"}}))
        self.assertEqual(len(value["result"]["tools"]), 4)
        value = session.handle(
            request(
                "tools/call",
                {
                    "name": "skill_route",
                    "arguments": {"record": example("skill-route")},
                    "_meta": {"private": "SYNTHETIC_METADATA"},
                },
            )
        )
        self.assertNotIn("SYNTHETIC_METADATA", json.dumps(value))
        self.assertFalse(value["result"]["structuredContent"]["details"]["authorization_granted"])
        self.assertIn("error", session.handle(request("tools/list", {"_meta": "bad"})))

    def test_lifecycle_tool_schema_and_record_equivalence(self):
        session = Session()
        self.assertIn("error", session.handle(request("tools/list")))
        init = initialize(session)
        self.assertEqual(init["result"]["protocolVersion"], "2025-11-25")
        listed = session.handle(request("tools/list"))["result"]["tools"]
        self.assertEqual(len(listed), 4)
        for name, operation in ASSURANCE.items():
            value = session.handle(
                request(
                    "tools/call",
                    {"name": name.replace("-", "_"), "arguments": {"record": example(name)}},
                )
            )
            self.assertEqual(value["result"]["structuredContent"], operation(example(name)))
            self.assertFalse(value["result"]["isError"])

    def test_no_tool_notification_execution_or_uninitialized_calls(self):
        session = Session()
        self.assertIn("error", session.handle(request("tools/call")))
        self.assertIsNone(
            session.handle(
                {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "skill_route"}}
            )
        )
        initialize(session)
        self.assertIn("error", session.handle(request("initialize")))
        self.assertIn("error", session.handle(request("resources/read")))

    def test_unknown_tools_bad_parameters_and_no_echo(self):
        session = Session()
        initialize(session)
        for params in (
            {"name": "shell", "arguments": {"command": "private-secret"}},
            {"name": "skill_route", "arguments": {"path": "private-secret"}},
        ):
            value = session.handle(request("tools/call", params))
            self.assertIn("error", value)
            self.assertNotIn("private-secret", json.dumps(value))
        value = session.handle(
            request(
                "tools/call",
                {"name": "skill_route", "arguments": {"record": {"private-secret": "value"}}},
            )
        )
        self.assertTrue(value["result"]["isError"])
        self.assertNotIn("private-secret", json.dumps(value))

    def test_protocol_fallback_and_older_supported_version(self):
        for version, expected in (("unknown", "2025-11-25"), ("2025-06-18", "2025-06-18")):
            session = Session()
            value = session.handle(
                request(
                    "initialize",
                    {
                        "protocolVersion": version,
                        "capabilities": {},
                        "clientInfo": {"name": "test", "version": "1"},
                    },
                )
            )
            self.assertEqual(value["result"]["protocolVersion"], expected)

    def test_invalid_json_duplicate_keys_batches_and_nonfinite_numbers(self):
        for raw in (b"{bad}\n", b'{"x":1,"x":2}\n', b"[]\n", b'{"x":NaN}\n', b"\xff\n"):
            sink = io.BytesIO()
            self.assertEqual(serve(io.BytesIO(raw), sink), 0)
            self.assertIn("error", json.loads(sink.getvalue()))
        for identity in (True, [], 1.5):
            self.assertIn("error", Session().handle(request("ping", identity=identity)))

    def test_oversized_message_closes_session_without_echo(self):
        sink = io.BytesIO()
        self.assertEqual(serve(io.BytesIO(b"x" * (MAX_MESSAGE_BYTES + 1)), sink), 2)
        self.assertLess(len(sink.getvalue()), 200)

    def test_real_subprocess_uses_only_jsonrpc_stdout(self):
        messages = [
            request(
                "initialize",
                {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "fixture", "version": "1"},
                },
            ),
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            request("tools/list", identity=2),
            request(
                "tools/call",
                {"name": "skill_route", "arguments": {"record": example("skill-route")}},
                identity=3,
            ),
        ]
        environment = dict(os.environ, PYTHONPATH=str(ROOT / "src"), PYTHONUTF8="1")
        result = subprocess.run(
            [sys.executable, "-m", "security_agent_skills.mcp_stdio"],
            input="\n".join(map(json.dumps, messages)) + "\n",
            capture_output=True,
            text=True,
            cwd=ROOT.parent,
            env=environment,
            timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        replies = list(map(json.loads, result.stdout.splitlines()))
        self.assertEqual([reply["id"] for reply in replies], [1, 2, 3])
        self.assertEqual(replies[2]["result"]["structuredContent"]["result"], "PARTIAL")
