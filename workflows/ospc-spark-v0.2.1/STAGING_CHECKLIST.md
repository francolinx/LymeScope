# 08:00 staging checklist — existing Team 15 volume

Everything below is **PREPARED / NOT EXECUTED**, except the saved infrastructure proof and this addendum's read-only timeout observations. The [storage plan](VAST_STORAGE_PLAN.md) is authoritative for paths/footprint; the existing [venue handoff](VENUE_HANDOFF.md) remains authoritative for science.

## Before any remote write

- [ ] Obtain the bounded transfer/staging/pilot/trial authorization and a valid execution window. The current addendum permits reads and preparation only.
- [ ] Re-run the four requested volume/provisioner reads in the existing authorized context. Do not reauthenticate or change context without permission.
- [ ] Match volume and provisioner IDs to the saved receipt, confirm enabled/read-write state and at least 128 MiB remaining volume quota. Keep internal endpoints private.
- [ ] Ask the exact CIQ/VAST identity/policy question in the plan. Keep VAST UNVERIFIED until evidence ties the backend to this volume; no substitute volume without approval.
- [ ] Confirm the proposed object prefix and `/project/ospc-v0.2.1/venue-v021-20261115T140000Z` do not already exist. If filesystem inspection needs a job, include that read-only preflight in the explicit execution approval; do not infer emptiness from the object cache.
- [ ] Confirm the existing image is available without an unauthorized pull, Python works, and later GPU tasks have the required installed libraries. Preserve physical placement and pilot gates.

## Prepare exact transport bytes after approval

Create **only** the pinned scientific package archive at a new operator-chosen local filename. Never use the repository root as a recursive upload source:

```text
git archive --format=tar --output <NEW_SCIENCE_TAR> aafe818a20ea025370cf4b65145a9684e80aaaef sparkprep/experiments/stretch_v0.2.0_20261115T072916Z
```

Expected scientific tar: **6,543,360 bytes**, SHA256 **`bb9d036a96a918c62906398c269858eb12b53aac7c46f5b7f485002c61ada455`**. This was computed in memory from the local pinned Git object; no tar was saved/uploaded. If a different archiver produces different tar metadata, stop and review the byte contract rather than silently changing the planned hash.

Use the existing model tar on the personal Spark:

```text
/home/darkstar90/lymescope-sparkprep/.model-cache/transfer/esm2_t6_8M_UR50D_c731040fcd8d73dceaa04b0a8e6329b345b0f5df_six_files.tar
```

Expected **31,395,840 bytes**, SHA256 **`4e24f435628bb2c3b1a1a27664807c5d8c41ce7a94d3c2031b0f96363cb5d9ab`**. Establish the authorized route to a machine that already has both the bytes and the working Team 15 CLI; neither local laptop possession nor Spark CLI access is assumed. No model download, recursive cache upload or GitHub weight upload.

The CLI's local help confirms `object put LOCAL_PATH FB_URI`; use explicit files, no `--force` and no recursive upload. These are **future authorized writes**, not commands run during preparation:

```text
fuzzball object put <NEW_SCIENCE_TAR> fb://group/lymescope/ospc-v0.2.1/venue-v021-20261115T140000Z/science.tar
fuzzball object put <EXISTING_MODEL_TAR> fb://group/lymescope/ospc-v0.2.1/venue-v021-20261115T140000Z/model.tar
fuzzball object describe fb://group/lymescope/ospc-v0.2.1/venue-v021-20261115T140000Z/science.tar -o json
fuzzball object describe fb://group/lymescope/ospc-v0.2.1/venue-v021-20261115T140000Z/model.tar -o json
```

- [ ] Record actual digest, size, version, TTL and upload elapsed time; deduplicated cache hits are not upload-throughput measurements.
- [ ] In a **new approved execution copy** of `storage-stage-team15.HOLD.fz`, enable its two ingress entries and remove the unconditional exit. Preserve the original HOLD file.
- [ ] Run `fuzzball workflow validate <APPROVED_EXECUTION_COPY>`; resolve actual warnings without installing/changing the environment. Local YAML parsing alone is not server validation.
- [ ] Only then submit that exact reviewed copy under the separate authorization. Save its hash and workflow/job/stage IDs. No new volume declaration may appear.
- [ ] Read back `receipts/staging.json` and `receipts/package-model-verification.json` from the persistent volume through the approved workflow/export route. Match actual bytes/hashes. Retain failures/partial directories; do not clean them away.

## Science consumes the shared volume

- [ ] Set `$PACKAGE` to the expanded pinned package and `$MODEL` to the shared `model/`. Use fresh `runs/` subdirectories from the plan. No writes inside the scientific package.
- [ ] Hash-verify input/model bytes on each assigned physical node and record elapsed time separately. Run the existing deterministic probe and 210-mask pilot only after execution approval.
- [ ] Spark30 full result: 6,305/805. Concurrent Spark29/Spark30 shards: 3,156/403 and 3,149/402. Three warm-up calls per process remain separate. Use unchanged scorer arguments from `trial.HOLD.json` with the shared path bindings.
- [ ] Persist outputs and fsync/readback receipts; verify distinct physical nodes and overlapping shard intervals from scheduler evidence.
- [ ] Run the unchanged merge reading both persistent shard TSVs, then numerical/task-identity validation. Require all 6,305 tasks once and the predeclared tolerance; record absolute and relative deviations.
- [ ] Save final provenance, timings, hashes, failures and job IDs under `evidence/`; export only small reviewed evidence through an approved object-cache egress. The generic coordinator receipt is already in `docs/venue-receipt-template.json`.
- [ ] Import only validated event evidence into the separate viewer layer. Keep missing measurements null. Preserve the personal-Spark fallback and stop research by 10:30 AM Central.

Completion requires **backend identity evidence + successful real scientific read/write/merge + persisted readback**. Sentinel success alone is infrastructure proof, not completed scientific VAST integration.
