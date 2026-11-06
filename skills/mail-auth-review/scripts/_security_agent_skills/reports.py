"""One deterministic report contract for every workflow."""

from copy import deepcopy
from hashlib import sha256
from typing import Any

SCHEMA = "security-agent-skills/report-v1"


def finding(
    rule: str, path: str, line: int, message: str, severity: str = "review"
) -> dict[str, Any]:
    identity = f"{rule}:{path}:{line}".encode()
    return {
        "id": sha256(identity).hexdigest()[:16],
        "rule": rule,
        "path": path,
        "line": line,
        "severity": severity,
        "confidence": "review-lead",
        "message": message,
    }


def report(
    kind: str,
    scope: str,
    findings: list[dict[str, Any]],
    coverage: dict[str, Any],
    limitations: list[str],
    *,
    result: str = "PARTIAL",
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    unique: dict[str, dict[str, Any]] = {}
    for item in findings:
        if item["id"] in unique:
            previous = unique[item["id"]]
            previous["occurrences"] = previous.get("occurrences", 1) + 1
        else:
            unique[item["id"]] = dict(item)
    ordered = sorted(unique.values(), key=lambda f: (f["path"], f["line"], f["rule"]))
    return {
        "schema": SCHEMA,
        "workflow": kind,
        "result": result,
        "scope": scope,
        "finding_count": len(ordered),
        "findings": ordered,
        "coverage": coverage,
        "limitations": limitations,
        "details": details or {},
    }


def compact(value: dict[str, Any], limit: int) -> dict[str, Any]:
    if limit < 0:
        raise ValueError("Finding limit must be nonnegative")
    result = deepcopy(value)
    result["findings"] = result["findings"][:limit]
    result["omitted_findings"] = value["finding_count"] - len(result["findings"])
    return result


def markdown(value: dict[str, Any]) -> str:
    rows = [
        f"Result: {value['result']}",
        f"Workflow: {value['workflow']}",
        f"Findings: {value['finding_count']} (omitted: {value.get('omitted_findings', 0)})",
        "",
    ]
    for item in value["findings"]:
        path = str(item["path"]).encode("unicode_escape").decode("ascii").replace("`", "\\x60")
        rows.append(f"- {item['id']} {item['rule']} at `{path}:{item['line']}`: {item['message']}")
    rows.extend(["", "Limits:", *[f"- {text}" for text in value["limitations"]]])
    import json

    rows.extend(["", "Coverage: " + json.dumps(value["coverage"], sort_keys=True)])
    return "\n".join(rows) + "\n"
