"""Discoverable JSON shape contracts; semantic references are checked by assurance.py."""

from typing import Any

ID = {"type": "string", "pattern": "^[A-Za-z][A-Za-z0-9_-]{0,63}$"}
IDS = {"type": "array", "items": ID, "maxItems": 100, "uniqueItems": True}
FIELDS = {
    "type": "object",
    "minProperties": 1,
    "maxProperties": 16,
    "propertyNames": ID,
    "additionalProperties": {"type": "string", "maxLength": 256},
}


def obj(fields: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": fields,
        "required": list(fields),
        "additionalProperties": False,
    }


def array(item: dict[str, Any], maximum: int = 100, minimum: int = 0) -> dict[str, Any]:
    return {"type": "array", "items": item, "minItems": minimum, "maxItems": maximum}


def record(name: str, fields: dict[str, Any]) -> dict[str, Any]:
    return obj({"schema": {"const": f"security-agent-skills/{name}-v1"}, **fields})


CONTRACTS = {
    "attack-path": record(
        "attack-path",
        {
            "nodes": {**IDS, "minItems": 1},
            "entries": {**IDS, "minItems": 1},
            "assets": {**IDS, "minItems": 1},
            "edges": array(
                obj(
                    {
                        "id": ID,
                        "from": ID,
                        "to": ID,
                        "state": {"enum": ["open", "blocked", "unknown"]},
                        "evidence": IDS,
                    }
                ),
                200,
            ),
        },
    ),
    "detection-replay": record(
        "detection-replay",
        {
            "rules": array(obj({"id": ID, "equals": FIELDS}), 32, 1),
            "events": array(obj({"id": ID, "fields": FIELDS, "expected": IDS}), 100, 1),
        },
    ),
    "regression-board": record(
        "regression-board",
        {
            "cases": array(
                obj(
                    {
                        "id": ID,
                        "expected": IDS,
                        "baseline": IDS,
                        "candidate": IDS,
                        "baseline_status": {"enum": ["complete", "partial", "blocked"]},
                        "candidate_status": {"enum": ["complete", "partial", "blocked"]},
                    }
                ),
                100,
                1,
            ),
        },
    ),
    "skill-route": record(
        "skill-route",
        {
            "goals": {**IDS, "minItems": 1},
            "max_skills": {"type": "integer", "minimum": 1, "maximum": 24},
        },
    ),
}
