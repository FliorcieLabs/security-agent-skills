# Input and output contract

Pack with `python "<skill-dir>/scripts/run.py" "<report.json>" --archive "<new-pack.zip>"`. Verify with `python "<skill-dir>/scripts/run.py" verify "<pack.zip>"`. Archives have fixed timestamps and deterministic member order. Inputs are limited to 100 suite reports and 16 MB. Verification rejects unsafe paths, unexpected members, duplicate names, and digest mismatches. It does not extract files or upload anything.

Exit codes: 0 scoped PASS or generated data; 1 FIX; 2 BLOCKED; 3 PARTIAL. Static audits deliberately return PARTIAL. Reports retain the same schema across hosts.
