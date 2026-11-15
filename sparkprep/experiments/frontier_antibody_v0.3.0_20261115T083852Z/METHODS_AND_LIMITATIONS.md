# Frontier methods and limitations

## Status and conclusion

**COMPLETED:** exact mapping and coordinate-derived antibody contacts for 9BIF/B11 and secondary 7UIJ/B5; fixed exploratory comparisons; independent geometry/statistical audits; literature-only 8C1 interval; offline reproduction. **NOT RUN:** new ESM inference, model downloads, event-node access/jobs, prospective or independent biological validation.

The primary predeclared diagnostic does **not support incremental value for the signed discordance feature** beyond the specified baseline in this dataset. This is not a proof that no useful relationship exists: the dataset is one selected antigen/reference, labels are correlated, controls are limited, and no external validation was performed. Preserve the negative result rather than present a new antigen/epitope predictor.

## Frozen reference

Starting scientific commit: `aafe818a20ea025370cf4b65145a9684e80aaaef`. Reference raw scores are the existing 6,305 ESM-2 singleton-mask original-residue NLL values, SHA256 `b27d926285a8dc338abceba953229089be4f35fcba7c166c1a922be146a6317f`, checkpoint revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`. They were reused, not recomputed. Inputs are exact-byte copies with source-relative paths and hashes in `provenance/reused_inputs.json`. The frozen UniProt-derived Q07337 sequence is validated against its original record, the panel and every construct residue. This does not assert that a moving current UniProt record was refreshed.

The frozen input has 30 sequences, 218 columns, 202 full-coverage columns and 76 fully covered identical columns. Reference 1GGQ has 162 observed mapped residues; 159 columns are both full-coverage and observed. Its independently calculated dimer SASA and distance-contact fields are reused as separate geometry covariates. Frozen v0.1.0/v0.2.1 files, results and manifests are not edited.

## Coordinate sources, chain identities and numbering

Official RCSB mmCIF and core metadata were retrieved for 9BIF and 7UIJ. All URLs, retrieval UTC, bytes, actual SHA256 and HTTP metadata are retained. 9BIF has inner archive revision 1.0 (2024-11-20), X-ray resolution 3.09 Å; 7UIJ revision 1.3 (2024-11-20), resolution 2.701 Å. HTTP last-modified dates are not treated as experimental dates. See EVIDENCE_SOURCES.md.

For 9BIF biological assembly 1, OspC entity 3 is label chains C/D, author chains A/B. Fab entity 1 is label A/E (author H/C), and Fab entity 2 label B/F (author L/D). Source descriptions are preserved verbatim, including the upstream entity-2 description “VH-VL domain of B11 Fab”; its role here is Fab component, not antigen. For 7UIJ, OspC entity 3 is label E/F (author C/D); Fab entities 1/2 are label A/C and B/D. Do not transfer chain names between structures without the PDB namespace.

Both OspC constructs have 164 residues and exactly match the *entire* Q07337 substring at natural precursor positions 38–201. The unique full-construct match, depositor `_struct_ref_seq` range, chain-specific polymer scheme, every observed atom residue name, author numbering and insertion codes agree. Frozen alignment mapping is by counted original ungapped positions, not a guessed numbering offset. For example, 1GGQ has a different construct label numbering convention; its labels are not reused for these complexes.

All selected assembly-1 operations are the deposited identity operation, still explicitly applied and recorded. Biological assemblies contain two antigen and four Fab component chains. No neighboring asymmetric-unit chains, water, ions or other ligands are promoted into antibody-contact partners.

## Observed contacts and missingness

Use model 1, positive occupancy, no H/D and canonical protein residues. If alternates exist, choose one residue-level conformer by summed occupancy (lexical tie break), combine with common atoms, and deduplicate atom names. Actual selected structures have no alternate-location identifiers. Preserve author/label identifiers and insertion codes separately; actual selected antibody insertion-code sets are empty.

Primary cutoff is <=4.5 Å minimum antigen/Fab protein-heavy-atom distance. Repeat the predeclared labels at 4.0/5.0 Å. Raw residue pairs within 5 Å retain the responsible atom names, nearest distance, chain labels, author numbers and insertion codes. An independently computed full Cartesian distance matrix reproduces all 625 observed antigen-residue distance minima and all three cutoff labels with zero difference at saved precision.

Canonical heavy-atom completeness is checked against explicitly listed standard residue atom names (terminal OXT is optional). A strict site requires complete observed canonical atoms in both OspC copies. Missing copies or incomplete residues have a null strict label, even if some observed atoms can be described. An observed union contact is true if any observed copy contacts; a negative union is known only when all copies have observations. All missing-residue sets exactly match depositor unobserved-residue records. `MISSINGNESS_AUDIT.json` also records missing Fab residues and neighboring observed CA distances without reconstructing loops. For example, 9BIF Fab author chain H lacks label residue 34, with observed flanking CA atoms 6.04/8.74 Å from observed antigen heavy atoms; no missing contact is invented. Missing Fab coordinates can limit the observed footprint; a negative label is **absence of an observed distance contact**, not biological non-binding.

The primary endpoint collapses the two OspC copies to one label per alignment site. They are not independent biological replicates. Site union may combine primary and quaternary contributions from different Fabs. Contacts are not automatically functionally necessary epitope residues or determinants of protection. OspC–OspC homodimer contacts are a different field and were never counted as Fab contacts.

## Eligibility and exact counts

Primary gate: 202 full-panel columns → 159 also observed in 1GGQ → 159 with exact complex construct mapping → **152 with both complex antigen copies complete**. The seven lost sites remain excluded/null rather than becoming negatives. Nonexclusive exclusion counts over all 218 columns are also retained; do not add those overlapping counts as if disjoint.

9BIF/B11 has 32 observed union contact positions in the full mapped construct at 4.5 Å; **31** fall in the strict 152-site primary universe. At 4.0/5.0 Å the eligible contact counts are 28/35. Secondary 7UIJ/B5 has 27 observed construct contact positions and **25** in its 152-site eligible universe (21/27 at 4.0/5.0 Å). Its eligible sites are not assumed identical to B11's; each site list is explicit. No unmapped position receives an invented contact label.

The 8C1 paper's HDX-supported Q07337 interval 130–150 is a **literature regional annotation only**. Published K141/H142/T143/D144 identity anchors match the frozen sequence, and each native position is projected individually across alignment gaps. None of these 21 rows receives a direct-contact label. A separate later PDB 9BX7 peptide-complex record exists but was not retrieved/analyzed or pooled into endpoints here.

## Fixed exploratory analysis

`EXPERIMENT_QUESTION.md` was committed at `79b6d77a4c489fd9e0827c23bbccbabacad819a3` before coordinates were retrieved/contact outcomes calculated. Its SHA256 is checked on every analysis run. D is the frozen agreement-percentile minus predictability-percentile statistic from all 202 fully covered columns. It is deterministic in agreement and NLL; it is not an independent information source beyond those components.

Baselines B0/B1/B2 and augmentations B3/B4/B5 follow that declaration. B2 uses modal agreement, canonical Q07337 amino-acid indicators (A omitted), log1p(reference dimer SASA), log1p(reference dimerization SASA loss) and the homodimer-contact flag. B3 adds D; B4 adds panel mean NLL; B5 adds saved Q07337-specific NLL. There are no interactions, hyperparameter searches or outcome-selected cutoffs. Continuous predictors are standardized on training rows only. Amino-acid indicators remain 0/1.

The objective is summed binary negative log-likelihood plus lambda/2 times squared non-intercept coefficients, lambda=1 fixed; intercept unpenalized. Eight contiguous blocks were assigned from the 159 pre-antibody reference sites, with a five-alignment-column training guard around each held block. No random-residue splits or two-copy duplication are used. Every fold's sizes, class balance, scaling and coefficients are published. The global rank feature is a fixed prior descriptor, not an outcome-trained statistic. This is a within-reference held-region diagnostic, not external prediction validation.

In the secondary 7UIJ antibody B5 comparison at 4.0 Å, **regression model B1**, held block 5, returned L-BFGS `ABNORMAL` despite a well-defined convex problem. The initial partial output is preserved. An equivalent deterministic Newton/Hessian solver recovered that fit under the **same objective, penalty, features and split**, with gradient norm 1.50e-13. No scientific choices were retuned. The primary B11 metrics are unchanged. `numerical_solver_note.json` records the recovery. Separately, Newton/IRLS audits of 96 primary-cutoff fold fits agree within 2.83e-6 probability; an explicit pair-count ROC implementation agrees exactly with rank-based AUC.

Primary out-of-fold Brier(B3) minus Brier(B2) is **+0.00538833**, worse with discordance. Raw signed-D AUROC is **0.46201**, absolute-D AUROC **0.49840**. B2/B3 Brier are **0.168634/0.174022**; AUROC **0.620634/0.616369**. A simpler NLL-added comparator B4 has Brier **0.167708**, a small descriptive decrease of 0.000926, not validated new biology. All models, training fits, OOF predictions and endpoint variants are retained rather than selecting the favorable metric. The D-added Brier contrast is worse at all declared cutoffs and in secondary B5 diagnostics.

Intercept-only blocked AUC can be below 0.5 because fold-specific training prevalence is lowest when a held region is contact-rich. That is a property of spatially clustered labels and the split, not an invitation to flip signs. Do not replace the cross-fitted null with a full-data prevalence estimated using held labels. The count/solver audits independently verify this behavior.

## Limits and status boundaries

- One serotype/reference and correlated residues; selected related sequences; no population significance or independent-site confidence interval.
- Antibody-specific, cutoff-, resolution-, copy- and construct-dependent observed geometry. 9BIF copy reliability is a **posthoc quality audit**, not a replacement endpoint: contact Jaccard across four copies ranges about 0.81–0.94 on common complete positions. These copies are not biological replicates.
- Reference geometry comes from a different unliganded experimental construct. Matched CA RMSDs are approximately 0.48–0.53 Å, but loop/side-chain changes and missing Fab regions still matter. Antibody-bound SASA was not used as a predictor, which would largely restate the contact outcome.
- Panel-mean NLL combines different amino acids/contexts while the antibody binds one experimental sequence. Reference-AA indicators do not fully adjust panel composition or nonlinear chemistry. Sparse categories and 31 events constrain the multivariable diagnostic.
- D can encode nonlinear agreement transforms as well as NLL. No claim of a unique causal mechanism or calibrated immunological probability follows from adding it.
- B11 and B5 share antigen/epitope context and are related structural observations, not independent clinical validation sets.
- No novel antigen, mutation optimization, escape design, efficacy or clinical utility claim. A negative incremental diagnostic does not establish that all other models or datasets would fail.
- Publication/submission integration remains the laptop's responsibility. The validated v0.2.1 fallback is unchanged. Event-node benchmarking and external biological validation are NOT RUN.

## Offline reproduction

Use the existing Python environment with NumPy/SciPy/Matplotlib (personal Spark: `/home/darkstar90/ftvenv/bin/python`); system Python lacks NumPy and is not the tested runtime. No installation is implied. Source acquisition is not part of reproduction: archived source files are hash-verified locally.

```bash
PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4 \
  "$PYTHON" src/reproduce.py --destination /new/path/frontier_reproduction
```

Destination must not exist. The script copies archived inputs/source to a new location, never overwrites the reference, executes the CPU-only pipeline and tests, compares exact mapping/contact artifacts and numerical outputs, and records a receipt. No network retrieval, ESM calls or event access occur. Figures are regenerated from real data; renderer metadata/font bytes need not match. All raw model scores remain reused frozen evidence.
