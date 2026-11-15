# LYMESCOPE
**Making the invisible biology of Lyme disease explorable.**

**Problem and persona.** Researchers comparing bacterial proteins need to distinguish broadly supported agreement from sparse observations, and sequence agreement from model predictability. LymeScope makes that evidence inspectable.

**Scientific question.** Within a selected cross-species panel of 30 natural OspC sequences, how does empirical agreement differ from ESM-2 masked-original-residue predictability, and where do those observations map to deposited experimental coordinates?

**What we built.** An offline evidence workbench, immutable results, explicit residue mapping and four guided stories: the coverage trap, model disagreement, the experimental homodimer, and a negative antibody-contact diagnostic. Typed adapters and original figures keep agreement, NLL, antibody contacts, homodimer contacts and calculated SASA separate. Two correct 100% agreement values can have 30/30 versus 1/30 observations.

**Frozen baseline.** The CPU MAFFT alignment has 218 columns: 202 fully covered, 76 identical at full coverage. There are 162 observed mapped 1GGQ residues; 159 columns are both fully covered and observed. Columns 154/173 each have 1/30 coverage and no reference coordinates. These describe this selected panel, not universal conservation. All structures are pre-existing experimental coordinates; no new fold was predicted.

**Local computing and event integration.** The biological baseline ran on the personal DGX Spark CPU. CIQ Fuzzball separately scheduled a successful CUDA calculation on NVIDIA GB10 at event Spark30, wrote to Team 15 persistent storage, and verified the same bytes from Spark29 and Spark30. This is real infrastructure proof, not a multi-node scientific benchmark. [Saved event receipts](../findings/phase-b-results.json)

**Completed personal-Spark AI result.** ESM-2 8M scored **6,305** original residues with one mask per example, **805 scoring forwards** at batch size 8, float32, and **9.909294 s warm GPU scoring**. Three warm-up forwards are separate. Model load plus transfer: 0.313129 s; process time after imports: 10.510127 s, not full workflow time. The published 16-test suite and arithmetic audit passed. Agreement versus predictability has descriptive Spearman **rho 0.134696 over F=202**; example rank directions persist across **239** overlapping panel perturbations, not a confidence interval. Experimental 1GGQ/1G5Z contacts and separately calculated SASA provide distinct structural context; missing values stay null.

**Provenance and venue placeholder.** Published source [`aafe818a20ea025370cf4b65145a9684e80aaaef`](https://github.com/francolinx/LymeScope/tree/aafe818a20ea025370cf4b65145a9684e80aaaef/sparkprep/experiments/stretch_v0.2.0_20261115T072916Z), release v0.2.1, aggregate **full_panel_comparison_v2**; model revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`. Event scientific one/two-node timing and speedup: **NOT RUN**. The prepared identical workload uses 6,305 masks on Spark30, then concurrent 3,156/3,149-mask Spark29/Spark30 shards. Access, staging, runtime and venue pilots remain gates; no artificial workload enlargement.

**A tested, negative hypothesis.** Exact experimental mappings identify **31/152** eligible B11/9BIF contacts and **25/152** B5/7UIJ contacts in its own site set. Adding signed discordance to agreement, amino-acid identity and geometry worsened primary blocked Brier error **0.168634 → 0.174022 (+0.005388)**; AUROC **0.620634 → 0.616369**. No incremental predictive value was demonstrated. The existing scores were reused; 8C1 remains literature-region evidence only. [Pinned frontier source 82fb8b5](https://github.com/francolinx/LymeScope/tree/82fb8b53018ba4012ccebf02a29efa87b892f6ed/sparkprep/experiments/frontier_antibody_v0.3.0_20261115T083852Z)

**Limits.** Correlated sites, selected sequences and missing coordinates limit inference; no external functional validation, new target, protection or clinical claim. The [claim index](../docs/claim-index.json) preserves sources and limitations. Eligibility awaits organizers; no project license is invented.

**Repository:** https://github.com/francolinx/LymeScope · [Sources](SOURCE_REFERENCES.md) · [Offline workbench](../docs/index.html). Prepared for the reviewed main release; publication requires the lead's approval. Pages hosting is not claimed live.

Submission: November 15, 2026, noon Central. Live demo: 1:00 PM; five minutes maximum. New research cutoff: 10:30 AM Central. Saved CPU and personal-Spark GPU evidence work offline; event timing is optional.
