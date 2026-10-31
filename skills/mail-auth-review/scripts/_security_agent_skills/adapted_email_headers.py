# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 mukul975
# Upstream skill author metadata: mahipal.
# Adapted from analyzing-email-headers-for-phishing-investigation/scripts/agent.py at 54a798831d2266a3ca61ce68a7acb80b81160d57.
# Modified by Fliorcie Labs on 2026-10-31: retained selected pure functions only;
# removed network, subprocess, file/attachment writes, CLI, raw report, and grading paths.
# Added a result type annotation and standardized formatting/import order.
# See THIRD_PARTY_NOTICES.md and LICENSES/Apache-2.0.txt in the distribution.
"""Selected attributed offline helper functions. Private values must not be emitted by adapters."""

import email.utils
import re
from typing import Any


def extract_authentication_results(msg):
    """Extract SPF, DKIM, and DMARC results from Authentication-Results headers."""
    auth_results = msg.get_all("Authentication-Results") or []
    received_spf = str(msg.get("Received-SPF", ""))
    dkim_sig = str(msg.get("DKIM-Signature", ""))
    results: dict[str, Any] = {
        "spf": "unknown",
        "dkim": "unknown",
        "dmarc": "unknown",
        "raw_authentication_results": [],
        "received_spf": received_spf,
        "has_dkim_signature": bool(dkim_sig),
    }
    for ar in auth_results:
        results["raw_authentication_results"].append(ar.strip())
        ar_lower = ar.lower()
        if "spf=" in ar_lower:
            spf_match = re.search(r"spf=(\w+)", ar_lower)
            if spf_match:
                results["spf"] = spf_match.group(1)
        if "dkim=" in ar_lower:
            dkim_match = re.search(r"dkim=(\w+)", ar_lower)
            if dkim_match:
                results["dkim"] = dkim_match.group(1)
        if "dmarc=" in ar_lower:
            dmarc_match = re.search(r"dmarc=(\w+)", ar_lower)
            if dmarc_match:
                results["dmarc"] = dmarc_match.group(1)
    return results


def check_from_replyto_mismatch(headers):
    """Detect mismatch between From and Reply-To addresses."""
    from_addr = email.utils.parseaddr(headers["from"])[1].lower()
    reply_to = headers["reply_to"]
    if reply_to:
        reply_addr = email.utils.parseaddr(reply_to)[1].lower()
        if reply_addr and from_addr != reply_addr:
            return True, from_addr, reply_addr
    return False, from_addr, None
