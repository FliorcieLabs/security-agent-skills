# Repository branches

main is the default protected branch. integ is the integration branch for reviewed development. Do not push directly to main or force-push shared history.

Main protection requires one approving review, dismissal of stale approvals, approval of the latest push by another eligible reviewer, conversation resolution, linear history, and administrator enforcement. Force pushes and deletion are disabled. The quality-gate status must pass with the branch up to date before merging. There are no configured review bypass users, teams, or apps.

Maintainers can change repository administration settings; branch protection is not a cryptographic or immutable control. This policy does not create automatic releases, package publishing, tags, or auto-merge.
