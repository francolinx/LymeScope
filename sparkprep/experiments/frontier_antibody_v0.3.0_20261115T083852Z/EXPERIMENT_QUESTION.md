# Predeclared exploratory experiment: antibody contact versus OspC model/agreement discordance

Status at declaration: NOT RUN. Written before calculating antibody contacts or comparing contact outcomes to any model/agreement feature. Existing v0.2.1 features and published structural descriptions are known. No new protein-model inference is planned.

Question: Within the fixed natural OspC panel/reference coordinate system, does the existing disagreement between empirical modal agreement and ESM-2 original-residue predictability provide descriptive information about an experimentally observed antibody-contact footprint beyond reference amino-acid identity, ordinary agreement and pre-existing OspC dimer geometry?

This is not a test of protection, antigenicity, antibody escape, clinical utility, or a new sequence design. A discrepancy is a deterministic transformation of agreement and NLL; it cannot contain information beyond those inputs themselves. The meaningful comparison is against baselines that do not already include NLL, and against a simpler NLL-added comparator.

## Primary structure and endpoint

Primary: official PDB 9BIF, human B11–OspC complex, deposited biological assembly 1, model 1. Identify entities/chains from primary metadata and validate the OspC construct residue identities against the frozen UniProt-derived Q07337 reference (or another exact panel sequence if required; any change must be reported). Use deposited assembly operators, not arbitrary nearby chains in the asymmetric unit. Do not treat homologous numbering as identity.

Fixed contact definition: any observed protein heavy atom of an OspC residue within <=4.5 Å of any B11 Fab heavy/light-chain protein heavy atom in assembly 1. Exclude H/D, waters, ions and unrelated ligands; use positive occupancy and a single deterministic alternate-conformer selection. Keep insertion codes, label/auth chains, label/auth numbering, missing atoms/residues and construct extensions explicit. Contacts remain separate from OspC–OspC dimer contacts.

Map each antigen instance independently. The site-level primary label is any antibody contact across the OspC instances in that deposited assembly. Require exact natural residue identity, fully observed canonical heavy atoms in each antigen copy for strict negative/positive comparability, and observed CA/backbone context. Unmapped/missing/incomplete cases remain explicitly excluded/null; observed contact in an incomplete residue may be recorded but is excluded from the strict primary endpoint. Copies are not independent biological replicates. Atom pairs/residue pairs and per-copy labels are preserved.

## Eligible universe

Primary comparison: unique frozen alignment columns that (1) have all 30 natural residues, (2) map to observed 1GGQ chain-A reference coordinates with existing geometry, (3) map exactly into the 9BIF OspC construct and have complete observed canonical heavy atoms in every assembly antigen copy. Original reference amino-acid identity must match across coordinate systems. Existing reference eligibility is determined without antibody outcomes. Explicitly count losses at every gate. Incomplete-coverage columns are not promoted into the primary endpoint.

Primary discordance D is the already frozen v0.2.1 agreement-percentile minus predictability-percentile rank, computed over the 202 full-coverage columns. Positive D means agreement rank exceeds model predictability rank. Do not recompute its original ranking universe after seeing antibody contacts.

## Predeclared comparisons and controls

Descriptive metrics: contact/noncontact counts, prevalence, per-group means/medians and differences; raw-direction AUROC for modal agreement, mean NLL, signed D, absolute D, reference dimer SASA and dimer-contact flag. Do not reverse a score's sign to improve its AUC. No population p-value or residue-independence claim.

Primary model diagnostic compares ridge logistic baseline B2 against B2 plus signed D:

- B0: intercept only.
- B1: modal agreement only.
- B2: modal agreement + fixed canonical reference amino-acid indicators + log1p(reference 1GGQ dimer SASA Å²) + log1p(reference dimerization SASA loss Å²) + reference homodimer-contact indicator.
- B3: B2 + signed D.
- B4: B2 + panel-mean original-residue NLL (simpler PLM comparator).
- B5 (secondary): B2 + Q07337-specific original-residue NLL, reusing its existing saved scores.

Use existing NumPy/SciPy only. Logistic objective is sum negative log-likelihood + (1/2)*sum(non-intercept coefficients squared), fixed L2 lambda=1, with no tuning. Standardize continuous variables on training rows only; amino-acid indicators remain 0/1. Fixed alphabet ACDEFGHIKLMNPQRSTVWY with A as omitted reference. Constant columns have scale 1.

Blocked held-region diagnostic: split the pre-antibody frozen full-coverage/observed-reference universe into eight contiguous, equal-count alignment-order blocks. For each held block, exclude training positions within five alignment columns of that block's min/max eligible coordinates. Report all fold sizes/classes. Do not use random residue splits, select folds by outcomes or tune hyperparameters. If a training fold lacks either class, report that model diagnostic NOT RUN rather than silently changing the split. At least 60 eligible sites and at least 10 contact/noncontact sites overall are required for model diagnostics.

Primary numerical contrast: out-of-fold Brier(B3) minus Brier(B2), negative meaning lower error under this one diagnostic. Also report out-of-fold log loss and AUROC for every model, training fit for transparency, and all held-region predictions. This is exploratory performance within one fixed, correlated structure/footprint, not external validation. A modest improvement is not proof of additional biology. Negative/inconclusive outcomes must be preserved.

Sensitivity: repeat descriptive contact labels at 4.0 and 5.0 Å without choosing the best cutoff. Report both copy-specific footprints and site-union labels. Optional 7UIJ/B5 is a separately labeled secondary structural check; similar antigen/epitope biology prevents treating it as independent external validation. A literature-defined 8C1 region may be source-annotated but never substituted for atom-derived contacts or silently pooled into labels.

## Stop and interpretation rules

If exact chain/construct identity or assembly transformation cannot be validated promptly, stop extending that structure and deliver mapping-status evidence plus reusable importer/tests. One fully verified complex outranks several partial annotations. Do not expand the panel, design mutations, download weights, install packages or contact event nodes. Reused v0.2.1 artifacts and all frozen v0.1.0 outputs remain untouched. New results live only in this experiment directory and the Spark feature branch.
