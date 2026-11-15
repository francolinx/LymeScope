# LymeScope claim index

Machine-readable companion: [claim-index.json](claim-index.json). Generated from saved evidence; no new inference.

## C01

CDC distinguishes more than 80,000 annually reported Lyme cases from a claims-based estimate of 476,000 people diagnosed and treated.

**Level:** PUBLIC_HEALTH_SOURCE · **Status:** PRIMARY_RECORD_VERIFIED

Primary CDC surveillance page checked November 15, 2026.

**Limits:** Different measures; neither is an exact infection count. Claims estimates may overcount; surveillance has underreporting/misclassification.

- [Primary source 1](https://www.cdc.gov/lyme/data-research/facts-stats/)

## C02

The selected panel has 30 natural sequences, 218 fixed columns, F=202 fully covered, M=162 observed mapped columns, and MF=159.

**Level:** FROZEN_BASELINE · **Status:** VERIFIED_SAVED_EVIDENCE

Saved coverage and explicit coordinate-status mapping.

**Limits:** Selected related sequences; not universal conservation or independent residue samples.

- [sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/viewer_data.json](../sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/viewer_data.json) · SHA256 `d0b13b25800b908ed2a515b15c394666df34f361db1242d715978a1ee8e67f1e`

## C03

Columns 154 and 173 each have modal agreement 1.0 from one of 30 observations and no reference coordinate.

**Level:** FROZEN_BASELINE · **Status:** VERIFIED_SAVED_EVIDENCE

Observed standard-residue fraction; gaps excluded from agreement and retained in coverage.

**Limits:** The percentage is correctly calculated from one observation; that is insufficient support for broad conservation in this panel.

- [sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/viewer_data.json](../sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/viewer_data.json) · SHA256 `d0b13b25800b908ed2a515b15c394666df34f361db1242d715978a1ee8e67f1e`

## C04

The personal Spark completed 6,305 original-residue masks in 805 scoring forwards at per-sequence batch size 8.

**Level:** PERSONAL_SPARK_COMPUTATION · **Status:** VERIFIED_SAVED_EVIDENCE

One mask per example; sum of per-sequence ceil(length/batch size); actual successful calls recorded.

**Limits:** Three warm-up forwards / 24 examples are additional, not scientific rows.

- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/full_panel_v1/timings.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/full_panel_v1/timings.json) · SHA256 `84ac459bfc1df0e1986f6852967fcfeca8725b23e408063364a9b1e2c673fa1d`
- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/full_panel_validation.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/full_panel_validation.json) · SHA256 `972b1a4705885859315558b7eb9c36dfb1d542f472cdbfaf7ad324a1a8570e01`

## C05

Personal GB10 warm scoring took 9.909294 seconds; load/transfer took 0.313129 seconds.

**Level:** PERSONAL_SPARK_COMPUTATION · **Status:** VERIFIED_SAVED_EVIDENCE

Synchronized GPU scoring and separate load/transfer receipt.

**Limits:** One personal-host run, not a matched venue benchmark. Process wall starts after imports; OS page cache uncontrolled.

- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/full_panel_v1/timings.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/full_panel_v1/timings.json) · SHA256 `84ac459bfc1df0e1986f6852967fcfeca8725b23e408063364a9b1e2c673fa1d`

## C06

The primary score is masked-original-residue NLL under pinned ESM-2 8M, using all 33 vocabulary logits.

**Level:** METHOD_AND_PROVENANCE · **Status:** VERIFIED_SAVED_EVIDENCE

Natural-log softmax, eval/inference mode, fp32/eager, TF32 disabled, one masked original residue; exact token/mapping assertions.

**Limits:** Neither empirical conservation nor entropy, mutation effect, function, immunogenicity or an autoregressive sequence likelihood.

- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/provenance/method_contract.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/provenance/method_contract.json) · SHA256 `78c9126f67ebd4ea3a0d58d28a4c8e926686f72d5dc1270837ff1a598b9ab311`
- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/provenance/model_download_receipt.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/provenance/model_download_receipt.json) · SHA256 `df689a83c921688698c5c2c2131f2bcc975fac70f08311c58d4657cffa15760d`
- [Primary source 1](https://huggingface.co/facebook/esm2_t6_8M_UR50D)
- [Primary source 2](https://doi.org/10.1126/science.ade2574)

## C07

Agreement versus predictability has descriptive Spearman rho 0.134696 across F=202; 239 overlapping fixed-alignment subsets assess sensitivity.

**Level:** PERSONAL_SPARK_COMPUTATION · **Status:** VERIFIED_SAVED_EVIDENCE

Common full-coverage column set, average tied ranks; reuse unchanged per-sequence scores.

**Limits:** Overlapping subsets are not independent replicates or a population confidence interval; no significance claim.

- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/joint_sensitivity_summary.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/joint_sensitivity_summary.json) · SHA256 `6ae74fa76d6951acbadc70a7c9521dc58d133aa27936fc0d373d3577b3b88210`
- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/full_panel_comparison_v2/column_comparison.tsv](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/full_panel_comparison_v2/column_comparison.tsv) · SHA256 `9dd159882c783ae23f2c50535e2acf8afc572390a48c984766fc0bb0e5edc02d`

