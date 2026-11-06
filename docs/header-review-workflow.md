# Compact header-review workflow

## Select only the required skill

Route `email_headers` to `mail-auth-review`, and `http_headers` to `web-header-review`. Skill Router preserves deferred and unknown goals. Load that skill's short entrypoint first and its workflow reference only when constructing a record. Mail Auth Review replaces email-header-triage; Web Header Review replaces http-header-snapshot-review. The existing email-headers and http-headers CLI commands and input schemas are retained.

This change renames source bundles; it does not rename or overwrite previously installed copies. The copy installer still previews and refuses collisions. Choose the new skill name for a fresh project installation. Native assistant discovery remains a host-specific, unverified concern.

## Review one record or combine two

```sh
python scripts/security_check.py email-headers examples/adapted-headers/email-headers.json
python scripts/security_check.py http-headers examples/adapted-headers/http-headers.json
python scripts/security_check.py header-review examples/adapted-headers/header-review.json --output header-evidence.json
```

Run from the checkout. Each installed bundle uses scripts/run.py for its own record. Both renamed bundles also support `scripts/run.py header-review combined.json`. The combined input has exactly schema, email, and http. Schema is security-agent-skills/header-review-v1. Each non-null part is its existing strict header record. Both keys must be present, and at least one part must be non-null. Missing scope stays in details.not_supplied rather than becoming a clean result. No embedded path is opened.

The optional MCP interface remains four tools. It is not expanded by this local CLI workflow. No DNS/HTTP request, attachment processing, native agent delegation, or permission change is performed.

## Presentation and evidence

Default header output is brief JSON with at most three visible findings. It uses [header-brief-v1](../schemas/header-brief-v1.schema.json), a distinct presentation schema. Findings contain stable ID, rule, and concise message. Repeated location, severity, and confidence fields remain in the full report. The fixed input scope is a supplied local header record.

Result, total finding count, omitted count, all key observations, source-verification limits, and no-action flags are retained. Combined output includes counts and observations for each supplied part. No raw address, URL, cookie, or header value is printed. A brief report is still PARTIAL, including zero findings. Malformed records return BLOCKED using the existing error report. Missing execution access is not a passing check.

```sh
python scripts/security_check.py header-review examples/adapted-headers/header-review.json --view full --max-findings 20
python scripts/security_check.py header-review examples/adapted-headers/header-review.json --max-findings 0
```

`--view full` restores report-v1 console output. Console caps still apply; set a sufficient --max-findings value to see all leads. `--output new-file.json` always saves the unabridged full report, independently of console view or cap, and never overwrites an existing file. Save full evidence before a decision where omitted leads matter. Use full report-v1 JSON with Security Evidence Pack; brief JSON is intentionally not accepted as a complete evidence report. Markdown brief output includes observations and coverage; the existing full Markdown renderer has its original summary behavior.

In assistant replies, report the result, relevant IDs, next decision, and unresolved scope. Avoid repeating raw inputs, standard definitions, the complete report, or license boilerplate. Attribution and both licenses remain available in every bundle; compact presentation does not change those obligations.

## Reproduce output measurements

```sh
python scripts/benchmark_header_output.py
python scripts/benchmark_header_output.py --tokenizer cl100k_base
```

The first command requires only Python's standard library and measures UTF-8 bytes. The second requires optional authoring-time tiktoken. It can download its public vocabulary on first use; tokenization runs locally and does not send project records to a model. The shipped analysis helpers have no new runtime dependency. [Recorded measurements](header-output-benchmark.json).

| Fixture | Full tokens | Brief tokens, all findings | Reduction | Default brief tokens | Default omitted |
|---|---|---|---|---|---|
| Mail | 356 | 237 | 33.43% | 237 | 0 |
| Web | 383 | 264 | 31.07% | 264 | 0 |
| Combined | 634 | 461 | 27.29% | 355 | 3 of 6 |

Measured with tiktoken 0.14.0, cl100k_base, minified JSON including its terminating newline, and the three checked-in synthetic fixtures. Combined default reduction is 44.01%. All-findings brief measurements isolate presentation savings without dropping leads. Fixture SHA-256 values identify canonical parsed JSON (sorted keys, compact separators, ASCII escapes, UTF-8), so line endings and key order do not change identity. They are recorded with the results. Different tokenizer, record, host prompt, references, or provider accounting can produce different savings. No latency, quality, real-project cost, or universal platform performance was measured.

These remain attributed adaptations. [Original source, selected helpers, and exclusions](adapted-skills.md), [notices](../THIRD_PARTY_NOTICES.md). Supplied email authentication and HTTP headers are not verified evidence of identity or enforcement.
