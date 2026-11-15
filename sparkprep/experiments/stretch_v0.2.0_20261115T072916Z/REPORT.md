# Personal-Spark full-panel stretch report — v0.2.1

This release extends the pilot commit 69ceeee72bf705a7ddca1e0a1031e4703e44a64a in the same experiment directory. The original pilot archive and raw results remain preserved. Source baseline is main 8058846c05d4dccd60117dd29ef784af43570418. New results are versioned; frozen v0.1.0 results are unchanged.

## Compute and scientific execution

Personal GPU operational YES; real-model pilot PASS; approved full frozen-panel sweep PASS. Host spark-6771, NVIDIA GB10, driver 580.178.04, CUDA runtime 13.0, PyTorch 2.14.1+cu130, Transformers 5.20.0, float32, eager attention, batch 8, no gradients/TF32. Runtime fingerprint includes the PyTorch source Git revision and compiled architectures.

Exactly 30 natural sequences and 6,305 original-residue scores. Scoring forward passes 805; warmup passes 3 (24 additional masked examples); full-run validation forwards 0; total full-run forwards 808. The separate pilot had 210 scoring masks, 27 scoring passes, 3 warmup and 3 independent validation passes. Do not add pilot duplicate residues to the unique scientific task count.

Actual full-panel model load/GPU transfer 0.313129 s; first forward 0.237833 s; warm scoring 9.909294 s; process wall after imports 10.510127 s. Peak allocated GPU 137,314,816 bytes; reserved GPU 247,463,936 bytes; RSS 1,650,778,112 bytes. All 210 Q07337 values exactly repeat the earlier pilot. The warm-scoring time includes local validation/serialization preparation overhead as implemented; per-sequence synchronized forward/log-softmax time is separately recorded. Process-cold is not guaranteed disk-cold. Existing services were not stopped. These are personal-Spark measurements, not a matched event benchmark.

Raw full-panel scores: `results/full_panel_v1/residue_nll.tsv`, SHA256 `b27d926285a8dc338abceba953229089be4f35fcba7c166c1a922be146a6317f`. All values are finite/nonnegative. Independent audit verifies all masks, original sequence hashes, exact position/alignment mapping, 218 mean-NLL aggregates, 30 pseudo-perplexities and forward counts. All 16 unit tests pass. CPU routing/merge rehearsal verifies disjoint 3,156/3,149-mask shards and exact merged values, rejecting missing/duplicate shards; it performs no new inference or event access.

## Scientific results and limits

Read SCIENCE_FINDINGS.md for the detailed interpretation, examples and calculated-geometry assumptions. Across 202 fully covered columns, agreement versus negative mean NLL has descriptive Spearman rho 0.134696. Columns 177/58 are identical in all 30 sequences yet have mean NLL 4.01135/3.96498 nats; columns 129/137 have modal fractions 0.400/0.333 and mean NLL 1.54783/1.83479. These four discordance directions persist in all 239 real-panel perturbations. At column 134, 27/30 residues are C, but mean original-residue NLL is 7.28507. None of these observations identifies antigenicity, protective immunity, biological selection or a mutation effect. The per-sequence masked pseudo-perplexity range is 11.10218–13.15385.

Biological-dimer contacts are separate: 1GGQ assembly1/2 have 118/117 heavy-atom residue pairs at 4.5 A; 1G5Z assembly1 has 120 after proper symmetry transformation. Whole-construct sequence identity maps 1G5Z to Q44717. New CPU-only sampled SASA estimates 1GGQ total area loss 4,081.16 A², mean partner interface area 2,040.58 A², with 0.295% total-loss change between 960 and 1,920 points/atom. Analytic sphere checks pass. These are geometric calculations on static incomplete constructs, not measurements of physiological accessibility. Contact, computed SASA and model score remain distinct. No relative accessibility classification or antigen rank is created.

The v1 aggregate's missing-structure contact labels were corrected from False to null in `full_panel_comparison_v2/`; the earlier aggregate is explicitly superseded and retained. Raw NLL and numerical aggregates are unchanged. Unknown/unobserved structure context is never classified as no contact or zero area in the current adapter. `provenance/analysis_corrections.json` records this correction.

## Model integrity

Only the approved six files were downloaded: 31,387,085 bytes, below 32,000,000. Model revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`. No installations, alternative checkpoints, driver changes, larger models, embeddings or synthetic mutation library. All files were verified against upstream available identifiers, and all actual SHA256 values were recorded. Weights remain outside tracked paths.

| File | Bytes | Actual SHA256 |
|---|---:|---|
| README.md | 1705 | `462a2f24724e19c6be0efab926315c294a863c9a9770e2c8b3d859b2d81a07de` |
| config.json | 775 | `facb9355e8252149f6f99dff5fd1e32e890c3c655362b261d0c81cd6b5839c85` |
| model.safetensors | 31384292 | `24c5fa474c48f3b754b86efe752d5f189d2bcd88190fa2270fc92b2ef3034189` |
| special_tokens_map.json | 125 | `3aedcd4211c0d43aec4e607ff60a63255f3174ead795e997350f09a5f8cd9ee1` |
| tokenizer_config.json | 95 | `7e9161ecdb548ec45a41cbc6b24aa4476fdd418461f491c4207baa99419a29ad` |
| vocab.txt | 93 | `0b82cc0a7c7cf9e567b1e5892d793285b9fbae822c964ca48696f7db44598e03` |

A verified local six-file transfer tar was prepared separately from Git; its receipt is in `provenance/model_transfer_bundle_receipt.json`. This adds zero network downloads. No event transfer or access occurred.

## Publication and laptop handoff

Only `feat/ospc-esm2-spark-pilot` is used for publication; the laptop owns main integration. The complete inventory and hashes are FILE_MANIFEST.json / SHA256SUMS, excluding their own hashes. The prior pilot package is preserved separately; a new full-panel scientific package is produced without model weights. Current paths are detailed in LAPTOP_HANDOFF.md and VENUE_CONTRACT.md.

Consume `results/laptop_evidence_v1.json` for typed fields or the underlying versioned TSV files. The adapter contains all 218 columns, 30 sequences, per-column residue counts, sensitivity and conditional NLL, 324 existing experimental dimer CA coordinates, and separate contact/calculated-area annotations. PNG/SVG scientific figures are available for the laptop's demo; no competing UI or laptop files were edited.

The single most consequential remaining requirement is authorized execution on the actual event Spark29/Spark30 nodes with verified staged cache/runtime. The portable one-then-two-node workload is fully specified; actual event timing, scaling and numerical agreement are still NOT RUN. No further personal-Spark model expansion is required to carry this experiment to the venue.
