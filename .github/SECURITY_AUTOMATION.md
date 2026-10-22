# Repository security automation

Pushes and pull requests to the default branch run secret detection, dependency
review and changed Python/JSON/XML syntax validation. Checks use read-only tokens,
do not retain checkout credentials, and never execute application code or builds.
Fork pull requests receive no repository secrets. There is no pull_request_target.

The incoming-change checks compare against the push-before or PR-base commit.
Existing dependency advisories are not declared fixed: the weekly/manual full
audit checks all dependencies and Git history, and fails on existing findings.
No blanket secret allowlist or vulnerability ignore list is installed. Scanner
output and matching secret values are withheld from CI logs and artifacts.
Run the full audit from Actions > Repository security > Run workflow.

Dependency coverage includes supported OSV lockfiles, requirements variants,
literal exact Gradle coordinates and checked-in runtime inventories. Version
ranges, dynamic Gradle values, missing/stale inventories, native payloads and
unrecorded transitive dependencies need resolved lockfiles/SBOMs and separate
validation. A successful check does not prove the complete application is safe.
Syntax checks do not replace application unit tests, builds or emulator tests.

Dependabot opens grouped weekly update PRs; updates are never auto-merged.
Available native GitHub protections are configured separately from these files.
Private repositories on plans without branch protection cannot enforce these
checks before merge; CI does not substitute for server-side branch protection.
Keep changes on a branch and merge reviewed passing PRs. Exposed credentials
still require revocation/rotation; adding CI does not erase Git history.

## Tool provenance and licenses

- gitleaks/gitleaks v8.30.1: MIT; https://github.com/gitleaks/gitleaks/releases/tag/v8.30.1; license: https://github.com/gitleaks/gitleaks/blob/master/LICENSE; binary SHA-256 `551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`.
- google/osv-scanner v2.7.0: Apache-2.0; https://github.com/google/osv-scanner/releases/tag/v2.7.0; license: https://github.com/google/osv-scanner/blob/main/LICENSE; binary SHA-256 `160c6253e2922e9e0a6a9771c5c4c40a4b3c6090b34a3cdd5e80c96cc2e4218b`.
- actions/checkout: MIT; https://github.com/actions/checkout/blob/11d5960a326750d5838078e36cf38b85af677262/LICENSE; pinned commit `11d5960a326750d5838078e36cf38b85af677262`.

Scanners are downloaded only on CI runners after SHA-256 verification. Scanner binaries are not shipped in application distributions. This document grants no additional license to project source or third-party components.
