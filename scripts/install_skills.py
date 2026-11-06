"""Portable copy installer. Preview by default; collisions are never overwritten."""

import argparse
import json
import sys
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from security_agent_skills.inventory import reparse

HOSTS = {
    "claude": (".claude/skills", ".claude/skills"),
    "codex": (".agents/skills", ".agents/skills"),
    "cursor": (".cursor/skills", ".cursor/skills"),
    "copilot": (".github/skills", ".copilot/skills"),
}
SOURCE = Path(__file__).resolve().parents[1] / "skills"


def verify_bundle(source):
    manifest = json.loads((source / "bundle-manifest.json").read_text(encoding="utf-8"))
    actual = {
        p.relative_to(source).as_posix(): p
        for p in source.rglob("*")
        if p.is_file()
        and "__pycache__" not in p.parts
        and p.suffix != ".pyc"
        and p.name != "bundle-manifest.json"
    }
    if not isinstance(manifest, dict) or set(actual) != set(manifest):
        raise ValueError("Bundle inventory mismatch")
    for name, path in actual.items():
        if reparse(path) or sha256(path.read_bytes()).hexdigest() != manifest[name]:
            raise ValueError("Bundle digest mismatch")


def plan_install(agent, root, names, *, personal=False):
    root = Path(root).absolute()
    if not root.is_dir() or reparse(root):
        raise ValueError("Choose an existing non-link root")
    root = root.resolve()
    agents = list(HOSTS) if agent == "all" else [agent]
    plan = []
    for host in agents:
        if host not in HOSTS:
            raise ValueError("Unsupported host")
        destination = root / HOSTS[host][1 if personal else 0]
        for name in names:
            if name not in {
                p.name for p in SOURCE.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()
            }:
                raise ValueError("Unknown skill")
            target = destination / name
            for ancestor in [target, *target.parents]:
                if ancestor == root:
                    break
                if ancestor.exists() or ancestor.is_symlink():
                    if reparse(ancestor):
                        raise ValueError("Installation path contains a link or reparse point")
            if not target.resolve().is_relative_to(root):
                raise ValueError("Destination leaves selected root")
            if target.exists():
                raise FileExistsError("Destination already exists; no replacement permitted")
            for path in (SOURCE / name).rglob("*"):
                if reparse(path):
                    raise ValueError("Source bundle contains a link")
            verify_bundle(SOURCE / name)
            plan.append(
                {
                    "host": host,
                    "skill": name,
                    "source": str(SOURCE / name),
                    "destination": str(target),
                }
            )
    return plan


def apply_plan(plan):
    installed = []
    for entry in plan:
        source = Path(entry["source"])
        target = Path(entry["destination"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.mkdir()  # Reserve a new destination; never reuse an existing skill directory.
        for path in sorted(source.rglob("*")):
            rel = path.relative_to(source)
            if "__pycache__" in rel.parts or path.suffix == ".pyc":
                continue
            destination = target / rel
            if path.is_dir():
                destination.mkdir()
            else:
                with destination.open("xb") as stream:
                    stream.write(path.read_bytes())
        installed.append(
            {"host": entry["host"], "skill": entry["skill"], "destination": str(target)}
        )
    return installed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=[*HOSTS, "all"], required=True)
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--project", type=Path)
    scope.add_argument("--global", dest="personal", action="store_true")
    parser.add_argument("--skill", action="append")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        names = args.skill or sorted(
            p.name for p in SOURCE.iterdir() if p.is_dir() and (p / "SKILL.md").exists()
        )
        if len(set(names)) != len(names):
            raise ValueError("Duplicate selected skill")
        plan = plan_install(
            args.agent,
            Path.home() if args.personal else args.project,
            names,
            personal=args.personal,
        )
        changes = apply_plan(plan) if args.apply else plan
        print(
            json.dumps(
                {
                    "result": "PASS",
                    "mode": "installed" if args.apply else "preview",
                    "changes": changes,
                },
                indent=2,
            )
        )
        return 0
    except (OSError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "result": "BLOCKED",
                    "reason": type(exc).__name__,
                    "detail": "Check selected roots, links, and existing destinations. A failed copy may leave its new directory for inspection; nothing is recursively deleted.",
                }
            )
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
