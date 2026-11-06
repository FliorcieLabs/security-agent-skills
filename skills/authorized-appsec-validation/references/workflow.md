# Input and output contract

Required JSON fields: authorized (boolean), targets (1 to 20 exact HTTP(S) URLs without credentials, queries, or fragments), techniques (headers, access-control, input-validation, rate-limit-observation, staging-resilience), starts_at and expires_at (timezone-aware ISO timestamps), request_budget (1 to 1000), concurrency (1 to 4), duration_seconds (1 to 60), stop_on_error_rate (greater than 0 and at most 1), stop_on_latency_ms (greater than 0 and at most 60000). A valid document is not independent evidence of ownership.

Exit codes: 0 scoped PASS or generated data; 1 FIX; 2 BLOCKED; 3 PARTIAL. Static audits deliberately return PARTIAL. Reports retain the same schema across hosts.
