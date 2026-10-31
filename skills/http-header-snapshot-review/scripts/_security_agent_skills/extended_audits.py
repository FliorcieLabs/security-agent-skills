"""Local lexical reviews for five distinct AI delivery trust boundaries."""

import re
from collections.abc import Callable
from pathlib import PurePosixPath
from typing import Any

from .audits import STATIC_LIMITS
from .inventory import Inventory, SourceFile
from .reports import finding, report

Rules = dict[str, tuple[str, str]]

INSTRUCTION_RULES: Rules = {
    "instruction-priority-override": (
        r"(?:ignore|override|disregard).{0,45}(?:previous|system|developer|safety|higher.priority).{0,25}(?:instructions?|rules?|policy)",
        "Instruction priority override language; establish provenance and intended trust level.",
    ),
    "approval-bypass-language": (
        r"(?:skip|bypass|disable).{0,35}(?:approval|confirmation|permission|sandbox)",
        "Approval bypass language; retain the host's authorization boundary.",
    ),
    "concealment-language": (
        r"(?:do not|don't|never).{0,20}(?:tell|inform|notify|disclose).{0,20}(?:user|operator)|hide.{0,20}(?:upload|telemetry|transmission)",
        "Concealment language; inspect whether behavior is hidden from the operator.",
    ),
    "sensitive-transfer-instruction": (
        r"(?:upload|send|post|transmit|exfiltrate).{0,70}(?:secret|credential|api.key|environment|source.code)",
        "Sensitive-transfer instruction; confirm the source, destination, and authorization.",
    ),
    "invisible-instruction-character": (
        r"[\u200b\u200c\u200d\u202a-\u202e\u2066-\u2069\ufeff]",
        "Invisible or directional character; review rendered and raw text. Legitimate text may contain it.",
    ),
}

CI_RULES: Rules = {
    "privileged-workflow-trigger": (
        r"\b(?:pull_request_target|workflow_run)\s*:",
        "Privileged trigger; trace untrusted artifacts and code before granting write credentials.",
    ),
    "broad-workflow-permissions": (
        r"\bpermissions\s*:\s*write-all\b",
        "Workflow grants broad token permissions; review job-level minimum authority.",
    ),
    "inherited-workflow-secrets": (
        r"\bsecrets\s*:\s*inherit\b",
        "Reusable workflow inherits secrets; review the callee's trust and required credentials.",
    ),
    "untrusted-workflow-expression": (
        r"\$\{\{\s*github\.(?:event\.[^}]*\b(?:body|title|message|name|ref)|head_ref)\b[^}]*\}\}",
        "Untrusted event expression; check whether it reaches an executable script rather than a data argument.",
    ),
    "self-hosted-runner": (
        r"\bruns-on\s*:.*\bself-hosted\b",
        "Self-hosted runner; verify isolation, cleanup, and which untrusted events can select it.",
    ),
}

CONTAINER_RULES: Rules = {
    "privileged-container": (
        r"\bprivileged[\"']?\s*:\s*true\b|--privileged\b",
        "Privileged container request; review the host authority it exposes.",
    ),
    "container-host-namespace": (
        r"\b(?:hostNetwork|hostPID|hostIPC)[\"']?\s*:\s*true\b|\b(?:network_mode|pid|ipc)\s*:\s*[\"']?host\b",
        "Host namespace sharing; review isolation and reachable host services.",
    ),
    "container-daemon-socket": (
        r"(?:docker|podman)\.sock",
        "Container daemon socket reference; inspect mount direction and effective host authority.",
    ),
    "container-root-user": (
        r"^\s*USER\s+(?:root|0)(?::|\s|$)|\brunAsUser[\"']?\s*:\s*0\b|\buser\s*:\s*[\"']?(?:root|0)[\"']?\s*$",
        "Explicit root user; verify whether the effective runtime user can be reduced.",
    ),
    "container-privilege-escalation": (
        r"\ballowPrivilegeEscalation[\"']?\s*:\s*true\b|\bcap_add\s*:\s*.*\b(?:ALL|SYS_ADMIN)\b",
        "Additional privilege boundary; inspect effective capabilities and escalation controls.",
    ),
    "container-remote-add": (
        r"^\s*ADD\s+https?://",
        "Build downloads a remote artifact; verify its digest and source before a build.",
    ),
}

INFRASTRUCTURE_RULES: Rules = {
    "world-address-range": (
        r"(?:0\.0\.0\.0/0|::/0)",
        "World address range; determine ingress versus egress, protocol, identity, and compensating controls.",
    ),
    "wildcard-iam-authority": (
        r"\b(?:actions?|resources?)[\"']?\s*[:=]\s*(?:\[\s*)?[\"']\*[\"']",
        "Wildcard policy scope; review effect, conditions, and effective permissions.",
    ),
    "public-storage-setting": (
        r"\bacl\s*=\s*[\"']public-(?:read|read-write)[\"']|\b(?:block_public_acls|block_public_policy|restrict_public_buckets)\s*=\s*false\b",
        "Public storage control; inspect the complete policy and intended access.",
    ),
    "disabled-storage-encryption": (
        r"\b(?:encrypted|enable_encryption|encryption_enabled)\s*=\s*false\b",
        "Explicitly disabled encryption setting; verify resource defaults and data sensitivity.",
    ),
    "infrastructure-tls-bypass": (
        r"\b(?:insecure|skip_credentials_validation|insecure_skip_tls_verify|skip_tls_verify)\s*=\s*true\b",
        "Validation bypass setting; inspect the provider's exact meaning and trust boundary.",
    ),
}

