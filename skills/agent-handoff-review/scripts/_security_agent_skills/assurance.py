"""Bounded security decision experiments over declarations, never live targets."""

import re
from collections import deque
from typing import Any

from .reports import finding, report

LIMITS = [
    "Inputs and evidence references are caller declarations, not verified runtime observations.",
    "No target, rule code, exploit, external request, or permission change was executed.",
    "Only the declared graph, labels, exact-match predicates, or routing vocabulary was evaluated.",
    "Symbolic identifiers can still be sensitive; inspect outputs before sharing them.",
]


def _obj(value: Any, fields: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError("Unexpected record fields")
    return value


def _id(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,63}", value):
        raise ValueError("Expected symbolic identifier")
    return value


def _list(value: Any, maximum: int = 100) -> list[Any]:
    if not isinstance(value, list) or len(value) > maximum:
        raise ValueError("Expected bounded array")
    return value


def _ids(value: Any) -> list[str]:
    items = [_id(item) for item in _list(value)]
    if len(items) != len(set(items)):
        raise ValueError("Duplicate identifiers")
    return sorted(items)


def _record(value: Any, name: str, fields: set[str]) -> dict[str, Any]:
    doc = _obj(value, fields | {"schema"})
    if doc["schema"] != f"security-agent-skills/{name}-v1":
        raise ValueError("Unknown schema")
    return doc


def _choice(value: Any, choices: set[str]) -> str:
    if not isinstance(value, str) or value not in choices:
        raise ValueError("Unknown declared state")
    return value


def _result(name: str, details: dict[str, Any], leads: list[dict[str, Any]]) -> dict[str, Any]:
    return report(
        name,
        "supplied security decision record",
        leads,
        {"runtime_observed": False, "source_claims_verified": False},
        LIMITS,
        details={**details, "executed": False, "authorization_granted": False},
    )


def _paths(
    entries: list[str], edges: list[dict[str, Any]], *, possible: bool, removed: str = ""
) -> dict[str, list[str]]:
    adjacency: dict[str, list[dict[str, Any]]] = {}
    for edge in edges:
        if edge["id"] == removed or edge["state"] == "blocked":
            continue
        if not possible and (edge["state"] != "open" or not edge["evidence"]):
            continue
        adjacency.setdefault(edge["from"], []).append(edge)
    paths: dict[str, list[str]] = {entry: [] for entry in entries}
    queue = deque(entries)
    while queue:
        node = queue.popleft()
        for edge in sorted(adjacency.get(node, []), key=lambda edge: edge["id"]):
            if edge["to"] not in paths:
                paths[edge["to"]] = paths[node] + [edge["id"]]
                queue.append(edge["to"])
    return paths


def attack_path(value: Any) -> dict[str, Any]:
    """Bounded BFS passes with at most 100 nodes and 200 edge counterfactuals."""
    doc = _record(value, "attack-path", {"nodes", "entries", "assets", "edges"})
    nodes, entries, assets = (_ids(doc[key]) for key in ("nodes", "entries", "assets"))
    if not nodes or not entries or not assets or not set(entries + assets) <= set(nodes):
        raise ValueError("Missing graph scope")
    edges: list[dict[str, Any]] = []
    seen = set()
    for item in _list(doc["edges"], 200):
        edge = _obj(item, {"id", "from", "to", "state", "evidence"})
        identity, source, target = (_id(edge[key]) for key in ("id", "from", "to"))
        if identity in seen or source not in nodes or target not in nodes:
            raise ValueError("Invalid graph reference")
        seen.add(identity)
        edges.append(
            {
                "id": identity,
                "from": source,
                "to": target,
                "state": _choice(edge["state"], {"open", "blocked", "unknown"}),
                "evidence": _ids(edge["evidence"]),
            }
        )
    known = _paths(entries, edges, possible=False)
    possible = _paths(entries, edges, possible=True)
    routes = []
    leads = []
    for position, asset in enumerate(assets, 1):
        state = (
            "declared_open"
            if asset in known
            else ("requires_evidence" if asset in possible else "no_declared_route")
        )
        routes.append(
            {"asset": asset, "state": state, "edges": known.get(asset, possible.get(asset, []))}
        )
        if asset in possible:
            leads.append(
                finding(
                    "PATH-REVIEW",
                    "record",
                    position,
                    "A declared route reaches an asset; review edge evidence.",
                )
            )
    reachable = set(assets) & known.keys()
    controls = []
    for edge in sorted(edges, key=lambda edge: edge["id"]):
        after = _paths(entries, edges, possible=False, removed=edge["id"])
        interrupted = sorted(reachable - after.keys())
        if interrupted:
            controls.append({"edge": edge["id"], "assets_interrupted": interrupted})
    return _result(
        "attack-path",
        {
            "routes": routes,
            "single_edge_counterfactuals": controls,
            "route_count": len(routes),
            "counterfactual_count": len(controls),
            "evidence_references": sorted({ref for edge in edges for ref in edge["evidence"]}),
        },
        leads,
    )


def _score(expected: set[str], observed: set[str]) -> dict[str, int]:
    return {
        "tp": len(expected & observed),
        "fp": len(observed - expected),
        "fn": len(expected - observed),
    }


def _metrics(counts: dict[str, int]) -> dict[str, Any]:
    tp, fp, fn = (counts[key] for key in ("tp", "fp", "fn"))
    return {
        **counts,
        "precision": tp / (tp + fp) if tp + fp else None,
        "recall": tp / (tp + fn) if tp + fn else None,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else None,
    }


def regression_board(value: Any) -> dict[str, Any]:
    doc = _record(value, "regression-board", {"cases"})
    cases = _list(doc["cases"])
    if not cases:
        raise ValueError("No labeled cases")
    totals = {name: {"tp": 0, "fp": 0, "fn": 0} for name in ("baseline", "candidate")}
    seen: set[str] = set()
    excluded = []
    changes = []
    leads = []
    for position, item in enumerate(cases, 1):
        case = _obj(
            item, {"id", "expected", "baseline", "candidate", "baseline_status", "candidate_status"}
        )
        identity = _id(case["id"])
        if identity in seen:
            raise ValueError("Duplicate case")
        seen.add(identity)
        sets = {key: set(_ids(case[key])) for key in ("expected", "baseline", "candidate")}
        statuses = [
            _choice(case[key + "_status"], {"complete", "partial", "blocked"})
            for key in ("baseline", "candidate")
        ]
        if statuses != ["complete", "complete"]:
            excluded.append(identity)
            continue
        for name in totals:
            for key, count in _score(sets["expected"], sets[name]).items():
                totals[name][key] += count
        lost = sorted((sets["expected"] & sets["baseline"]) - sets["candidate"])
        new_fp = sorted(sets["candidate"] - sets["expected"] - sets["baseline"])
        changes.append({"case": identity, "lost_detections": lost, "new_false_positives": new_fp})
        if lost or new_fp:
            leads.append(
                finding(
                    "REGRESSION",
                    "record",
                    position,
                    "Candidate loses a labeled detection or adds a false positive.",
                )
            )
    return _result(
        "regression-board",
        {
            "case_count": len(cases),
            "scored_cases": len(cases) - len(excluded),
            "excluded_cases": excluded,
            "changes": changes,
            "metrics": {name: _metrics(counts) for name, counts in totals.items()},
            "metric_basis": "micro-averaged declared case/rule labels; no true-negative universe",
        },
        leads,
    )


def _fields(value: Any) -> dict[str, str]:
    if not isinstance(value, dict) or not 1 <= len(value) <= 16:
        raise ValueError("Expected one to sixteen exact string fields")
    for key, item in value.items():
        _id(key)
        if not isinstance(item, str) or len(item) > 256:
            raise ValueError("Expected bounded string field")
    return value


def detection_replay(value: Any) -> dict[str, Any]:
    doc = _record(value, "detection-replay", {"rules", "events"})
    rules: dict[str, dict[str, str]] = {}
    for item in _list(doc["rules"], 32):
        rule = _obj(item, {"id", "equals"})
        identity = _id(rule["id"])
        if identity in rules:
            raise ValueError("Duplicate rule")
        rules[identity] = _fields(rule["equals"])
    if not rules:
        raise ValueError("No rules")
    events = _list(doc["events"])
    if not events:
        raise ValueError("No labeled events")
    seen = set()
    totals = {"tp": 0, "fp": 0, "fn": 0}
    results = []
    leads = []
    for position, item in enumerate(events, 1):
        event = _obj(item, {"id", "fields", "expected"})
        identity = _id(event["id"])
        expected = set(_ids(event["expected"]))
        fields = _fields(event["fields"])
        if identity in seen or not expected <= rules.keys():
            raise ValueError("Invalid event or rule reference")
        seen.add(identity)
        observed = {
            key
            for key, predicate in rules.items()
            if all(fields.get(field) == text for field, text in predicate.items())
        }
        score = _score(expected, observed)
        for key, count in score.items():
            totals[key] += count
        results.append(
            {"event": identity, "expected": sorted(expected), "observed": sorted(observed), **score}
        )
        if score["fp"] or score["fn"]:
            leads.append(
                finding(
                    "DETECTION-MISMATCH",
                    "record",
                    position,
                    "Exact-match replay differs from the supplied event labels.",
                )
            )
    return _result(
        "detection-replay",
        {
            "rule_count": len(rules),
            "event_count": len(events),
            "metrics": _metrics(totals),
            "events": results,
            "engine": "case-sensitive exact string conjunction; not Sigma, SIEM, regex, or code",
        },
        leads,
    )


# A closed, reviewable routing vocabulary. This is not natural-language classification.
ROUTES = {
    "agent_egress": "agent-egress-audit",
    "dependencies": "dependency-provenance-audit",
    "mcp_authority": "mcp-authority-review",
    "app_exposure": "security-exposure-review",
    "authorized_testing": "authorized-appsec-validation",
    "package_upgrade": "agent-package-change-sentinel",
    "prompt_injection": "prompt-injection-boundary-lab",
    "secret_routes": "secret-route-mapper",
    "install_plan": "safe-install-sandbox",
    "evidence_archive": "security-evidence-pack",
    "instruction_trust": "instruction-boundary-audit",
    "ci_review": "ci-workflow-security-audit",
    "containers": "container-boundary-audit",
    "infrastructure": "infrastructure-exposure-audit",
    "llm_data": "llm-data-boundary-audit",
    "task_graph": "agent-task-planner",
    "handoff": "agent-handoff-review",
    "context_resume": "agent-context-checkpoint",
    "tool_proposal": "agent-tool-preflight",
    "retry": "agent-retry-guard",
    "attack_paths": "attack-path-rehearsal",
    "detection_rules": "detection-replay-lab",
    "regression_metrics": "security-regression-board",
    "skill_selection": "security-skill-router",
}


def skill_route(value: Any) -> dict[str, Any]:
    doc = _record(value, "skill-route", {"goals", "max_skills"})
    goals = _ids(doc["goals"])
    budget = doc["max_skills"]
    if not goals or type(budget) is not int or not 1 <= budget <= 24:
        raise ValueError("Invalid routing budget")
    unknown = sorted(set(goals) - ROUTES.keys())
    candidates = sorted({ROUTES[goal] for goal in goals if goal in ROUTES})
    selected = candidates[:budget]
    deferred = candidates[budget:]
    leads = (
        [
            finding(
                "ROUTE-INCOMPLETE",
                "record",
                1,
                "Unknown goals or a selection cap leave required work unresolved.",
            )
        ]
        if unknown or deferred
        else []
    )
    return _result(
        "skill-route",
        {
            "selected": selected,
            "deferred": deferred,
            "unknown_goals": unknown,
            "selected_count": len(selected),
            "candidate_count": len(candidates),
            "catalog_count": len(ROUTES),
            "selection_order": "lexical, not risk priority",
            "load_references": [f"skills/{name}/SKILL.md" for name in selected],
            "selection_complete": not unknown and not deferred,
        },
        leads,
    )


ASSURANCE = {
    "attack-path": attack_path,
    "detection-replay": detection_replay,
    "regression-board": regression_board,
    "skill-route": skill_route,
}
