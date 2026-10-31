"""Opt-in record-only MCP stdio server. No file paths, sockets, sampling, or shell tools."""

import json
import sys
from typing import Any, BinaryIO

from . import __version__
from .assurance import ASSURANCE
from .assurance_contracts import CONTRACTS, obj

PROTOCOLS = ("2025-11-25", "2025-06-18")
MAX_MESSAGE_BYTES = 1_000_000
DESCRIPTIONS = {
    "attack-path": "Analyze a declared graph and single-edge counterfactuals. Not a live attack.",
    "detection-replay": "Replay exact-match predicates on supplied labeled events. Not Sigma or SIEM.",
    "regression-board": "Compare supplied paired case/rule labels. No external benchmark claims.",
    "skill-route": "Select skills using declared goals and a cap. No host installation or execution.",
}


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON key")
        result[key] = value
    return result


def _constant(value: str) -> Any:
    raise ValueError("Nonfinite JSON number")


def error(identity: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": identity, "error": {"code": code, "message": message}}


class Session:
    def __init__(self) -> None:
        self.initialized = False
        self.ready = False

    def handle(self, message: Any) -> dict[str, Any] | None:
        if not isinstance(message, dict):
            return error(None, -32600, "Expected one JSON-RPC object")
        identity = message.get("id")
        if identity is not None and type(identity) not in (str, int):
            return error(None, -32600, "Invalid request identifier")
        if (
            message.get("jsonrpc") != "2.0"
            or not isinstance(message.get("method"), str)
            or set(message) - {"jsonrpc", "id", "method", "params"}
        ):
            return error(identity, -32600, "Invalid request")
        method = message["method"]
        params = message.get("params", {})
        # Notifications never receive a response or trigger a tool call.
        if "id" not in message:
            if (
                method == "notifications/initialized"
                and self.initialized
                and isinstance(params, dict)
            ):
                self.ready = True
            return None
        if not isinstance(params, dict):
            return error(identity, -32602, "Expected object parameters")
        # MCP request metadata is transport context, never tool authority or record input.
        if "_meta" in params:
            if not isinstance(params["_meta"], dict):
                return error(identity, -32602, "Expected object metadata")
            params = {key: value for key, value in params.items() if key != "_meta"}
        if method == "ping":
            result: dict[str, Any] = {}
        elif method == "initialize":
            if self.initialized:
                return error(identity, -32600, "Already initialized")
            if (
                not isinstance(params.get("protocolVersion"), str)
                or not isinstance(params.get("capabilities"), dict)
                or not isinstance(params.get("clientInfo"), dict)
            ):
                return error(identity, -32602, "Missing initialization fields")
            proposed = params["protocolVersion"]
            version = proposed if proposed in PROTOCOLS else PROTOCOLS[0]
            self.initialized = True
            result = {
                "protocolVersion": version,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": "security-agent-skills-records", "version": __version__},
            }
        elif not self.ready:
            return error(identity, -32600, "Complete initialization first")
        elif method == "tools/list":
            if params:
                return error(identity, -32602, "No pagination or extra parameters")
            result = {
                "tools": [
                    {
                        "name": name.replace("-", "_"),
                        "description": DESCRIPTIONS[name],
                        "inputSchema": obj({"record": CONTRACTS[name]}),
                        "annotations": {
                            "readOnlyHint": True,
                            "destructiveHint": False,
                            "idempotentHint": True,
                            "openWorldHint": False,
                        },
                    }
                    for name in ASSURANCE
                ]
            }
        elif method == "tools/call":
            if set(params) != {"name", "arguments"} or not isinstance(params["name"], str):
                return error(identity, -32602, "Expected tool name and arguments")
            name = params["name"].replace("_", "-")
            if name not in ASSURANCE:
                return error(identity, -32602, "Unknown tool")
            arguments = params["arguments"]
            if not isinstance(arguments, dict) or set(arguments) != {"record"}:
                return error(identity, -32602, "Expected record argument only")
            try:
                value = ASSURANCE[name](arguments["record"])
                result = {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(
                                value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
                            ),
                        }
                    ],
                    "structuredContent": value,
                    "isError": False,
                }
            except (ValueError, TypeError, KeyError, RecursionError):
                result = {
                    "content": [{"type": "text", "text": "BLOCKED: invalid bounded record."}],
                    "isError": True,
                }
        else:
            return error(identity, -32601, "Method not found")
        return {"jsonrpc": "2.0", "id": identity, "result": result}


def serve(source: BinaryIO, sink: BinaryIO) -> int:
    session = Session()
    response: dict[str, Any] | None
    while raw := source.readline(MAX_MESSAGE_BYTES + 1):
        if len(raw) > MAX_MESSAGE_BYTES:
            response = error(None, -32600, "Message byte limit; connection closed")
            sink.write((json.dumps(response) + "\n").encode("utf-8"))
            sink.flush()
            return 2
        try:
            message = json.loads(
                raw.decode("utf-8"), object_pairs_hook=_unique, parse_constant=_constant
            )
            response = session.handle(message)
        except (ValueError, UnicodeError, RecursionError):
            response = error(None, -32700, "Invalid JSON message")
        if response is not None:
            sink.write(
                (json.dumps(response, separators=(",", ":"), ensure_ascii=True) + "\n").encode(
                    "utf-8"
                )
            )
            sink.flush()
    return 0


def main() -> int:
    return serve(sys.stdin.buffer, sys.stdout.buffer)


if __name__ == "__main__":
    raise SystemExit(main())
