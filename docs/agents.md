# Portable security agents

The five files in agents/ are role instructions. Attach, paste, or load them in an assistant that accepts Markdown. They do not register native subagents, install plugins, start services, or grant tools. No automatic delegation is implied.

| Profile | Use when | Companion command |
|---|---|---|
| Instruction Boundary Auditor | Reviewing a skill, prompt pack, or agent instruction file | instructions |
| CI Workflow Security Reviewer | Reviewing GitHub Actions authority and contribution boundaries | ci |
| Container Boundary Reviewer | Reviewing Dockerfiles and deployment YAML before execution | containers |
| Infrastructure Exposure Reviewer | Reviewing literal Terraform HCL exposure controls | iac |
| LLM Data Boundary Reviewer | Reviewing explicit AI content capture, endpoints, and trust settings | llm-data |

Resolve the target folder and scope, then load only the relevant profile. Preserve its Result, Findings, Coverage, Validation, and Remaining fields. Each companion skill bundles the profile at references/agent.md and has no dependency on this checkout.

With a terminal and Python 3.11+, the assistant can run the helper. Without them, it can review supplied excerpts but must label partial coverage. Missing required execution access is BLOCKED. Never fabricate helper results.

Native custom-agent registration uses the chosen host's current configuration and permissions. There is no universal native registration format here. Text portability, native discovery, helper execution, and model behavior are separate claims.

Do not upload private files just to use a profile. Follow the project's existing data-sharing policy and keep credentials out of prompts. The helpers themselves operate locally.
