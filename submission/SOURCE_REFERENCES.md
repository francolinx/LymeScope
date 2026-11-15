# Sources and attribution

Reviewed November 15, 2026. These links identify primary research, institutional sources and local evidence. No paper figure, stock footage or third-party video is copied into the presentation.

## Public-health context

- [CDC, Lyme Disease Surveillance and Data](https://www.cdc.gov/lyme/data-research/facts-stats/), page dated September 9, 2026. Supports the annual surveillance count, claims-based estimate and limitations; those measures are not interchangeable.
- [HHS, Invisible Illness: Lyme Disease](https://www.hhs.gov/lyme/index.html). Supports the most-common-vector-borne-disease framing. Other clinical claims on that page are not adopted by this project.

## OspC and project evidence

- Kumaran et al. (2001), *Crystal structure of outer surface protein C from the Lyme disease spirochete, Borrelia burgdorferi*. [DOI](https://doi.org/10.1093/emboj/20.5.971), [PDB 1GGQ](https://www.rcsb.org/structure/1GGQ). Deposited coordinates and biological assembly, not a LymeScope structure prediction.
- Eicken et al. (2001), *Crystal structure of Lyme disease antigen outer surface protein C from Borrelia burgdorferi*. [DOI](https://doi.org/10.1074/jbc.M010062200), [PDB 1G5Z](https://www.rcsb.org/structure/1G5Z). Separate mapping verified to Q44717 native 40–203; historical accession retained.
- [UniProt Q07337](https://www.uniprot.org/uniprotkb/Q07337/entry), [Q44717](https://www.uniprot.org/uniprotkb/Q44717/entry). The annotation layer uses the **saved records**, including evidence codes, not an assumed current revision. Predicted processing is not measured cleavage.
- [Frozen methods, sources and limitations](../sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/METHOD_AND_LIMITATIONS.md), [saved viewer data](../sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/viewer_data.json), [overlay provenance](../demo/v0.2.0/context.json), [original-animation manifest](../demo/v0.2.0/assets/manifest.json).
- [Event infrastructure receipts](../findings/phase-b-results.json), [laptop integration receipt](../findings/laptop-spark-integration.json). Historical evidence reused without rerunning infrastructure.

## Timeline sources

- Kendrew et al. (1958), X-ray myoglobin model. [Nature](https://www.nature.com/articles/181662a0).
- Havel & Wüthrich (1985), NMR/distance-geometry solution conformations. [PubMed](https://pubmed.ncbi.nlm.nih.gov/2582141/). An example of the experimental/computational partnership, not a claim of first-ever NMR work.
- Jones, Taylor & Thornton (1992), threading/fold recognition. [Nature](https://www.nature.com/articles/358086a0).
- Šali & Blundell (1993), comparative modeling with spatial restraints. [DOI](https://doi.org/10.1006/jmbi.1993.1626).
- Simons et al. (1997), fragment-based tertiary-structure assembly. [PubMed](https://pubmed.ncbi.nlm.nih.gov/9149153/).
- [EMBL-EBI CASP history](https://www.ebi.ac.uk/training/online/courses/alphafold/validation-and-impact/how-have-alphafolds-predictions-of-protein-structure-been-validated/) supports CASP's 1994 beginning.
- [Google DeepMind chronology](https://deepmind.google/science/alphafold/) supports AlphaFold at CASP13 in 2018 and subsequent milestones.
- Jumper et al. (2021), AlphaFold2 publication following CASP14 in 2020. [Nature](https://www.nature.com/articles/s41586-021-03819-2).
- [EMBL-EBI, July 2022 database expansion](https://www.ebi.ac.uk/about/news/technology-and-innovation/alphafold-200-million/) documents the 2021 launch and wider predicted-structure availability.
- Lin et al. (2023), *Evolutionary-scale prediction of atomic-level protein structure with a language model*. [PubMed 36927031](https://pubmed.ncbi.nlm.nih.gov/36927031/). Attribution: FAIR, Meta AI; not Chan Zuckerberg Initiative. ESMFold is historical context; the project uses ESM-2 masked scoring, currently unrun.
- Abramson et al. (2024), *Accurate structure prediction of biomolecular interactions with AlphaFold 3*. [Nature](https://www.nature.com/articles/s41586-024-07487-w). Broad research context, not a LymeScope feature. Publisher access can vary; the [developer's chronology](https://deepmind.google/science/alphafold/) also records the 2024 release. No paid content or figures are reproduced.

## Rights and event eligibility

UniProt's [CC BY 4.0 terms and rights disclaimer](https://rest.uniprot.org/help/license) and [RCSB policies](https://www.rcsb.org/pages/policies) are retained. PDB archive data are CC0; other website/paper content has its own rights. Credit primary investigators. Original project-rendered pixels do not make underlying third-party content unrestricted. Fonts are rasterized from the existing local installation; no font files are redistributed.

The repository has no newly invented license. Public GitHub visibility does not grant redistribution rights. [Open organizer questions](../docs/v0.2.0/ATTRIBUTION_AND_ELIGIBILITY.md) cover team eligibility, pre-existing work/personal hardware, AI assistance, track and submission logistics. No organizer was contacted. [Official event page](https://ciq.com/events/local-ai-hackathon-2026); noon submission and 1:00 PM demo are the project lead's supplied schedule.
## Completed personal-Spark experiment

Exact published source: [commit aafe818a20ea025370cf4b65145a9684e80aaaef](https://github.com/francolinx/LymeScope/tree/aafe818a20ea025370cf4b65145a9684e80aaaef/sparkprep/experiments/stretch_v0.2.0_20261115T072916Z), release v0.2.1. The current aggregate is v2; the raw NLL scores are unchanged by its null-contact correction. [Scientific findings](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/SCIENCE_FINDINGS.md), [exact venue contract](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/VENUE_CONTRACT.md), [published attribution](../sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/ATTRIBUTION.md). Original experiment figures are reused unchanged. The personal model cache includes the approved upstream README; weights remain outside Git. Public repository visibility does not replace source attribution or third-party terms.
