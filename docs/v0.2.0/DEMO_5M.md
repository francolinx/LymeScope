# LymeScope demo — five minutes

> Current measured-result script: [submission/DEMO_SCRIPT.md](../../submission/DEMO_SCRIPT.md). The unrun-model script below is a preserved historical checkpoint.


Primary local page: `demo/v0.2.0/index.html`. The original viewer is linked at the top. Keep `DEMO_4M30S.md` as the shorter existing script; this version adds the targeted biological context. No live model, cluster or internet connection is needed. Actual browser rendering still requires the normal approved browser check; do not infer it from unit tests.

| Time | Action and factual narration |
|---|---|
| 0:00–0:40 | Show the population badges. “We have 30 natural sequences and 218 aligned columns. The 202 fully covered columns, 162 observed 1GGQ residues and their 159-column intersection are different populations. This is a description of the analyzed panel, not a vaccine-protection claim.” |
| 0:40–1:25 | Select columns 154 and 173. “Each has a modal fraction of one, but only one of 30 sequences contributes. Both remain alignment-only. Coverage and coordinate availability are shown separately.” |
| 1:25–2:15 | Open the frozen viewer link if useful; inspect its alignment and primary mapping. “This completed CPU alignment and all saved outputs are unchanged. Missing coordinates, construct-external positions and reference gaps are not filled or scored as if observed.” |
| 2:15–3:10 | In the overlay, show processing/construct regions and assembly context. “Signal peptide 1–18 is a predicted annotation, not cleavage measured by us. Downstream sequence outside the construct is a tether candidate. We verified deposited 1GGQ assembly 1, the A/B dimer, before calculating this C-alpha proximity proxy. It is not solvent or antibody accessibility.” |
| 3:10–3:40 | Switch to 1G5Z. “Its 164-residue construct uniquely matches Q44717 positions 40–203; residue identity and numbering were checked. The historical accession is preserved. The biological dimer requires a symmetry operation, so no secondary interchain proxy is claimed here.” |
| 3:40–4:25 | Show the NOT RUN model panel. “The prepared primary metric is masked-original-residue NLL. There are 6,305 actual examples and 415 scoring forwards at this batching policy. Two independent GPU shards would split calls 208/207. Warm-up and correctness calls are separate; no speedup is promised.” |
| 4:25–5:00 | Show provenance and close. “The CPU result is complete. CUDA and two-node shared storage were verified separately. Model correctness and scientific scaling are not yet run. We retain source credit, uncertainty and open eligibility questions. The 10:30 AM Central research cutoff protects the noon submission.” |

The optional structural overlay is not a submission prerequisite. If it fails to display, use the original viewer or its saved summary/tables and follow the 4½-minute fallback script. No driver repair, downloads or scientific reruns during the presentation.

Leave these placeholders unchanged unless later approved receipts pass ingestion: **actual-model pilot NOT RUN; masked NLL results NOT RUN; one-node benchmark NOT RUN; two-node benchmark NOT RUN**. A fixture is not inference evidence. A single timing pair, even if later successful, is a pilot observation rather than a scaling law.
