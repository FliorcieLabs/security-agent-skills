# Optional local MCP interface

The preview server exposes four pure record-analysis tools over stdio. It does not read arbitrary file paths, execute commands, connect to target servers, open a network listener, request sampling, or install skills. Starting it is optional; existing skills have no MCP dependency.

Launch from a source checkout:

```sh
python scripts/security_mcp.py
```

It waits for newline-delimited JSON-RPC on stdin. stdout contains protocol messages only. EOF ends the process. Stop it using the host's normal server controls. It is not an HTTP service and should not be exposed through an unauthenticated network bridge.

An installed CLI wheel also provides `security-agent-skills-mcp`, or use `python -m security_agent_skills.mcp_stdio` with the interpreter where the package is installed. No third-party runtime package is needed.

## Register with a capable client

Use your host's documented stdio server settings. Set command to your chosen Python interpreter and arguments to the absolute path of `scripts/security_mcp.py`. For a client using an `mcpServers` map, the following is a template, not a universal configuration format:

```json
{
  "mcpServers": {
    "security-records": {
      "command": "python",
      "args": ["/absolute/path/to/security-agent-skills/scripts/security_mcp.py"]
    }
  }
}
```

Replace the example path and interpreter with actual local locations. JSON on Windows requires escaped backslashes or forward slashes. Other clients use different configuration keys, surfaces, and approval controls. No host settings are changed by this repository. Do not grant shell or network permissions merely to run these tools. Existing host sandbox controls still apply.

## Tools and contracts

| MCP name | CLI command | Input |
|---|---|---|
| `attack_path` | `attack-path` | Declared nodes, entries, assets, and edges |
| `detection_replay` | `detection-replay` | Exact string predicates and labeled events |
| `regression_board` | `regression-board` | Paired baseline/candidate label records |
| `skill_route` | `skill-route` | Closed-vocabulary goals and a selection cap |

Each tool accepts one argument, `record`, containing the same document as its CLI example under [examples/assurance](../examples/assurance). `tools/list` provides full input shapes. Helpers enforce semantic references and budgets as well. Valid calls return the standard report in `structuredContent` plus JSON text. Invalid record content returns `isError: true` with a fixed BLOCKED message. Unknown tools or malformed protocol parameters return JSON-RPC errors without echoing submitted arguments. Request IDs are echoed for protocol correlation. A valid PARTIAL security report is not a protocol error.

Supported protocol versions: `2025-11-25` and `2025-06-18`. Initialization and the initialized notification precede tool calls. Ping and object-valued request `_meta` are supported. Metadata is ignored for analysis and cannot authorize anything. No prompts, resources, notifications of tool changes, batching, tasks, roots, sampling, elicitation, or HTTP transport is advertised. Messages are limited to 1,000,000 bytes, including the terminating newline; an oversized line closes the connection after an error. Duplicate keys, nonfinite JSON constants, invalid UTF-8, and invalid record shapes are rejected. The server is sequential and computations have fixed input bounds.

The implementation follows the official [stdio transport](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports), [lifecycle](https://modelcontextprotocol.io/specification/2025-11-25/basic/lifecycle), and [tools](https://modelcontextprotocol.io/specification/2025-11-25/server/tools) specifications for this limited capability surface. Local protocol tests are not full MCP conformance certification or evidence of a real assistant session.

## Data boundary

The server emits reports back to its invoking host over stdout. A hosted AI client may send tool arguments or results to its provider under its own policy. The helper makes no independent external requests, but stdio is still a deliberate data flow to the host. Use synthetic events and symbolic references instead of private logs or source. No raw event values are returned by detection replay. IDs, graph topology, expected labels, and references still appear in reports and can be sensitive. Read-only annotations describe behavior; they are not an OS security boundary.
