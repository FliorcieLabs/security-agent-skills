# Input and output contract

Input is a JSON array. Each record has canary, source, and sink strings. Canary must match SYNTHETIC_ followed by 1 to 80 uppercase letters, digits, or underscores. HTTP(S) and WS(S) sinks are classified as declared network routes. The report omits input values and payloads. No event capture is performed.

Exit codes: 0 scoped PASS or generated data; 1 FIX; 2 BLOCKED; 3 PARTIAL. Static audits deliberately return PARTIAL. Reports retain the same schema across hosts.
