Historical pilot checkpoint; superseded for current state by REPORT.md.

# Personal-Spark experiment report — pilot checkpoint

## Verified state

Host spark-6771 / darkstar90. Model download PASS: exactly six pinned files, 31,387,085 bytes, no matching local files found in the inspected project/model caches. Revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`. Model loads YES. Personal GPU usable YES, deterministic CUDA probe exact numerical agreement. Real-model Q07337 correctness pilot PASS. No full 30-sequence model sweep has been run, and no event cluster has been accessed.

| File | Bytes | Actual SHA256 |
|---|---:|---|
| README.md | 1705 | `462a2f24724e19c6be0efab926315c294a863c9a9770e2c8b3d859b2d81a07de` |
| config.json | 775 | `facb9355e8252149f6f99dff5fd1e32e890c3c655362b261d0c81cd6b5839c85` |
| model.safetensors | 31384292 | `24c5fa474c48f3b754b86efe752d5f189d2bcd88190fa2270fc92b2ef3034189` |
| special_tokens_map.json | 125 | `3aedcd4211c0d43aec4e607ff60a63255f3174ead795e997350f09a5f8cd9ee1` |
| tokenizer_config.json | 95 | `7e9161ecdb548ec45a41cbc6b24aa4476fdd418461f491c4207baa99419a29ad` |
| vocab.txt | 93 | `0b82cc0a7c7cf9e567b1e5892d793285b9fbae822c964ca48696f7db44598e03` |

## Real measured pilot

Q07337 original sequence SHA256: `8939ee76df09336cca51badd169a15d142bcd48b90b928cfcebc1ef733ac1d7e`. Scored positions are all full-length natural residues 1..210, including precursor context. Exactly 210 scored masks / 27 scoring forward passes. Three warmup passes used 24 additional masked examples; three independent batch-one validations used three additional masked examples. Total forwards 33, total processed masked examples 237; scientific result rows 210.

Model parameters: 7,512,474. Float32, eager attention, eval/inference_mode, TF32 disabled, batch 8. Model load/GPU transfer 0.338836 s; first forward 0.299191 s; two subsequent warm forwards 0.012495 / 0.011979 s. Warm scoring wall 0.384158 s; synchronized forward+log-softmax sum 0.342025 s. Process wall after imports through correctness/score export 1.104543 s. Not shell startup-to-exit or a disk-cold measurement.

Peak allocated GPU 135,659,520 bytes; peak reserved GPU 182,452,224 bytes; max process RSS 1,716,289,536 bytes. Other GPU services were left running. Personal timings are not a matched event-cluster benchmark.

Mean masked-original-residue NLL 2.519368982 nats; masked pseudo-perplexity 12.420756469. All scores finite/nonnegative; tokenizer exactly preserves original residues with CLS/EOS untouched and exactly one mask per example. Independent batch-one checks at residues 1/105/210 differ by at most 9.53674316406e-07 nats. Score file SHA256: `c55a8edff430b36c29a6e56068a85ec53ab29f3c79d8e51f09d9e5161f527dda`. These values are a one-sequence correctness pilot, not a panel result or biological validation.

## Independent completed CPU science

All 30 leave-one-out panels, 200 deterministic half-panels of 15 real sequences, and nine metadata-organism-group omissions preserve the fixed alignment. Of 202 fully covered columns, 96 have modal-fraction range at least 0.20 across the 200 half-panels; the maximum leave-one-out range over fully covered columns is 1/29 (0.034483). Across all 218 columns the half-panel count is 106; four sparse columns are undefined in at least one half-panel. Sensitivity ranges are not confidence intervals, and this convenience panel is not population-representative.

Deposited biological dimers: 1GGQ assemblies 1/2 have 118/117 interchain residue pairs at minimum heavy-atom distance <=4.5 A, with 51 contacting residues on each partner. 1G5Z assembly 1 has 120 pairs and 51 residues per partner after applying the deposited symmetry operator. Cutoff sensitivity at 4/5 A is included. 1GGQ maps exactly to Q07337; the entire 1G5Z construct matches Q44717 exactly before alignment mapping, rather than trusting the historical O31117 accession alone. Missing residues remain missing. Contact is not SASA, surface exposure, antigenicity or protection.

The full residue/alignment bijection contains 6,305 tasks. Deterministic two-node assignments contain 3,156 and 3,149 masks, requiring 403 and 402 scoring passes at batch 8 (805 on one node). No synthetic sequences or mutations, new sequence collection or realignment were performed.

## Branch and handoff

Dedicated branch: `feat/ospc-esm2-spark-pilot`, created only after checking the existing remote refs and confirming this name was absent. Base main: `8058846c05d4dccd60117dd29ef784af43570418`. Laptop retains integration ownership. Only this new versioned experiment subtree is proposed for publication; main and the laptop's files are unchanged. New tracked paths are enumerated by FILE_MANIFEST.json. No model weights, compiled caches, unrelated models, credentials or transcripts are included.

Laptop: review this feature branch's `sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/` subtree. Consume `results/residue_alignment_mapping.tsv`, `results/panel_sensitivity.tsv`, `results/dimer_alignment_mapping.tsv`, and the optional scientific figure. `results/pilot_v1/residue_nll.tsv` is only Q07337; never display it as complete-panel data. Use VENUE_CONTRACT.md, the pinned receipt, runtime spec and shard manifest for the exact one-then-two-node workload. Model cache requires separate authorized transfer and six-file hash verification.

## Next bounded approval

The single consequential blocker to a panel-wide predictability/agreement result is approval of the full sweep after this measured pilot review. Proposed next run: all 6,305 singleton masks on this same GB10, batch 8, no downloads, maximum 120 seconds external timeout, GPU allocated cap 2 GiB / reserved cap 4 GiB, process RSS cap 16 GiB and >=8 GiB free GPU-visible memory after load. Linear pilot estimate is about 12 seconds warm scoring; actual full-panel resource use is not yet measured. Further model-size expansion is not proposed. Venue access remains separately unauthorized.
