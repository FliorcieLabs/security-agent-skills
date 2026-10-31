"""Local record adapters for attributed offline header helpers; never fetch or emit values."""

import re
from email import policy
from email.message import Message
from email.parser import HeaderParser
from typing import Any

from .adapted_email_headers import check_from_replyto_mismatch, extract_authentication_results
from .adapted_http_headers import (
    check_content_type_options,
    check_hsts,
    check_info_disclosure,
    check_referrer_policy,
)
from .reports import finding, report

LIMITS = [
    "Only caller-supplied headers were analyzed, without requests, DNS, or attachment processing.",
    "Headers can be forged, stale, incomplete, or irrelevant to another response or message.",
    "No sender authentication, TLS enforcement, exploitability, or complete policy was verified.",
    "Selected helpers are Apache-2.0 adaptations; see THIRD_PARTY_NOTICES.md for origin and changes.",
]


def _record(value: Any, name: str, fields: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields | {"schema"}:
        raise ValueError("Record fields do not match")
    if value["schema"] != f"security-agent-skills/{name}-v1":
        raise ValueError("Unknown header record schema")
    return value


def _result(name: str, details: dict[str, Any], leads: list[dict[str, Any]]) -> dict[str, Any]:
    return report(
        name,
        "supplied local header record",
        leads,
        {"runtime_observed": False, "source_claims_verified": False},
        LIMITS,
        details={**details, "executed": False, "authorization_granted": False},
    )


def email_headers(value: Any) -> dict[str, Any]:
    doc = _record(value, "email-headers", {"headers"})
    text = doc["headers"]
    if not isinstance(text, str) or not 1 <= len(text) <= 65536 or "\x00" in text:
        raise ValueError("Expected bounded header text")
    normalized = text.replace("\r\n", "\n")
    if "\r" in normalized or "\n\n" in normalized.rstrip("\n"):
        raise ValueError("Provide headers only, without a message body")
    msg = HeaderParser(policy=policy.default).parsestr(normalized + "\n\n")
    if msg.defects or len(list(msg.raw_items())) > 100:
        raise ValueError("Malformed or excessive email headers")
    for name in ("From", "Reply-To", "Return-Path"):
        if len(msg.get_all(name, [])) > 1:
            raise ValueError("Ambiguous duplicate identity headers")
        header: Any = msg[name]
        if header is not None and getattr(header, "defects", False):
            raise ValueError("Malformed identity header")
    if msg["From"] is None:
        raise ValueError("Missing From header")
    # Preserve conflicting claims instead of letting the last Authentication-Results win.
    states: dict[str, set[str]] = {name: set() for name in ("spf", "dkim", "dmarc")}
    allowed = {"pass", "fail", "softfail", "neutral", "none", "temperror", "permerror", "unknown"}
    for item in msg.get_all("Authentication-Results", []):
        single = Message()
        single["Authentication-Results"] = str(item)
        result = extract_authentication_results(single)
        for name in states:
            claim = result[name]
            states[name].add(claim if claim in allowed else "unknown")
    headers = {"from": str(msg["From"]), "reply_to": str(msg["Reply-To"] or "")}
    mismatch, _, _ = check_from_replyto_mismatch(headers)
    leads: list[dict[str, Any]] = []
    if mismatch:
        leads.append(
            finding(
                "EMAIL-REPLY-MISMATCH",
                "record",
                1,
                "From and Reply-To differ; legitimate forwarding can also differ.",
            )
        )
    for position, name in enumerate(states, 2):
        if states[name] & {"fail", "softfail", "permerror", "temperror"}:
            leads.append(
                finding(
                    "EMAIL-CLAIM-" + name.upper(),
                    "record",
                    position,
                    "A supplied authentication header contains a failure claim.",
                )
            )
    return _result(
        "email-headers",
        {
            "header_count": len(list(msg.raw_items())),
            "received_count": len(msg.get_all("Received", [])),
            "authentication_header_count": len(msg.get_all("Authentication-Results", [])),
            "claimed_results": {
                name: sorted(values) or ["unknown"] for name, values in states.items()
            },
            "from_reply_to_mismatch": mismatch,
            "claims_authoritative": False,
        },
        leads,
    )


def http_headers(value: Any) -> dict[str, Any]:
    doc = _record(value, "http-headers", {"secure_transport", "headers"})
    items = doc["headers"]
    if type(doc["secure_transport"]) is not bool or not isinstance(items, list) or len(items) > 100:
        raise ValueError("Expected bounded header list and transport declaration")
    headers: dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict) or set(item) != {"name", "value"}:
            raise ValueError("Unexpected header fields")
        name, text = item["name"], item["value"]
        if (
            not isinstance(name, str)
            or not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]{0,63}", name)
            or not isinstance(text, str)
            or len(text) > 4096
            or any(character in text for character in "\r\n\x00")
        ):
            raise ValueError("Invalid header text")
        if name.lower() in headers:
            raise ValueError("Duplicate header names need separate response records")
        headers[name.lower()] = text
    leads: list[dict[str, Any]] = []
    checks = []

    def add(rule: str, message: str) -> None:
        leads.append(finding(rule, "record", len(leads) + 1, message))

    if doc["secure_transport"]:
        hsts = check_hsts(headers)
        checks.append("hsts")
        if not hsts["present"]:
            add("HTTP-HSTS-MISSING", "HSTS is absent from the supplied HTTPS response headers.")
        elif "max_age" not in hsts:
            add("HTTP-HSTS-AGE-UNKNOWN", "A bounded numeric HSTS max-age could not be established.")
        elif not hsts["max_age_sufficient"]:
            add(
                "HTTP-HSTS-AGE-REVIEW",
                "HSTS max-age is below the helper's one-year review threshold.",
            )
    content = check_content_type_options(headers)
    checks.append("content_type_options")
    if not content["correct"]:
        add("HTTP-NOSNIFF-REVIEW", "X-Content-Type-Options is absent or is not exactly nosniff.")
    checks.append("referrer_policy_presence")
    if not check_referrer_policy(headers)["present"]:
        add(
            "HTTP-REFERRER-MISSING",
            "Referrer-Policy is absent; inspect browser and application context.",
        )
    disclosure = check_info_disclosure(headers)
    checks.append("information_disclosure_presence")
    if disclosure:
        add(
            "HTTP-DISCLOSURE-REVIEW",
            "A selected server or framework identification header is present.",
        )
    return _result(
        "http-headers",
        {
            "header_count": len(headers),
            "checks": checks,
            "transport_is_declared": True,
            "hsts_not_evaluated": not doc["secure_transport"],
            "identification_header_count": len(disclosure),
            "not_evaluated": [
                "CSP semantics",
                "cookies",
                "framing",
                "redirects",
                "live TLS",
                "header authenticity",
            ],
        },
        leads,
    )


HEADER_RECORDS = {"email-headers": email_headers, "http-headers": http_headers}
