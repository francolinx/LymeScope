# Venue trial — prepared, NOT SUBMITTED

Use the completed personal-Spark package at commit `aafe818a20ea025370cf4b65145a9684e80aaaef`, directory `sparkprep/experiments/stretch_v0.2.0_20261115T072916Z`. The authoritative [VENUE_CONTRACT](../../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/VENUE_CONTRACT.md) defines this batch-8 trial. The earlier batch-16 laptop `.HOLD.fz` plans are preserved development work and must not be used for this matched comparison.

## One bounded next authorization

Authorize event access and transfer of this existing scientific package plus the already verified six-file model cache to **Spark29 and Spark30**, followed by the deterministic probe and Q07337 correctness pilot on each node, then **one** complete Spark30 trial and **one** concurrent two-shard Spark29/Spark30 trial only if both pilots pass. Each inference process has a 120-second timeout. No model redownload, dependency install, driver repair, visibility change or publication is included. New research must finish before the existing 10:30 AM Central cutoff; if the window has passed, require a revised explicit execution window.

This is a proposed scope, not approval. Nothing has been transferred or executed from the laptop.

Storage addendum: [VAST_STORAGE_PLAN.md](VAST_STORAGE_PLAN.md) and [STAGING_CHECKLIST.md](STAGING_CHECKLIST.md) now specify the existing shared-volume route, exact byte contracts and an inert v4 staging workflow. This prepares a single shared model/package copy; it changes no scientific task or scoring setting. VAST backend identity remains UNVERIFIED, and current live storage reads timed out. No remote write is authorized by that read-only inspection.

## Stage existing bytes

- Scientific source/data/figures are committed. Preserve their bytes and verify `FILE_MANIFEST.json` with the supplied `src/verify_package.py` in a fresh venue copy.
- The full scientific archive remains on the personal Spark. Its local location/transport route must be confirmed before transfer; do not invent a GitHub archive attachment. The committed directory is sufficient to obtain scientific files.
- The separate model-only tar is **not in Git**: `/home/darkstar90/lymescope-sparkprep/.model-cache/transfer/esm2_t6_8M_UR50D_c731040fcd8d73dceaa04b0a8e6329b345b0f5df_six_files.tar`.
- Tar size **31,395,840 bytes**, SHA256 `4e24f435628bb2c3b1a1a27664807c5d8c41ce7a94d3c2031b0f96363cb5d9ab`. Six extracted files total **31,387,085 bytes per node**. Check safe member paths and the six SHA256 values in `provenance/model_download_receipt.json`; use a new ignored/cache destination, never a Git upload.
- Pinned ESM-2 revision: `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`. Weight SHA256: `24c5fa474c48f3b754b86efe752d5f189d2bcd88190fa2270fc92b2ef3034189`.
- Keep run outputs outside the imported source/evidence directory. Do not overwrite package manifests or prior run directories.

## Resolve these blockers before submission

1. Explicit authorization, valid execution window and an authorized transfer/access route to the two event nodes.
2. Current runtime availability. Start with the previously verified Team 15 PyTorch image `docker://nvcr.io/nvidia/pytorch:25.11-py3` and existing volume. It does **not** establish that Transformers/safetensors/tokenizers or the pinned checkpoint are currently staged. Record actual versions; no implicit installation or image download.
3. Confirm supported scheduler placement for physical Spark30 versus Spark29/Spark30. A container hostname or two generic workers alone is insufficient. Save the scheduler task-to-physical-node mapping and require concurrent shard intervals on distinct physical nodes. The JSON task specification is not claimed to be scheduler-validated Fuzzball YAML.
4. Verify the package/cache, deterministic GPU probe, and real Q07337 pilot on each actual runtime. Compare all 210 pilot scores against the saved personal reference with the declared tolerance before full execution.

## Exact trial

The machine-readable [trial.HOLD.json](trial.HOLD.json) records the commands and required task identities. Use the same package, model, batch size **8**, float32/eager settings, seed 0, TF32 disabled, no autocast and four CPU threads for both complete trials. Whole sequences follow their frozen alignment ordinal modulo shard count.

| Trial | Physical node | Shard | Scientific masks | Scoring calls |
|---|---|---:|---:|---:|
| One node | Spark30 | 0/1 | 6,305 | 805 |
| Two nodes, concurrent | Spark29 | 0/2 | 3,156 | 403 |
| Two nodes, concurrent | Spark30 | 1/2 | 3,149 | 402 |

Each process additionally uses three warm-up calls / 24 examples. Each Q07337 pilot uses 210 masks / 27 scoring calls, three warm-ups / 24 examples, and three independent validation calls / examples. Those pilot/warm-up observations are excluded from the complete scientific inventory. No repeated biological data or larger model is used.

Set `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `PYTHONDONTWRITEBYTECODE=1`, and `CUBLAS_WORKSPACE_CONFIG=:4096:8`. Resolve `$PYTHON`, `$MODEL`, `$PACKAGE`, `$RUN` only after authorization. Launch the published scorer directly; no second implementation is required. Run `src/summarize_scores.py` on the two saved shards, then `src/compare_runs.py` against the single-node output, writing new output paths.

Acceptance requires exact input/model hashes, accession/residue/mapping/task identity, all 6,305 tasks once, correct per-node assignments and successful counts, finite NLLs, and `abs(candidate-reference) <= 1e-4 + 1e-5*abs(reference)`. Keep the tolerance fixed. Record maximum absolute and relative deviation (for zero reference use zero if equal, otherwise report undefined/infinite explicitly) in a new venue receipt; the published comparison tool currently reports maximum absolute error only. Record failures and missing positions; never fill them with zeros.

## Timing and resource limits

Record coordinator queue/dispatch/startup, package/model transfer, model load plus GPU transfer, first forward, other warmups, warm scoring, output transfer, merge/validation and complete launch-to-result makespan separately. Published worker `end_to_end_wall_s` starts after imports and is not the entire workflow. Preserve that label. Two-node wall time is coordinator makespan, not the sum of workers. `max(shard warm scoring)` may be shown separately as compute-only wall time. One timing pair is a pilot; negative scaling is a valid result.

Abort thresholds: 120 seconds per inference process, GPU allocated below 2 GiB, reserved below 4 GiB, process RSS below 16 GiB, at least 8 GiB free GPU-visible memory after loading. These are checks, not memory reservations. Preserve existing services. Runtime mismatch/failure means NOT RUN with the exact error; no silent CPU/model/precision substitution.

Independent Fuzzball tasks demonstrate task throughput, not NCCL/RDMA, tensor parallelism or distributed model capacity. The completed offline demo and personal-Spark result remain the fallback.
