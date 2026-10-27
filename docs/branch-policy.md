# Repository branches

main is the default protected branch. integ holds reviewed development. Do not push directly to main or force-push shared history.

As of October 27, 2026, the maintainer requested no CI pipeline or pipeline requirement. GitHub Actions is disabled for the repository, workflow files are removed, and main's required status checks have been deleted. There is no quality-gate merge prerequisite and no automatic or manual pipeline configured. Local tests and recorded release verification remain available.

Main still requires one approving review, dismissal of stale approvals, approval of the latest push by another eligible reviewer, conversation resolution, linear history, and administrator enforcement. Force pushes and deletion are disabled. There are no configured review bypass users, teams, or apps. Removing the CI prerequisite does not remove human review.

At this review, the active administrator is also PR #1's author. That account cannot provide the required independent approval. Prepare the preview and release artifacts for review; do not self-approve, fabricate approval, disable review controls, or publish around the protected branch.

Maintainers can change repository administration settings; branch protection is not a cryptographic or immutable control. This policy does not create automatic releases, package publishing, tags, or auto-merge.
