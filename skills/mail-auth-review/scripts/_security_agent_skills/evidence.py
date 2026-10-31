"""Reproducible local report archives. Hash checks are not signatures."""

import json
import re
import zipfile
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any

from .inventory import reparse
from .reports import SCHEMA, report

PACK_SCHEMA = "security-agent-skills/evidence-pack-v1"
MAX_BYTES = 16_000_000
MAX_REPORTS = 100


def scrub(value: Any) -> Any:
    if isinstance(value, str):
        return re.sub(
            r"(?:gh[pousr]_[A-Za-z0-9_]{15,}|sk-[A-Za-z0-9_-]{15,}|Bearer\s+[A-Za-z0-9._~+/-]+)",
            "[REDACTED]",
            value,
        )
    if isinstance(value, list):
        return [scrub(item) for item in value]
    if isinstance(value, dict):
        return {
            key: (
                "[REDACTED]"
                if re.search(r"password|secret|token|api[_-]?key|authorization", key, re.I)
                else scrub(item)
            )
            for key, item in value.items()
        }
    return value


def export_report(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        raise ValueError("Only suite report-v1 documents can be packed")
    required = {
        "schema",
        "workflow",
        "result",
        "scope",
        "finding_count",
        "findings",
        "coverage",
        "limitations",
    }
    if not required <= value.keys() or value["result"] not in {"PASS", "FIX", "PARTIAL", "BLOCKED"}:
        raise ValueError("Incomplete suite report")
    if not isinstance(value["findings"], list) or not isinstance(value["limitations"], list):
        raise ValueError("Invalid report lists")
    count = value["finding_count"]
    if type(count) is not int or count < len(value["findings"]):
        raise ValueError("Inconsistent report finding count")
    omitted = count - len(value["findings"])
    if omitted and value.get("omitted_findings") != omitted:
        raise ValueError("Incomplete reports must retain the omitted count")
    result = {key: value[key] for key in required}
    if "omitted_findings" in value:
        result["omitted_findings"] = value["omitted_findings"]
    result["scope"] = "Local path omitted from export"
    result["details"] = {"omitted": "Local arguments and freeform details excluded from export"}
    return scrub(result)


def pack_reports(sources: list[Path], output: Path) -> dict[str, Any]:
    if not sources or len(sources) > MAX_REPORTS:
        raise ValueError("Select 1 to 100 suite reports")
    payloads = {}
    entries = []
    total = 0
    for i, source in enumerate(sources):
        source = Path(source)
        if reparse(source) or not source.is_file() or source.stat().st_size > MAX_BYTES:
            raise ValueError("Report input must be a bounded regular non-link file")
        with source.open("rb") as stream:
            raw = stream.read(MAX_BYTES + 1)
        total += len(raw)
        if total > MAX_BYTES:
            raise ValueError("Report input byte limit exceeded")
        value = export_report(json.loads(raw))
        packed = json.dumps(
            value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
        ).encode()
        name = f"reports/{i:04d}.json"
        payloads[name] = packed
        entries.append(
            {
                "path": name,
                "sha256": sha256(packed).hexdigest(),
                "source_sha256": sha256(raw).hexdigest(),
            }
        )
    manifest: dict[str, Any] = {
        "schema": PACK_SCHEMA,
        "entries": entries,
        "limitations": [
            "Local hashes do not establish external truth or authenticity.",
            "Redaction is best-effort pattern scrubbing. Inspect the archive before sharing.",
        ],
    }
    payloads["manifest.json"] = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode()
    with Path(output).open("xb") as stream:
        with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for name, raw in sorted(payloads.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, raw)
    return report(
        "security-evidence-pack",
        "selected local suite reports",
        [],
        {"reports_packed": len(entries), "runtime_observed": False},
        manifest["limitations"],
        result="PASS",
        details={"archive_sha256": sha256(Path(output).read_bytes()).hexdigest()},
    )


def verify_pack(source: Path) -> dict[str, Any]:
    if reparse(Path(source)) or Path(source).stat().st_size > MAX_BYTES:
        raise ValueError("Archive must be a bounded non-link file")
    with zipfile.ZipFile(source) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if (
            len(infos) > MAX_REPORTS + 1
            or sum(i.file_size for i in infos) > MAX_BYTES
            or len(names) != len(set(names))
        ):
            raise ValueError("Archive inventory limit or duplicate entry")
        for info in infos:
            if info.flag_bits & 1:
                raise ValueError("Encrypted entries are unsupported")
            name = info.filename
            if (
                PurePosixPath(name).is_absolute()
                or ".." in PurePosixPath(name).parts
                or "\\" in name
                or ":" in name
                or (info.external_attr >> 16) & 0o170000 == 0o120000
            ):
                raise ValueError("Unsafe archive entry")
        manifest = json.loads(archive.read("manifest.json"))
        if manifest.get("schema") != PACK_SCHEMA or not isinstance(manifest.get("entries"), list):
            raise ValueError("Invalid pack manifest")
        entries = manifest["entries"]
        if any(
            not isinstance(e, dict)
            or not isinstance(e.get("path"), str)
            or not re.fullmatch(r"[a-f0-9]{64}", str(e.get("sha256", "")))
            for e in entries
        ):
            raise ValueError("Invalid manifest entry")
        expected = [e["path"] for e in entries]
        if (
            len(set(expected)) != len(expected)
            or set(names) != {"manifest.json", *expected}
            or any(not re.fullmatch(r"reports/\d{4}\.json", n) for n in expected)
        ):
            raise ValueError("Manifest does not exactly account for archive members")
        for entry in entries:
            raw = archive.read(entry["path"])
            if sha256(raw).hexdigest() != entry["sha256"]:
                raise ValueError("Report integrity mismatch")
            export_report(json.loads(raw))
    return report(
        "security-evidence-pack",
        "local archive verification",
        [],
        {"reports_verified": len(entries), "runtime_observed": False},
        [
            "Only internal archive integrity was checked. A rewritten archive and manifest can remain self-consistent."
        ],
        result="PASS",
    )
