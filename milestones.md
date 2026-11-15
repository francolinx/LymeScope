# LymeScope milestones

Current laptop integration checkpoint: November 14, 2026, 10:16 PM Central. Recovery commit `55fcd984554eb12d7a62bd42d42675863fe0f2ea` was fast-forwarded with ignored-file overwrite protection.

| State | Current milestone | Evidence / limitation |
|---|---|---|
| DONE | Personal-Spark recovery integrated locally | 311 added files; 308 source files match the existing audit, plus three audit documents; recovery branch retained |
| DONE | Saved scientific result and inputs available | 30-sequence/218-column CPU alignment; experimental 1GGQ mapping; no new scientific run during integration |
| DONE | Existing checksums verified | 367 available SHA256 entries, 489 JSON-manifest entries; zero mismatches; four intentionally excluded archive/sidecar paths |
| DONE | Existing laptop tests | 26 passed using Python 3.14.4; two early-baseline unclosed-file warnings |
| PARTIAL | Completed viewer checked locally | File/data/seven links verified; Chrome launch confirmed by window title; rendering NOT VERIFIED because automation access was denied |
| DONE | Local work preserved before integration | 35 synthetic fixture files verified in a private ZIP; browser profile/cache retained untouched |
| NOT RUN | New cluster/GPU experiments or scaling pilot | Outside this integration; no downloads or new scientific execution |
| NOT STARTED | Final submission review | Retains Sunday noon Central deadline; no license selected |

See [the integration receipt](findings/laptop-spark-integration.json) and [current handoff](NEXT_SESSION.md). Final commit/publication equality and refreshed private backup hashes are recorded outside the repository under `C:\Users\franc\Projects\LymeScope-recovery` after the normal push.

## Historical departure milestones

The original state below is preserved for chronology; its missing-input and protein-result blockers were superseded by the recovered personal-Spark result above. Event-cluster GPU/protein work remains distinct and was not added by this recovery.

Updated 2026-11-14T18:03:08-06:00. Organizer's ten-minute departure checkpoint overrides all later evening targets. No overnight event-cluster access. Sunday November 15: return 8 AM Central, public submission noon, five-minute demo 1 PM.

| State | Milestone | Evidence / limitation |
|---|---|---|
| DONE | Driver smoke by 5:15 PM | findings/gpu-smoke-run.json; finished about 5:02 PM |
| DONE | CUDA and durable storage by 5:45 PM | findings/phase-b-results.json; Spark30 CUDA/write and Spark29/Spark30 shared reads passed |
| DONE | Local report/log exports | portable_results/manifest.json; all 40 original files reverified at departure |
| DONE | Final-job decision | SKIPPED; no new workflow; findings/departure-checkpoint.json |
| DONE | Tracked-job reconciliation | All three existing workflows finished; none active |
| BLOCKED | Personal-Spark frozen input import | Host key not trusted; strict verification stopped transfer; expected hash in NEXT_SESSION.md |
| BLOCKED | First protein result (former 6:15 PM target) | No imported input or fixed method; target abandoned for export checkpoint |
| NOT STARTED | Identical-workload pilot (former 6:50 PM target) | No scientific baseline; infrastructure tests do not count |
| DONE | Inspectable infrastructure viewer | findings/departure-viewer-validation.json; Chrome rendered with cluster/network requests disabled; 17 local links verified; no scientific outputs claimed |
| DONE | Local Git/recovery/GitHub checkpoint | findings/departure-publication.json and departure-recovery.json; initial commit pushed and compared with remote main; final receipt outside repository |
| NOT STARTED | Final submission review | Public repository content review required before Sunday noon |

No fabricated scientific output, benchmark or timing. The earlier 7:30 PM access assumption is withdrawn. The final 45-minute export reserve could not be retained after the short-notice cutoff; export and offline verification were prioritized immediately. No additional event-cluster calls are needed for viewing or backup.
