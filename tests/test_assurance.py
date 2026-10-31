"""Security decision fixtures verify actual algorithms and conservative coverage."""

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from security_agent_skills.assurance import (
    ASSURANCE,
    ROUTES,
    attack_path,
    detection_replay,
    regression_board,
    skill_route,
)
from security_agent_skills.assurance_contracts import CONTRACTS

ROOT = Path(__file__).resolve().parents[1]


def example(name):
    return json.loads((ROOT / "examples/assurance" / (name + ".json")).read_text())


class AssuranceTests(unittest.TestCase):
    def test_published_shape_contracts_match_discovered_mcp_contracts(self):
        document = json.loads((ROOT / "schemas/assurance-v1.schema.json").read_text())
        self.assertEqual(document["oneOf"], list(CONTRACTS.values()))

    def test_graph_unknown_edge_does_not_become_proven_route(self):
        value = attack_path(example("attack-path"))
        self.assertEqual(value["details"]["routes"][0]["state"], "requires_evidence")
        self.assertEqual(value["details"]["single_edge_counterfactuals"], [])
        self.assertEqual(value["result"], "PARTIAL")

    def test_graph_single_edge_control_and_missing_evidence(self):
        doc = example("attack-path")
        doc["edges"][1].update(state="open", evidence=["reviewB"])
        value = attack_path(doc)["details"]
        self.assertEqual(value["routes"][0]["edges"], ["retrieval", "readVault"])
        self.assertEqual(value["counterfactual_count"], 2)
        doc["edges"][1]["evidence"] = []
        self.assertEqual(attack_path(doc)["details"]["routes"][0]["state"], "requires_evidence")

    def test_graph_alternate_paths_are_not_single_edge_cuts(self):
        doc = example("attack-path")
        doc["edges"][1].update(state="open", evidence=["reviewB"])
        doc["edges"].append(
            {
                "id": "direct",
                "from": "entry",
                "to": "vault",
                "state": "open",
                "evidence": ["reviewC"],
            }
        )
        self.assertEqual(attack_path(doc)["details"]["single_edge_counterfactuals"], [])

    def test_graph_blocked_path_cycles_and_entry_asset(self):
        doc = example("attack-path")
        doc["edges"][1]["state"] = "blocked"
        doc["edges"].append(
            {
                "id": "cycle",
                "from": "agent",
                "to": "entry",
                "state": "open",
                "evidence": ["reviewD"],
            }
        )
        self.assertEqual(attack_path(doc)["details"]["routes"][0]["state"], "no_declared_route")
        doc["assets"] = ["entry"]
        value = attack_path(doc)["details"]
        self.assertEqual(value["routes"][0]["edges"], [])
        self.assertEqual(value["routes"][0]["state"], "declared_open")

    def test_graph_rejects_duplicate_ids_unknown_nodes_and_overflow(self):
        doc = example("attack-path")
        mutations = [
            lambda d: d["edges"].append(d["edges"][0]),
            lambda d: d["edges"][0].update(to="missing"),
            lambda d: d.update(nodes=["n" + str(i) for i in range(101)]),
            lambda d: d.update(edges=d["edges"] * 101),
            lambda d: d.update(entries=[]),
        ]
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                value = copy.deepcopy(doc)
                mutate(value)
                with self.assertRaises(ValueError):
                    attack_path(value)

    def test_graph_results_ignore_input_order(self):
        doc = example("attack-path")
        before = attack_path(doc)
        doc["nodes"].reverse()
        doc["edges"].reverse()
        self.assertEqual(before, attack_path(doc))

    def test_replay_detects_schema_drift_and_preserves_privacy(self):
        doc = example("detection-replay")
        doc["events"][0]["fields"]["privateNote"] = "SENSITIVE_SYNTHETIC_VALUE"
        output = detection_replay(doc)
        metric = output["details"]["metrics"]
        self.assertEqual((metric["tp"], metric["fp"], metric["fn"]), (1, 0, 1))
        self.assertEqual(metric["precision"], 1)
        self.assertEqual(metric["recall"], 0.5)
        self.assertNotIn("SENSITIVE_SYNTHETIC_VALUE", json.dumps(output))
        self.assertNotIn("privateNote", json.dumps(output))

    def test_replay_exact_conjunction_false_positive_and_case(self):
        doc = example("detection-replay")
        doc["rules"][0]["equals"] = {"effect": "write"}
        output = detection_replay(doc)
        self.assertEqual(output["details"]["metrics"]["fn"], 0)
        doc["events"][1]["fields"]["effect"] = "write"
        self.assertEqual(detection_replay(doc)["details"]["metrics"]["fp"], 1)
        doc["events"][0]["fields"]["effect"] = "WRITE"
        self.assertEqual(detection_replay(doc)["details"]["metrics"]["fn"], 1)

    def test_replay_rejects_dangling_labels_and_executable_predicates(self):
        doc = example("detection-replay")
        doc["events"][0]["expected"] = ["unknownRule"]
        with self.assertRaises(ValueError):
            detection_replay(doc)
        doc = example("detection-replay")
        doc["rules"][0]["equals"] = {"effect": {"eval": "arbitrary"}}
        with self.assertRaises(ValueError):
            detection_replay(doc)

    def test_replay_rejects_empty_duplicate_and_excessive_records(self):
        for key in ("rules", "events"):
            for count in (0, 101):
                doc = example("detection-replay")
                doc[key] = doc[key][:1] * count
                with self.assertRaises(ValueError):
                    detection_replay(doc)
        doc = example("detection-replay")
        doc["events"].append(doc["events"][0])
        with self.assertRaises(ValueError):
            detection_replay(doc)

    def test_regression_pair_exclusions_and_measured_labels(self):
        value = regression_board(example("regression-board"))["details"]
        self.assertEqual(value["scored_cases"], 2)
        self.assertEqual(value["excluded_cases"], ["unavailableHost"])
        self.assertEqual(value["metrics"]["baseline"]["f1"], 0)
        self.assertEqual(value["metrics"]["candidate"]["f1"], 1)

    def test_regression_aggregate_improvement_does_not_hide_lost_detection(self):
        doc = example("regression-board")
        doc["cases"][0].update(expected=["a", "b", "c"], baseline=["a"], candidate=["b", "c"])
        value = regression_board(doc)
        self.assertEqual(value["details"]["changes"][0]["lost_detections"], ["a"])
        self.assertEqual(value["finding_count"], 1)

    def test_regression_all_excluded_and_undefined_denominators(self):
        doc = example("regression-board")
        for case in doc["cases"]:
            case["candidate_status"] = "partial"
        value = regression_board(doc)
        self.assertEqual(value["result"], "PARTIAL")
        self.assertEqual(value["details"]["scored_cases"], 0)
        self.assertIsNone(value["details"]["metrics"]["candidate"]["precision"])
        self.assertIsNone(value["details"]["metrics"]["candidate"]["recall"])

    def test_regression_new_false_positive_and_duplicate_cases(self):
        doc = example("regression-board")
        doc["cases"][0]["candidate"].append("spurious")
        self.assertEqual(regression_board(doc)["finding_count"], 1)
        doc["cases"].append(doc["cases"][0])
        with self.assertRaises(ValueError):
            regression_board(doc)

    def test_router_preserves_deferred_unknowns_and_never_invents_skills(self):
        doc = example("skill-route")
        doc["goals"].append("unknown")
        value = skill_route(doc)["details"]
        self.assertEqual(value["selected_count"], 2)
        self.assertEqual(len(value["deferred"]), 1)
        self.assertEqual(value["unknown_goals"], ["unknown"])
        self.assertFalse(value["selection_complete"])

    def test_router_vocabulary_matches_catalog_and_cap_types(self):
        catalog = json.loads((ROOT / "catalog.json").read_text())
        self.assertEqual(set(ROUTES.values()), {item["name"] for item in catalog})
        for budget in (True, False, 0, 25, "2"):
            doc = example("skill-route")
            doc["max_skills"] = budget
            with self.assertRaises(ValueError):
                skill_route(doc)

    def test_all_contracts_reject_unknown_fields_versions_and_identifiers(self):
        for name, operation in ASSURANCE.items():
            for field, bad in (("schema", "other"), ("extra", "private")):
                doc = example(name)
                doc[field] = bad
                with self.assertRaises(ValueError):
                    operation(doc)
            for doc in ([], None, True, "private"):
                with self.assertRaises(ValueError):
                    operation(doc)
        doc = example("skill-route")
        doc["goals"] = ["../../private"]
        with self.assertRaises(ValueError):
            skill_route(doc)

    def test_cli_invalid_record_and_duplicate_keys_do_not_echo_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            for raw in (
                '{"schema":"private-secret","schema":"other"}',
                '{"schema":"private-secret"}',
            ):
                path.write_text(raw)
                result = subprocess.run(
                    [
                        sys.executable,
                        str(ROOT / "scripts/security_check.py"),
                        "skill-route",
                        str(path),
                    ],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 2)
                self.assertNotIn("private-secret", result.stdout + result.stderr)

    def test_all_valid_records_remain_partial_and_do_not_mutate_input(self):
        for name, operation in ASSURANCE.items():
            doc = example(name)
            before = copy.deepcopy(doc)
            value = operation(doc)
            self.assertEqual(doc, before)
            self.assertEqual(operation(doc), value)
            self.assertEqual(value["result"], "PARTIAL")
            self.assertFalse(value["coverage"]["source_claims_verified"])
            self.assertFalse(value["details"]["executed"])
