# Reference review and independent product decisions

Historical T27 research below describes the independent 0.1.0a2 additions. On October 31, 2026, T28 subsequently imported selected pure functions for two attributed offline adaptations. Current provenance is in [third-party notices](../../THIRD_PARTY_NOTICES.md) and [adaptation limits](../adapted-skills.md). Statements below that no content was imported apply to T27, not the later attributed additions.

Reviewed October 31, 2026. Reference: [Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/tree/54a798831d2266a3ca61ce68a7acb80b81160d57), revision `54a798831d2266a3ca61ce68a7acb80b81160d57`.

## Coverage and limits

The full tracked inventory contains 4,532 files, 33,005,288 bytes, 4,531 UTF-8 text files, one binary image, 818 skill entrypoints, and 1,103 Python sources. Every tracked file was read for the inventory. Every Python source was parsed with Python's AST parser without importing it; no syntax errors were found. Selected scripts produced invalid-escape warnings under this interpreter. That is not a runtime correctness test.

File-level lexical indicators occurred in 801 files for network terms, 371 for subprocess/system calls, and 179 for environment access. These counts include documentation, examples, and legitimate security workflows. They are not maliciousness, telemetry, confirmed transfer, or vulnerability counts. Complete semantic review of every line, dependency audit, script execution, binary analysis, and live target testing were not performed. The full-codebase inventory must not be described as a complete security certification.

[Machine-readable review](reference-review.json) records counts and exclusions. [File hashes](reference-file-hashes.json) identify every reviewed tracked file without copying its content. Deeper manual review covered the selected MCP, RAG injection, indirect-injection, Sigma, threat-model, and SBOM workflows, plus license, scope, security policy, plugin metadata, developer tools, and pipeline definitions.

## What drives adoption

The repository API showed 35,321 stars and 4,303 forks on the review date. These are repository-wide signals; no trustworthy individual-skill usage or viral ranking was available. The name does not make the collection Claude-only. Its [README](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/54a798831d2266a3ca61ce68a7acb80b81160d57/README.md) already advertises multiple AI platforms and the Agent Skills format.

Observed presentation strengths are concrete task names, broad domain coverage, one-command adoption, progressive references, recognizable framework mappings, examples, and visible community participation. These can help discovery. Stars do not establish technical accuracy, installation safety, model quality, or the causes of growth.

Our positioning is a narrower security decision toolkit: inspect a package, model a declared boundary, replay a small fixture, compare the evidence, and retain unknowns. The difference is executable local contracts and consistent evidence, not the number of topics or a promise to cover everything. The reference [scope](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/54a798831d2266a3ca61ce68a7acb80b81160d57/SCOPE.md) explicitly excludes runtimes, MCP engines, and platform layers. Our record-analysis MCP is an additional product surface, not a claim that their catalogue failed at its stated purpose.

## Ten prioritized opportunities

Priority reflects fit for this project and demo clarity, not measured popularity. No upstream skill was imported.

| Priority | Area and reference example | Decision in this project | Reason |
|---|---|---|---|
| 1 | MCP trust: auditing-mcp-servers-for-tool-poisoning | Keep MCP Authority Review, Instruction Boundary Audit, and Change Sentinel | Existing complementary boundaries; avoid a duplicate scanner and avoid launching an untrusted server during static review |
| 2 | Agent/RAG injection: testing-prompt-injection-in-rag-pipelines, detecting-indirect-prompt-injection | Keep Boundary Lab and instruction audit; add paired Regression Board | Explicit forbidden-action evidence and excluded cases are more useful here than importing network probes or a phrase-based exploit verdict |
| 3 | Threat modeling: implementing-threat-modeling-with-mitre-attack, performing-threat-modeling-with-owasp-threat-dragon | Add independent Attack Path Rehearsal | User-declared graph reachability and alternate-path-aware single-edge counterfactuals answer a concrete fix question without a live intelligence feed |
| 4 | Detection engineering: building-detection-rules-with-sigma | Add independent Detection Replay Lab | Small exact-match labeled fixtures make missing fields and false positives visible; it deliberately does not replace Sigma or a SIEM |
| 5 | Supply chain: analyzing-sbom-for-supply-chain-vulnerabilities, generating-and-analyzing-sboms | Keep Provenance Audit and Change Sentinel; defer live CVE enrichment | Provenance already exists; a correct offline advisory snapshot/import contract is needed before claiming vulnerability matching |
| 6 | Cloud/container posture | Keep infrastructure and container reviews | Existing narrow static checks; avoid a second catalogue of vendor procedures and credential-dependent cloud operations |
| 7 | API authorization testing: conducting-api-security-testing | Keep authorized plan validation; defer active API execution | An executable live test runner needs owned target fixtures, exact authorization, and enforceable budgets beyond an inert plan |
| 8 | SOC/incident evidence | Defer raw log ingestion and incident automation | Real parsers, time normalization, sensitive-data handling, and evidence integrity need their own verified boundary |
| 9 | Evidence-based upgrade decisions | Add independent Security Regression Board | Preserves per-case regressions even when headline F1 improves; incomplete cases never become negatives |
| 10 | Context-efficient discovery | Add independent Security Skill Router and optional record-only MCP | Load explicit goal matches and report deferrals; four record tools expose the same algorithms without requiring native agent registration |

