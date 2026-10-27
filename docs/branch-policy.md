# Repository branches

main is the default protected branch. integ is the integration branch for reviewed development. Do not push directly to main or force-push shared history.

Main protection requires one approving review, dismissal of stale approvals, approval of the latest push by another eligible reviewer, conversation resolution, linear history, and administrator enforcement. Force pushes and deletion are disabled. The quality-gate status must pass with the branch up to date before merging. There are no configured review bypass users, teams, or apps.

As of October 27, 2026, the maintainer requested CI disablement. The Quality workflow is disabled remotely; its retained definition supports workflow_dispatch only, with no push or pull-request trigger. Required main checks and review protections were not removed. This leaves quality-gate required but unavailable on new commits. Before merging, a maintainer must explicitly choose to restore verification or change the required-check policy while retaining the intended review controls. Disabling CI does not create a passing status or authorize a merge.

Maintainers can change repository administration settings; branch protection is not a cryptographic or immutable control. This policy does not create automatic releases, package publishing, tags, or auto-merge.