## C08

Columns 177 and 129 illustrate high agreement/high NLL versus lower agreement/lower NLL.

**Level:** PERSONAL_SPARK_COMPUTATION · **Status:** VERIFIED_SAVED_EVIDENCE

Column mean NLL among observed original residues, shown beside empirical residue counts.

**Limits:** Illustrative selected positions, not an antibody-binding or biological-function prediction.

- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/laptop_evidence_v1.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/laptop_evidence_v1.json) · SHA256 `35ff10c8979ad364e0e39cb2350439b1cfd742212a2bf66594a13b993dab57d5`

## C09

1GGQ assembly 1 has 118 interchain heavy-atom residue pairs within 4.5 Å and 51 contacting residues per partner.

**Level:** COMPUTED_EXPERIMENTAL_GEOMETRY · **Status:** VERIFIED_SAVED_EVIDENCE

minimum interchain nonhydrogen atom distance <=4.5 A; model1, positive occupancy, alt . or A; deposited biological dimer assembly operators applied; waters/ions/nonprotein excluded

**Limits:** OspC–OspC dimer contacts, not antibody contacts. Cutoff/construct dependent; missing coordinates are unknown.

- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/dimer_context_summary.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/dimer_context_summary.json) · SHA256 `ecd344751b0adbcecbedb81065413b4804e4bf903ca605569b891b01d815b841`
- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/dimer_contacts.tsv](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/dimer_contacts.tsv) · SHA256 `d0c76c9c87dd9b0eeab06fcbb618cb21101392d23125648ee72b8537b42ee85d`
- [Primary source 1](https://www.rcsb.org/structure/1GGQ)
- [Primary source 2](https://doi.org/10.1093/emboj/20.5.971)

## C10

1GGQ calculated total SASA loss is 4,081.16 Å²; mean partner interface area is half, 2,040.58 Å².

**Level:** CALCULATED_SASA · **Status:** VERIFIED_SAVED_EVIDENCE

Heavy-atom Shrake–Rupley-style Fibonacci sampling, stated element radii, 1.40 Å probe, 1,920 points/atom.

**Limits:** Static incomplete constructs; no physiological/antibody accessibility measurement or exposed/buried classification.

- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/sasa_context_summary.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/sasa_context_summary.json) · SHA256 `82b63e6649d493951da3c28d8eec8bbd52a09cf03ce4c4a47844b8c03ebd5209`
- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/sasa_dimer_context.tsv](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/sasa_dimer_context.tsv) · SHA256 `bee61c0cd4e16ab9bd409386ed65415bd0f62cb5def792f219fcafe6c2d08b1d`

## C11

The second reference 1G5Z uses an explicitly transformed symmetry partner and an exact Q44717 construct correspondence.

**Level:** COMPUTED_EXPERIMENTAL_GEOMETRY · **Status:** VERIFIED_SAVED_EVIDENCE

Whole-construct sequence identity and deposited assembly operators.

**Limits:** Residue numbering is not transferred by accession metadata alone. Separate structure, not a new model-generated fold.

- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/dimer_alignment_mapping.tsv](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/dimer_alignment_mapping.tsv) · SHA256 `88708adf90315d63204a64c9bd0e41aa802f9f14067567846df0876bd49bfef9`
- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/dimer_context_summary.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/dimer_context_summary.json) · SHA256 `ecd344751b0adbcecbedb81065413b4804e4bf903ca605569b891b01d815b841`
- [Primary source 1](https://www.rcsb.org/structure/1G5Z)
- [Primary source 2](https://doi.org/10.1074/jbc.M010062200)

## C12

Current v2 unknown/unobserved contacts and SASA remain null, distinct from observed false and calculated zero.

**Level:** DATA_SEMANTICS · **Status:** VERIFIED_SAVED_EVIDENCE

Typed adapter and explicit coordinate status; v2 supersedes the earlier false labels.

**Limits:** The schema suffix evidence.v1 does not mean the superseded comparison_v1 aggregate.

- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/laptop_evidence_v1.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/laptop_evidence_v1.json) · SHA256 `35ff10c8979ad364e0e39cb2350439b1cfd742212a2bf66594a13b993dab57d5`
- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/provenance/analysis_corrections.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/provenance/analysis_corrections.json) · SHA256 `d262917a9fe35686bcdd56c65664be96f0cc0d9101b1a5dd045083803da0e4d1`

