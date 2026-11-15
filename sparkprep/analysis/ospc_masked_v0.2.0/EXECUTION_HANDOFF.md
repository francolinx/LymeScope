# Prepared execution handoff — HOLD

Nothing here is authorization to execute. Current stage: local implementation/offline fixtures only. Model staging is the next bounded request; dependency preparation, real-model pilot and the matched benchmark each need their appropriate later scope. No model/library/cluster availability is inferred from the old infrastructure receipts.

## Staged project layout

After later explicit staging approval, preserve the repository-relative layout below `/project/lymescope-v0.2.0/` on the existing project volume. The new code finds the original frozen data by relative path. No new volume or resize is needed by the design. Model transfer to this event volume is **not** included in the current laptop staging request.

- `sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/`: original required saved inputs/results, unchanged.
- `sparkprep/analysis/ospc_masked_v0.2.0/`: source, lock and plans from this feature branch.
- `models/esm2_t6_8M_UR50D/<pinned revision>/`: the five verified allowed files, no alternate weights.
- `approvals/pilot.json`, then separately `approvals/one.json` and `approvals/two.json`: scope receipts supplied only after approval.
- `approved-pilot/pilot.json`: exact passing actual-model pilot receipt, preserved and hashed.
- `runs/<unique approved run_id>/`: new results; existing receipt paths cannot be overwritten.

Approval receipt required fields: `approved: true`, `mode: pilot|one|two`, unique safe `run_id`, `plan_sha256`, `source_sha256`, `model_revision`, `max_wall_seconds: 300`, `max_nodes: 1` (pilot/one) or `2` (two), and `downloads_allowed: false`. Use the exact hashes from `plans/workload.json`. There is deliberately no ready-approved receipt in the repository. These fields guard accidental execution; they do not replace the user's actual authorization.

## Runtime and pilot gates

Confirm the selected already-present event image has compatible torch, transformers and safetensors and supports the assigned GPU. Verify availability through separately authorized inspection before using the HOLD workflows; do not automatically pull an image or install missing packages. Current-runtime/import compatibility and scheduler syntax validation remain NOT RUN. A failure stays a failure; no alternate model, package installer, driver fix or CPU inference fallback is embedded in the worker.

Run the real-model pilot only after its bounded approval. It uses eight actual positions, singleton, batch-16 and repeated batch-16 passes on the same loaded model: 14 pilot forwards, 24 pilot examples, plus one separately counted warm-up. All three pairwise comparisons, token assertions and independent float64 normalization checks must pass. Record allocator memory, runtime and absolute/relative deviations. No new training, embeddings, mutations, permutation tests or alignment is included. A fixture or failed pilot cannot unlock benchmark execution.

## Matched one-node/two-node pair

The three prepared files are `workflows/ospc-masked-v0.2.0-{pilot,one-node,two-node}.HOLD.fz`. They reuse the original event v4 image/resource/mount and generic multinode pattern. They are **not scheduler-validated** in this task. Before submission, separately authorized placement must establish **Spark30 alone**, then **Spark29 and Spark30**. The generic templates do not themselves guarantee exact host placement; if the authorized scheduler cannot target those nodes, HOLD. Ingestion rejects any other node set. Export the scheduler Hosts/container mapping; logical ranks/container hostnames alone are insufficient.

Both benchmark modes use the same frozen input/alignment, pinned model, source, float32 settings, batch size and complete scored-position set. Two nodes divide whole sequences; they do not repeat examples. Each worker loads the same pinned model once and performs one separately timed/countable warm-up call. Model load and warm-up overhead may outweigh any compute gain. Do not enlarge work to force a favorable graph.

No automatic remote export or extra job is implemented. Preserve/export the small rank JSON receipts and scheduler lifecycle/host evidence through the existing authorized export process after each completed run. Record export completion time so workflow wall time includes it. Workflow files mount only the existing volume and do not create reports volumes or new repositories.

## Ingestion evidence shape

Create a factual scheduler-export JSON from the completed job's recorded evidence, with `source: scheduler_export`, the approved `run_id`, actual `workflow_id` and `job_id`, and `ranks` containing `rank`, `container_hostname`, `container_id`, `physical_node_id`. Exact physical IDs are `CIQ-CHI-SPARK30` (one), and `CIQ-CHI-SPARK29` plus `CIQ-CHI-SPARK30` (two). Preserve the raw scheduler export and record its source file/hash; do not infer physical identifiers from ranks. Record timezone-aware `submitted_at`, `started_at`, `finished_at`, `export_completed_at`, plus `queued_at`/`dequeued_at` from the actual queue events and `startup_started_at`/`startup_finished_at` spanning recorded image/container startup. Queue/startup can overlap other phases and are not summed as wall time. Missing events must remain a blocker for this complete timing contract, not invented zeroes.

Ingest one/two receipts separately with `python -B ingest.py --plan plans/workload.json --groups plans/grouping.json --mode one|two --receipts <rank receipts> --scheduler <scheduler evidence> --output <new versioned result.json>`. The API `compare_runs(one_result, two_result, plan)` validates the matched pair against predeclared float tolerances; it refuses fixture results by default. Save its returned comparison to a new path with `core.write_new`.

Report loading, model transfer, per-batch host/device transfer, compute, output transfer, worker time, queue/staging, job wall, export and total workflow separately. Preserve aggregate denominators and the exact common eligible rank columns. A one-pair timing result supports a pilot observation only; dependent alignment columns do not support naive significance claims.

Ingestion additionally measures validation, merging and sensitivity time, and reports elapsed workflow plus that processing time as time to analyzed result. It explicitly excludes final JSON serialization and any manual idle delay after export. Failure receipts retain successful position inventories, failed batch positions and actual/successful call counts; a killed process without a receipt requires scheduler failure evidence and cannot pass. Per-sequence hashes and maximum length (214 residues) accompany complete receipts.

## Cutoff and fallback

The worker rejects new inference at or after `2026-11-15T10:30:00-06:00`, checks the deadline between forwards, and refuses a passing receipt if a forward returns beyond it. The scheduler's five-minute timeout is the external hard stop for hung work. Submission preparation takes priority. If any gate is unmet, leave the model results **NOT RUN** and use the completed CPU baseline for noon submission and the 4½-minute demo.
