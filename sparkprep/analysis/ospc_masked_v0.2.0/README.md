# OspC masked-residue scoring v0.2.0

Feature branch: `feature/ospc-masked-scoring-v0.2.0`. Incremental extension of the preserved v0.1.0 CPU result. No existing viewer, frozen input/output or historical receipt is changed.

The user's final Claude reference and accepted corrections are reconciled in [CONTRACT.md](CONTRACT.md). Gemini's targeted biological/presentation amendments reuse the completed baseline. Kimi's embedding-dispersion and optional 59-sequence expansion remain outside this implementation. Model correctness still requires the separately authorized real-model gate.

## Primary method

For each observed standard residue in an ungapped original sequence, mask that residue only and score `log P(actual residue | the same sequence with that residue masked)`. The model receives original single sequences, not a gapped MSA. The fixed alignment supplies the mapping back to columns. We use the full model vocabulary for log-softmax; no renormalization onto the 20 amino acids. Negative log-probability is called surprisal. Smaller surprisal means higher model compatibility in this context, not protection or biological efficacy.

The primary reported metric is **masked-original-residue NLL**. No entropy, substitution log-odds or embedding dispersion is substituted. The frozen inputs yield exactly **6,305 standard-residue examples**, **415 scoring forwards** at per-sequence batch size 16, and a two-shard split of **208/207 forwards**. Maximum sequence length is 214. The pilot scores eight distinct positions in singleton, batched and repeated-batched passes: 14 pilot forwards, 24 pilot examples, plus one separate warm-up. Production one/two-node warm-ups add one/two calls respectively; they are not part of the 415 scoring calls.

`core.py` imports the existing frozen parser and column-statistics implementation. It asserts exact BOS/residue/EOS offsets, no truncation and one mask per example. Gaps have no sequence position or score; nonstandard observations are excluded from scoring; padding/BOS/EOS never receive scores. Each output row records accession, sequence position, token offset, original alignment column and actual residue. All eligible positions are intended for the main run. Any partial-position sequence summary explicitly calls itself a subset; its pseudo-perplexity is `exp(mean negative log-probability)` only over its listed scored positions.

Examples are batched **within each sequence**, batch size 16. The call count is `sum(ceil(scored_positions_s / 16))`. The backend increments the actual counter at each model forward; masked examples are a separate count. Each worker has one separately counted warm-up call. Pilot calls, warm-up and scoring have separate counters and phase timings.

Model/settings: pinned ESM-2 8M safetensors, float32, eager attention, evaluation/inference mode, no autocast, TF32 disabled, deterministic algorithms enabled, seed 0, two CPU threads. The model's original token-dropout configuration is preserved and recorded. Tokenizer, config, weight hashes and installed library versions accompany each receipt. Runtime import is lazy; offline tests never import torch or Transformers.

## Fixed-alignment sensitivity

Leave-out aggregation reuses the existing per-sequence model scores; it has no model backend and performs zero additional forwards. Coverage is standard observations divided by the **remaining** sequence count. Deleting rows cannot make an originally fully covered column incomplete, and exhaustive small-fixture subsets test this invariant.

Report conservation changes at originally variable columns, coverage changes at originally incomplete columns and newly apparent conservation after removal of minority observations. A gapped column may have a descriptive masked-score average with its explicit score count, but it does not enter full-coverage statistics.

The prepared grouping manifest contains 30 leave-one-accession folds and ten leave-one-**supplied-taxon-ID** groups, retaining all original metadata and its hash. Strain-specific taxonomy labels are not silently merged into species; supplied strain labels are not biological replicate identities. This exact metadata grouping is declared for the final contract's taxonomic sensitivity. No alignment is recomputed, no indices are transferred from a 59-sequence panel, and no permutation experiment is implemented.

Every rank comparison records its exact common eligible columns before ranking. Full-coverage comparisons use columns fully eligible on both sides, with a complete model-score count when comparing scores. Newly complete subset columns are described but do not silently enlarge the ranking population. Ranks ascend; exact numeric ties receive average ranks, without rounding or tolerance-based tie merging. Spearman correlation is descriptive; constant vectors or fewer than two columns return null. There are no p-values or significance claims for dependent columns.

