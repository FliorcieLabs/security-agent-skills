# README security media

These local assets illustrate the toolkit. They do not represent security certification, a live attack, or interactive recognition inside an AI product.

| File | Purpose |
|---|---|
| [security-banner.png](security-banner.png) | Decorative circuit-node shield, generated with the built-in imagegen tool. |
| [security-demo.gif](security-demo.gif) | Five-frame rendered walkthrough of a real CLI run on synthetic text. |
| [security-demo.png](security-demo.png) | Static alternative showing the last frame. |
| [demo-fixture.txt](demo-fixture.txt) | Inert source-like text inspected by the helper. Never imported or executed. |
| [demo-compact.json](demo-compact.json) | Console JSON with two visible findings, three total, and one omitted. |
| [demo-report.json](demo-report.json) | Complete three-finding JSON report. |
| [render_demo.py](render_demo.py) | Source for the synthetic fixture, real CLI capture, and demo rendering. |

## Text walkthrough

1. The renderer creates a temporary `synthetic-demo` folder. `agent.txt` contains three source-like lines referencing environment access, an HTTP client, and subprocess execution. An `.env` file contains an inert placeholder.
2. It invokes the existing egress CLI with `--max-findings 2 --output report.json`. The helper reads text without importing it. The endpoint uses the reserved `.invalid` suffix and is never requested.
3. The helper returns `PARTIAL`, exit code `3`. It reports `sensitive-source` at `agent.txt:1`, `outbound-client` at `agent.txt:2`, and `execution-hook` at `agent.txt:3`.
4. Coverage records one text file read, one credential filename excluded, no runtime observation, and no atomic snapshot. These limits stay visible in both reports.
5. The console report has two findings and an omitted count of one. The new full report retains all three findings, stable IDs, file locations, coverage, and limitations. The temporary scope path is replaced with `<synthetic-demo>` in the committed JSON examples. No other report fields are rewritten.

The GIF is a designed summary of these results, not a terminal screen recording. Its five frames loop over 15.6 seconds without flashing effects. The PNG and this text provide alternatives to animation.

## Reproduce the demo

Use Python 3.11+ and the optional authoring dependency Pillow. Pillow is not required for the CLI or installed skills. The checked-in media were rendered with Pillow 12.3.0. Install optional dependencies in your own development environment if needed.

From the repository root:

```sh
python docs/assets/security/render_demo.py
```

The renderer asserts the CLI exit, three expected rules, compact omitted count, and coverage fields before writing its own files in this folder. It creates only synthetic temporary inputs, runs the existing local helper, and makes no network requests. Rendering replaces the generated demo PNG, GIF, fixture text, and JSON examples. It leaves the banner unchanged. Font rendering and binary image bytes can differ across Pillow versions; the fixture results are the reproducibility boundary.

## Banner provenance

The original banner was generated for this repository with the built-in imagegen tool on October 26, 2026. No source code, report, credentials, or local files were sent as input. Only the following visual prompt was supplied:

```text
Use case: logo-brand.
Asset type: a polished security illustration for an open-source AI security toolkit README.
Primary request: wide horizontal banner, approximately 3:1 aspect ratio, on a deep navy background. A single distinctive outlined shield centered in the composition, with three small connected circuit nodes inside the shield suggesting an AI agent permission boundary. Restrained teal and icy cyan luminous edges, flat dimensional editorial illustration with fine grid accents receding into the dark background, generous negative space, crisp clean silhouette, serious engineering aesthetic, subtle lighting, no photorealistic chrome.
Constraints: no text, no letters, no numbers, no checkmark, no product UI, no third-party logos, no badges, no watermark. Do not imply verified safety or certification. This is decorative project artwork.
```

The banner PNG is included as generated. The demo graphics are rendered independently with Pillow; they do not modify the generated banner. The assets and renderer are distributed with this repository under its [MIT license](../../../LICENSE).
