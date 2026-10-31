# Http Header Snapshot Review workflow

Adapted helper provenance: performing-security-headers-audit from mukul975/Anthropic-Cybersecurity-Skills at revision 54a798831d2266a3ca61ce68a7acb80b81160d57. Copyright 2026 mukul975; upstream skill author metadata mahipal. Selected runtime portions remain Apache-2.0. Fliorcie Labs added this bounded offline adapter and workflow on October 31, 2026. See THIRD_PARTY_NOTICES.md and LICENSES/Apache-2.0.txt in this bundle. No affiliation or endorsement is implied.

Required fields: schema, secure_transport, headers. secure_transport is a boolean declaration, not measured TLS. headers contains at most 100 objects with exactly name and value. Names match [A-Za-z][A-Za-z0-9-]{0,63}; values are strings of at most 4096 characters without CR, LF, or NUL. Duplicate names are rejected case-insensitively; split observations into separate response records. The helper checks HSTS presence and bounded numeric max-age only for a declared secure response, nosniff equality, Referrer-Policy presence, and selected server/framework header presence. The one-year HSTS threshold is a review heuristic, not a mandatory project policy or preload certification. CSP, framing, cookies, complete HSTS grammar, referrer-policy validity, redirects, live TLS, and header authenticity remain unverified. No header values, cookies, destinations, or response bodies are returned.

The CLI reads a bounded regular non-link JSON file, rejects duplicate JSON keys and unknown record fields, and uses the shared report schema. Nothing is sent to an independent external endpoint. Results return to the invoking host, whose AI provider policy remains separate. IDs and counts can still be sensitive.

## Synthetic example

```json
{
  "schema": "security-agent-skills/http-headers-v1",
  "secure_transport": true,
  "headers": [
    {
      "name": "Strict-Transport-Security",
      "value": "max-age=300"
    },
    {
      "name": "X-Content-Type-Options",
      "value": "nosniff"
    },
    {
      "name": "Server",
      "value": "Synthetic-Server"
    }
  ]
}
```

These two tools are available through the CLI or their standalone skill bundles. They are not added to the optional four-tool MCP server.

## Compact workflow

Console defaults to security-agent-skills/header-brief-v1, with three visible findings. Result, full finding count, omitted count, stable IDs, all observations, and coverage remain. Brief finding entries omit repeated location/severity fields; the fixed scope is the supplied header record. `--view full` uses the original report-v1 schema, and `--max-findings 20` reveals all current header leads. `--output` always writes the full report before presentation. Use that file for Evidence Pack; brief summaries deliberately use a different schema and are not evidence-pack inputs.

Route email_headers to mail-auth-review and http_headers to web-header-review. For both, use the shared header-review command with the exact record below. Both keys are required; a null value marks a scope not supplied. At least one record must be supplied. The other embedded record uses its existing schema above. No path inside the document is opened.

```json
{
  "schema": "security-agent-skills/header-review-v1",
  "email": {
    "schema": "security-agent-skills/email-headers-v1",
    "headers": "From: Sender <sender@example.invalid>\nReply-To: reply@example.invalid\nAuthentication-Results: mx.example.invalid; spf=fail; dkim=pass; dmarc=fail\nReceived: from relay.example.invalid by mx.example.invalid\n"
  },
  "http": {
    "schema": "security-agent-skills/http-headers-v1",
    "secure_transport": true,
    "headers": [
      {
        "name": "Strict-Transport-Security",
        "value": "max-age=300"
      },
      {
        "name": "X-Content-Type-Options",
        "value": "nosniff"
      },
      {
        "name": "Server",
        "value": "Synthetic-Server"
      }
    ]
  }
}
```

The combined report keeps per-part observations and counts. Summaries never turn missing scopes, omitted leads, or unknown authentication into PASS. The four-tool MCP interface is unchanged.
