# Optional scientific frontier handoff — SPARK

**COMPLETED:** two exact experimental-complex mappings and a predeclared controlled comparison with a negative primary result. This is an optional extension. The laptop should keep integrating the known-good v0.2.1 commit `aafe818a20ea025370cf4b65145a9684e80aaaef` without waiting for this directory.

The Spark only writes `feat/ospc-esm2-spark-pilot`. The final sprint report supplies the exact completed publication commit; pin that SHA when consuming new files rather than assuming a moving branch tip. Predeclaration was committed separately at `79b6d77a4c489fd9e0827c23bbccbabacad819a3` before contact outcomes were calculated. The frozen v0.1.0/v0.2.1 data/manifests and the laptop's README/demo/submission files were not edited.

## What you may now show as verified

- **B11/9BIF:** official existing experimental coordinates, biological assembly 1, exactly validated OspC-to-frozen-Q07337 mapping. OspC label C/D are author A/B; Fab label A/B/E/F are author H/L/C/D. The 164-residue construct matches native Q07337 positions 38–201 in full. There are 32 observed union-contact positions at 4.5 Å, of which 31 are in the strict 152-site full-coverage/reference-observed/complete-complex analysis universe.
- **B5/7UIJ:** separately validated secondary experimental complex. OspC label E/F are author C/D. It has 27 observed construct-contact positions, 25 in its own 152-site eligible universe. These are related biological/structural observations, not independent clinical validation.
- **8C1:** source-verified HDX regional annotation at Q07337 130–150, projected individually across alignment gaps after identity-anchor checks. It is **not an atom-contact footprint**. Leave its contact field null. A later official 9BX7 peptide-complex deposition exists but is NOT RUN here; do not invent or infer its contacts from the 2025 paper's broader interval.

## The result that must stay visible

The proposed discordance feature does **not improve** the predeclared B11 blocked diagnostic beyond agreement + reference amino-acid identity + unbound-reference geometry:

| Primary 9BIF, 4.5 Å | Brier error, lower is better | AUROC |
|---|---:|---:|
| B2: agreement + AA + geometry | 0.168634 | 0.620634 |
| B3: B2 + signed discordance | 0.174022 | 0.616369 |
| B4: B2 + panel-mean NLL | 0.167708 | 0.648094 |

Primary added-discordance Brier change is **+0.00538833**, worse. Raw absolute discordance has AUROC **0.49840**. The negative incremental direction persists across the stated distance sensitivities and related B5 comparison. The small NLL-added difference is exploratory, not a validated biological advance. Do not turn this into “the AI detected an antibody epitope” or a target ranking. The meaningful advance is exact experimental-evidence mapping plus an inspectable, falsifiable test that preserved its negative result.

## Current files to consume

All paths below are relative to this new experiment directory.

| File | Meaning |
|---|---|
| `results/FRONTIER_EVIDENCE.json` | Typed optional adapter: 436 site rows (218 per complex), real assembly-1 CA coordinates (1,170 for 9BIF; 1,160 for 7UIJ), evidence levels, nullable contact states and display rules |
| `EXPERIMENTAL_MAPPING.tsv` | Exact unique-site projection, missingness/exclusion reasons, copy counts, all cutoff labels and reused features |
| `results/9BIF_RESIDUE_MAPPING.tsv`, `7UIJ_RESIDUE_MAPPING.tsv` | Every construct residue/copy with label/auth numbering, insertion code, observed atoms and completeness |
| `results/*_FAB_CONTACT_PAIRS_5A.tsv` | Responsible atom names and distances for observed residue-pair contacts; filter to the fixed 4.5 Å primary cutoff if needed |
| `ANALYSIS_RESULTS.json` | Complete predeclared primary/control/sensitivity results, full fits, OOF metrics, exclusions and limitations |
| `results/COMPARISON_METRICS.tsv`, `BLOCKED_OOF_PREDICTIONS.tsv` | Simple model metric table and all held-region predictions |
| `results/FRONTIER_EXPERIMENT.png` / `.svg` | Original scientific figure from real experimental coordinates; illustrates the negative controlled result |
| `results/8C1_LITERATURE_REGION.tsv` | Regional annotation only, with no direct-contact labels |
| `results/INDEPENDENT_GEOMETRY_AUDIT.json`, `INDEPENDENT_STATISTICS_AUDIT.json`, `MISSINGNESS_AUDIT.json` | Independent calculations and missing-coordinate limitations |
| `EXPERIMENT_QUESTION.md`, `METHODS_AND_LIMITATIONS.md`, `EVIDENCE_SOURCES.md` | Predeclaration, exact method and source-verified provenance |

The source 9BIF/7UIJ coordinate files and entity metadata are archived under inputs/ with byte hashes. Reused model data are copied exactly with source commit/hash provenance; no new ESM inference occurred. FILE_MANIFEST.json / SHA256SUMS describe the final package without self-recursive hashes.

## Integration rules

1. Keep antibody contacts, homodimer contacts and calculated SASA as separately named fields. They are different measurements/derivations.
2. Namespace every coordinate by PDB, assembly and instance. Never join two structures on a chain letter alone. Frozen alignment column, native Q07337 position, label_seq_id and author number are distinct fields.
3. `null` is unknown/excluded. False means no observed atom contact under the defined coordinate endpoint, not biological non-binding. The observed footprint and strict comparison eligibility are separate properties.
4. Draw a trace only between consecutive label positions in the same instance. Missing antigen/Fab loops remain gaps. 9BIF Fab heavy-chain label 34 is missing near the interface; do not fill it with a fabricated contact.
5. Gray/teal/magenta figure colors refer to Fab, OspC and atom-derived contact sites. Existing experimental structures are not AlphaFold/ESMFold predictions.
6. The source figure and typed adapter may enrich Story 4. Laptop owns its UI/README/submission and may choose a static evidence card if integration would risk the fallback. Do not hold the complete submission for this optional work.

## Exact Sunday readiness

The existing v0.2.1 one-then-two-GB10 deployment contract is unchanged: pinned six-file ESM-2 8M cache; full frozen 6,305 masks, not just these 152 sites; one-node 805 scoring passes; two-node 3,156/3,149 masks. Keep queue/process startup, load, warm scoring, merge and end-to-end scopes separate. Actual event access/execution and speedup are **NOT RUN**. The local model transfer bundle and original package remain available; this new CPU-only evidence does not require a larger model, new weights or a venue job.

After the lead returns, the highest-value integration action is to review/pin this optional frontier commit and add the verified B11 footprint plus the negative test to the evidence story, while preserving the known-good submission. Morning venue authorization/runtime/cache verification precedes all actual event jobs. No automated external submission was performed by the Spark.
