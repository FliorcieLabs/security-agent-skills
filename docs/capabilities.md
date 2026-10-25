# Capabilities and limits

The product is a set of workflows with bounded local helpers. A skill is an instruction package, not an independent security boundary.

Static audits inspect UTF-8 source text and supported JSON/TOML manifests. They intentionally return PARTIAL. Strings in comments or tests can match; computed destinations, obfuscated code, dynamic imports, reflection, native binaries, dependency behavior, generated code, and runtime configuration can escape detection. Inspect each lead. No match is not a safety decision.

Dependency parsing supports package.json, npm package-lock packages maps, npm-shrinkwrap, pyproject.toml project dependencies, and requirements text. Poetry, uv, Yarn, pnpm, Go, Rust, vendored binary provenance, license obligations, and live advisories need separate review. Missing supported manifests are not counted as examined dependencies.

MCP inspection supports mcpServers, mcp_servers, and servers maps in selected JSON files or config.toml. It does not connect to servers or enumerate actual tool schemas. Environment/header values and command arguments are not emitted. Client filters do not enforce OS or server permissions.

AppSec validates a declared scope and never sends requests. Boundary Lab grades supplied records for exact synthetic canary disclosure and named forbidden calls. Secret Route Mapper interprets supplied synthetic events and never instruments processes or captures traffic. Missing evidence stays unknown.

Safe Install Sandbox emits a restricted Docker plan but does not execute it, attest the daemon, pull an image, enforce a timeout, capture egress, or compute a filesystem diff. Full runtime sandboxing is an integration responsibility. Use synthetic package copies with no credentials and a disposable OS environment. Even a network-disabled container can read any files mounted into it.

Evidence Pack checks local report inventory and hash consistency. A malicious actor can rewrite both reports and the manifest. No signing, remote attestation, immutable storage, WORM, or compliance status is implied. Redaction is best-effort pattern scrubbing. Output paths, findings, and even filenames may contain sensitive information; review before sharing.

Filesystem reads are bounded and avoid links, reparse points, special files, and known credential filenames. Root and file checks do not provide an atomic snapshot or defeat every concurrent filesystem race on every OS. Input supplied by another process can change; rescan stable copies where content identity matters. Generated dependencies and credentials are excluded explicitly in coverage.
