# LYMESCOPE
**Making the invisible biology of Lyme disease explorable.**

**Research question.** When should researchers trust a biological AI output, and what evidence can challenge it? Within a selected panel of 30 natural OspC sequences, LymeScope compares empirical sequence agreement with a protein language model's ability to predict each masked original residue, then maps observations to deposited experimental coordinates.

**Built for protein researchers.** The offline evidence workbench joins a frozen CPU alignment, ESM-2 scores, explicit sequence-to-structure mapping, original figures and antibody-contact evidence. It keeps sequence agreement, model predictability, contact geometry and calculated solvent-accessible surface area separate. A correctly calculated 100% agreement value can have 30/30 or only 1/30 observations.

**Completed biology.** The alignment contains 218 columns: 202 fully covered, 162 mapped to observed 1GGQ residues, and 159 in their intersection. Columns 154 and 173 each have 1/30 coverage and no reference coordinates. The personal-Spark experiment measured all 6,305 original-residue NLL values with the pinned Meta FAIR ESM-2 8M checkpoint. Agreement versus predictability has descriptive Spearman rho 0.134696 over the 202 fully covered columns; this is not a causal or protective-immunity result.

**A useful negative result.** Experimental mappings identify 31/152 eligible B11/9BIF contacts and 25/152 B5/7UIJ contacts within their respective analysis sets. Adding signed discordance to the controlled B11 diagnostic worsened blocked Brier error from 0.168634 to 0.174022. No incremental predictive value was demonstrated. Existing scores were reused; no new antibody model was trained.

**Verified event execution.** CIQ Fuzzball ran the same natural tasks on physical Spark29 and Spark30 NVIDIA GB10s. The one-node run and the merged two-node shards covered all 6,305 tasks exactly once, with zero absolute and relative deviation in saved scores. Both pilots passed. The concurrent scoring intervals overlapped for 16.233 seconds. Twenty-five exported artifacts passed laptop size/SHA256 readback. Scientific inputs/results used the staff-confirmed VAST-backed Team 15 volume; model weights stayed in separate private ephemeral storage.

| Measured scope | Single node | Original two-node | Exploratory two-node |
|---|---:|---:|---:|
| Warm scoring; two-node value is the slower shard | 30.224 s | 42.397 s | 22.871 s |
| Prepared-input coordinator phase | 52.111 s | 67.982 s | 51.952 s |

**Preserved baseline and one post-hoc experiment.** The original equal-count two-node run took 30.5% longer than one node. A later deterministic whole-sequence reassignment used 1,691 masks/216 forwards on Spark29 and 4,614 masks/589 forwards on Spark30. All 6,305 original tasks appeared exactly once; absolute and relative saved-score deviations remained zero. The new coordinator phase was **23.6% shorter than the original two-node phase**, but its 0.3% difference from the single-node phase is **near parity, not established acceleration**. Both GPUs scored concurrently for 22.707 seconds. Eighteen exported artifacts passed laptop hash readback.

These are prepared-input phases excluding common runtime/model setup and final object export. Whole-workflow speedup was not measured. The exploratory trial was selected after observing the original slowdown, with no repeated timing uncertainty estimate; it also added a roughly 1 Hz diagnostic sampler. Host-clock scoring overlap lacks independent clock calibration. The historical root cause of the node performance asymmetry remains unresolved. This is evidence about this small workload, not a general scaling result or a novel scheduler.

**Method and limits.** Pinned ESM-2 8M; singleton original-residue masking; batch 8; float32/eager; TF32 disabled; no autocast. Three warm-up forwards per process are separate. Fixed tolerance: `abs(candidate-reference) <= 1e-4 + 1e-5*abs(reference)`. Selected sequences, correlated sites, missing coordinates and one timing comparison limit inference. No diagnosis, protective-antigen discovery, vaccine safety or clinical recommendation is claimed. Experimental structures are existing evidence, not AI-generated folds.

**Reproducibility and attribution.** Meta FAIR/Meta AI ESM-2; UniProt sequence accessions; MAFFT alignment; RCSB PDB experimental structures. Frozen scientific source: [aafe818a](https://github.com/francolinx/LymeScope/tree/aafe818a20ea025370cf4b65145a9684e80aaaef/sparkprep/experiments/stretch_v0.2.0_20261115T072916Z). Negative diagnostic: [82fb8b5](https://github.com/francolinx/LymeScope/tree/82fb8b53018ba4012ccebf02a29efa87b892f6ed/sparkprep/experiments/frontier_antibody_v0.3.0_20261115T083852Z). Event workflow: `79319e56-f368-4eba-8cae-7c646737b9fc`. Exploratory workflow: `3f511bf2-b3b7-4346-b5d8-9a56cef5fc53`. The original result is preserved and reported alongside the single post-hoc trial.

**Public repository:** https://github.com/francolinx/LymeScope

November 15, 2026 | Scientific AI Hackathon, Chicago | Offline demonstration available; no GitHub Pages dependency.
