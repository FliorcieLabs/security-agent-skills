# Capabilities and limits

## Internal operation records

Five workflows validate supplied local records without orchestrating an agent runtime. Task Planner checks graph order, ownership declarations, evidence requirements, and step caps. Handoff Review checks permission subsets and status/evidence consistency. Context Checkpoint produces a bounded reference capsule that retains mandatory context. Tool Preflight compares exact declared policy fields. Retry Guard returns a stop, reconcile, or review decision. [Contracts and limits](internal-operations.md).

These helpers do not verify record claims, resolve evidence, grant permissions, invoke tools, send handoffs, persist memory, or retry effects. Checkpoint and matching preflight stay PARTIAL. PASS for task/handoff checks means record consistency only; PASS for Retry Guard means stop without retry under the supplied declarations. Resource aliasing, actual authority, freshness, hidden side effects, and runtime behavior remain unresolved.

## Additional boundary audits

The following five audits use bounded local text, fixed messages, stable finding IDs, and file/line locations. They always return PARTIAL. Coverage distinguishes files admitted by inventory from files evaluated by the selected workflow. Zero evaluated files does not establish safety.

| Workflow | Selected inputs | Current checks | Not established |
|---|---|---|---|
| Instruction Boundary Audit | Named agent instruction files and text under agents/prompts/instructions/rules | Priority overrides, approval bypass language, concealment, sensitive-transfer language, invisible characters | Intent, provenance, instruction compliance, or resistance to an actual attack |
| CI Workflow Security Audit | .github/workflows/*.yml and *.yaml relative to the project root | Mutable uses references, privileged triggers, broad permissions, inherited secrets, self-hosted selection, untrusted expressions | Full YAML semantics, expressions in aliases, effective nested permissions, callee trust, or exploitability |
| Container Boundary Audit | Dockerfile*/Containerfile* and YAML | Explicit root, privilege, host namespaces, daemon socket references, selected escalation settings, remote ADD | Complete Compose/Kubernetes policy, image defaults, multiline arrays, cluster admission, or runtime isolation |
| Infrastructure Exposure Audit | .tf HCL | Literal world ranges, wildcard action/resource lists, public storage controls, encryption and validation bypass settings | Terraform JSON, plans, state, variable expansion, modules, Allow/Deny meaning, or live cloud exposure |
| LLM Data Boundary Audit | JSON/TOML/YAML and Python/JavaScript/TypeScript text | Explicit capture/scrubbing/trust/TLS flags and configured provider/proxy endpoints | Actual transfers, all providers, retention/training terms, reachability, or source-to-sink data flow |

Comments, quoted fixtures, prohibitions, data-only expressions, and unrelated YAML may produce review leads. These helpers are not full parsers. Findings omit matched values; inspect the cited source locally before recommending a change.

Primary references for the delivery review questions:

- [GitHub Actions secure use](https://docs.github.com/en/actions/reference/security/secure-use)
- [GitHub Actions script injections](https://docs.github.com/en/actions/concepts/security/script-injections)
- [Docker build practices](https://docs.docker.com/build/building/best-practices/)
- [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)

These references motivate review questions, not a claim that the lexical scanner implements or certifies the complete guidance.

## Shared and original helper limits

The product is a set of workflows with bounded local helpers. A skill is an instruction package, not an independent security boundary.

Static audits inspect UTF-8 source text and supported JSON/TOML manifests. They intentionally return PARTIAL. Strings in comments or tests can match; computed destinations, obfuscated code, dynamic imports, reflection, native binaries, dependency behavior, generated code, and runtime configuration can escape detection. Inspect each lead. No match is not a safety decision.

Dependency parsing supports package.json, npm package-lock packages maps, npm-shrinkwrap, pyproject.toml project dependencies, and requirements text. Poetry, uv, Yarn, pnpm, Go, Rust, vendored binary provenance, license obligations, and live advisories need separate review. Missing supported manifests are not counted as examined dependencies.

MCP inspection supports mcpServers, mcp_servers, and servers maps in selected JSON files or config.toml. It does not connect to servers or enumerate actual tool schemas. Environment/header values and command arguments are not emitted. Client filters do not enforce OS or server permissions.

AppSec validates a declared scope and never sends requests. Boundary Lab grades supplied records for exact synthetic canary disclosure and named forbidden calls. Secret Route Mapper interprets supplied synthetic events and never instruments processes or captures traffic. Missing evidence stays unknown.

Safe Install Sandbox emits a restricted Docker plan but does not execute it, attest the daemon, pull an image, enforce a timeout, capture egress, or compute a filesystem diff. Full runtime sandboxing is an integration responsibility. Use synthetic package copies with no credentials and a disposable OS environment. Even a network-disabled container can read any files mounted into it.

Evidence Pack checks local report inventory and hash consistency. A malicious actor can rewrite both reports and the manifest. No signing, remote attestation, immutable storage, WORM, or compliance status is implied. Redaction is best-effort pattern scrubbing. Output paths, findings, and even filenames may contain sensitive information; review before sharing.

Filesystem reads are bounded and avoid links, reparse points, special files, and known credential filenames. Root and file checks do not provide an atomic snapshot or defeat every concurrent filesystem race on every OS. Input supplied by another process can change; rescan stable copies where content identity matters. Generated dependencies and credentials are excluded explicitly in coverage.

## Security decision experiments and MCP

Four [record workflows](assurance-workflows.md) analyze graph paths, exact-match labeled events, paired metrics, and explicit skill goals. All valid reports remain PARTIAL. They do not construct a full graph from source, validate exploits, implement Sigma, authenticate labels, measure real model quality, or infer natural-language intent. The [optional stdio MCP interface](mcp.md) exposes only those four pure record functions and returns data to the invoking host. No host installation, independent network request, arbitrary file read, or target execution occurs through these tools.

## Attributed header adaptations

Two [offline header adaptations](adapted-skills.md) reuse selected Apache-2.0 helper functions with attribution. Email headers yield unverified authentication claims and From/Reply-To differences. HTTP snapshots check a limited subset of header presence/values. Neither acquires live evidence, sends DNS/HTTP requests, processes attachments, or verifies sender or application security. All valid reports remain PARTIAL.
