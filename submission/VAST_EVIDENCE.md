# VAST / shared-storage evidence

**VAST backend: UNVERIFIED. Scientific storage integration: PREPARED, NOT RUN.**

The existing Team 15 persistent volume is meaningful infrastructure: Spark30 wrote a 78-byte sentinel and both Spark29 and Spark30 read the identical SHA256, `39fdbdc8e6d379b229fbab22b10b75fb803d6a257df97604adebe9a2d9be870d`. The writer workflow is `2f5d31fa-223c-4f5f-8df4-721fee85309a`; the reader workflow is `9d279ac6-741f-48b1-88c3-1a61a0a56aa6`. Those completed tests did not run the protein-model workload or measure storage bandwidth.

The saved provisioner record identifies **NFS**, group `team15`, and the existing **1 GiB** volume `lymescope-project`. Current live provisioner/volume reads all timed out after a 12-second bound; no context changes or reauthentication were attempted. NFS and an event sponsor name do not independently identify a VAST backend. A sanitized CIQ/VAST confirmation tying the actual provisioner/volume IDs to its backend is still required.

The [storage plan](../workflows/ospc-spark-v0.2.1/VAST_STORAGE_PLAN.md) adds a concrete scientific route: authorized Fuzzball object-cache ingress → existing shared volume → unchanged ESM-2 scorer on the assigned GB10 nodes → separate shared output shards → published merge/validation → reviewed viewer evidence. Its Mermaid diagram labels every scientific arrow **PLANNED** and the older sentinel arrows **COMPLETED**.

The workload remains 6,305 natural original-residue masks, batch size 8, pinned model revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`. One shared six-file cache serves both nodes. Estimated incremental peak including original tars, extracted package/cache and a 32 MiB output budget is **104.3 MiB**, or **10.18%** of the existing quota. Require **128 MiB confirmed headroom**; current usage is unknown. No additional volume is proposed.

Storage staging, hash verification, model load/device transfer, output completion, merge and coordinator makespan will be recorded separately from GPU scoring. No throughput, RDMA/NCCL, speedup or durable-media claim is made before measurement.

Prepared artifacts: [staging checklist](../workflows/ospc-spark-v0.2.1/STAGING_CHECKLIST.md), [inert v4 workflow](../workflows/ospc-spark-v0.2.1/storage-stage-team15.HOLD.fz), [exact byte plan](../workflows/ospc-spark-v0.2.1/storage-plan.HOLD.json), [sanitized inspection](../workflows/ospc-spark-v0.2.1/storage-inspection.json). The historical proof remains in [phase-b-results.json](../findings/phase-b-results.json) and the original two workflow files; no new private endpoint/configuration is copied here.

[Validation receipt](../workflows/ospc-spark-v0.2.1/storage-validation.json): eight offline transport/HOLD tests and eleven presentation/provenance tests passed. The CLI's workflow-validation request timed out; server acceptance and real storage execution remain unverified. These fixtures do not constitute scientific VAST integration or a storage benchmark.

At 08:00 Central: confirm actual VAST backing, volume identity/policy/free quota, working existing context and authorized transfer route; obtain bounded execution approval; validate and stage the exact package/cache; then run the established node pilots and matched scientific trial with persistent output readback. If any gate fails, retain the completed personal-Spark result and mark the venue integration NOT RUN.
