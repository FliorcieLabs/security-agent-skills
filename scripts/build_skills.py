"""Build deterministic self-contained bundles; --check never writes."""

import argparse
import json
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generated_files():
    catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    package = ROOT / "src/security_agent_skills"
    for skill in catalog:
        base = ROOT / "skills" / skill["name"]
        command = skill["command"]
        modes = {"compare": ["snapshot"], "pack": ["verify"]}.get(command, [])
        launcher = (
            '"""Standalone skill entrypoint. No target code is imported."""\n'
            "import sys\nfrom pathlib import Path\nsys.dont_write_bytecode = True\n"
            "sys.path.insert(0, str(Path(__file__).resolve().parent))\n"
            "from _security_agent_skills.cli import main\n"
            "arguments = sys.argv[1:]\n"
            f"command = arguments.pop(0) if arguments and arguments[0] in {modes!r} else {command!r}\n"
            'if __name__ == "__main__":\n    raise SystemExit(main([command, *arguments]))\n'
        ).encode()
        files = {
            "scripts/run.py": launcher,
            "LICENSE": (ROOT / "LICENSE").read_bytes().replace(b"\r\n", b"\n"),
        }
        for source in sorted(package.glob("*.py")):
            files["scripts/_security_agent_skills/" + source.name] = source.read_bytes().replace(
                b"\r\n", b"\n"
            )
        files["SKILL.md"] = (base / "SKILL.md").read_bytes().replace(b"\r\n", b"\n")
        files["references/workflow.md"] = (
            (base / "references/workflow.md").read_bytes().replace(b"\r\n", b"\n")
        )
        manifest = {name: sha256(raw).hexdigest() for name, raw in sorted(files.items())}
        files["bundle-manifest.json"] = (
            json.dumps(manifest, sort_keys=True, indent=2) + "\n"
        ).encode()
        for relative, raw in files.items():
            yield base / relative, raw


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    errors = []
    count = 0
    for target, raw in generated_files():
        count += 1
        if args.check:
            if not target.is_file() or target.read_bytes() != raw:
                errors.append(str(target.relative_to(ROOT)))
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
    print(
        json.dumps(
            {"result": "FIX" if errors else "PASS", "generated_files": count, "mismatches": errors}
        )
    )
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
