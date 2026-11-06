# Input and output contract

Create snapshots with `python "<skill-dir>/scripts/run.py" snapshot "<target>" --output "<new-snapshot.json>"`. Compare with `python "<skill-dir>/scripts/run.py" "<baseline.json>" "<candidate.json>"`. Snapshots contain relative file paths, SHA-256 values, capability labels, and incomplete-coverage information. Neither snapshot nor digest authenticates a release.

Exit codes: 0 scoped PASS or generated data; 1 FIX; 2 BLOCKED; 3 PARTIAL. Static audits deliberately return PARTIAL. Reports retain the same schema across hosts.