LLM_RULES: Rules = {
    "llm-content-capture": (
        r"[\"']?\b(?:log_prompts|log_completions|capture_content|include_inputs|trace_content)[\"']?\s*[:=]\s*(?:true|1)\b",
        "Content capture is configured; trace prompt and response storage, readers, retention, and consent.",
    ),
    "llm-redaction-disabled": (
        r"[\"']?\b(?:redact|redaction_enabled|mask_secrets|scrub_sensitive_data)[\"']?\s*[:=]\s*(?:false|0)\b",
        "Scrubbing is explicitly disabled; inspect sensitive fields before any external provider call.",
    ),
    "llm-remote-code-trust": (
        r"[\"']?\btrust_remote_code[\"']?\s*[:=]\s*true\b",
        "Remote model code trust is enabled; review pinned code and execution authority separately.",
    ),
    "llm-configured-endpoint": (
        r"[\"']?\b(?:base_url|api_base|endpoint|proxy_url)[\"']?\s*[:=]\s*[\"']https?://",
        "Provider or proxy endpoint is configured; verify operator approval, routing, payload, and redirects.",
    ),
    "llm-tls-verification-disabled": (
        r"[\"']?\b(?:verify_ssl|verify_tls|ssl_verify)[\"']?\s*[:=]\s*false\b",
        "TLS verification is disabled; inspect the effective client and transport configuration.",
    ),
}


def _instruction_file(path: PurePosixPath) -> bool:
    return path.name.lower() in {
        "skill.md",
        "agents.md",
        "claude.md",
        "gemini.md",
        "system.txt",
        "developer.txt",
    } or (
        path.suffix.lower() in {".md", ".mdc", ".txt"}
        and any(part in {"agents", "instructions", "prompts", "rules"} for part in path.parts)
    )


def _container_file(path: PurePosixPath) -> bool:
    name = path.name.lower()
    return name.startswith(("dockerfile", "containerfile")) or path.suffix.lower() in {
        ".yml",
        ".yaml",
    }


def _review(
    inventory: Inventory,
    workflow: str,
    rules: Rules,
    selected: Callable[[PurePosixPath], bool],
    *,
    comments_are_content: bool = False,
    extra: Callable[[SourceFile], list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    findings = []
    evaluated = 0
    compiled = [
        (name, re.compile(pattern, re.I), message) for name, (pattern, message) in rules.items()
    ]
    for source in inventory.files:
        if not selected(PurePosixPath(source.path)):
            continue
        evaluated += 1
        for number, line in enumerate(source.text.splitlines(), 1):
            if not comments_are_content and line.lstrip().startswith(("#", "//")):
                continue
            for name, pattern, message in compiled:
                if pattern.search(line):
                    findings.append(finding(name, source.path, number, message))
        if extra:
            findings.extend(extra(source))
    coverage = inventory.coverage()
    coverage.update(
        {"files_evaluated": evaluated, "files_outside_workflow": len(inventory.files) - evaluated}
    )
    return report(
        workflow,
        str(inventory.root),
        findings,
        coverage,
        [
            *STATIC_LIMITS,
            "Lexical checks do not parse full language semantics, expand templates, resolve inheritance, or prove effective runtime policy.",
            "Commented examples, negated instructions, and data-only expressions can produce review leads. Zero evaluated files is incomplete evidence.",
        ],
    )


def _action_references(source: SourceFile) -> list[dict[str, Any]]:
    findings = []
    for number, line in enumerate(source.text.splitlines(), 1):
        match = re.match(r"\s*(?:-\s*)?uses:\s*[\"']?([^\s\"'#]+)", line)
        if not match:
            continue
        reference = match[1]
        if reference.startswith("./"):
            continue
        pinned = (
            re.fullmatch(r"docker://[^\s]+@sha256:[a-fA-F0-9]{64}", reference)
            if reference.startswith("docker://")
            else re.fullmatch(r"[^@\s]+@[a-fA-F0-9]{40}", reference)
        )
        if not pinned:
            findings.append(
                finding(
                    "mutable-action-reference",
                    source.path,
                    number,
                    "External action reference is not content-pinned; review and pin the resolved action or image.",
                )
            )
    return findings


def audit_instructions(inventory: Inventory) -> dict[str, Any]:
    return _review(
        inventory,
        "instruction-boundary-audit",
        INSTRUCTION_RULES,
        _instruction_file,
        comments_are_content=True,
    )


def audit_ci(inventory: Inventory) -> dict[str, Any]:
    return _review(
        inventory,
        "ci-workflow-security-audit",
        CI_RULES,
        lambda p: p.parts[:2] == (".github", "workflows") and p.suffix in {".yaml", ".yml"},
        extra=_action_references,
    )


def audit_containers(inventory: Inventory) -> dict[str, Any]:
    return _review(inventory, "container-boundary-audit", CONTAINER_RULES, _container_file)


def audit_infrastructure(inventory: Inventory) -> dict[str, Any]:
    return _review(
        inventory,
        "infrastructure-exposure-audit",
        INFRASTRUCTURE_RULES,
        lambda p: p.suffix.lower() == ".tf",
    )


def audit_llm(inventory: Inventory) -> dict[str, Any]:
    return _review(
        inventory,
        "llm-data-boundary-audit",
        LLM_RULES,
        lambda p: p.suffix.lower() in {".json", ".toml", ".yaml", ".yml", ".py", ".js", ".ts"},
    )
