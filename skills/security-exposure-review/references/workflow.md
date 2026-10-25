# Input and output contract

Supported source formats and findings are conservative review leads. JSON and Markdown are available. --max-findings bounds console output only; --output creates a new full-result JSON file. Scans skip links, reparse points, hardlinks, credential filenames, binaries, large files, generated dependencies, and unreadable paths. Coverage reports every observed skip and budget stop. Live package behavior, transitive runtime dependencies, and concurrent filesystem changes remain unverified.

Exit codes: 0 scoped PASS or generated data; 1 FIX; 2 BLOCKED; 3 PARTIAL. Static audits deliberately return PARTIAL. Reports retain the same schema across hosts.
