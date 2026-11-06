# Repository contract

Build portable, local security skills. Never execute reviewed package code during static inspection. Do not upload source, findings, credentials, or manifests. No network is required by the analysis CLI. Explicit GitHub repository maintenance authorized by the maintainer is separate from the shipped tools.

Keep each skill small. Use the shared report schema. Preserve partial coverage and unknown outcomes. A pattern match is a review lead, not proof of exploitability or exfiltration. No security score establishes safety. Do not bypass host permission checks. Require explicit target authorization before active tests; the built-in AppSec helper only validates a plan.

Validate with `python -m unittest discover -s tests -t . -v`, `python scripts/validate_skills.py`, and `python scripts/build_skills.py --check`. Runtime code uses Python 3.11+ standard library only. Keep Claude, Codex, Cursor, and Copilot adapters free of machine-specific paths. Installers preview changes and never overwrite existing files. Do not publish packages, create tags, or enable automatic releases without maintainer authorization.
