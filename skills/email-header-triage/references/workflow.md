# Email Header Triage workflow

Adapted helper provenance: analyzing-email-headers-for-phishing-investigation from mukul975/Anthropic-Cybersecurity-Skills at revision 54a798831d2266a3ca61ce68a7acb80b81160d57. Copyright 2026 mukul975; upstream skill author metadata mahipal. Selected runtime portions remain Apache-2.0. Fliorcie Labs added this bounded offline adapter and workflow on October 31, 2026. See THIRD_PARTY_NOTICES.md and LICENSES/Apache-2.0.txt in this bundle. No affiliation or endorsement is implied.

Required fields: schema and headers. Headers is a nonempty string of at most 65,536 characters, without NUL, a body, or bare CR. Provide LF or CRLF header lines only. At most 100 header fields. From is required; duplicate From, Reply-To, or Return-Path and malformed identity headers are rejected. Multiple Authentication-Results remain separate declarations; contradictory pass/fail claims are retained. Missing results are unknown. The original extraction uses simple patterns, not a full Authentication-Results grammar. Never treat those fields as trusted without identifying the receiving system's trust boundary. No DNS, DKIM cryptography, origin proof, body/URL parsing, attachments, PST/MSG parsing, or reputation checks. Header addresses and values are not returned. Differences can be legitimate and are review leads, not phishing verdicts.

The CLI reads a bounded regular non-link JSON file, rejects duplicate JSON keys and unknown record fields, and uses the shared report schema. Nothing is sent to an independent external endpoint. Results return to the invoking host, whose AI provider policy remains separate. IDs and counts can still be sensitive.

## Synthetic example

```json
{
  "schema": "security-agent-skills/email-headers-v1",
  "headers": "From: Sender <sender@example.invalid>\nReply-To: reply@example.invalid\nAuthentication-Results: mx.example.invalid; spf=fail; dkim=pass; dmarc=fail\nReceived: from relay.example.invalid by mx.example.invalid\n"
}
```

These two tools are available through the CLI or their standalone skill bundles. They are not added to the optional four-tool MCP server.
