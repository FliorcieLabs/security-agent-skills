# Third-party notices

Selected helper functions are adapted from Anthropic-Cybersecurity-Skills, https://github.com/mukul975/Anthropic-Cybersecurity-Skills, revision 54a798831d2266a3ca61ce68a7acb80b81160d57.

Copyright 2026 mukul975. Upstream skill author metadata: mahipal. These retained portions are licensed under Apache License 2.0, provided in LICENSES/Apache-2.0.txt. No upstream NOTICE file was found in the reviewed checkout. This notice documents origin and does not imply endorsement.

Affected runtime files, also copied into every standalone bundle under scripts/_security_agent_skills/:

- adapted_email_headers.py: extract_authentication_results and check_from_replyto_mismatch from skills/analyzing-email-headers-for-phishing-investigation/scripts/agent.py.
- adapted_http_headers.py: check_hsts, check_content_type_options, check_referrer_policy, and check_info_disclosure from skills/performing-security-headers-audit/scripts/agent.py.

Modified by Fliorcie Labs on October 31, 2026: extracted selected pure functions; excluded all other code, network clients, DNS/subprocess paths, filesystem or attachment writes, CLI entrypoints, grading, and complete upstream reports. HTTP methods became functions. HSTS max-age parsing was bounded and made case-insensitive. An explicit result type annotation was added to the email helper. Formatting and import order follow this project. Fliorcie adapters validate bounded local records and suppress raw values from public reports. These are limited adaptations, not complete imports of the upstream workflows.

Exact upstream source and license hashes are recorded in third-party-provenance.json. Each modified runtime file carries an origin and change notice. The new skill entrypoints and workflow references clearly identify their adapted helper provenance.

Original Fliorcie-authored project files remain under the root MIT license unless otherwise marked. The two adapted runtime modules retain Apache-2.0 terms. A distributed standalone bundle contains both licenses because it includes both original and adapted runtime code. Do not describe all distributed code as exclusively MIT or wholly original.
