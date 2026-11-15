# Sunday morning: exact deployment, protected submission

**Prepared only. No event connection, transfer or job was performed during the Frontier sprint.** All times are Chicago / Central on November 15, 2026. The noon submission and 1:00 PM five-minute demo take priority over additional science.

The complete fallback is commit `9e46ec46b85ed2990f89e16cbf6e7aba707e0c95`, protected by local branch `fallback/frontier-20261115T084009Z` and the published feature history. The current submission review URL is [feature/ospc-masked-scoring-v0.2.0](https://github.com/francolinx/LymeScope/tree/feature/ospc-masked-scoring-v0.2.0). **Default main is deliberately unchanged** until the lead approves integration. Use the branch-specific URL if submitting before that approval.

## 07:30–08:00 — Access and eligibility

1. Ask organizers to confirm solo-team eligibility, pre-existing work/personal-hardware use, AI-assisted development and the exact submission destination/file requirements. Do not infer eligibility from repository visibility or attendance.
2. Obtain [the single bounded authorization](BOUNDED_VENUE_APPROVAL.md) for event access, transfer and the pilot/one-node/two-node trial. The overnight sprint does not authorize those actions.
3. Confirm Team 15 access and assigned **physical Spark29 and Spark30**, preserving existing volumes, services and users' workloads. Record the supported scheduler placement method. Do not assume a generic two-worker job guarantees these physical nodes.
4. Inspect the existing `lymescope-project` volume and already available runtime/image. The historical image is `docker://nvcr.io/nvidia/pytorch:25.11-py3`; this is a starting candidate, not proof of current dependencies or a license to pull/install anything.
5. Open `docs/index.html` locally and rehearse the four stories before any venue GPU test. Keep the frozen viewer and original PNG/SVG figures available. Browser rendering still needs a real check.

## 08:00–08:30 — Verify and stage the exact science

Authoritative inputs: [VENUE_CONTRACT.md](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/VENUE_CONTRACT.md), [staging handoff](../workflows/ospc-spark-v0.2.1/VENUE_HANDOFF.md), and [exact task plan](../workflows/ospc-spark-v0.2.1/trial.HOLD.json). Use scientific commit **`aafe818a20ea025370cf4b65145a9684e80aaaef`**. New optional antibody work must not silently replace this benchmark input.

Stage a fresh scientific copy from the committed experiment directory or the verified personal-Spark archive through an authorized route. The archive and model tar are not GitHub attachments. Confirm source location/transport explicitly; preserve host-key/security checks. Record copy start/end, bytes, source/destination and SHA256.

The model-only tar already on the personal Spark is:

```text
/home/darkstar90/lymescope-sparkprep/.model-cache/transfer/esm2_t6_8M_UR50D_c731040fcd8d73dceaa04b0a8e6329b345b0f5df_six_files.tar
31,395,840 bytes
SHA256 4e24f435628bb2c3b1a1a27664807c5d8c41ce7a94d3c2031b0f96363cb5d9ab
```

Inspect safe member names before extraction into a **new** model directory. Allow only `README.md`, `config.json`, `model.safetensors`, `special_tokens_map.json`, `tokenizer_config.json`, `vocab.txt`. The extracted payload is **31,387,085 bytes per node**, with hashes in the published model receipt. No alternative checkpoint or `.bin` format; no Git weight upload or blind redownload.

Pinned revision: `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`. Weight SHA256: `24c5fa474c48f3b754b86efe752d5f189d2bcd88190fa2270fc92b2ef3034189`.

Record actual node/runtime versions. Personal reference: Linux aarch64, Python 3.12.3, torch 2.14.1+cu130, CUDA runtime 13.0, Transformers 5.20.0, safetensors 0.8.0, tokenizers 0.23.3, huggingface-hub 2.2.0. CPU science tests also use numpy/scipy. A mismatch must be reported and validated against the reference; no package installation or driver repair is implied.

### Operator command sheet — execute only after authorization

On each confirmed node, set `PACKAGE`, `MODEL`, `RUN` and `PYTHON` to the approved existing paths. `RUN` must be a new result directory **outside the immutable package**. Assign `NODE` only from verified physical-node evidence, not a guessed container hostname. Use the same package, runtime, model and precision on both nodes.

```bash
set -euo pipefail
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
export CUBLAS_WORKSPACE_CONFIG=:4096:8
# Required operator-resolved values; no defaults or automatic downloads:
: "${PACKAGE:?verified scientific copy}" "${MODEL:?verified six-file cache}"
: "${RUN:?new external output root}" "${PYTHON:?existing compatible Python}"
: "${NODE:?scheduler-confirmed Spark29 or Spark30}"
test ! -e "$RUN"
mkdir -p "$RUN"
cd "$PACKAGE"
"$PYTHON" -B src/verify_package.py --model-dir "$MODEL" --output "$RUN/package-model-verification.json"
"$PYTHON" -B -m unittest discover -s tests -v >"$RUN/tests.log" 2>&1
"$PYTHON" -B src/gpu_probe.py >"$RUN/gpu-probe.json"
timeout 120s "$PYTHON" -B src/masked_nll.py \
  --model-dir "$MODEL" --method-contract provenance/method_contract.json \
  --pilot --shards 1 --shard 0 --batch-size 8 --output "$RUN/pilot"
"$PYTHON" -B src/compare_runs.py \
  --reference results/pilot_v1/residue_nll.tsv \
  --candidate "$RUN/pilot/residue_nll.tsv" --reference-subset \
  --output "$RUN/pilot-vs-personal.json"
```

The GPU probe is an execution step requiring approval. A passing probe does not replace the model pilot. The Q07337 pilot must contain all **210** original residues: **27 scoring calls**, **3 warm-up calls / 24 examples**, **3 independent validation calls / examples**. Save actual device identity, memory, model hashes and tokenizer/correctness checks. If either venue pilot fails, stop the scientific benchmark and retain the completed personal result.

## 08:30–09:30 — One identical-workload timing pair

The operator dispatches these as **independent Fuzzball GPU tasks** through the verified Team 15 workflow. Reuse the published scorer directly. Confirm supported placement, job IDs and physical-node readback before interpreting the comparison; no unverified YAML placement field is supplied here.

### Trial A: Spark30 only

```bash
# On scheduler-confirmed physical Spark30, using a fresh process:
timeout 120s "$PYTHON" -B src/masked_nll.py \
  --model-dir "$MODEL" --method-contract provenance/method_contract.json \
  --shards 1 --shard 0 --batch-size 8 --output "$RUN/one_node_run1"
```

Expected: **6,305 successful scientific masks / 805 scoring calls**, plus three warm-ups / 24 examples.

### Trial B: launch concurrently on distinct physical nodes

```bash
# Spark29 task:
timeout 120s "$PYTHON" -B src/masked_nll.py \
  --model-dir "$MODEL" --method-contract provenance/method_contract.json \
  --shards 2 --shard 0 --batch-size 8 --output "$RUN/two_node_run1_shard0"
# Spark30 task (concurrent, not sequential after the command above):
timeout 120s "$PYTHON" -B src/masked_nll.py \
  --model-dir "$MODEL" --method-contract provenance/method_contract.json \
  --shards 2 --shard 1 --batch-size 8 --output "$RUN/two_node_run1_shard1"
```

Expected Spark29: **3,156 masks / 403 scoring calls**. Expected Spark30: **3,149 masks / 402 scoring calls**. Each task has three additional warm-up calls / 24 examples. Fixed alignment sequence ordinal modulo two assigns complete sequences; no artificial repetitions.

Collect both outputs plus the one-node result to a fresh coordinator directory `COLLECTED`, record transfer/collection time, then:

```bash
"$PYTHON" -B src/summarize_scores.py \
  --scores "$COLLECTED/two_node_run1_shard0/residue_nll.tsv" \
           "$COLLECTED/two_node_run1_shard1/residue_nll.tsv" \
  --output "$COLLECTED/two_node_run1_merged"
"$PYTHON" -B src/compare_runs.py \
  --reference "$COLLECTED/one_node_run1/residue_nll.tsv" \
  --candidate "$COLLECTED/two_node_run1_merged/residue_nll_merged.tsv" \
  --output "$COLLECTED/one_vs_two_validation.json"
```

Exact task IDs, original residues, accessions, original sequence SHA256 and alignment columns must match, with **6,305 tasks exactly once**. Nonfinite scores, missing/duplicate tasks or mismatched method/model/precision fail acceptance. Numerical tolerance remains `abs(candidate-reference) <= 1e-4 + 1e-5*abs(reference)`. Never widen tolerances after observing outcomes.

The laptop's [small acceptance extension](compare_venue_scores.py) reuses the published comparator, checks both files against frozen residue identities, and adds maximum relative deviation with an explicit zero-denominator policy. It needs only the Python standard library and the reviewed repository checkout, including the original scientific package; it does not execute a model. On the coordinator, set `CHECKOUT` to that reviewed checkout and run:

```bash
"$PYTHON" -B "$CHECKOUT/docs/compare_venue_scores.py" \
  --reference "$COLLECTED/one_node_run1/residue_nll.tsv" \
  --candidate "$COLLECTED/two_node_run1_merged/residue_nll_merged.tsv" \
  --output "$COLLECTED/one_vs_two_complete_numeric_receipt.json"
```

For each 210-residue pilot, use `--pilot` and the published pilot reference. Output creation is exclusive: choose a new receipt filename instead of overwriting a prior run. A numerical PASS does **not** establish matching model/runtime, physical placement, simultaneous execution or timing; those require the separate receipts below. Five offline saved-data/fixture tests passed on the laptop; no venue inference was performed.

### Timing receipt required before a speedup claim

Save scheduler exports mapping job/container identities to physical nodes; verify Spark29/Spark30 are distinct and the shard execution intervals overlap. Record all stages from one coordinator clock: queue, dispatch/startup, staging, load/transfer, first forward, other warm-ups, warm compute, output transfer, merge/validation and total launch-to-result makespan. Keep per-node values as well. A worker hostname alone is not physical attribution.

Worker `end_to_end_wall_s` begins after imports. Report it as such. **Do not add worker elapsed times and call the sum two-node wall time.** `max(shard warm scoring)` is a separately labeled compute-only estimate; coordinator makespan is the full-workflow comparison. One timing pair is a pilot, not a scaling law. Negative scaling is valid evidence.

The pinned scorer's `timing_scope` text contains the literal phrase “Personal Spark”; preserve its source and raw receipt. For a future event run, the separate coordinator receipt must establish actual venue/workflow/node provenance rather than treating that hardcoded text as the run location. No timing from the saved personal result substitutes for a measured one-node event baseline.

Use [the receipt template](venue-receipt-template.json); all null fields are unmeasured. No speedup is populated automatically.

Abort thresholds: **120 seconds per inference process**, allocated GPU <2 GiB, reserved GPU <4 GiB, RSS <16 GiB, at least 8 GiB free GPU-visible memory after load. These are code abort checks, not reservations. Preserve existing services; no cache flush, larger model, changed batch size, repeated data, package repair or driver work.

## 09:30–10:30 — Controlled stretch only if secure

Integrate a validated Spark experimental-evidence handoff only after reviewing its exact commit, source provenance, chain/residue mapping, null semantics, eligible set, tests and interpretation. One verified complex outranks several speculative overlays. Keep the existing benchmark and submission fallback intact. No automatic larger checkpoint, ProteinMPNN, new sequence design or unbounded sweep.

## 10:30–11:30 — Freeze and submit

Stop new research jobs at **10:30 AM Central**. Preserve failures/inconclusive results. Review the final branch commit, machine-readable claim index and sources; update only verified claims. Confirm public branch accessibility and browser/media behavior. Ask the lead for main/hosting approval as needed; otherwise deliver the exact feature-branch URL.

Prepare the organizer-requested files and verify the destination Google Drive folder with the lead/organizer. **No automated external submission is authorized by this runbook.** Keep the one-pager, five-minute script and saved figures available offline. Rehearse to 4:30 with a 30-second buffer.

**12:00 PM Central — hard submission deadline. 1:00 PM — live demonstrations.** A failed venue test must not jeopardize the already completed scientific submission.
