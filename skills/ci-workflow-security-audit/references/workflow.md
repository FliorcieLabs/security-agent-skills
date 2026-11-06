# CI Workflow Security Reviewer: input and interpretation

Input: an existing non-link target directory. The inventory enforces file, entry, depth, and byte limits and excludes links, credential filenames, binaries, and dependency folders. Skips stay visible in coverage.

Selected input: .github/workflows/*.yml and .github/workflows/*.yaml.

```text
python "<skill-dir>/scripts/run.py" "<target-dir>" --format markdown --max-findings 5 --output "<new-report.json>"
```

Exit 3 is expected for this static review. Zero findings or zero evaluated files does not establish safety. Console limits do not change the full report. An existing output path is blocked rather than overwritten.

Check the trigger, token permissions, runner ownership, action provenance, and checkout revision together. Trace event expressions to executable contexts. A reference pin is content identity, not evidence that the referenced code is safe.

These are lexical, line-based checks. They do not parse a complete language, resolve aliases or inheritance, expand templates, evaluate policy, inspect provider terms, or observe runtime behavior. Comments and negations can produce leads. Review context before changing anything. Full reports omit source excerpts and configuration values, but include scope paths and relative filenames; inspect them before sharing.

Prefer one evidence-backed next action per unresolved boundary. Describe the smallest corrective change and how to verify it. Do not automatically install, execute, publish, or contact a service.