The workload manifest keeps **202 fully covered columns**, **162 mapped observed 1GGQ residues** and the **159-column intersection** as separate explicit sets. Columns 154 and 173 retain their one-of-30 support and alignment-only status. Ingestion adds scores to the saved reference map only in new result files; missing/unmapped coordinates remain unscored. The separate `demo/v0.2.0/` overlay adds verified annotation/assembly context without changing the existing application.

## Tests versus inference

Run `python -B -m unittest -v test_offline` in this directory. Fixtures exercise masking, offsets, numerics, ingestion rejection, coverage, provenance and scheduling contracts. They do **not** validate real-model inference. Fixture ingestion is rejected by default; its explicit unit-test path labels results `FIXTURE_ONLY_NOT_SCIENCE` and cannot unlock the benchmark.

The prepared real-model pilot compares singleton, batch-16 and repeated batch-16 scoring on the same loaded model for eight explicit positions, including sequence boundaries, coordinate-missing positions and both low-coverage columns. It independently cross-checks float32 log-softmax against float64 logsumexp on the same logits, with no hidden forward. All three score comparisons must pass; absolute/relative deviations and allocator memory are recorded. Pilot and benchmark are **NOT RUN**.

Before any production benchmark, accept or revise these declared tolerances in a new plan: `abs(a-b) <= 1e-4 + 1e-5 * max(abs(a), abs(b))` for log probabilities. Task identity and coverage must match exactly. Input/model/source hashes establish provenance; float comparisons use the tolerance, not hash equality. A failed tolerance stops the run; do not silently loosen it after viewing results.

## Prepared execution and ingestion

`plans/workload.json` records exact tasks, pilot positions, per-sequence call counts and deterministic complete-sequence partitions for one/two nodes. One/two-node work uses identical inputs, position sets, batch size, source and runtime. It does not enlarge the model or repeat data. A small workload may be slower on two nodes.

These are independent Fuzzball GPU task shards, each with its own small model instance. The generic multi-node wrapper launches the independent workers; no NCCL/RDMA, tensor parallelism or distributed-model-capacity claim is made. Receipts distinguish attempted forwards, successful forwards and successful masked examples.

`run_worker.py` requires a separately approved scope/source/plan receipt, a pinned local model directory, and the Sunday November 15 **10:30 AM Central** cutoff. Benchmark modes require a passing actual-model pilot from the same plan, source, assets and runtime. Worker time is capped at five minutes; the prepared scheduler timeout supplies the external hard stop. No code here downloads anything or submits cluster jobs.

`ingest.py` rejects missing, extra, duplicate or incorrectly mapped scores, changed models/settings/inputs and incorrect forward counts. Scheduler exports must link container hostname/ID to physical nodes: Spark30 alone versus Spark29 and Spark30. Container names alone do not prove placement; generic templates require an authorized placement check before use. Runtime/source identities, sequence hashes and every scored position are compared across the matched pair.

Worker receipts separate asset verification, loading, model-device transfer, batch transfers and compute; warm-up/pilot/scoring are separate. Required scheduler lifecycle evidence adds queue/startup intervals, job wall, export and elapsed workflow time. Ingestion measures merge/analysis time separately and reports time to analyzed result with its explicit serialization/idle-time exclusions. Sum of overlapping phases or worker times is not elapsed wall time. A single pair is a pilot, not a scaling law.

The `.HOLD.fz` files reuse the existing event image and generic multi-node pattern. They are prepared artifacts, **not submitted or validated against the current scheduler**. Current cached-image availability and installed model libraries on event nodes are unknown; historical CUDA evidence does not establish present inference readiness. No implicit image pull or package install is authorized.

## Delivery and next approval

- Current submission: `submission/ONE_PAGER.md`; earlier versioned drafts remain available.
- Current demo: `submission/DEMO_SCRIPT.md`, 4:30 narration plus 30-second buffer; earlier scripts are retained.
- Next bounded request: `STAGING_REQUEST.md`; **model staging only**, no execution or dependency install.
- The existing CPU viewer remains the fallback. New research stops at 10:30 AM Central; noon submission takes precedence.

API references inspected: [official ESM documentation](https://huggingface.co/docs/transformers/model_doc/esm), [exact model repository](https://huggingface.co/facebook/esm2_t6_8M_UR50D/tree/c731040fcd8d73dceaa04b0a8e6329b345b0f5df). `model_lock.json` records metadata-derived immutable identities; model content has not been fetched.
