# Reproducible report-size benchmark

Fixture: 1,000 synthetic review findings. Full result: pretty JSON. Console result: compact JSON limited to 20 findings, preserving the total count, omitted count, coverage, and limitations.

| Measurement | Full | Bounded console | Reduction |
|---|---|---|---|
| UTF-8 bytes | 267,150 | 4,335 | 98.38% |
| cl100k_base tokens, tiktoken 0.14.0 | 78,487 | 1,157 | 98.53% |

Reproduce byte counts using only the runtime standard library:

```sh
python scripts/benchmark_reports.py
```

To reproduce the tokenizer measurement in an optional temporary development environment:

```sh
uv run --no-project --with tiktoken==0.14.0 python scripts/benchmark_reports.py --tokenizer cl100k_base
```

The optional tokenizer may download its public encoding table on first use. No source code or report is sent to a tokenizer service. Runtime analysis does not require uv, tiktoken, or any API key. Raw measurements are in report-benchmark.json.

These are synthetic serialization measurements. They do not measure a model conversation, billing, hidden prompts, tool metadata, real repositories, user comprehension, or security accuracy. Truncation is not evidence reduction: save the full report separately with --output, and follow up on omitted findings when required. The fixture is deliberately large, so smaller reports will see different savings.
