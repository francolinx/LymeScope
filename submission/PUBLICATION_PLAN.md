# Reviewed main release proposal — awaiting approval

Work remains on `feature/ospc-masked-scoring-v0.2.0`. Local and remote main remain `8058846c05d4dccd60117dd29ef784af43570418`. The public feature branch was previously published at `4898f5531c91df26a64be0aa92e177be3b63f223`; the newer reviewed local candidate has not been pushed. No main integration, Pages setting change or organizer submission has been performed for this release.

Review the final full candidate SHA returned with the [release review](RELEASE_REVIEW.md), [claims](CLAIM_VERIFICATION.md), [optional-science validation](frontier-science-integration-validation.json) and current manual visual checklist. The exact main-to-candidate inventory is recorded in [release-review.json](release-review.json). Existing personal-statement and organizer questions remain listed; publication does not claim their resolution. Browser rendering and PDF pagination remain unverified.

The exact main release is an ordinary fast-forward because main is an ancestor of the candidate. After the lead explicitly approves that exact candidate, recheck the clean working tree and remote main. Preserve any new local work or remote commits; do not silently replace a changed baseline. The proposed commands are:

```powershell
git fetch origin main
# Verify origin/main and local main still equal the reviewed base, and the tree is clean.
git switch main
git merge --ff-only --no-overwrite-ignore <approved-full-commit-sha>
git push origin main
# Read back git rev-parse HEAD and git ls-remote --heads origin main.
```

This advances main to the reviewed feature history and preserves both scientific-source commits, every historical receipt and the feature branch. It creates no rewritten history and uses no force option. If remote history advances, reconcile separately and review the new candidate. A branch-protection requirement may necessitate a pull request; do not bypass it. This document is preparation, not authorization.

Pages is a separate approval: after main publication, configure `main` + `/docs` using [the prepared hosting plan](../docs/PAGES_PREPARATION.md), then verify the deployment and live URL. Until then `https://francolinx.github.io/LymeScope/` is a candidate address, not a working-demo claim. No automated event submission is included in either approval.

Personal-Spark model inference is now complete. The next bounded request is the [venue transfer and trial](../workflows/ospc-spark-v0.2.1/VENUE_HANDOFF.md): reuse the existing six-file cache, not a new download. Actual event runtime, physical placement, venue pilots and execution authorization remain blockers. The earlier five-file laptop staging proposal remains development history and is not the venue plan.
