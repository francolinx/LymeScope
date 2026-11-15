# Laptop integration handoff — full-panel result

Review the latest verified head of `feat/ospc-esm2-spark-pilot` in the existing francolinx/LymeScope repository. The Spark only writes this feature branch; the laptop owns merge/integration into main. The initial pilot is preserved at 69ceeee72bf705a7ddca1e0a1031e4703e44a64a and in its original local archive. All new work stays under `sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/`. The experiment directory ID is stable; the completed release is v0.2.1.

## Use these current files

| Purpose | Path within experiment |
|---|---|
| Typed adapter for the laptop's existing demo | `results/laptop_evidence_v1.json` |
| Exact 6,305 raw original-residue model scores | `results/full_panel_v1/residue_nll.tsv` |
| Actual full-panel timings, counts and memory | `results/full_panel_v1/timings.json` |
| Current 218-column means and context | `results/full_panel_comparison_v2/column_comparison.tsv` |
| 30 sequence pseudo-perplexities and SHA256 | `results/full_panel_comparison_v2/sequence_summary.tsv` |
| All 6,305 residue/alignment task mappings | `results/residue_alignment_mapping.tsv` |
| Frozen-input IDs, sizes and hashes | `provenance/frozen_inputs.json`, `results/shard_manifest.json` |
| 239 real-panel sensitivity designs and results | `results/panel_designs.json`, `results/joint_panel_sensitivity.tsv` |
| Dimer contact pairs and exact alignment mapping | `results/dimer_contacts.tsv`, `results/dimer_alignment_mapping.tsv` |
| Separate calculated SASA (not experimental exposure) | `results/sasa_dimer_context.tsv`, `results/sasa_context_summary.json` |
| Numerical/coverage audit and offline routing proof | `results/full_panel_validation.json`, `results/shard_merge_rehearsal.json` |
| Readable interpretation and exact venue workload | `SCIENCE_FINDINGS.md`, `VENUE_CONTRACT.md` |
| Scientific figures, ready to use or export | `results/full_panel_agreement_predictability.{png,svg}`, `results/experimental_dimer_comparison.{png,svg}`, `results/calculated_sasa_dimer_context.{png,svg}` |

The typed adapter is a new explicit adapter schema, not an assumed drop-in replacement for an existing laptop bundle contract. It contains 218 columns and 30 sequence summaries, original residue counts, model/provenance identity, 324 existing experimental 1GGQ CA coordinates, per-column conditional NLL, agreement, real-panel sensitivity, contact and separately calculated SASA. The raw 6,305 scores remain in TSV. Render the laptop's current UI against these fields; no Spark UI competes with it.

## Field semantics that must survive integration

- `alignment_column` and `sequence_position` are 1-based; they are not interchangeable. Never use a token index as a PDB author residue number.
- The model score is **masked original-residue NLL**, lower is more predictable. A column averages the observed natural residues. It is not an epitope, mutation-effect, protection or surface-exposure score.
- `sequence_sha256` hashes the ungapped original amino-acid string, not the entire FASTA file.
- Only the 202 fully covered columns receive the rank-discordance statistic; incomplete columns retain coverage and NLL but have null rank-discordance.
- `reference_1GGQ_A_contact_4_5_A = null` means unknown/unobserved/unmapped, `false` means an observed reference residue without the defined partner contact, and `true` means observed contact. Never coerce null into false.
- Calculated SASA fields have square-Å units and remain null for missing structure. A calculated value of zero is a different state. Use the recorded radii, probe and sphere resolution. Do not label these static-construct calculations as experimental or physiological accessibility.
- Dimer coordinates are existing experimental PDB 1GGQ assembly1, not a new AI-predicted fold. Connect CA traces only for consecutive label_seq_id in the same chain. Model colors are panel-column annotations, not a new structure prediction or B-factor confidence.
- Current aggregate is **v2**. `full_panel_comparison_v1` is retained but superseded for its unknown-contact labeling; raw NLL is unchanged. REPORT_PILOT.md / VENUE_CONTRACT_PILOT.md and the early CPU figure are historical checkpoints.

## Accurate demonstration narrative

1. We start from 30 selected natural OspC sequences and a frozen 218-column alignment. We actually ran 6,305 independent singleton-mask model examples, scored the original residues, and verified the exact mapping.
2. Agreement and small-model conditional predictability differ. Illustrate columns 177/58 versus 129/137, show the actual residue counts and NLL, and show sensitivity over real subpanels. The directions persist in all 239 perturbations, within this selected panel and fixed alignment. This is not proof of mechanism or a vaccine screen.
3. Project the summaries onto an existing experimental dimer. Keep distance contacts and separately calculated area loss distinct; show missing regions explicitly. Use the exact same model/scoring/task contract on one venue node and then two genuinely concurrent venue nodes. Present actual event timing only after authorized execution and validation.

## Venue transfer and run readiness

The scientific archive contains no weights or dependencies. All six approved model files are already present on the personal Spark and verified. A separate local model-only tar is at `/home/darkstar90/lymescope-sparkprep/.model-cache/transfer/esm2_t6_8M_UR50D_c731040fcd8d73dceaa04b0a8e6329b345b0f5df_six_files.tar`, SHA256 `4e24f435628bb2c3b1a1a27664807c5d8c41ce7a94d3c2031b0f96363cb5d9ab`, 31,395,840 bytes. It is NOT in Git and no venue transfer has occurred. Do not substitute another checkpoint or download the repository wholesale.

After explicit event access/transfer authorization: stage the scientific package and the separately verified six-file cache on both nodes; verify package/model hashes; inspect runtime and execute the core deterministic GPU probe; validate the venue pilot against the published personal pilot/full reference; then run the one-node 6,305-mask task set and the two concurrent 3,156/3,149-mask shards with identical model/precision/batch size. Follow VENUE_CONTRACT.md for commands, timing scopes and tolerance. The CPU routing rehearsal validates routing/merge only, not inference or two-node speedup. Dependencies must already exist or require a separate bounded approval; no installation or repair is implied.

Use a new extraction/copy for any CPU reconstruction so that original artifact bytes remain preserved. CPU SASA reproduction uses existing numpy/scipy; figure regeneration additionally uses matplotlib. Those libraries are not required for simply consuming the supplied TSV/JSON/PNG/SVG outputs.

The remaining blocker is access and measured execution on the real event nodes, not personal-Spark GPU availability or model loading. No event jobs, larger model, extra model downloads, or infrastructure changes were performed.
