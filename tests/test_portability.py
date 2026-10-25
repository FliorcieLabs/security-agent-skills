import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("installer", ROOT / "scripts/install_skills.py")
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class PortabilityTests(unittest.TestCase):
    def test_preview_has_no_writes_and_native_host_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = installer.plan_install("all", directory, ["agent-egress-audit"])
            self.assertEqual(len(plan), 4)
            self.assertEqual(list(Path(directory).iterdir()), [])
            self.assertTrue(any(".github" in p["destination"] for p in plan))

    def test_install_is_standalone_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = installer.plan_install("codex", directory, ["agent-egress-audit"])
            installer.apply_plan(plan)
            target = Path(plan[0]["destination"])
            result = subprocess.run(
                [sys.executable, str(target / "scripts/run.py"), "--help"],
                cwd=directory,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            with self.assertRaises(FileExistsError):
                installer.plan_install("codex", directory, ["agent-egress-audit"])

    def test_all_ten_entrypoints_load_without_repo_context(self):
        with tempfile.TemporaryDirectory() as directory:
            for path in (ROOT / "skills").glob("*/scripts/run.py"):
                r = subprocess.run(
                    [sys.executable, str(path), "--help"], cwd=directory, capture_output=True
                )
                self.assertEqual(r.returncode, 0, (path, r.stderr))

    def test_shared_bundle_is_complete_for_each_host(self):
        with tempfile.TemporaryDirectory() as directory:
            plan = installer.plan_install("all", directory, ["security-evidence-pack"])
            installer.apply_plan(plan)
            for entry in plan:
                run = Path(entry["destination"]) / "scripts/run.py"
                result = subprocess.run(
                    [sys.executable, str(run), "--help"], cwd=directory, capture_output=True
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_bundle_detects_unaccounted_files(self):
        import shutil

        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / "skill"
            shutil.copytree(ROOT / "skills/agent-egress-audit", copy)
            (copy / "unexpected.py").write_text("print('unexpected')")
            with self.assertRaises(ValueError):
                installer.verify_bundle(copy)