## C13

CIQ Fuzzball ran a CUDA calculation on Spark30 and verified identical stored bytes on Spark29 and Spark30.

**Level:** EVENT_INFRASTRUCTURE · **Status:** VERIFIED_SAVED_EVIDENCE

Saved CUDA and shared-NFS write/read receipts with physical-node attribution.

**Limits:** Infrastructure proof, not the scientific throughput benchmark. Vendor/backend identity is not established by identical-byte reads alone.

- [findings/phase-b-results.json](../findings/phase-b-results.json) · SHA256 `0e85a5ef8a39fe7cdd0e72d5572491e3788f80f84609f73fab3431c18fcacedf`
- [findings/phase-b-compatibility.json](../findings/phase-b-compatibility.json) · SHA256 `43028ba6d40b1df7e87d81b348436f2024630d483e88226bc7e4b22021b108b8`
- [workflows/ospc-spark-v0.2.1/storage-inspection.json](../workflows/ospc-spark-v0.2.1/storage-inspection.json) · SHA256 `aa48bbb2527c0df5bb9675316c8cdcc5759a89b756b40cfdc2d91ebe75469e94`

## C14

The matched event scientific one-node/two-node comparison is prepared but NOT RUN.

**Level:** PLANNED_WORKFLOW · **Status:** NOT_RUN

Spark30 all tasks, then concurrent Spark29/Spark30 shards; identical batch-8 protocol.

**Limits:** Authorization, staging, runtime, placement and venue pilots are gates. No measured speedup.

- [workflows/ospc-spark-v0.2.1/trial.HOLD.json](../workflows/ospc-spark-v0.2.1/trial.HOLD.json) · SHA256 `7e1d408df0cc974e384cfc7a729539abfb24f6e2917537a29446858c6bdc4a13`

## C15

Published B11/9BIF, B5/7UIJ and the 8C1 study supply independent experimental context; no antibody residue overlay is yet imported.

**Level:** PUBLISHED_EXPERIMENTAL_CONTEXT · **Status:** SOURCE_VERIFIED_MAPPING_PENDING

Official PDB metadata and primary paper records checked; educational source card only.

**Limits:** Published numbering requires validated chain/sequence/alignment mapping. Homodimer contacts are not antibody contacts.

- [docs/frontier_v0.3.0/experimental-evidence.json](../docs/frontier_v0.3.0/experimental-evidence.json) · SHA256 `517479305fe353d8c054b6729f121b133910f5d338fd7bdb0fdb3a269cf605ca`
- [Primary source 1](https://pubmed.ncbi.nlm.nih.gov/39240158/)
- [Primary source 2](https://pubmed.ncbi.nlm.nih.gov/36976016/)
- [Primary source 3](https://journals.asm.org/doi/10.1128/spectrum.02883-24)

## C16

The animations use saved alignment/coordinates and rigid camera motion; they are not new predicted structures or dynamics.

**Level:** PRESENTATION_OF_SAVED_EVIDENCE · **Status:** VERIFIED_SAVED_EVIDENCE

Original Pillow/NumPy renders, static alternatives, source hashes and decoded-frame checks.

**Limits:** The legacy dimer amber color is a separate 8 Å Cα proxy (49 residues/chain), not the 4.5 Å heavy-atom field. Browser playback requires its own check.

- [demo/v0.2.0/assets/manifest.json](../demo/v0.2.0/assets/manifest.json) · SHA256 `4aee04a6c73a6cc47ce860db8e0caaa74cfeff216247af27c5a729e724957069`

## C17

The published personal-Spark experiment reports sixteen passing tests and an independent full-result arithmetic audit.

**Level:** PUBLISHED_VALIDATION · **Status:** VERIFIED_SAVED_EVIDENCE

Saved runtime test receipt plus independent CSV arithmetic, task identity and mapping checks.

**Limits:** Laptop offline fixtures do not validate new real-model inference; local runtime limitations are reported separately.

- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/provenance/tests_full_release.log](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/provenance/tests_full_release.log) · SHA256 `2435c770b78306d2c4f92ec4dfc09cfb7b958dcaee72e053013aaa8b165c73d9`
- [sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/full_panel_validation.json](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/full_panel_validation.json) · SHA256 `972b1a4705885859315558b7eb9c36dfb1d542f472cdbfaf7ad324a1a8570e01`
