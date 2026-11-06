"""Validate authorization documents and produce inert container plans."""

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .inventory import reparse
from .reports import finding, report

TECHNIQUES = {
    "headers",
    "access-control",
    "input-validation",
    "rate-limit-observation",
    "staging-resilience",
}


def appsec_plan(scope: dict[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    current = now or datetime.now(UTC)
    failures = []
    if not isinstance(scope, dict):
        raise ValueError("Scope must be an object")
    targets = scope.get("targets")
    if scope.get("authorized") is not True:
        failures.append("authorization")
    if not isinstance(targets, list) or not targets or len(targets) > 20:
        failures.append("targets")
    else:
        for target in targets:
            try:
                if (
                    not isinstance(target, str)
                    or len(target) > 2048
                    or any(ord(c) < 33 for c in target)
                ):
                    raise ValueError("Invalid target URL")
                parsed = urlsplit(target)
                if parsed.port is not None and not 1 <= parsed.port <= 65535:
                    raise ValueError("Invalid target port")
                if (
                    parsed.scheme not in {"http", "https"}
                    or not parsed.hostname
                    or "*" in parsed.hostname
                    or parsed.username is not None
                    or parsed.password is not None
                    or parsed.query
                    or parsed.fragment
                ):
                    failures.append("target-format")
            except (ValueError, TypeError, AttributeError):
                failures.append("target-format")
    techniques = scope.get("techniques", [])
    if (
        not isinstance(techniques, list)
        or not techniques
        or any(not isinstance(t, str) or t not in TECHNIQUES for t in techniques)
    ):
        failures.append("techniques")
    try:
        start = datetime.fromisoformat(scope["starts_at"])
        expiry = datetime.fromisoformat(scope["expires_at"])
        if start.tzinfo is None or expiry.tzinfo is None or not start <= current < expiry:
            failures.append("time-window")
    except (KeyError, ValueError, TypeError):
        failures.append("time-window")
    limits = {"request_budget": (1, 1000), "concurrency": (1, 4), "duration_seconds": (1, 60)}
    for name, (minimum, maximum) in limits.items():
        value = scope.get(name)
        if type(value) is not int or not minimum <= value <= maximum:
            failures.append(name)
    for name, maximum in [("stop_on_error_rate", 1), ("stop_on_latency_ms", 60000)]:
        value = scope.get(name)
        if (
            not isinstance(value, (int, float)) or isinstance(value, bool)
        ) or not 0 < value <= maximum:
            failures.append(name)
    findings = [
        finding(
            "invalid-authorization-scope",
            "scope",
            i + 1,
            "Missing, expired, or invalid scope field: " + name,
        )
        for i, name in enumerate(sorted(set(failures)))
    ]
    return report(
        "authorized-appsec-validation",
        "authorization document only",
        findings,
        {"scope_validated": not failures, "runtime_observed": False},
        [
            "This validates a declared plan, not ownership or permission from a third party.",
            "No requests, exploitation, load generation, or penetration tests are executed.",
        ],
        result="BLOCKED" if failures else "PASS",
        details={
            "next_action": (
                "Resolve invalid fields"
                if failures
                else "Review exact targets and permission with the operator before using separate active tools"
            )
        },
    )


def sandbox_plan(target: str, image: str, command: list[str]) -> dict[str, Any]:
    source = Path(target).absolute()
    if not source.is_dir() or reparse(source):
        raise ValueError("Sandbox input must be a local non-link directory")
    source = source.resolve()
    if any(c in str(source) for c in [",", "\n", "\r"]):
        raise ValueError("Ambiguous container mount path")
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9./:_-]*@sha256:[a-f0-9]{64}", image):
        raise ValueError("Container image must be pinned to a SHA-256 digest")
    if (
        not isinstance(command, list)
        or not command
        or any(not isinstance(arg, str) or not arg or "\x00" in arg for arg in command)
    ):
        raise ValueError("Provide an explicit command argument array")
    argv = [
        "docker",
        "run",
        "--rm",
        "--network",
        "none",
        "--read-only",
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--pids-limit",
        "64",
        "--memory",
        "256m",
        "--cpus",
        "0.5",
        "--user",
        "65534:65534",
        "--mount",
        "type=bind,src=" + str(source) + ",dst=/work,readonly",
        "--tmpfs",
        "/tmp:rw,noexec,nosuid,size=16777216",
        "--workdir",
        "/work",
        image,
        *command,
    ]
    return report(
        "safe-install-sandbox",
        "container execution plan",
        [],
        {"runtime_observed": False, "filesystem_diff_captured": False, "egress_captured": False},
        [
            "Plan generation does not execute a container or prove isolation.",
            "An operator must verify the selected image, Docker daemon isolation, host support, cancellation, and resource controls.",
            "Read-only input is still readable by package code. Use synthetic copies without credentials; never mount home directories or the Docker socket.",
            "Docker availability and an external timeout/watchdog remain required before execution.",
        ],
        details={"argv": argv, "executed": False},
    )
