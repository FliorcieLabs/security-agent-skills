"""Explicit local CLI. Static outcomes never silently become clean passes."""

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

from .assurance import ASSURANCE
from .audits import audit_dependencies, audit_egress, audit_exposure, audit_mcp
from .boundaries import grade_injection, injection_cases, map_routes
from .evidence import pack_reports, verify_pack
from .extended_audits import (
    audit_ci,
    audit_containers,
    audit_infrastructure,
    audit_instructions,
    audit_llm,
)
from .header_records import HEADER_RECORDS
from .internal_operations import OPERATIONS
from .inventory import collect, reparse
from .plans import appsec_plan, sandbox_plan
from .reports import SCHEMA, compact, markdown, report
from .sentinel import compare_snapshots, snapshot

EXIT_CODES = {"PASS": 0, "FIX": 1, "BLOCKED": 2, "PARTIAL": 3}


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("Duplicate JSON object key")
        value[key] = item
    return value


def read_json(path: str, *, unique_keys: bool = False) -> Any:
    source = Path(path)
    if not source.is_file() or reparse(source) or source.stat().st_size > 8_000_000:
        raise ValueError("JSON input must be a bounded regular non-link file")
    with source.open("rb") as stream:
        raw = stream.read(8_000_001)
    if len(raw) > 8_000_000:
        raise ValueError("JSON input byte limit")
    return json.loads(raw, object_pairs_hook=_unique_object if unique_keys else None)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Local security workflows. No target code execution, telemetry, or network calls."
    )
    subs = result.add_subparsers(dest="command", required=True)
    for name in [
        "egress",
        "dependencies",
        "mcp",
        "exposure",
        "instructions",
        "ci",
        "containers",
        "iac",
        "llm-data",
        "snapshot",
        "compare",
        "appsec-plan",
        "injection-lab",
        "routes",
        "sandbox-plan",
        "pack",
        "verify",
        *OPERATIONS,
        *ASSURANCE,
        *HEADER_RECORDS,
    ]:
        sub = subs.add_parser(name)
        sub.add_argument(
            "--output", help="Write the full JSON result to a new file; never overwrite"
        )
        sub.add_argument("--format", choices=["json", "markdown"], default="json")
        sub.add_argument(
            "--max-findings",
            type=int,
            default=20,
            help="Bound console findings only; total counts and coverage remain visible",
        )
        if name in {
            "egress",
            "dependencies",
            "mcp",
            "exposure",
            "snapshot",
            "instructions",
            "ci",
            "containers",
            "iac",
            "llm-data",
        }:
            sub.add_argument("target")
            sub.add_argument("--max-files", type=int, default=10000)
            sub.add_argument("--max-file-bytes", type=int, default=1_000_000)
        elif name == "compare":
            sub.add_argument("before")
            sub.add_argument("after")
        elif name == "appsec-plan":
            sub.add_argument("scope")
        elif name == "injection-lab":
            sub.add_argument("--responses")
        elif name == "routes":
            sub.add_argument("trace")
        elif name == "sandbox-plan":
            sub.add_argument("target")
            sub.add_argument("--image", required=True)
            sub.add_argument(
                "--command-json",
                required=True,
                help="JSON argv array; it is never executed by this helper",
            )
        elif name == "pack":
            sub.add_argument("reports", nargs="+")
            sub.add_argument("--archive", required=True)
        elif name == "verify":
            sub.add_argument("archive")
        elif name in {*OPERATIONS, *ASSURANCE, *HEADER_RECORDS}:
            sub.add_argument("record", help="Bounded local JSON operation record, never executed")
    return result


def dispatch(args: argparse.Namespace) -> dict[str, Any] | list[dict[str, Any]]:
    if args.command in HEADER_RECORDS:
        return HEADER_RECORDS[args.command](read_json(args.record, unique_keys=True))
    if args.command in ASSURANCE:
        return ASSURANCE[args.command](read_json(args.record, unique_keys=True))
    if args.command in OPERATIONS:
        return OPERATIONS[args.command](read_json(args.record, unique_keys=True))
    audits = {
        "egress": audit_egress,
        "dependencies": audit_dependencies,
        "mcp": audit_mcp,
        "exposure": audit_exposure,
        "instructions": audit_instructions,
        "ci": audit_ci,
        "containers": audit_containers,
        "iac": audit_infrastructure,
        "llm-data": audit_llm,
    }
    if args.command in {*audits, "snapshot"}:
        inventory = collect(args.target, max_files=args.max_files, max_bytes=args.max_file_bytes)
        return (
            snapshot(inventory) if args.command == "snapshot" else audits[args.command](inventory)
        )
    if args.command == "compare":
        return compare_snapshots(read_json(args.before), read_json(args.after))
    if args.command == "appsec-plan":
        return appsec_plan(read_json(args.scope))
    if args.command == "injection-lab":
        return grade_injection(read_json(args.responses)) if args.responses else injection_cases()
    if args.command == "routes":
        return map_routes(read_json(args.trace))
    if args.command == "sandbox-plan":
        return sandbox_plan(args.target, args.image, json.loads(args.command_json))
    if args.command == "pack":
        return pack_reports([Path(p) for p in args.reports], Path(args.archive))
    return verify_pack(Path(args.archive))


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.max_findings < 0:
            raise ValueError("Finding limit must be nonnegative")
        value = dispatch(args)
        if args.output:
            with Path(args.output).open("x", encoding="utf-8") as stream:
                json.dump(value, stream, sort_keys=True, indent=2, ensure_ascii=True)
                stream.write("\n")
        if isinstance(value, dict) and value.get("schema") == SCHEMA:
            shown = compact(value, args.max_findings)
            text = (
                markdown(shown)
                if args.format == "markdown"
                else json.dumps(shown, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
                + "\n"
            )
            code = EXIT_CODES[value["result"]]
        else:
            text = (
                json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
            )
            code = 0
        sys.stdout.write(text)
        return code
    except (
        OSError,
        ValueError,
        TypeError,
        KeyError,
        AttributeError,
        RecursionError,
        zipfile.BadZipFile,
    ) as exc:
        # Do not echo untrusted filenames, command arguments, JSON fragments, or credential values.
        blocked = report(
            args.command,
            "requested local operation",
            [],
            {"runtime_observed": False},
            [
                "Operation could not complete: "
                + type(exc).__name__
                + ". Check paths, schema, permissions, and output collisions locally."
            ],
            result="BLOCKED",
        )
        sys.stdout.write(json.dumps(blocked, separators=(",", ":")) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
