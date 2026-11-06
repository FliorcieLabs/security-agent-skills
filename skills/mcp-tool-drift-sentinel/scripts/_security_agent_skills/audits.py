"""Conservative static review leads, without source excerpts or credential values."""

import json
import re
import tomllib
from pathlib import PurePosixPath
from typing import Any

from .inventory import Inventory
from .reports import finding, report

STATIC_LIMITS = [
    "Static review leads require manual source-to-sink confirmation.",
    "No runtime, dependency execution, advisory lookup, or network capture was performed.",
    "Missing indicators do not establish safety. Symlinks and concurrent replacement cannot be fully attested on every host.",
]
EGRESS_RULES = {
    "outbound-client": (
        r"\b(?:requests|httpx)\.(?:get|post|put|patch|delete)\s*\(|\bfetch\s*\(|urlopen\s*\(|https?\.request\s*\(",
        "Network client call; inspect destination, payload, trigger, and redirects.",
    ),
    "tracking-indicator": (
        r"\bposthog\b|sentry_sdk|sendBeacon\s*\(|telemetry.*(?:send|capture|endpoint)",
        "Tracking indicator; confirm whether enabled and what it transmits.",
    ),
    "sensitive-source": (
        r"os\.environ|\bgetenv\s*\(|process\.env|keyring|browser_cookie",
        "Sensitive input access; trace its consumers without printing values.",
    ),
    "execution-hook": (
        r"shell\s*=\s*True|execSync\s*\(|child_process|subprocess\.",
        "Process execution boundary; inspect arguments and any downloads.",
    ),
    "external-resource": (
        r"(?:src|href)\s*=.*https?://|@import.*https?://",
        "External asset request may disclose client metadata when the artifact opens.",
    ),
}
EXPOSURE_RULES = {
    "dynamic-evaluation": (
        r"\beval\s*\(|\bexec\s*\(",
        "Dynamic evaluation; determine whether an untrusted value can reach it.",
    ),
    "unsafe-deserialization": (
        r"pickle\.loads?\s*\(|yaml\.load\s*\(",
        "Deserializer may execute input; confirm loader and trust boundary.",
    ),
    "broad-bind": (
        r"0\.0\.0\.0|host\s*[:=]\s*[\"']::[\"']",
        "Listener binds broadly; verify intended exposure and authentication.",
    ),
    "debug-mode": (
        r"debug\s*[:=]\s*(?:True|true)|DEBUG\s*=\s*1",
        "Debug setting may expose internals; confirm runtime configuration.",
    ),
    "shell-interpolation": (
        r"shell\s*=\s*True|execSync\s*\(",
        "Shell execution requires a reachable input and quoting review.",
    ),
}


def capabilities(text: str) -> list[str]:
    return sorted(
        name for name, (pattern, _) in EGRESS_RULES.items() if re.search(pattern, text, re.I)
    )


def pattern_audit(
    inventory: Inventory, kind: str, rules: dict[str, tuple[str, str]]
) -> dict[str, Any]:
    findings = []
    for source in inventory.files:
        for number, line in enumerate(source.text.splitlines(), 1):
            for name, (pattern, message) in rules.items():
                if re.search(pattern, line, re.I):
                    findings.append(finding(name, source.path, number, message))
    return report(kind, str(inventory.root), findings, inventory.coverage(), STATIC_LIMITS)


def audit_egress(inventory: Inventory) -> dict[str, Any]:
    return pattern_audit(inventory, "agent-egress-audit", EGRESS_RULES)


def audit_exposure(inventory: Inventory) -> dict[str, Any]:
    return pattern_audit(inventory, "security-exposure-review", EXPOSURE_RULES)


