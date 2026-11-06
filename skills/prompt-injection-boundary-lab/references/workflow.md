# Input and output contract

Run without arguments to emit five synthetic cases. Each response record requires case_id, tool_calls (an array of objects with tool names), and output (a string). Evaluate with `python "<skill-dir>/scripts/run.py" --responses "<responses.json>"`. Unknown IDs and duplicates are rejected. Complete supplied records can pass this bounded checker; that does not independently verify the agent or all injection mechanisms.

Exit codes: 0 scoped PASS or generated data; 1 FIX; 2 BLOCKED; 3 PARTIAL. Static audits deliberately return PARTIAL. Reports retain the same schema across hosts.
