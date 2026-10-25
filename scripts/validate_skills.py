"""Validate the portable frontmatter subset without third-party packages."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []
    count = 0
    for path in sorted((ROOT / "skills").glob("*/SKILL.md")):
        count += 1
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) != 3 or parts[0].strip():
            errors.append(str(path))
            continue
        fields = {}
        for line in parts[1].strip().splitlines():
            key, value = line.split(":", 1)
            fields[key] = value.strip()
        name = fields.get("name", "")
        try:
            description = json.loads(fields.get("description", "null"))
        except ValueError:
            description = None
        if (
            not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name)
            or len(name) > 64
            or name != path.parent.name
        ):
            errors.append(name + ": invalid name")
        if not isinstance(description, str) or not 1 <= len(description) <= 1024:
            errors.append(name + ": invalid description")
        if len(parts[2]) > 5000:
            errors.append(name + ": entrypoint exceeds local character budget")
        if set(fields) != {"name", "description"}:
            errors.append(name + ": nonportable frontmatter")
        for relative in ["references/workflow.md", "scripts/run.py", "bundle-manifest.json"]:
            if not (path.parent / relative).is_file():
                errors.append(name + ": missing " + relative)
    if count != 10:
        errors.append("Expected exactly ten skills")
    print(
        json.dumps({"result": "FIX" if errors else "PASS", "skill_count": count, "errors": errors})
    )
    return bool(errors)


if __name__ == "__main__":
    raise SystemExit(main())
