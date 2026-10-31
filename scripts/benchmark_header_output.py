"""Measure fixed synthetic full/brief CLI serialization, with optional local tokenization."""

import argparse
import importlib.metadata
import json
import sys
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from security_agent_skills.header_records import HEADER_RECORDS, brief_header_report
from security_agent_skills.reports import compact


def serialize(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"


def benchmark(tokenizer=None):
    encoding = None
    if tokenizer:
        import tiktoken

        encoding = tiktoken.get_encoding(tokenizer)
    rows = []
    for command, operation in HEADER_RECORDS.items():
        raw = (ROOT / "examples/adapted-headers" / (command + ".json")).read_bytes()
        record = json.loads(raw)
        canonical = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        full = operation(record)
        baseline = serialize(compact(full, 20))
        summaries = {
            "default_brief": brief_header_report(full, 3),
            "all_findings_brief": brief_header_report(full, 100),
        }
        row = {
            "workflow": command,
            "fixture_sha256": sha256(canonical.encode("utf-8")).hexdigest(),
            "full_bytes": len(baseline.encode()),
            "finding_count": full["finding_count"],
            "full_tokens": len(encoding.encode(baseline)) if encoding else None,
        }
        for name, summary in summaries.items():
            text = serialize(summary)
            metrics = {
                "bytes": len(text.encode()),
                "omitted_findings": summary["omitted_findings"],
                "byte_reduction_percent": round(
                    100 * (1 - len(text.encode()) / len(baseline.encode())), 2
                ),
            }
            if encoding:
                metrics["tokens"] = len(encoding.encode(text))
                metrics["token_reduction_percent"] = round(
                    100 * (1 - metrics["tokens"] / row["full_tokens"]), 2
                )
            row[name] = metrics
        assert row["all_findings_brief"]["bytes"] < row["full_bytes"]
        rows.append(row)
    return {
        "result": "PASS",
        "scope": "three fixed synthetic header records; minified JSON CLI output",
        "fixture_hash_basis": "canonical JSON: sorted keys, compact separators, ASCII escapes, UTF-8",
        "tokenizer": (
            {
                "encoding": tokenizer,
                "library": "tiktoken",
                "version": importlib.metadata.version("tiktoken"),
            }
            if encoding
            else None
        ),
        "cases": rows,
        "limits": [
            "Not a real-project, model-quality, latency, or billing benchmark.",
            "Default brief caps findings at three; omitted counts and all observations remain.",
            "All-findings brief measures presentation savings without dropping findings.",
            "Tokenizer selection does not establish another platform's actual token accounting.",
            "Optional tokenizer is authoring-only; the shipped helpers remain standard-library only.",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokenizer", choices=["cl100k_base"])
    args = parser.parse_args()
    print(json.dumps(benchmark(args.tokenizer), indent=2, sort_keys=True))