## Concrete source observations

The [MCP helper](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/54a798831d2266a3ca61ce68a7acb80b81160d57/skills/auditing-mcp-servers-for-tool-poisoning/scripts/agent.py) has a static mode that may invoke mcp-scan through a subprocess and an enumeration mode that launches a configured stdio server. Those are meaningful execution boundaries for an adoption review. We did not run either mode or determine a third-party scanner's complete data policy.

The [RAG helper](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/54a798831d2266a3ca61ce68a7acb80b81160d57/skills/testing-prompt-injection-in-rag-pipelines/scripts/agent.py) can POST prompts with an optional bearer token to a configured endpoint. It marks matches to success strings in returned text as vulnerable, including general phrases. That heuristic warrants inspection of actual disclosures; it does not by itself establish exploitability. Its embedding mode imports model dependencies and model acquisition behavior needs separate review.

The [SBOM helper](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/54a798831d2266a3ca61ce68a7acb80b81160d57/skills/analyzing-sbom-for-supply-chain-vulnerabilities/scripts/agent.py) includes NVD requests with component-derived query parameters and an optional API key. Public lookups still transmit query data. This is an explicit functional data flow, not evidence of hidden telemetry.

The [Sigma helper](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/54a798831d2266a3ca61ce68a7acb80b81160d57/skills/building-detection-rules-with-sigma/scripts/agent.py) uses Sigma libraries and a Splunk backend. The [threat-model helper](https://github.com/mukul975/Anthropic-Cybersecurity-Skills/blob/54a798831d2266a3ca61ce68a7acb80b81160d57/skills/implementing-threat-modeling-with-mitre-attack/scripts/agent.py) imports attackcti and uses external threat intelligence. These have capabilities our bounded exact-match and declared-graph helpers intentionally do not implement.

## Independent implementation and honest comparisons

The reference is Apache-2.0 licensed. Our existing project remains MIT. We copied no skill text, scripts, templates, tests, artwork, framework mapping datasets, or plugin metadata. Research links, public filenames, metadata counts, and file digests document the review. The four new contracts, algorithms, fixtures, tests, profiles, and docs were independently authored for this product's existing report interface. This is independent implementation with transparent research attribution, not a claim of legal clearance for every possible similarity.

The new helpers solve common security problems with standard graph and metric algorithms. Do not claim those algorithms are novel inventions, a patentable breakthrough, or absent from every other project. Distinction lies in their bounded contracts, explicit uncertainty, deterministic evidence, and the integrated workflow here.

There is no measured head-to-head result against the reference library. Its workflows were not executed. The [local benchmark](../assurance-workflows.md) compares an openly labeled toy baseline and exact-match replay on eight synthetic events, preserving the recall regression. It cannot support a claim that this repository beats 818 workflows, a model, or another platform.

## Presentation and distribution

The README leads with a user decision, a short demonstration, and a clear privacy boundary. It exposes three access layers: readable Markdown roles, standalone Python skill bundles, and optional record-only stdio MCP. It separates text portability, directory installation, protocol behavior, and actual assistant sessions. No claim of universal native integration is made.

Demonstrate one evidence-backed change: show an unknown edge, attach a reviewed symbolic reference, add an alternate route, and show which proposed control no longer disconnects the asset. Then replay a labeled event whose schema changed and show the missing detection. Both examples give a useful result without inventing an attack or inflating a benchmark. Shareability and adoption remain hypotheses, not guaranteed outcomes.
