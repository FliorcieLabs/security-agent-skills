"""Launch the optional local record-only MCP server from a source checkout."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from security_agent_skills.mcp_stdio import main

if __name__ == "__main__":
    raise SystemExit(main())