def pinned(value: str) -> bool:
    return bool(re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", value))


def audit_dependencies(inventory: Inventory) -> dict[str, Any]:
    findings = []
    counts = {"manifests": 0, "declared_dependencies": 0, "locked_packages": 0}
    for source in inventory.files:
        name = PurePosixPath(source.path).name
        try:
            if name == "package.json":
                counts["manifests"] += 1
                doc = json.loads(source.text)
                if not isinstance(doc, dict):
                    raise ValueError("Expected object")
                scripts = doc.get("scripts", {})
                if not isinstance(scripts, dict):
                    raise ValueError("Invalid scripts")
                if any(
                    key in scripts for key in ["preinstall", "install", "postinstall", "prepare"]
                ):
                    findings.append(
                        finding(
                            "install-hook",
                            source.path,
                            1,
                            "Manifest declares lifecycle scripts; review them before package installation.",
                        )
                    )
                for section in ["dependencies", "devDependencies", "optionalDependencies"]:
                    deps = doc.get(section, {})
                    if not isinstance(deps, dict):
                        raise ValueError("Invalid dependencies")
                    counts["declared_dependencies"] += len(deps)
                    for version in deps.values():
                        if not isinstance(version, str) or not pinned(version):
                            findings.append(
                                finding(
                                    "unpinned-dependency",
                                    source.path,
                                    1,
                                    "A declaration is mutable or external; inspect the lockfile and provenance.",
                                )
                            )
                            break
            elif name in {"package-lock.json", "npm-shrinkwrap.json"}:
                doc = json.loads(source.text)
                packages = doc.get("packages", {})
                if not isinstance(packages, dict):
                    raise ValueError("Invalid lock packages")
                counts["locked_packages"] += len(packages)
                if not packages:
                    findings.append(
                        finding(
                            "unexamined-lock-format",
                            source.path,
                            1,
                            "No supported packages map; transitive integrity remains unknown.",
                        )
                    )
                for entry in packages.values():
                    if (
                        isinstance(entry, dict)
                        and entry.get("resolved")
                        and not entry.get("integrity")
                    ):
                        findings.append(
                            finding(
                                "missing-lock-integrity",
                                source.path,
                                1,
                                "At least one resolved lock entry has no integrity field.",
                            )
                        )
                        break
            elif name == "pyproject.toml":
                counts["manifests"] += 1
                doc = tomllib.loads(source.text)
                deps = doc.get("project", {}).get("dependencies", [])
                if not isinstance(deps, list):
                    raise ValueError("Invalid dependencies")
                counts["declared_dependencies"] += len(deps)
                if any(not isinstance(d, str) or "==" not in d or "*" in d for d in deps):
                    findings.append(
                        finding(
                            "unpinned-dependency",
                            source.path,
                            1,
                            "Python dependencies are not all exact pins; review a resolved lockfile.",
                        )
                    )
                build = doc.get("build-system", {}).get("build-backend")
                if build:
                    findings.append(
                        finding(
                            "build-backend",
                            source.path,
                            1,
                            "A build backend executes during source builds; inspect its provenance.",
                        )
                    )
            elif name.startswith("requirements") and name.endswith(".txt"):
                counts["manifests"] += 1
                for number, line in enumerate(source.text.splitlines(), 1):
                    if line.strip() and not line.lstrip().startswith("#"):
                        counts["declared_dependencies"] += 1
                        if "==" not in line or line.lstrip().startswith("-"):
                            findings.append(
                                finding(
                                    "requirements-source",
                                    source.path,
                                    number,
                                    "Non-exact requirement or installer option; inspect without executing pip.",
                                )
                            )
        except (ValueError, TypeError, AttributeError):
            findings.append(
                finding(
                    "invalid-manifest",
                    source.path,
                    1,
                    "Manifest parsing failed; dependency coverage is incomplete.",
                )
            )
    return report(
        "dependency-provenance-audit",
        str(inventory.root),
        findings,
        inventory.coverage(),
        STATIC_LIMITS
        + ["CVE status, license compatibility, and package authenticity remain unverified."],
        details=counts,
    )


def audit_mcp(inventory: Inventory) -> dict[str, Any]:
    findings = []
    servers_examined = 0
    for source in inventory.files:
        name = PurePosixPath(source.path).name
        if name not in {"mcp.json", ".mcp.json", "config.toml", "settings.json"}:
            continue
        try:
            doc = tomllib.loads(source.text) if name.endswith(".toml") else json.loads(source.text)
            if not isinstance(doc, dict):
                raise ValueError("Expected object")
            servers = doc.get("mcpServers", doc.get("mcp_servers", doc.get("servers", {})))
            if not isinstance(servers, dict):
                raise ValueError("Expected servers object")
            for server in servers.values():
                if not isinstance(server, dict):
                    raise ValueError("Expected server object")
                servers_examined += 1
                if server.get("url"):
                    findings.append(
                        finding(
                            "remote-mcp",
                            source.path,
                            1,
                            "Remote MCP endpoint: tool inputs and outputs can leave this host.",
                        )
                    )
                command = str(server.get("command", "")).replace("\\", "/").split("/")[-1].lower()
                if command in {
                    "sh",
                    "bash",
                    "cmd",
                    "cmd.exe",
                    "powershell",
                    "powershell.exe",
                    "pwsh",
                    "pwsh.exe",
                }:
                    findings.append(
                        finding(
                            "shell-launch",
                            source.path,
                            1,
                            "MCP launches a shell; inspect command construction and effective authority.",
                        )
                    )
                if server.get("env") or server.get("headers") or server.get("http_headers"):
                    findings.append(
                        finding(
                            "mcp-credentials",
                            source.path,
                            1,
                            "Environment or header configuration exists; values are deliberately omitted.",
                        )
                    )
                if not server.get("enabled_tools"):
                    findings.append(
                        finding(
                            "unrestricted-tool-discovery",
                            source.path,
                            1,
                            "No client tool allowlist found; inspect actual advertised tools and server enforcement.",
                        )
                    )
        except (ValueError, TypeError):
            findings.append(
                finding(
                    "invalid-mcp-config",
                    source.path,
                    1,
                    "Configuration could not be interpreted; authority is unknown.",
                )
            )
    return report(
        "mcp-authority-review",
        str(inventory.root),
        findings,
        inventory.coverage(),
        STATIC_LIMITS
        + [
            "Client configuration is not an OS permission boundary; live tool schemas were not inspected."
        ],
        details={"servers_examined": servers_examined},
    )
