"""Reproducible synthetic size benchmark; token counts require optional tiktoken."""

import argparse
import importlib.metadata
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from security_agent_skills.reports import compact, finding, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tokenizer", choices=["cl100k_base"])
    args = parser.parse_args()
    value = report(
        "synthetic-benchmark",
        "synthetic-fixture",
        [
            finding(
                "review-lead",
                f"src/module_{i}.py",
                i + 1,
                "Inspect the local source-to-sink path before installing.",
            )
            for i in range(1000)
        ],
        {"files_read": 1000, "runtime_observed": False},
        ["Synthetic repeated findings; not a real project benchmark."],
    )
    full = json.dumps(value, sort_keys=True, indent=2)
    small = json.dumps(compact(value, 20), sort_keys=True, separators=(",", ":"))
    result = {
        "fixture_findings": 1000,
        "console_findings": 20,
        "full_json_bytes": len(full.encode()),
        "compact_json_bytes": len(small.encode()),
        "bytes_reduction_percent": round(100 * (1 - len(small.encode()) / len(full.encode())), 2),
        "token_counts": None,
        "limitations": [
            "Synthetic report only. Context, model billing, hidden prompts, and real-project savings are not measured.",
            "Bounded console output retains total counts, coverage, limitations, and an omitted-findings count; full evidence remains available separately.",
        ],
    }
    if args.tokenizer:
        import tiktoken

        encoder = tiktoken.get_encoding(args.tokenizer)
        left = len(encoder.encode(full))
        right = len(encoder.encode(small))
        result["token_counts"] = {
            "encoding": args.tokenizer,
            "tiktoken_version": importlib.metadata.version("tiktoken"),
            "full": left,
            "compact": right,
            "reduction_percent": round(100 * (1 - right / left), 2),
        }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
