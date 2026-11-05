"""Review bounded caller-declared control evidence without executing targets."""

import re
from typing import Any

from .reports import finding, report

CONTROLS = {
    "agent-memory-integrity-review": {
        "write_provenance": "Trace persistent writes to source and trust level; retrieved content cannot approve itself.",
        "scope_isolation": "Check project, user, and tenant isolation on memory reads and writes.",
        "instruction_boundary": "Verify stored observations cannot replace trusted instructions or tool policy.",
        "expiry_reset": "Check expiry, deletion, cache invalidation, and restored copies.",
        "poisoning_regression": "Use synthetic poisoned entries to check later task behavior.",
    },
    "mcp-tool-drift-sentinel": {
        "identity_pin": "Compare server identity, package digest, and configuration rather than display names.",
        "schema_diff": "Compare required fields, defaults, enums, additional properties, and limits.",
        "authority_diff": "Trace changed filesystem, process, credential, write, and destination authority into implementation.",
        "description_boundary": "Check changed descriptions for instructions crossing the tool-data boundary.",
        "upgrade_regression": "Compare allowed and denied synthetic calls in an isolated candidate.",
    },
    "agent-approval-binding-review": {
        "action_binding": "Bind approval to canonical action, arguments, target, identity, and effects.",
        "freshness": "Check expiry, revocation, session identity, and changed policy before dispatch.",
        "argument_substitution": "Test changed arguments or targets between approval and dispatch in disposable fixtures.",
        "replay_control": "Check one-time use, idempotency, and reconciliation after ambiguous effects.",
        "enforcement": "Enforce approval at execution; model-written text cannot approve itself.",
    },
    "tenant-isolation-review": {
        "identity_context": "Trace trusted tenant context from authentication into services and workers.",
        "object_authorization": "Check ownership for reads, writes, batches, nested resources, and exports.",
        "cache_storage": "Check cache keys, storage paths, signed URLs, and index partitions.",
        "async_context": "Check jobs, queues, retries, and scheduled tasks preserve ownership.",
        "negative_matrix": "Test two synthetic tenants across roles and operations.",
    },
    "webhook-trust-review": {
        "raw_signature": "Verify the provider signature over exact raw bytes before parsing or effects.",
        "timestamp_window": "Check freshness, clock assumptions, and missing or malformed signature rejection.",
        "key_rotation": "Check key selection and rotation cannot fall back to unsigned processing.",
        "duplicate_delivery": "Bind event identity to idempotent processing and ambiguous-effect reconciliation.",
        "event_authority": "Validate event type, account, and ownership independently of a valid signature.",
    },
    "archive-path-boundary-review": {
        "destination_containment": "Resolve members inside the root, including absolute, drive, UNC, and parent paths.",
        "link_boundary": "Check symlinks, hardlinks, reparse points, and parent replacement races.",
        "name_collisions": "Check case folding, Unicode normalization, reserved names, duplicates, and overwrite rules.",
        "resource_budget": "Bound member count, expanded bytes, compression ratio, nesting, and time.",
        "atomic_failure": "Test partial failures and concurrent destination changes in disposable directories.",
    },
    "ci-identity-oidc-review": {
        "trust_subject": "Check issuer, audience, repository, ref, environment, and subject constraints.",
        "untrusted_events": "Trace fork and pull request content into privileged jobs and reusable workflows.",
        "token_scope": "Check minimal cloud and job token permissions, lifetime, and separation of duties.",
        "artifact_boundary": "Check artifact and cache provenance before privileged consumers execute them.",
        "denied_contexts": "Compare allowed and denied repository and ref contexts in local policy fixtures.",
    },
    "sensitive-logging-review": {
        "source_inventory": "Map sensitive sources to logging, tracing, error, and transcript sinks.",
        "scrubbing_order": "Check best-effort scrubbing before serialization and transport, including exceptions and nesting.",
        "canary_validation": "Use synthetic secret and personal-data markers across success, error, and retry paths.",
        "retention_access": "Review access, retention, exports, sampling, and downstream processors.",
        "capture_controls": "Check debug flags, bodies, headers, attachments, and opt-out behavior.",
    },
    "race-replay-review": {
        "state_invariants": "Define legal transitions and final-state invariants before selecting schedules.",
        "atomic_boundary": "Trace transactions, locks, uniqueness constraints, and compare-and-swap operations.",
        "idempotency_scope": "Bind keys to identity and request semantics; check expiry and conflicting payloads.",
        "crash_reconciliation": "Check crash windows, lost responses, and reconciliation before retry.",
        "schedule_regression": "Reproduce deterministic interleavings in isolated fixtures with final-state evidence.",
    },
    "oauth-integration-review": {
        "flow_binding": "Check state, PKCE, nonce where applicable, issuer, audience, and session binding for the flow.",
        "redirect_boundary": "Check registered redirect matching, callback handling, open redirects, and code leakage.",
        "token_lifecycle": "Review scope, storage, expiry, refresh rotation, revocation, and errors.",
        "account_linking": "Bind linking to the intended authenticated account; do not trust email equality alone.",
        "negative_callbacks": "Test synthetic expired, mismatched, reused, and wrong-issuer callbacks in an authorized fixture.",
    },
    "browser-agent-boundary-review": {
        "page_instruction_boundary": "Keep page content, labels, and downloads separate from trusted instructions.",
        "origin_identity": "Bind actions to the intended origin, account, frame, and current state.",
        "consequential_actions": "Check approval binding for submissions, purchases, messages, downloads, and uploads.",
        "local_resources": "Review clipboard, file chooser, download execution, and local file boundaries.",
        "adversarial_fixture": "Use a local synthetic page and inspect whether action traces stay within the task.",
    },
    "rag-access-boundary-review": {
        "ingest_acl": "Trace ownership and access metadata through ingestion, chunking, and index updates.",
        "query_enforcement": "Check trusted access filters before retrieval and reranking, including fallbacks.",
        "cache_citations": "Check answer caches, embeddings, snippets, citations, and direct links for cross-access leaks.",
        "revocation": "Test revocation and deletion against stale indexes, caches, and restored snapshots.",
        "access_matrix": "Use synthetic per-user document markers and inspect retrieved chunks and outputs.",
    },
    "cryptographic-usage-review": {
        "purpose_primitive": "Match primitives and parameters to the purpose; do not invent cryptographic constructions.",
        "randomness_nonce": "Trace randomness and nonce uniqueness through concurrency, restart, and key reuse.",
        "key_lifecycle": "Check generation, storage, separation, rotation, revocation, and backups.",
        "verification": "Check authentication before plaintext use, signature verification, algorithm selection, and errors.",
        "known_answer_tests": "Use authoritative test vectors and modified ciphertext, signature, and metadata cases.",
    },
    "security-fix-verification": {
        "baseline_reproduction": "Reproduce the original failure at the affected revision in a disposable authorized environment.",
        "candidate_equivalence": "Run the same bounded case at the exact candidate with comparable configuration.",
        "variant_coverage": "Review relevant alternate encodings, roles, endpoints, nested inputs, and bypass paths.",
        "legitimate_behavior": "Check authorized behavior still works; blocked tests do not establish a fix.",
        "evidence_identity": "Bind results to revision, environment, exact commands, expectations, and retained artifacts.",
    },
    "data-deletion-propagation-review": {
        "lineage_inventory": "Map identifiers and derived copies across stores, queues, indexes, caches, and exports.",
        "deletion_semantics": "Separate access removal, soft deletion, physical deletion, and backup retention with deadlines.",
        "propagation": "Trace deletion jobs, retries, dead letters, deduplication, and failure visibility.",
        "restore_recreation": "Check restoration and replay apply deletion records before recreating derived data.",
        "canary_evidence": "Use synthetic IDs to check each declared location; inaccessible systems remain unknown.",
    },
}


