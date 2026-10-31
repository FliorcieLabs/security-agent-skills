"""Content snapshots and capability deltas; snapshots are not attestations."""

import re
from pathlib import PurePosixPath
from typing import Any

from .audits import capabilities
from .inventory import Inventory
from .reports import finding, report

SNAPSHOT_SCHEMA = "security-agent-skills/snapshot-v1"


def snapshot(inventory: Inventory) -> dict[str, Any]:
    return {
        "schema": SNAPSHOT_SCHEMA,
        "files": [
            {"path": f.path, "sha256": f.sha256, "capabilities": capabilities(f.text)}
            for f in inventory.files
        ],
        "coverage": inventory.coverage(),
    }


def validate_snapshot(value: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if (
        not isinstance(value, dict)
        or value.get("schema") != SNAPSHOT_SCHEMA
        or not isinstance(value.get("files"), list)
    ):
        raise ValueError("Unsupported snapshot schema")
    if len(value["files"]) > 10000:
        raise ValueError("Snapshot exceeds file limit")
    result = {}
    for entry in value["files"]:
        if not isinstance(entry, dict):
            raise ValueError("Invalid snapshot entry")
        path = entry.get("path")
        if (
            not isinstance(path, str)
            or not path
            or "\\" in path
            or ":" in path
            or any(ord(c) < 32 for c in path)
            or PurePosixPath(path).is_absolute()
            or ".." in PurePosixPath(path).parts
            or path in result
        ):
            raise ValueError("Unsafe or duplicate snapshot path")
        if not re.fullmatch(r"[a-f0-9]{64}", str(entry.get("sha256", ""))):
            raise ValueError("Invalid file digest")
        caps = entry.get("capabilities")
        if not isinstance(caps, list) or any(
            not isinstance(c, str)
            or c
            not in {
                "outbound-client",
                "tracking-indicator",
                "sensitive-source",
                "execution-hook",
                "external-resource",
            }
            for c in caps
        ):
            raise ValueError("Unknown capability")
        result[path] = entry
    return result


def compare_snapshots(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    old = validate_snapshot(before)
    new = validate_snapshot(after)
    findings = []
    for path in sorted(set(old) | set(new)):
        if path not in old:
            findings.append(finding("file-added", path, 1, "New package file requires review."))
        elif path not in new:
            findings.append(finding("file-removed", path, 1, "Previously observed file is absent."))
        elif old[path]["sha256"] != new[path]["sha256"]:
            findings.append(
                finding(
                    "file-changed", path, 1, "File content digest changed; inspect the local diff."
                )
            )
        if path in new:
            prior = set(old.get(path, {}).get("capabilities", []))
            if set(new[path]["capabilities"]) - prior:
                findings.append(
                    finding(
                        "new-capability",
                        path,
                        1,
                        "New static capability indicators require review before upgrade.",
                    )
                )
    return report(
        "agent-package-change-sentinel",
        "two supplied snapshots",
        findings,
        {
            "baseline_files": len(old),
            "candidate_files": len(new),
            "runtime_observed": False,
            "baseline_coverage": before.get("coverage", {}),
            "candidate_coverage": after.get("coverage", {}),
        },
        [
            "Snapshots are caller-supplied local observations, not signed upstream provenance.",
            "Capability detection is incomplete. An unchanged snapshot does not establish safety.",
        ],
    )
