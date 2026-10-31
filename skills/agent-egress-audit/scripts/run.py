"""Standalone skill entrypoint. No target code is imported."""
import sys
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _security_agent_skills.cli import main
arguments = sys.argv[1:]
command = arguments.pop(0) if arguments and arguments[0] in [] else 'egress'
if __name__ == "__main__":
    raise SystemExit(main([command, *arguments]))
