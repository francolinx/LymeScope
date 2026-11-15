# Proposed publication — not executed

Work remains on `feature/ospc-masked-scoring-v0.2.0`. Main remains at the reviewed baseline `8058846c05d4dccd60117dd29ef784af43570418`. No remote push, submission or visibility change occurred.

First resolve the project lead's personal-statement draft and organizer eligibility/submission questions. Review the exact local feature commit, [claims](CLAIM_VERIFICATION.md), [validation](validation.json), and the manual visual checklist. Current browser rendering is not independently verified.

The proposed **feature-branch review push**, only after publication approval, is:

```powershell
git push -u origin feature/ospc-masked-scoring-v0.2.0
```

If the lead instead separately approves publishing the reviewed change to main, recheck the working tree and current remote main first, then integrate without discarding concurrent work. The proposed ordinary final push is:

```powershell
git push origin main
```

That main push requires a reviewed integration first; it must not be issued while main still points to the old baseline. If remote history advances, stop any incompatible fast-forward and reconcile without reset, clean or force-push. Read back local/remote SHAs after any future authorized publication. This document is a proposal, not authorization.

Personal-Spark model inference is now complete. The next bounded request is the [venue transfer and trial](../workflows/ospc-spark-v0.2.1/VENUE_HANDOFF.md): reuse the existing six-file cache, not a new download. Actual event runtime, physical placement, venue pilots and execution authorization remain blockers. The earlier five-file laptop staging proposal remains development history and is not the venue plan.
