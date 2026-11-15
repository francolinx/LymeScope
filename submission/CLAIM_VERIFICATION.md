# Claim verification — version 0.2.0

| Claim or visual | Evidence and verification | Allowed interpretation |
|---|---|---|
| Lyme is the most common US vector-borne disease; annual counts differ | CDC/HHS pages checked; [sources](SOURCE_REFERENCES.md) | Public-health motivation, not a LymeScope clinical claim |
| 30 sequences; 218 columns; F=202, M=162, MF=159 | Saved viewer data, FASTA and explicit mapping; local tests | Panel description only |
| M minus F = 75, 86, 119 | Derived set difference from saved mapping and coverage | Three incomplete-coverage mapped columns; show counts |
| 76 identical full-coverage columns | Existing summary and tests | Not an independent robustness or protection result |
| 154/173 = one observation each | Actual rows: N/G respectively, 29 gaps; reference gaps | Correct percentage, insufficient broad-conservation support |
| Rotation and dimer | Original renders from saved 1GGQ model-1 CA atoms; assembly-1 identity transform and A/B selection checked | Rigid camera motion; not folding or dynamics |
| Dimer amber regions | Minimum other-chain CA distance ≤8 Å; 49 of 162 per chain | Geometric proxy only, not measured solvent/antibody accessibility |
| Column 68 → native 67 → A Ser67 | Saved explicit mapping; residue and coordinates checked | One experimental correspondence; 30/30 coverage, 66.7% agreement |
| Signal/tether/construct/observed regions | Saved annotation evidence and CIF mapping | Predicted processing boundary; tether candidate, not measured removal/flexibility |
| Secondary 1G5Z | Exact unique 164-residue match, atom/residue/author-number checks | Mapped reference only; no unvalidated second-chain contact rendering |
| 6,305 masks and 415 model calls | Actual FASTA inventory; per-sequence ceil at batch 16 | Locked workload counts; actual successful calls still NOT RUN |
| Task-shard animation | Deterministic plan, whole-sequence split 208/207 | Conceptual distribution; no speedup/time encoding |
| GB10 CUDA and shared storage | Existing event receipts identify Spark30 calculation and Spark29/30 reads | Infrastructure only, not scientific scaling |
| Scorer correctness | Offline fixture tests | Gate A only; not real inference |
| ESM model results, pilot, one/two-node scientific benchmark | No completed receipts | NOT MEASURED / NOT RUN |
| Historical milestones | Linked primary/institutional sources | No universal historical accuracy percentage |
| Future applications | Explicit prospective research framing | Not current LymeScope features or clinical promises |
| Personal motivation | Proposed wording submitted to lead | DRAFT until explicitly approved; no invented personal illness |

All animation files are original local CPU renders. Asset decoding and static frame inspection are distinct from browser playback. See [asset manifest](../demo/v0.2.0/assets/manifest.json) and [validation receipt](validation.json). The main branch, frozen evidence and manifests are preserved.

The scientific contract is the user's final Claude reference plus accepted corrections. No entropy, embedding dispersion, substitution log-odds, permutation experiment or 59-sequence expansion has replaced masked-original-residue NLL.
