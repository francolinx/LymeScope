# What this experiment actually found

This is a descriptive, reproducible comparison of two different quantities on the same fixed natural OspC panel, with experimental-structure context. It is not an epitope or vaccine-candidate screen.

## Direct result

Thirty natural sequences, exactly 6,305 original-residue singleton masks, all 218 frozen alignment columns. Original identifiers and sequence SHA256 are preserved. Every scored ungapped residue maps exactly to a frozen alignment column. All 202 fully covered columns are eligible for the ranked agreement/predictability comparison; incomplete columns remain visible with their coverage but are not ranked against the complete columns.

Empirical modal agreement and model predictability have a weak descriptive Spearman correlation of **0.134696** across the 202 complete columns. This is not a significance test: neighboring columns are dependent, sequences are related, and the panel was selected rather than randomly sampled. The 200 deterministic half-panels give correlation range 0.061684–0.175435; these overlapping perturbations are sensitivity checks, not a confidence interval.

Some illustrative differences are below. NLL is in natural-log units; lower means more predictable to this particular ESM-2 8M checkpoint. The table uses alignment columns; Q07337 native residue positions differ after gaps.

| Alignment column | Empirical residues | Modal agreement | Mean masked NLL | Q07337 reference | 1GGQ contact <=4.5 Å | Calculated SASA loss on dimerization |
|---:|---|---:|---:|---|---|---:|
| 177 | G:30 | 1.000 | 4.01135 | G169 | No, observed | 0.00 Å² |
| 58 | L:30 | 1.000 | 3.96498 | L57 | Yes, observed | 79.11 Å² |
| 134 | C:27, A:2, W:1 | 0.900 | 7.28507 | C130 | No, observed | 0.00 Å² |
| 129 | E:12, A:9, K:5, D:3, T:1 | 0.400 | 1.54783 | D125 | No, observed | 0.00 Å² |
| 137 | A:10, E:9, K:7, D:3, T:1 | 0.333 | 1.83479 | T133 | No, observed | 0.00 Å² |

Columns 177/58 (agreement above model-predictability rank) and 129/137 (model-predictability rank above agreement) maintain the same discordance direction in all 30 leave-one-out panels, all 200 half-panels and all nine organism-group omissions. This stability is within the chosen alignment and available panel, not proof of a general biological mechanism.

Amino-acid type and position matter. At column 134 the dominant residue is cysteine; one selected sequence contains the panel's only tryptophan. Original-residue-type score summaries are supplied, but their sample sizes and contexts are unequal. Do not turn a high NLL into a claim of positive selection, pathogenicity, unusual immunogenicity, model error, or a mutation effect. No substitutions were scored.

## Experimental-coordinate context, kept separate

The 1GGQ biological assembly 1 heavy-atom contact definition gives 118 interchain residue pairs and 51 contacting residues per partner at 4.5 Å. The second deposited dimer copy has 117 pairs. The symmetry-generated 1G5Z dimer has 120 pairs, with its full deposited construct sequence matched exactly to Q44717. Historical accession/strain metadata alone was not used to assign that mapping.

A separate CPU calculation estimates probe-center solvent-accessible surface area using element radii, a 1.40 Å probe and Fibonacci sphere sampling. For 1GGQ at 1,920 points/atom:

- Separated-monomer SASA sum: **18,609.80 Å²**.
- Biological-dimer SASA: **14,528.64 Å²**.
- Total SASA lost: **4,081.16 Å²**; mean partner interface area: **2,040.58 Å²** (half of the total loss, a different convention).
- Total loss changes by **0.295%** between 960 and 1,920 points; the largest per-residue loss difference is **1.272 Å²**.
- Isolated/disjoint sphere checks agree analytically; two overlapping equal spheres differ from their analytic value by at most **0.0138 Å²** at the test resolution.

1G5Z gives total calculated loss 4,106.90 Å² at 960 points/atom; only one sampling resolution was run for that alternative. These are computed areas on incomplete, static crystal constructs, not experimental measurements of physiological exposure. Lipid anchoring, membranes, missing residues/atoms, conformational motion and ligands are not modeled. Absolute per-residue SASA is supplied without a relative-accessibility normalization or an exposed/buried classification threshold. Contact distance and SASA loss remain independent fields.

For example, column 177's reference G169 has zero sampled SASA in both modeled contexts, despite high NLL; column 58's L57 has substantial calculated area loss at the interface, also despite high NLL. These examples demonstrate why likelihood cannot be treated as a surface-exposure annotation. Unobserved or unmapped residues have null contact/SASA values, not a negative-contact label or zero area.

## Limits of the model result

- This is one small, pretrained checkpoint, not an ensemble or a benchmark of model capacity. Training-set overlap and OspC homology in pretraining were not established.
- The model's 33-token conditional probability and empirical panel frequency differ in support, conditioning and calibration. Scores were not renormalized to 20 amino acids.
- Full-length precursor sequences are scored, including signal-peptide context; structure constructs omit much of that context. No mature-protein processing was inferred.
- Panel selection, sequence relatedness, taxon imbalance and strain-provenance ambiguity limit representativeness. Organism-group omissions are metadata groups, not phylogenetic corrections.
- The alignment is fixed. Panel sensitivity does not test alternative alignments.
- Mean column NLL can hide different residue-specific/context-specific scores. Raw per-residue results and residue counts are supplied for inspection.
- Masked pseudo-perplexity is exp(mean singleton-mask NLL over documented positions). It is not an autoregressive sequence likelihood, a probability of biological function, or a protection score.

No embeddings, synthetic mutation library, new sequence collection, folding experiment or larger model was used. The 16-test suite and separate full-data arithmetic audit passed. Personal GPU timing is not a matched event-cluster comparison. The two-node evidence still requires authorized execution on the actual event nodes.
