# LymeScope departure handoff

**SUBMISSION TODO:** review contents and confirm a public final submission repository before Sunday, November 15, noon Central. Existing francolinx/LymeScope was already public; preserve its history and visibility. Do not add a license without the owner's choice.

Organizer reported about ten minutes of access at the urgent checkpoint, superseding the 7:30 PM target. No overnight event-cluster access. Return Sunday, November 15 at **8 AM Central**, submission **noon**, five-minute demo **1 PM**. Returning does not guarantee node availability until organizers confirm it. No further cluster work is planned tonight.

## Completed event-cluster work


- Original smoke 79a4aa69-4307-4184-9764-84b915f58579 finished at 5:02 PM, exit 0. Never rerun; original report and hash preserved.
- CUDA/write workflow 2f5d31fa-223c-4f5f-8df4-721fee85309a, job 434b8807-bc70-527b-ad12-26896e66a050, finished at 5:36:27 PM, exit 0, on CIQ-CHI-SPARK30 (192.168.99.39/7331).
- Real CUDA matrix multiplication: 32x32 float32 all-ones matrices on cuda:0, synchronization, exact correctness checks, sum 32768. Python 3.12.3; PyTorch 2.10.0a0+b558c986e8.nv25.11; runtime CUDA 13.0; driver 580.173.02; GB10. Registry image metadata specifies CUDA 13.0.2.006. Evidence: findings/phase-b-writer-run.json.
- Created team15/lymescope-project: persistent NFS, exactly 1 GiB, group GID 100056 matching team15. No resize or permissions changes. Evidence: findings/phase-b-volume.json.
- Unique file: /project/verification/phase-b-20261114T173521-7908c2da/sentinel.txt; 78 bytes; SHA256 39fdbdc8e6d379b229fbab22b10b75fb803d6a257df97604adebe9a2d9be870d.
- Reader workflow 9d279ac6-741f-48b1-88c3-1a61a0a56aa6, job efeba751-fe73-540e-a992-a6d0e8c2cbcf, finished exit 0. Rank 0/container storage-two-node-read-0 maps to Spark30; rank 1/container storage-two-node-read-1 to Spark29 (192.168.99.38/7331). Scheduler Hosts and head ContainerId establish this mapping; both receipts match expected bytes/hash. Evidence: findings/phase-b-reader-run.json.
- Label: **two-node shared-storage verification**. Not GPU scaling, RDMA or a scientific benchmark. A roughly 30-second wait for the worker receipt occurred; cause not diagnosed.
- Both images reported cache hits. Public OCI metadata exposed the ARM64 PyTorch variant and digests; Fuzzball did not expose its executed OCI digest. Do not assert that current registry digest equals cached-image digest.
- Reports, logs, stages and exact workflows are local and in portable_results; digest verification passed. Summary: findings/phase-b-results.json. Manifest: portable_results/manifest.json.
- Exactly one persistent volume, two temporary report volumes and two Phase B submissions. **No tracked job remains running.** MCP is read-only.


## Departure decision and incomplete work

- Final optional job SKIPPED; no new workflow ID, submission, pull or cancellation. Real scientific bundle and method were unavailable; a documented, validated Spark29 placement with a known cached image was not established in the departure gate.
- All three existing workflow statuses were read back as finished. No tracked jobs remain running. Evidence: findings/departure-checkpoint.json.
- Protein analysis, Spark29 CUDA calculation, generated protein structures and identical-workload one-node/two-node pilot: NOT RUN. Setup timings are not scientific performance results.
- The shared/datasets volume exists; its contents have not been inspected. No claim of model weights or scientific assets there.

## Personal Spark inputs and provenance

These are expected remote inputs, not event-cluster results and not local files:

- Host/account: darkstar90@spark-6771
- Workspace: /home/darkstar90/lymescope-sparkprep
- Frozen archive: /home/darkstar90/lymescope-sparkprep/exports/lymescope_ospc_handoff_v0.1.0.tar.gz
- Expected bytes: 264149
- Expected SHA256: 1ce0fff5a1b8d7d24ed6d70844f798484ac81231bcf2350ddcd8f6551ec1fa0f
- Transfer FAILED before import: no trusted ED25519 host key for spark-6771. Strict checking was preserved. Obtain the host fingerprint over a trusted channel and establish the correct known-host entry; do not accept an unverified key or disable checking.
- Separate source/analysis checkpoint: NOT IMPORTED, filename/hash not yet available. Preserve under a new sparkprep/ subdirectory after inspection; never overwrite laptop code or execute unreviewed imported scripts.
- Laptop Codex is the sole publisher. The personal Spark worker exports work, not concurrent GitHub pushes.

## Laptop-only work tonight

1. Open portable_results/index.html. It must say "Saved results from completed cluster runs." and remain infrastructure-only until real science outputs exist.
2. Restore trusted SSH host verification, then use the exact transfer command in RUN_LOCALLY.md. Verify archive size/hash before inspecting archive members. Reject path traversal, symlinks and unexpected credentials. Preserve original outside the repository.
3. The existing importer accepts a directory or ZIP, **not tar.gz**. Inspect the actual tar manifest/method first; safely extract to a new directory and reconcile its schema without altering original provenance. Do not invent a manifest or method.
4. Inspect scientific code, method, citations, licensing, FASTA identifiers and pre-existing references. Select a genuinely meaningful bounded analysis using existing runtime packages and no model downloads. Prepare its exact workflow, input list and expected output contract locally.
5. Verify backup hashes, Git bundle and GitHub branch head. Review source/data redistribution and secrets before the public submission deadline. GitHub upload can continue without cluster access.

## First action Sunday at 8 AM

Confirm organizer-granted node access and reconcile any independently completed work before any submission. Do not repeat the three passed infrastructure jobs. Verify the real frozen bundle and fix the exact scientific method locally first.

**First scientific command/workflow: NOT YET AVAILABLE.** It cannot be specified honestly until the missing archive and scientific method are inspected. findings/next-scientific-run-proposal.json remains HOLD; it is not executable approval. The first local validation command after safe extraction and schema reconciliation is:

    python scripts/import_scientific_bundle.py "C:\path\to\reviewed-extracted-bundle" --import-to scientific_inputs

Then author and validate the exact scientific workflow and scheduling request. Obtain bounded approval for the selected real inputs, precise command, resources and outputs; tonight's unused final-job allowance is not an open-ended authorization for tomorrow. Prefer the verified PyTorch image, existing 1 GiB team15 NFS, no packages/models, <=5 MiB input and <=1 MiB report. Export each completed result immediately.

## Future node-dependent work

Run the first meaningful protein analysis, then prepare an identical-input/method one-node/two-node pilot with physical host evidence. A single pair is a pilot; incomplete comparisons must stay labeled incomplete. Verify actual availability of cluster storage tomorrow; never assume overnight access. Reserve the last 45 minutes of actual access for export/validation and last 15 minutes for local viewing with cluster requests disabled.

