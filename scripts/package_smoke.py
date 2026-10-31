"""Install a locally built wheel offline into a temporary environment."""

import json
import subprocess
import sys
import tempfile
import venv
from pathlib import Path

root = Path(__file__).resolve().parents[1]
wheels = list((root / "dist").glob("*.whl"))
if len(wheels) != 1:
    raise SystemExit("Build exactly one wheel before smoke checking")
with tempfile.TemporaryDirectory() as temporary:
    env = Path(temporary) / "env"
    venv.EnvBuilder(with_pip=True).create(env)
    python = env / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    subprocess.run(
        [str(python), "-m", "pip", "install", "--no-index", "--no-deps", str(wheels[0])], check=True
    )
    subprocess.run(
        [str(python), "-m", "security_agent_skills.cli", "--help"], cwd=temporary, check=True
    )
    fixture = Path(temporary) / "fixture"
    fixture.mkdir()
    (fixture / "app.py").write_text("requests.post(url)")
    result = subprocess.run(
        [str(python), "-m", "security_agent_skills.cli", "egress", str(fixture)],
        cwd=temporary,
        capture_output=True,
        text=True,
        check=False,
    )
    value = json.loads(result.stdout)
    assert result.returncode == 3 and value["finding_count"] == 1 and value["result"] == "PARTIAL"
    record = Path(temporary) / "preflight.json"
    record.write_bytes((root / "examples/internal-operations/preflight.json").read_bytes())
    result = subprocess.run(
        [str(python), "-m", "security_agent_skills.cli", "preflight", str(record)],
        cwd=temporary,
        capture_output=True,
        text=True,
        check=False,
    )
    value = json.loads(result.stdout)
    assert result.returncode == 3 and value["result"] == "PARTIAL"
    assert value["details"]["authorization_granted"] is False
    # Exercise the installed MCP entrypoint from outside the source tree, offline.
    messages = [
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-11-25",
                "capabilities": {},
                "clientInfo": {"name": "offline-wheel-smoke", "version": "1"},
            },
        },
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
    ]
    for position, command in enumerate(
        ["attack-path", "detection-replay", "regression-board", "skill-route"], 3
    ):
        doc = json.loads((root / "examples/assurance" / (command + ".json")).read_text())
        messages.append(
            {
                "jsonrpc": "2.0",
                "id": position,
                "method": "tools/call",
                "params": {"name": command.replace("-", "_"), "arguments": {"record": doc}},
            }
        )
    entrypoint = env / (
        "Scripts/security-agent-skills-mcp.exe"
        if sys.platform == "win32"
        else "bin/security-agent-skills-mcp"
    )
    result = subprocess.run(
        [str(entrypoint)],
        cwd=temporary,
        input="\n".join(map(json.dumps, messages)) + "\n",
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    assert not result.stderr
    replies = [json.loads(line) for line in result.stdout.splitlines()]
    assert len(replies) == 6 and len(replies[1]["result"]["tools"]) == 4
    for reply in replies[2:]:
        assert reply["result"]["structuredContent"]["result"] == "PARTIAL"
        assert reply["result"]["structuredContent"]["details"]["executed"] is False
print("Installed-package offline smoke: PASS")
