"""Fixture identity follows JSON meaning, not Git newline conversion."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "header_benchmark", ROOT / "scripts/benchmark_header_output.py"
)
benchmark_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark_module)


class HeaderBenchmarkTests(unittest.TestCase):
    def test_fixture_hashes_survive_checkout_formatting_but_detect_content_changes(self):
        baseline = benchmark_module.benchmark()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            examples = root / "examples/adapted-headers"
            examples.mkdir(parents=True)
            for path in (ROOT / "examples/adapted-headers").glob("*.json"):
                record = json.loads(path.read_bytes())
                reordered = dict(reversed(list(record.items())))
                text = json.dumps(reordered, indent=4).replace("\n", "\r\n")
                (examples / path.name).write_bytes(text.encode("utf-8"))
            with patch.object(benchmark_module, "ROOT", root):
                self.assertEqual(benchmark_module.benchmark(), baseline)
                path = examples / "email-headers.json"
                record = json.loads(path.read_bytes())
                record["headers"] = record["headers"].replace(
                    "sender@example.invalid", "other@example.invalid"
                )
                path.write_text(json.dumps(record), encoding="utf-8")
                changed = benchmark_module.benchmark()
                self.assertNotEqual(
                    changed["cases"][0]["fixture_sha256"], baseline["cases"][0]["fixture_sha256"]
                )
