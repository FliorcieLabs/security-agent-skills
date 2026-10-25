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
print("Installed-package offline smoke: PASS")
