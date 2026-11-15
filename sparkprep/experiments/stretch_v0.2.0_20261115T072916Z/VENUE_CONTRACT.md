# OspC masked-original-residue workload — implementation contract v1

Status: the personal-Spark real-model Q07337 correctness pilot passed. Full-panel execution requires approval of the measured resource proposal. No event node has been contacted. This package extends the frozen v0.1.0 analysis; its files are unchanged.

## Immutable inputs and scientific question

Use `inputs/panel.fasta` (30 original natural sequences) and the exact `inputs/aligned.fasta` (218 columns). `provenance/frozen_inputs.json` pins source file bytes; `results/shard_manifest.json` records all accessions, sequence SHA256, lengths and deterministic assignments. Removing gaps reproduces every original sequence exactly. There are 6,305 original standard residues and therefore exactly 6,305 scored masking examples. The 202 fully covered columns and 76 fully covered identical columns are preserved baseline facts.

Research question: where do empirical panel agreement and model predictability diverge? The pilot alone does not answer that across the panel. Conservation, learned conditional likelihood, contact geometry, accessibility, antigenicity and protection remain separate concepts.

## Pinned model and runtime

Model: `facebook/esm2_t6_8M_UR50D`, revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`; 7,512,474 actual parameters. Only six files are allowed; all identities/sizes/checksums are in `provenance/model_download_receipt.json`. Approved payload and verified actual payload: 31,387,085 bytes, below 32,000,000 bytes. No weights are included in Git or the portable scientific archive.

Tested personal runtime: Linux aarch64, Python 3.12.3, PyTorch 2.14.1+cu130, CUDA runtime 13.0, Transformers 5.20.0, safetensors 0.8.0, tokenizers 0.23.3, huggingface-hub 2.2.0, numpy 2.5.4. Driver 580.178.04, NVIDIA GB10 capability 12.1. Do not silently substitute a runtime: record venue actual versions and validate against the reference scores/tolerance. If unavailable, report runtime mismatch rather than install packages without approval. Matplotlib is used only to reproduce the optional scientific figure, not inference.

## Exact scoring and correctness

`provenance/method_contract.json` records the user's supplied Claude final definition. For sequence s and natural residue i, construct an independent copy of the original full-length sequence with only that residue replaced by MASK. NLL = minus the natural-log softmax probability assigned to its original amino-acid token at that position. The softmax uses all 33 model vocabulary logits; do not renormalize to 20 amino acids. Multiple independently masked copies may share a batch; never put multiple masked residues into one example.

No alignment gaps, CLS, EOS or padding are masked/scored. Token count must equal L+2; token 0 is CLS, tokens 1..L are the exact original residues, token L+1 is EOS. Unknown/special residue tokens cause failure. `residue_alignment_mapping.tsv` gives the accession:position task key and exact frozen alignment column. Each sequence SHA256 is carried into every score row. Full-length sequences include precursor/signal-peptide context; no mature-protein trimming is performed.

Use model.eval(), torch.inference_mode(), float32, eager attention, TF32 disabled, no autocast or gradients; seed 0, deterministic algorithms, CUBLAS_WORKSPACE_CONFIG=:4096:8, four CPU threads, batch size 8 (last batch may be smaller). A pilot scores all 210 residues of Q07337 and independently recomputes first/middle/last positions in batch size one, using logsumexp minus original-token logit. Ten tests cover masking and a known analytical full-vocabulary probability, task completeness and alignment/structure mapping.

## Task assignment and exact counts

FASTA/alignment sequence order is fixed. A sequence of ordinal k belongs to shard k modulo N, N=1 or 2. All masks for one sequence stay together. One node: shard 0, all 6,305 masks, 805 scoring forward passes at batch size 8. Two nodes: shard 0 has 3,156 masks/403 scoring passes; shard 1 has 3,149 masks/402 scoring passes. No task may be missing or duplicated. Each process separately records three warmup forward passes, each with eight masked examples; these 24 examples are not scientific result rows. Pilot-only validation adds three batch-one forward passes and examples. Report these counts separately; do not equate forward passes with mask count.

## Invocation on one node, then two

After explicit venue access authorization, transfer this package and a separately verified local model cache to each node. Run the same package/runtime/model/precision/batch size for both trials. Start each timed process fresh. Use an existing matching Python as PYTHON and the verified local six-file cache as MODEL. No inference code downloads models.

```bash
# Run from the extracted package directory. Output directories must be new.
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
"$PYTHON" -m unittest discover -s tests -v
# One node, full scientific task set:
timeout 120s "$PYTHON" src/masked_nll.py --model-dir "$MODEL" --method-contract provenance/method_contract.json --shards 1 --shard 0 --batch-size 8 --output results/event_one_node_run1
# Two nodes, launched concurrently by the authorized venue operator:
# Spark29:
timeout 120s "$PYTHON" src/masked_nll.py --model-dir "$MODEL" --method-contract provenance/method_contract.json --shards 2 --shard 0 --batch-size 8 --output results/event_two_node_run1_shard0
# Spark30:
timeout 120s "$PYTHON" src/masked_nll.py --model-dir "$MODEL" --method-contract provenance/method_contract.json --shards 2 --shard 1 --batch-size 8 --output results/event_two_node_run1_shard1
# Collect both shard outputs locally, then:
"$PYTHON" src/summarize_scores.py --scores results/event_two_node_run1_shard0/residue_nll.tsv results/event_two_node_run1_shard1/residue_nll.tsv --output results/event_two_node_run1_merged
# Verify all 6,305 scores against the one-node result:
"$PYTHON" src/compare_runs.py --reference results/event_one_node_run1/residue_nll.tsv --candidate results/event_two_node_run1_merged/residue_nll_merged.tsv --output results/event_one_vs_two_validation.json
```

Compare one-node and two-node values using absolute error <= 1e-4 + 1e-5 * abs(reference NLL). IDs, original residues, original sequence SHA256, alignment columns and task sets must match exactly. Nonfinite values or missing/duplicate tasks fail the run. This tolerance is a proposed cross-node acceptance criterion; the personal pilot's observed batch-one/batch-eight difference was at most 9.54e-7 nats, not an empirical two-node validation. Compare Q07337 against the personal pilot to validate venue runtime before the full event run.

## Timing and resources

Synchronize CUDA around every timed forward/log-softmax block and report model load+GPU transfer, first forward after loading, remaining warmup forwards, warm scoring wall time, per-sequence synchronized inference/log-softmax time, process wall scope and peak process/GPU memory separately. New-process loading is **process-cold**, not guaranteed disk-cold; the OS page cache is uncontrolled. Do not flush caches or disturb other services.

Personal pilot: model load+transfer 0.338836 s; first forward 0.299191 s; next warm forwards 0.012495/0.011979 s; 210-mask warm scoring 0.384158 s; inference+log-softmax 0.342025 s. Peak allocated GPU 135,659,520 bytes, reserved GPU 182,452,224 bytes; RSS 1,716,289,536 bytes. Recorded process wall is 1.104543 s after imports through correctness/score export, not shell startup-to-exit.

Full-panel proposal, pending approval: about 12 seconds warm scoring by linear pilot extrapolation, hard external process timeout 120 seconds, allocated GPU cap 2 GiB, reserved cap 4 GiB, process RSS cap 16 GiB, require at least 8 GiB free GPU-visible memory after model load. These are abort thresholds, not measured full-panel usage or hard memory reservations. Do not train, expand the panel, change model or increase batch size. The code checks memory/time after each bounded batch; external timeout bounds a stalled process. Leave existing services untouched.

For a benchmark, record one coordinator's launch-to-completion makespan for each trial, including dispatch/collection overhead as explicitly selected, plus individual node timings. Do not add per-node elapsed times and call that two-node wall time. Approximate compute-only two-node wall by max(shard warm-scoring times), labeled accordingly; report coordinator makespan separately. One trial is demonstrative, not a robust performance distribution. Personal-Spark timings are never matched event-cluster baselines.

## Output and analysis contract

`residue_nll.tsv`: task_id, accession, sequence_position (1-based), alignment_column (1-based), original_residue, sequence_sha256, nll_nats, shard. `timings.json` records model/runtime hashes and masked-example/forward counts. `pilot_correctness.json` records token/mask and independent batch-one checks. PPL = exp(mean NLL) over each sequence's documented original positions 1..L, more precisely masked pseudo-perplexity, not autoregressive sequence perplexity.

`summarize_scores.py` rejects incomplete/duplicate/incorrectly mapped inputs, then emits per-sequence mean NLL/pseudo-perplexity and per-column arithmetic mean NLL over observed standard residues, sample SD, coverage, modal fraction and panel sensitivity. No gaps are imputed. Column rank discordance uses only the 202 fully covered columns and remains descriptive, not a significance/protection score. Dimer contacts remain a separate annotation. Training-set overlap, taxonomic sampling, phylogenetic relatedness, small model capacity, token conditioning, precursor context and alignment uncertainty limit interpretation.

## Cache plan and fallback

On this Spark, weights are in `/home/darkstar90/lymescope-sparkprep/.model-cache/esm2_t6_8M_UR50D_c731040fcd8d73dceaa04b0a8e6329b345b0f5df`, outside tracked paths. Stage only these six verified files to each event node by an authorized transfer, with an additional 31,387,085 bytes per node. Validate hashes before loading. Do not redownload blindly or upload caches to GitHub. Dependencies must already match or need a separate approval.

If model load/GPU execution fails, record NOT RUN with the exact error; run standard-library CPU panel/structure checks and preserve their results. Do not invent NLLs, silently swap checkpoint/device/dtype, repair drivers, install packages or submit event jobs without approval. The tests requiring torch can run in the existing CPU-capable runtime; CPU real-model scoring would need a bounded measured proposal if GPU execution fails.
