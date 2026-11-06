"""Reproduce local synthetic metrics. Never executes a reference repository or calls a model."""

import json
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from security_agent_skills.assurance import detection_replay, regression_board, skill_route


def benchmark():
    # These are independently authored fixtures and a deliberately broad toy baseline.
    # Neither the baseline nor its outputs represent another project's implementation.
    fixtures = [
        ("deniedWrite", {"effect": "write", "approved": "false"}, True),
        ("allowedWrite", {"effect": "write", "approved": "true"}, False),
        ("deniedRead", {"effect": "read", "approved": "false"}, False),
        ("allowedRead", {"effect": "read", "approved": "true"}, False),
        ("misleadingNote", {"effect": "read", "note": "write false"}, False),
        ("approvedNote", {"effect": "write", "approved": "true", "note": "false"}, False),
        ("missingField", {"effect": "write", "note": "false"}, False),
        ("schemaDrift", {"effect": "write", "approval": "false"}, True),
    ]
    record = {
        "schema": "security-agent-skills/detection-replay-v1",
        "rules": [{"id": "deniedWriteRule", "equals": {"effect": "write", "approved": "false"}}],
        "events": [
            {"id": name, "fields": fields, "expected": ["deniedWriteRule"] if expected else []}
            for name, fields, expected in fixtures
        ],
    }
    replay = detection_replay(record)
    outputs = {event["event"]: event["observed"] for event in replay["details"]["events"]}
    cases = []
    for name, fields, expected in fixtures:
        raw = json.dumps(fields)
        baseline = ["deniedWriteRule"] if "write" in raw and "false" in raw else []
        cases.append(
            {
                "id": name,
                "expected": ["deniedWriteRule"] if expected else [],
                "baseline": baseline,
                "candidate": outputs[name],
                "baseline_status": "complete",
                "candidate_status": "complete",
            }
        )
    board = regression_board(
        {"schema": "security-agent-skills/regression-board-v1", "cases": cases}
    )
    metrics = board["details"]["metrics"]
    assert (metrics["baseline"]["tp"], metrics["baseline"]["fp"], metrics["baseline"]["fn"]) == (
        2,
        3,
        0,
    )
    assert (metrics["candidate"]["tp"], metrics["candidate"]["fp"], metrics["candidate"]["fn"]) == (
        1,
        0,
        1,
    )
    selection = skill_route(
        {
            "schema": "security-agent-skills/skill-route-v1",
            "goals": ["agent_egress", "instruction_trust", "mcp_authority"],
            "max_skills": 3,
        }
    )["details"]
    catalog = json.loads((ROOT / "catalog.json").read_text())
    all_bytes = sum(
        (ROOT / "skills" / entry["name"] / "SKILL.md").stat().st_size for entry in catalog
    )
    selected_bytes = sum((ROOT / path).stat().st_size for path in selection["load_references"])
    return {
        "result": "PASS",
        "scope": "synthetic metric arithmetic and selected SKILL.md byte counts",
        "fixture_sha256": sha256(json.dumps(record, sort_keys=True).encode()).hexdigest(),
        "fixture_count": len(fixtures),
        "metrics": metrics,
        "routing": {
            "catalog_entries": len(catalog),
            "selected_entries": selection["selected_count"],
            "all_entrypoint_bytes": all_bytes,
            "selected_entrypoint_bytes": selected_bytes,
            "entrypoint_byte_reduction_percent": round(100 * (1 - selected_bytes / all_bytes), 2),
        },
        "limits": [
            "Toy baseline authored here; no competitor or model run was measured.",
            "Precision improves but recall worsens on schema drift; there is no overall dominance.",
            "Selected document bytes are not tokens, assistant context, latency, or billing.",
            "Benchmarks do not establish real-world coverage or host compatibility.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(benchmark(), indent=2, sort_keys=True))