def review_domain(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != {"schema", "domain", "scope", "checks"}:
        raise ValueError("Unexpected fields")
    if value["schema"] != "security-agent-skills/domain-review-v1":
        raise ValueError("Unknown schema")
    domain = value["domain"]
    if not isinstance(domain, str) or domain not in CONTROLS:
        raise ValueError("Unknown domain")
    scope = value["scope"]
    if not symbolic(scope):
        raise ValueError("Expected symbolic scope")
    checks = value["checks"]
    if not isinstance(checks, list) or len(checks) > len(CONTROLS[domain]):
        raise ValueError("Invalid check budget")
    supplied = {}
    for check in checks:
        if not isinstance(check, dict) or set(check) != {"id", "outcome", "basis", "evidence"}:
            raise ValueError("Unexpected check fields")
        identity = check["id"]
        if (
            not isinstance(identity, str)
            or identity not in CONTROLS[domain]
            or identity in supplied
        ):
            raise ValueError("Unknown or duplicate control")
        outcome, basis, refs = check["outcome"], check["basis"], check["evidence"]
        if not isinstance(outcome, str) or outcome not in {
            "pass",
            "fail",
            "unknown",
            "not_applicable",
        }:
            raise ValueError("Unknown outcome")
        if not isinstance(basis, str) or basis not in {"observed", "reproduced", "unknown"}:
            raise ValueError("Unknown basis")
        if not isinstance(refs, list) or len(refs) > 8 or any(not symbolic(ref) for ref in refs):
            raise ValueError("Invalid evidence references")
        if len(refs) != len(set(refs)):
            raise ValueError("Duplicate evidence references")
        if (outcome == "unknown" and basis != "unknown") or (
            outcome != "unknown" and (basis == "unknown" or not refs)
        ):
            raise ValueError("Inconsistent evidence basis")
        supplied[identity] = {
            "id": identity,
            "outcome": outcome,
            "basis": basis,
            "evidence": sorted(refs),
        }
    findings, states, missing = [], [], []
    for position, identity in enumerate(CONTROLS[domain], 1):
        item = supplied.get(identity)
        if item is None:
            missing.append(identity)
            item = {"id": identity, "outcome": "unknown", "basis": "unknown", "evidence": []}
        states.append(item)
        if item["outcome"] in {"fail", "unknown"}:
            message = (
                "Declared control failure needs review."
                if item["outcome"] == "fail"
                else "Control evidence is missing or unresolved."
            )
            findings.append(finding("DOMAIN-" + identity.upper(), domain, position, message))
    return report(
        "domain-review",
        scope,
        findings,
        {
            "expected_checks": len(states),
            "supplied_checks": len(supplied),
            "missing_checks": missing,
            "source_claims_verified": False,
            "runtime_observed": False,
        },
        [
            "Only declared evidence consistency was checked; references were not opened or verified.",
            "No target inspection, attack, external request, permission grant, or host change occurred.",
            "Declared passes and reproductions are not independent proof; coverage remains PARTIAL.",
        ],
        details={
            "domain": domain,
            "checks": states,
            "counts": {
                state: sum(item["outcome"] == state for item in states)
                for state in ("pass", "fail", "unknown", "not_applicable")
            },
            "executed": False,
            "authorization_granted": False,
        },
    )


def symbolic(value: Any) -> bool:
    return (
        isinstance(value, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", value) is not None
    )
