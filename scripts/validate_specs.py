"""Check bounded portfolio traceability without repository-specific paths."""

import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
catalog = json.loads((root / "catalog.json").read_text())
trace = (root / ".specs/01-requirements/traceability.md").read_text(encoding="utf-8")
missing = [item["name"] for item in catalog if item["name"] not in trace]
for i in range(1, 29):
    if f"SEC-{i:03d}" not in trace:
        missing.append(f"SEC-{i:03d}")
print(json.dumps({"result": "FIX" if missing else "PASS", "requirements": 28, "missing": missing}))
raise SystemExit(bool(missing))
