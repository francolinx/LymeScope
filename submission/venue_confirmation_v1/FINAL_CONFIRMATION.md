# LymeScope — final confirmation, November 15, 2026

**PASS. Scientific execution is complete.** One predeclared confirmation pair ran a fresh full-panel Spark30 reference followed by the exact previously selected optimized two-node partition. Both complete outputs contained all 6,305 original tasks exactly once, with zero maximum absolute and relative NLL deviation against the immutable reference. No further scientific runs are planned.

| Observation | Spark29 warm scoring | Spark30 warm scoring | Prepared-input coordinator |
|---|---:|---:|---:|
| Original single node | idle | 30.224 s | 52.111 s |
| Original equal-count two nodes | 42.397 s | 16.233 s | 67.982 s |
| First optimized two nodes | 22.707 s | 22.871 s | 51.952 s |
| Confirmation: fresh single node | idle | 32.488 s | 54.568 s |
| Confirmation: same optimized two nodes | 20.765 s | 24.156 s | 50.039 s |

The confirmation pair's prepared-input coordinator time decreased by **8.3%**, a **1.091× ratio**, from its fresh single-node reference. The two optimized observations were **23.6% and 26.4% shorter** than the preserved original equal-count two-node phase. The direction of improvement recurred, with exact scientific reproducibility.

This is preliminary engineering evidence: the equal-count control was not repeated, the partition was originally selected after seeing the slowdown, and one confirmation pair does not establish timing variance, statistical significance, a general scaling law or a novel scheduler. Both confirmation phases had read-only telemetry; the original equal-count baseline did not. Phase order was fixed: single node then two nodes. No fastest-run-only selection is used; every completed observation is retained above.

## Identical scientific work

- Fresh single: physical Spark30, **6,305 masks / 805 scoring forwards**.
- Distributed Spark29: **1,691 masks / 216 forwards**, the same eight whole sequences as the first optimized trial.
- Distributed Spark30: **4,614 masks / 589 forwards**, the same remaining 22 sequences.
- Pinned ESM-2 8M checkpoint, six checkpoint files, tokenizer, original FASTA/alignment, residue identifiers/hashes, and frozen scorer unchanged.
- Batch 8, float32/eager, TF32 disabled, no autocast. Three warm-up forwards per process are separate. No new pilots, model search, partition retuning or additional experiments.
- Fixed tolerance: `abs(candidate-reference) <= 1e-4 + 1e-5*abs(reference)`.
- Independent laptop validation checked task identities, accession/position pairs, original residues, sequence hashes, finite scores, counts, model/runtime provenance, memory caps and per-process 120-second limits.
- All four comparisons passed: fresh single versus frozen; merged versus frozen; merged versus original single; merged versus fresh single. Maximum absolute and relative deviations were **0** in every comparison.
- The executed assignment hash was unchanged: `bc65b4c29ea0959e5df52fbbe8687c5c3c7893b741d3b3d4464097f79bc85547`.

## Physical execution and timing scope

Workflow: `d8331ef3-53ba-4cdb-94c9-985a4cd4377c`.

| Job | Physical machine | Job ID | Final state |
|---|---|---|---|
| Runtime preparation | Spark30 | `f3c7e2e7-ca49-5ded-821b-0819329c0565` | Finished, exit 0 |
| Worker A | Spark29 | `8148bb6d-ee81-50c3-a5a0-e1826d37aeed` | Finished, exit 0 |
| Worker B | Spark30 | `21c346d8-0dc1-5383-a759-b1798b628a4c` | Finished, exit 0 |

Physical-node attribution joins Fuzzball scheduler placement to node metadata and independently checks the known assigned GPU identities. The distributed scoring intervals overlapped for **20.765 seconds**. Host UTC epochs establish recorded overlap; independent clock calibration was not performed. Durations use monotonic process timers.

Both coordinator phases used already verified inputs/runtime. Spark29 remained reserved but idle during single-node science. The phases include child startup, model load/transfer, computation, result writing and applicable validation/merge; common initial preparation and final object export are excluded from both. The full combined workflow took **182.188 seconds** and includes BOTH phases. It is not a separate one-node versus two-node cold-launch experiment; no whole-workflow speedup is claimed. Component timings and known instrumentation gaps are recorded separately.

## Telemetry: measured clue, unresolved cause

During confirmation distributed scoring, Spark29 reported 507 MHz SM clock across 19 samples, 41°C and median 6.78 W. Spark30's 23 samples reported 2,483–2,515 MHz, 45–49°C and median 24.18 W. Both reported P0, four PyTorch threads and 2,808,000 kHz on allowed CPU cores. Runtime versions matched the prior accepted run.

Peak PyTorch allocation was 138,363,392 bytes on Spark29 and 137,579,008 bytes on Spark30; reserved memory and process RSS remained below the existing caps. GPU memory-used, memory-clock and power-limit fields were unavailable in the existing probe. No direct throttling-reason measurement was obtained. The clock/power difference is observed; its cause and any causal explanation of historical performance remain **UNRESOLVED**. No clocks, power limits, affinity, drivers or host settings were changed.

## Storage and provenance

The existing staff-confirmed VAST-backed project volume supplied immutable scientific inputs and persisted new result shards. Model weights remained in separate private ephemeral storage. All **24 exported artifacts, totaling 2,372,268 bytes**, passed object digest/size verification and independent laptop SHA256 readback. Worker fsync/readback receipts are retained. No vendor-throughput claim is made.

- Fresh single TSV SHA256: `b27d926285a8dc338abceba953229089be4f35fcba7c166c1a922be146a6317f`.
- Merged optimized TSV SHA256: `ea043d2df33841260d322caebe2a8939750f0df9818920653008b872ffbfee84`.
- Different single/merged hashes reflect ordering and shard metadata; all scientific task values compare exactly.
- Original and first optimized receipts, frozen inputs/results, negative B11 biological diagnostic and six animations remain unchanged.
- A local log-retrieval command initially used a stage UUID where the CLI expected a job name. Correcting the read-only command retrieved all logs; no scientific job was retried.

## Protected submission

The existing reviewed PDF remains [LYMESCOPE_FRONTIER_VERIFIED_20261115.pdf](../../output/pdf/LYMESCOPE_FRONTIER_VERIFIED_20261115.pdf), with the clean `LymeScope-offline-submission-event-v4.zip` as its offline package. They contain the original and first optimized results and are preserved unchanged. This confirmation is a separately reviewed addendum, not a reason to delay submitting that valid package.

Public main advanced independently to `6ad4bb776a1f0a89132f465fd6f63ecff93c73a2`, containing the original benchmark fallback. Its sanitization and other new work must be preserved. Local release `1aa8f2e922b3db0efdda8c1adfd88aa000c344b8` remains protected; it must not be force-pushed over newer main. Publication reconciliation is prepared in a separate worktree. New GitHub publication and actual organizer upload still require explicit lead approval. Organizer format/eligibility confirmation and a successful upload receipt are not yet available.

[Independent acceptance](RESULT.json) · [Readback hashes](READBACK_RECEIPT.json) · [Physical workflow receipts](WORKFLOW_RECEIPT.json) · [Telemetry](NODE_OBSERVATIONS.json) · [Assignment](ASSIGNMENT.json)
