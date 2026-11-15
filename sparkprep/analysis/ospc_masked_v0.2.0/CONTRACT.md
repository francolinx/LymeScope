# Locked method — Claude final reference and accepted corrections

Source: the project lead's final Claude contract supplied in this session, November 15, 2026. This reconciles the implementation already underway; it does not replace the frozen baseline or authorize execution.

Primary question: compare empirical agreement with the probability of the **original** residue under ESM-2 when only that position is masked. Primary metric: `nll[s,i] = -log P(original residue | sequence masked at i)`, full model vocabulary normalization. No entropy, embedding dispersion, substitution log-odds or permutation experiment.

| Analysis set | Fixed columns |
|---|---|
| F: coverage 1.0 | 202; primary comparison |
| M: observed 1GGQ coordinate mapping | 162; structural descriptive view |
| MF: intersection | 159 |
| M minus F | 75, 86, 119 |
| Sparse reference gaps | 154, 173; 1/30 each, alignment-only |

All residues retain accession, ungapped position, token offset and fixed alignment column. Only standard observed residues are scored; gaps and special tokens are excluded. Sequence hashes identify exact ungapped ASCII strings; original FASTA, mapping, alignment and manifest files are hashed separately. Per-residue scores, per-sequence pseudo-perplexity over explicitly listed positions, and column means are separate levels. Counts/coverage remain visible for partial columns; rank comparisons list common eligible columns and exact-tie average ranks.

Per-sequence batch size 16 gives 6,305 examples and 415 scoring calls; actual calls, successful examples and failed/successful position inventories are recorded separately. Float32, eval/inference mode, deterministic algorithms, eager attention and TF32/autocast off are locked before execution. Runtime versions, config/tokenizer/checkpoint identities, maximum input length, GPU identity, timings and allocator memory are recorded.

**Gate A:** offline labeled fixtures test indexing, gaps, mapping, aggregation, coverage invariants, shards, failures and schemas. Fixture results never establish actual inference or unlock production.

**Gate B, prepared only:** eight actual input positions run as singleton, batch-16, then a repeated batch-16 pass on the same loaded model: 14 pilot forwards, 24 pilot examples, plus one separately counted warm-up. This tests repeatability within a process, not independent launches. Token offsets, finite scores, float32 log-softmax versus independent float64 logsumexp and all three pairwise score comparisons must pass. Record memory/runtime and maximum absolute/relative deviations. Tolerance: `abs(a-b) <= 1e-4 + 1e-5*max(abs(a),abs(b))`, fixed before results. No tolerance widening.

Fixed-alignment sensitivity includes leave-one-accession and exact supplied taxon-ID groups, preserving missing/ambiguous strain provenance. Coverage denominator is the remaining subset size. Report originally variable-column agreement changes, originally incomplete-column coverage changes, and newly apparent identity after removing minority observations. Reuse per-sequence scores. Full coverage and identity cannot be lost merely by row deletion; those mathematical invariants are not biological robustness evidence. No significance claims for dependent columns.

The prepared matched benchmark requires **Spark30 alone**, then **Spark29 and Spark30**, attributed through scheduler evidence. Independent sequence shards have 208/207 calls, with identical biological inputs, checkpoint and precision. No NCCL/RDMA or distributed-model-capacity claim. Record queue/startup, loading, warm inference, transfers, output export, merge and total time to result; exact task coverage and numerical equivalence precede any timing claim. A single pair is a pilot, including negative scaling.

Permitted interpretation: within-panel agreement, checkpoint-specific predictability, divergence worthy of follow-up under a stated hypothesis. Not demonstrated: universal conservation, antigenicity, protective immunity, accessibility, safety, cross-reactivity, immune escape, clinical recommendations or new biological function.

No model download, GPU run, cluster submission, driver/environment change or main push is authorized by this contract. The prepared worker enforces the November 15, 10:30 AM Central cutoff. The completed CPU viewer and noon submission are independent of GPU success.
