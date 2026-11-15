# LYMESCOPE
**Making the invisible biology of Lyme disease explorable.**

**Problem and persona.** A researcher comparing bacterial proteins needs to see whether an apparently conserved position is supported by many sequences or just one. Lyme is the most common US vector-borne disease; CDC reports over 80,000 annual reported cases and a separate, uncertain claims-based estimate of 476,000 people diagnosed and treated. These are different measures. [CDC](https://www.cdc.gov/lyme/data-research/facts-stats/) · [HHS](https://www.hhs.gov/lyme/index.html)

**Scientific question.** Within a selected cross-species panel of 30 natural OspC sequences, which corresponding positions agree, how much coverage supports them, and which map to deposited experimental coordinates? A prepared extension asks how observed agreement differs from ESM-2 masked-original-residue predictability.

**What we built.** An offline evidence viewer, immutable scientific inputs/results, explicit residue mapping and a separate presentation overlay. Original animations connect the actual alignment to experimental 1GGQ coordinates and expose missing information. A versioned masked-NLL scorer, receipt ingestion and leave-out aggregation reuse the existing panel. The display starts with two correct 100% agreement values supported by 30/30 versus 1/30 observations.

**Actually measured.** The CPU MAFFT alignment has 218 columns: 202 fully covered and 76 identical at full coverage. Mapping reaches 162 observed 1GGQ chain-A residues; 159 mapped columns are also fully covered. Mapped columns 75, 86 and 119 have incomplete coverage. Columns 154/173 each have 1/30 coverage and no reference coordinates. These describe this panel, not universal conservation or immunity. The deposited A/B dimer is checked before a clearly labeled geometric C-alpha contact proxy is shown. No new fold was predicted.

**Local computing and event integration.** The biological baseline ran on the personal DGX Spark CPU. CIQ Fuzzball separately scheduled a successful CUDA calculation on NVIDIA GB10 at event Spark30, wrote to Team 15 persistent storage, and verified the same bytes from Spark29 and Spark30. This is real infrastructure proof, not a multi-node scientific benchmark. [Saved event receipts](../findings/phase-b-results.json)

**Stretch result placeholders.** Actual ESM-2 pilot: **NOT RUN**. Masked NLL: **NOT MEASURED**. One/two-node scientific timing and speedup: **NOT RUN**. The locked 30-sequence workload has 6,305 masks and 415 scoring forwards; model staging and execution need separate authorization. No repeated data or larger model is used to manufacture scaling.

**Limits and reproducibility.** This convenience panel is unweighted and alignment dependent. Coordinates are published experimental evidence; statistics, proximity proxies and any future model outputs have different meanings. No diagnosis, protection, accessibility or vaccine-safety claim is made. Frozen hashes, sources, tests and missing states remain inspectable. Eligibility and the project lead's personal statement await confirmation; no project license is invented.

**Repository:** https://github.com/francolinx/LymeScope · [Sources](SOURCE_REFERENCES.md) · [Demo](../demo/v0.2.0/index.html)

Submission: November 15, 2026, noon Central. Live demo: 1:00 PM; five minutes maximum. New research cutoff: 10:30 AM Central. Completed CPU evidence is sufficient for this demonstration.
