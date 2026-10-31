# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 mukul975
# Upstream skill author metadata: mahipal.
# Adapted from performing-security-headers-audit/scripts/agent.py at 54a798831d2266a3ca61ce68a7acb80b81160d57.
# Modified by Fliorcie Labs on 2026-10-31: retained selected pure functions only;
# removed network, subprocess, file/attachment writes, CLI, raw report, and grading paths.
# HTTP class methods converted to functions; HSTS max-age parsing bounded and case-insensitive.
# See THIRD_PARTY_NOTICES.md and LICENSES/Apache-2.0.txt in the distribution.
"""Selected attributed offline helper functions. Private values must not be emitted by adapters."""

import re


def check_hsts(headers):
    """Check HTTP Strict Transport Security configuration."""
    hsts = headers.get("Strict-Transport-Security", headers.get("strict-transport-security", ""))
    finding = {
        "header": "Strict-Transport-Security",
        "present": bool(hsts),
        "value": hsts,
        "severity": "High" if not hsts else "Info",
    }
    if hsts:
        finding["has_includeSubDomains"] = "includesubdomains" in hsts.lower()
        finding["has_preload"] = "preload" in hsts.lower()
        max_age_match = re.search(
            r"(?:^|;)\s*max-age\s*=\s*([0-9]{1,10})(?=\s*(?:;|$))", hsts, re.I
        )
        if max_age_match:
            max_age = int(max_age_match.group(1))
            finding["max_age"] = max_age
            finding["max_age_sufficient"] = max_age >= 31536000
            if max_age < 31536000:
                finding["severity"] = "Medium"
                finding["recommendation"] = "Increase max-age to at least 31536000 (1 year)"
    else:
        finding["recommendation"] = (
            "Add: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload"
        )
    return finding


def check_content_type_options(headers):
    """Check X-Content-Type-Options."""
    xcto = headers.get("X-Content-Type-Options", headers.get("x-content-type-options", ""))
    return {
        "header": "X-Content-Type-Options",
        "present": bool(xcto),
        "value": xcto,
        "correct": xcto.lower() == "nosniff" if xcto else False,
        "severity": "Medium" if not xcto else "Info",
        "recommendation": "Add: X-Content-Type-Options: nosniff" if not xcto else None,
    }


def check_referrer_policy(headers):
    """Check Referrer-Policy."""
    rp = headers.get("Referrer-Policy", headers.get("referrer-policy", ""))
    return {
        "header": "Referrer-Policy",
        "present": bool(rp),
        "value": rp,
        "severity": "Medium" if not rp else "Info",
        "recommendation": (
            "Add: Referrer-Policy: strict-origin-when-cross-origin" if not rp else None
        ),
    }


def check_info_disclosure(headers):
    """Check for information disclosure headers."""
    findings = []
    disclosure_headers = ["Server", "X-Powered-By", "X-AspNet-Version", "X-Generator"]
    for h in disclosure_headers:
        value = headers.get(h, headers.get(h.lower(), ""))
        if value:
            findings.append(
                {
                    "header": h,
                    "value": value,
                    "severity": "Low",
                    "recommendation": f"Remove or genericize {h} header",
                }
            )
    return findings
