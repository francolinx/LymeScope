# LYMESCOPE — verified original event benchmark

**PASS: all 6,305 original scientific evaluations reproduced exactly across physical Spark29 and Spark30 NVIDIA GB10s. This first validated full event benchmark showed negative scaling.**

The two-node workload reproduced all 6,305 scientific evaluations exactly, but took longer than the single-node baseline in this measurement.

Release: `lymescope-venue-verified-20261115`. The experiment finished at **10:43:33 AM Central on November 15, 2026** (`16:43:33.281543Z`). This publication contains only the original completed experiment; later optimization results are excluded. No inference or benchmark was run for this publication.

## Measurements and scope

| Measurement | Single node: Spark30 | Two nodes: Spark29 + Spark30 |
|---|---:|---:|
| Original tasks | 6,305 | 3,156 + 3,149 = 6,305 |
| Scoring forwards, batch 8 | 805 | 403 + 402 = 805 |
| Warm scoring wall time | 30.224031 s | 42.397251 s (maximum shard) |
| Spark29 shard warm scoring | — | 42.397251 s |
| Spark30 shard warm scoring | — | 16.233051 s |
| Prepared-input coordinator makespan | 52.110527 s | 67.982290 s |
| Maximum saved-score absolute / relative deviation | 0 / 0 | 0 / 0 |

Recorded warm-scoring overlap was **16.233049 s**. The coordinator phase took **30.457881% longer** on two nodes. The single/two ratio was **0.766531×** (rounded **0.767×**, below parity); the warm-scoring ratio was **0.712877×**. Neither is an acceleration claim. Full recorded precision is in [RESULT.json](RESULT.json) and [TIMING_BREAKDOWN.json](TIMING_BREAKDOWN.json).

These are prepared-input phases inside **one workflow**, with both GPU workers reserved. Spark29 was idle during single-node science. Coordinator makespans include process startup, model loading, computation, output writing, readback and validation; the two-node phase includes the merge. Common initial allocation/staging and final export are excluded from both ratios. Separate cold-launch one-node/two-node workflow makespans were not measured. One matched comparison provides no timing-variance estimate, general scaling result or established cause of the node asymmetry.

The common runtime restoration took 29.061633 s; final 25-file export window 6.542391 s; whole workflow 224.697596 s; independent laptop transfer/hash readback 4.053705 s. These overlapping stages must not be summed. Queue and dispatch cannot be separated precisely at subsecond resolution. Worker UTC clocks were not independently calibrated; local durations use `perf_counter`. A common wrapper observed frozen-scorer warm-loop boundaries without changing scoring.

## Scientific method and immutable identity

The frozen 30-sequence OspC panel contains 6,305 original-residue evaluations. Each example masks exactly one original residue; batch 8 groups examples without changing masks. Model: `facebook/esm2_t6_8M_UR50D`, revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`. Evaluation/inference mode, float32, eager attention, TF32 disabled, no autocast and full-vocabulary log-softmax were unchanged. No synthetic expansion, new dataset, new checkpoint or tuning was used in this original comparison.

Three warm-up forwards per process are separate from scoring. Each 210-mask correctness pilot used 27 scoring forwards plus three independent validation forwards. The full-panel and shard processes added no pilot-validation forwards. This workflow ran four inference processes: the Spark29 pilot, one full panel and two shards. The earlier successful Spark30 pilot was preserved rather than rerun.

Fixed tolerance: `abs(candidate-reference) <= 1e-4 + 1e-5*abs(reference)`. Acceptance checked exact task IDs, accession/position pairs, original residues, alignment mappings, sequence hashes, finite nonnegative scores, and model/settings provenance. Shards were disjoint and their union contained exactly 6,305 tasks, with no missing or duplicate tasks. Both absolute and relative differences in saved scores were zero.

The unchanged scorer emitted a legacy `timing_scope` string describing its personal-Spark origin inside raw timing receipts. That inherited string is **not the venue measurement scope**. The workflow IDs, phase records and timing breakdown above establish the event scope; it is documented here rather than silently rewriting the scorer's scientific receipt.

- [Frozen biological findings and methods](../../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/SCIENCE_FINDINGS.md).
- [Frozen reference scores](../../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/full_panel_v1/residue_nll.tsv), SHA256 `b27d926285a8dc338abceba953229089be4f35fcba7c166c1a922be146a6317f`.
- [Merged event scores](evidence/two-merged.tsv), SHA256 `c3675c9810d650b2358a70fff9e0df5b0d779718b699f22682c4a4ee2595cb69`. Byte hashes differ because ordering/shard metadata differ; task identities and numeric scores agree.
- [Frozen scorer/comparator hashes and task counts](WORKLOAD_CHECKS.json); six-file checkpoint hashes are preserved in [run timings](evidence/runs/one-Spark30/timings.json). No weights are included.
- [Original negative B11 diagnostic](../../sparkprep/experiments/frontier_antibody_v0.3.0_20261115T083852Z/RESULT_SUMMARY.md) remains unchanged: added signed discordance did not improve the primary diagnostic. Predictability does not establish antibody accessibility, antigen protection or clinical utility.

## Completed workflows and provenance

| Completed execution | ID |
|---|---|
| Original matched single/two-node workflow | `79319e56-f368-4eba-8cae-7c646737b9fc` |
| Spark29 worker | `3cb9809a-e25c-5aba-a112-48b6727f0a6d` |
| Spark30 worker/coordinator | `408e7d1c-34e5-5011-9610-a17e1ad551b5` |
| CPU runtime restoration on Spark30 | `ce0814b4-d6e2-57a8-8312-910e9421cea7` |
| Preserved earlier Spark30 correctness pilot | `37c34002-2578-4fe5-ac48-8798147235d3` |

The matched workflow and all three jobs finished; job exit codes were 0, with no recorded cleanup warnings. Scheduler physical-node attribution agreed with the original GPU inventory. [Sanitized workflow receipt](WORKFLOW_RECEIPT.json) preserves completed IDs, times, status and placement while omitting internal paths and raw infrastructure configuration.

**VAST backing was confirmed by onsite staff**, as documented in the original completed report with an approximately 39:17 recording reference. This public release does not include the private recording. Actual scientific I/O is supported separately by write/hash/readback receipts. Model weights used separate ephemeral storage. Effective quota was not independently established; no VAST throughput measurement, RDMA/NCCL claim or distributed-model capacity claim is made.

All **25 exported artifacts, 2,250,063 bytes**, passed independent size/SHA256 readback and were rehashed against the immutable receipts before publication. [Original readback receipt](READBACK_RECEIPT.json) describes the original bytes. [Publication provenance](PUBLICATION_PROVENANCE.json) maps original hashes to public hashes and explicitly records sanitization. All score TSVs and acceptance metrics remain byte-identical. The archive's 106 regular files comprise 104 manifest-listed payload files plus two manifest/checksum files, with no omissions.

## Presentation and publication boundary

The [completed offline event display and timing bars](../../demo/venue-secondnode-v1/index.html) and [short demo insert](DEMO_INSERT.md) reuse the existing experimental dimer image. Relative media/data dependencies are checked. HTML links on GitHub show source; use a local checkout to view the display. Browser rendering remains unverified, and Pages hosting is not claimed live.

Historical NOT RUN/HOLD receipts, the frozen biology, six README GIFs, prior Git history, datasets, model identity, scientific method and license terms are preserved. Current summaries identify this completed result. The existing verified PDF is not regenerated or replaced in this fallback release. Organizer eligibility/route confirmation, final approval and actual submission/upload remain separate manual actions; this GitHub release is not an organizer submission.
