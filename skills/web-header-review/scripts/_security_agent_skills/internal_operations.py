"""Offline checks of declared operation records, never an agent runtime or authority grant."""

import re
from collections import deque
from typing import Any

from .reports import finding, report

LIMITS = [
    "Only a supplied local record was checked; its claims and referenced evidence were not verified.",
    "No agent, tool, retry, network request, or permission change was executed or authorized.",
    "Reference identifiers can be sensitive. Inspect reports before sharing them with an assistant.",
]


def _object(value: Any, fields: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError("Record fields do not match the contract")
    return value


def _identifier(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", value):
        raise ValueError("Expected a bounded symbolic identifier")
    return value


def _identifiers(value: Any) -> list[str]:
    if not isinstance(value, list) or len(value) > 100:
        raise ValueError("Expected a bounded reference list")
    items = [_identifier(item) for item in value]
    if len(set(items)) != len(items):
        raise ValueError("Duplicate references")
    return items


def _integer(value: Any, minimum: int, maximum: int) -> int:
    if type(value) is not int or not minimum <= value <= maximum:
        raise ValueError("Integer outside the contract budget")
    return value


def _boolean(value: Any) -> bool:
    if type(value) is not bool:
        raise ValueError("Expected a boolean")
    return value


def _choice(value: Any, choices: set[str]) -> str:
    if not isinstance(value, str) or value not in choices:
        raise ValueError("Unknown contract value")
    return value


def _record(value: Any, schema: str, fields: set[str]) -> dict[str, Any]:
    record = _object(value, fields | {"schema"})
    if record["schema"] != f"security-agent-skills/{schema}-v1":
        raise ValueError("Unknown operation schema")
    return record


def _result(
    name: str,
    failures: list[tuple[str, int, str]],
    details: dict[str, Any],
    *,
    success: str = "PASS",
    failure: str = "FIX",
) -> dict[str, Any]:
    return report(
        name,
        "supplied local operation record",
        [finding(rule, "record", position, message) for rule, position, message in failures],
        {"records_validated": 1, "runtime_observed": False, "source_claims_verified": False},
        LIMITS,
        result=failure if failures else success,
        details={**details, "executed": False, "authorization_granted": False},
    )


def task_plan(value: Any) -> dict[str, Any]:
    doc = _record(value, "task-plan", {"tasks", "max_total_steps"})
    budget = _integer(doc["max_total_steps"], 1, 1000)
    tasks = doc["tasks"]
    if not isinstance(tasks, list) or not 1 <= len(tasks) <= 100:
        raise ValueError("Expected one to one hundred tasks")
    ids: dict[str, int] = {}
    dependencies: list[list[str]] = []
    resources: set[str] = set()
    failures: list[tuple[str, int, str]] = []
    steps = 0
    for position, value in enumerate(tasks, 1):
        task = _object(
            value,
            {"id", "owner", "depends_on", "write_resources", "max_steps", "evidence_required"},
        )
        identity = _identifier(task["id"])
        _identifier(task["owner"])
        if identity in ids:
            raise ValueError("Duplicate task identifier")
        ids[identity] = position - 1
        dependencies.append(_identifiers(task["depends_on"]))
        writes = set(_identifiers(task["write_resources"]))
        if resources & writes:
            failures.append(
                (
                    "shared-write-owner",
                    position,
                    "A write resource has multiple task owners; split ownership or plan a separate serial phase.",
                )
            )
        resources.update(writes)
        steps += _integer(task["max_steps"], 1, 100)
        if not _boolean(task["evidence_required"]):
            failures.append(
                (
                    "missing-task-evidence",
                    position,
                    "Completion evidence is not required for this task.",
                )
            )
    edges: list[list[int]] = [[] for _ in tasks]
    remaining = [0] * len(tasks)
    for index, names in enumerate(dependencies):
        for name in names:
            if name not in ids:
                failures.append(
                    (
                        "unknown-task-dependency",
                        index + 1,
                        "A dependency does not name a task in this plan.",
                    )
                )
            else:
                edges[ids[name]].append(index)
                remaining[index] += 1
    queue = deque(index for index, count in enumerate(remaining) if count == 0)
    order = []
    while queue:
        index = queue.popleft()
        order.append(index + 1)
        for child in edges[index]:
            remaining[child] -= 1
            if remaining[child] == 0:
                queue.append(child)
    if len(order) != len(tasks):
        failures.append(("cyclic-task-plan", 1, "The dependency graph contains a cycle."))
    if steps > budget:
        failures.append(
            ("task-step-budget", 1, "The sum of declared task step caps exceeds the plan budget.")
        )
    return _result(
        "agent-task-planner",
        failures,
        {
            "task_count": len(tasks),
            "declared_steps": steps,
            "max_total_steps": budget,
            "candidate_order_positions": [] if failures else order,
            "next_action": "revise_plan" if failures else "review_plan_before_execution",
        },
    )


def handoff_review(value: Any) -> dict[str, Any]:
    doc = _record(
        value,
        "handoff",
        {
            "task_id",
            "source_agent",
            "target_agent",
            "parent_permissions",
            "delegated_permissions",
            "acceptance_refs",
            "evidence_refs",
            "unresolved_refs",
            "status",
        },
    )
    _identifier(doc["task_id"])
    source, target = _identifier(doc["source_agent"]), _identifier(doc["target_agent"])
    parent = set(_identifiers(doc["parent_permissions"]))
    delegated = set(_identifiers(doc["delegated_permissions"]))
    acceptance = _identifiers(doc["acceptance_refs"])
    evidence = _identifiers(doc["evidence_refs"])
    unresolved = _identifiers(doc["unresolved_refs"])
    status = _choice(doc["status"], {"ready", "blocked", "complete"})
    failures = []
    if delegated - parent:
        failures.append(
            (
                "handoff-authority-expansion",
                1,
                "Delegated permissions exceed the declared parent permissions.",
            )
        )
    if source == target:
        failures.append(("handoff-same-agent", 1, "Source and target identify the same agent."))
    if not acceptance:
        failures.append(("handoff-no-acceptance", 1, "The handoff omits acceptance references."))
    if not evidence:
        failures.append(("handoff-no-evidence", 1, "The handoff omits evidence references."))
    if status == "complete" and unresolved:
        failures.append(
            (
                "handoff-unresolved-completion",
                1,
                "Completion is claimed while unresolved references remain.",
            )
        )
    if status == "blocked" and not unresolved:
        failures.append(
            (
                "handoff-no-blocker",
                1,
                "Blocked status omits unresolved references explaining the blocker.",
            )
        )
    return _result(
        "agent-handoff-review",
        failures,
        {
            "acceptance_count": len(acceptance),
            "evidence_count": len(evidence),
            "unresolved_count": len(unresolved),
            "declared_status": status,
            "next_action": (
                "revise_handoff" if failures else "review_source_evidence_before_handoff"
            ),
        },
    )


def context_checkpoint(value: Any) -> dict[str, Any]:
    doc = _record(
        value,
        "checkpoint",
        {
            "objective_ref",
            "revision_ref",
            "constraint_refs",
            "evidence_refs",
            "unresolved_refs",
            "decision_refs",
            "next_action_ref",
            "max_refs",
        },
    )
    core = {
        name: _identifier(doc[name])
        for name in ("objective_ref", "revision_ref", "next_action_ref")
    }
    mandatory = {
        name: _identifiers(doc[name])
        for name in ("constraint_refs", "evidence_refs", "unresolved_refs")
    }
    decisions = _identifiers(doc["decision_refs"])
    budget = _integer(doc["max_refs"], 1, 400)
    required = len(core) + sum(map(len, mandatory.values()))
    failures = []
    if not mandatory["constraint_refs"]:
        failures.append(
            ("checkpoint-no-constraints", 1, "A checkpoint must retain constraint references.")
        )
    if not mandatory["evidence_refs"]:
        failures.append(
            ("checkpoint-no-evidence", 1, "A checkpoint must retain evidence references.")
        )
    if required > budget:
        failures.append(
            (
                "checkpoint-budget",
                1,
                "Mandatory references exceed the budget; raise it or narrow the task without dropping constraints, evidence, or unresolved work.",
            )
        )
    retained = decisions[: max(0, budget - required)]
    return _result(
        "agent-context-checkpoint",
        failures,
        {
            "capsule": {} if failures else {**core, **mandatory, "decision_refs": retained},
            "mandatory_refs": required,
            "decision_refs_omitted": len(decisions) - len(retained),
            "next_action": (
                "revise_checkpoint" if failures else "resolve_references_and_recheck_freshness"
            ),
        },
        success="PARTIAL",
        failure="BLOCKED",
    )


def tool_preflight(value: Any) -> dict[str, Any]:
    doc = _record(value, "preflight", {"policy", "action"})
    policy = _object(
        doc["policy"],
        {
            "allowed_tools",
            "allowed_resources",
            "allowed_effects",
            "external_transfer_allowed",
            "approval_required_for_write",
        },
    )
    action = _object(
        doc["action"],
        {
            "tool",
            "resources",
            "effect",
            "external_transfer",
            "approval_recorded",
        },
    )
    tools = _identifiers(policy["allowed_tools"])
    resources = _identifiers(policy["allowed_resources"])
    effects = _identifiers(policy["allowed_effects"])
    if not set(effects) <= {"read", "write"}:
        raise ValueError("Unknown policy effect")
    tool = _identifier(action["tool"])
    targets = _identifiers(action["resources"])
    if not targets:
        raise ValueError("Action resources are required")
    effect = _choice(action["effect"], {"read", "write"})
    external_allowed = _boolean(policy["external_transfer_allowed"])
    approval_required = _boolean(policy["approval_required_for_write"])
    external = _boolean(action["external_transfer"])
    approval = _boolean(action["approval_recorded"])
    failures = []
    if tool not in tools:
        failures.append(
            ("preflight-tool", 1, "The proposed tool is outside the declared allowlist.")
        )
    if not set(targets) <= set(resources):
        failures.append(
            ("preflight-resource", 1, "A proposed resource is outside the declared allowlist.")
        )
    if effect not in effects:
        failures.append(
            ("preflight-effect", 1, "The proposed effect is outside the declared allowlist.")
        )
    if external and not external_allowed:
        failures.append(
            (
                "preflight-external-transfer",
                1,
                "The proposal declares an external transfer that the supplied policy does not allow.",
            )
        )
    if effect == "write" and approval_required and not approval:
        failures.append(
            (
                "preflight-write-approval",
                1,
                "The supplied policy requires recorded approval for a write.",
            )
        )
    return _result(
        "agent-tool-preflight",
        failures,
        {
            "declared_policy_match": not failures,
            "next_action": (
                "stop_and_resolve_policy"
                if failures
                else "verify_host_permission_and_fresh_authorization"
            ),
        },
        success="PARTIAL",
        failure="BLOCKED",
    )


def retry_guard(value: Any) -> dict[str, Any]:
    doc = _record(
        value, "retry", {"effect", "outcome", "attempts", "max_attempts", "reconciliation"}
    )
    effect = _choice(doc["effect"], {"read", "write"})
    outcome = _choice(doc["outcome"], {"not_started", "succeeded", "failed_no_effect", "unknown"})
    attempts = _integer(doc["attempts"], 0, 100)
    maximum = _integer(doc["max_attempts"], 1, 100)
    reconciliation = _choice(
        doc["reconciliation"], {"not_checked", "effect_absent", "effect_present", "inconclusive"}
    )
    failures = []
    if (outcome == "not_started") != (attempts == 0):
        raise ValueError("Attempt count contradicts the declared outcome")
    if outcome == "succeeded" and reconciliation == "effect_absent":
        raise ValueError("Success contradicts reconciliation")
    if outcome in {"not_started", "failed_no_effect"} and reconciliation == "effect_present":
        raise ValueError("No-effect outcome contradicts reconciliation")
    if effect == "read" and reconciliation != "not_checked":
        raise ValueError("Effect reconciliation is only defined for writes")
    if outcome != "unknown" and reconciliation == "inconclusive":
        raise ValueError("Conclusive outcome contradicts inconclusive reconciliation")
    success = "PARTIAL"
    if outcome == "succeeded" or reconciliation == "effect_present":
        next_action = "stop_without_retry"
        success = "PASS"
    elif attempts >= maximum:
        next_action = "stop_budget_exhausted"
        failures.append(("retry-budget-exhausted", 1, "The declared attempt budget is exhausted."))
    elif effect == "write" and outcome == "unknown" and reconciliation != "effect_absent":
        next_action = "reconcile_ambiguous_write"
        failures.append(
            (
                "retry-ambiguous-write",
                1,
                "A write may have taken effect; reconcile its outcome before considering another attempt.",
            )
        )
    else:
        next_action = "review_candidate_with_host_policy"
    return _result(
        "agent-retry-guard",
        failures,
        {
            "next_action": next_action,
            "attempts_remaining": max(0, maximum - attempts),
            "retry_executed": False,
        },
        success=success,
        failure="BLOCKED",
    )


OPERATIONS = {
    "task-plan": task_plan,
    "handoff": handoff_review,
    "checkpoint": context_checkpoint,
    "preflight": tool_preflight,
    "retry": retry_guard,
}
