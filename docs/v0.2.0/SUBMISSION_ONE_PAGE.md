# LymeScope: an inspectable OspC comparison

**Submission draft — completed evidence only.** Repository: https://github.com/francolinx/LymeScope

LymeScope makes a small protein comparison inspectable from frozen inputs through saved results. Our question is narrow: where are residues conserved within this particular OspC panel, how many sequences support each observation, and which positions correspond to an existing experimental structure?

We completed a CPU MAFFT alignment on a personal DGX Spark using 30 distinct natural sequences. The saved alignment has 218 columns: 202 have standard residues from all 30 sequences, 16 contain gaps, and 76 are identical at full coverage. Six additional columns have identical observed residues but incomplete coverage. At two columns, only one sequence contributes; the viewer exposes that denominator rather than presenting the apparent conservation as broad support.

The comparison maps 162 observed residues to the pre-existing experimental structure PDB 1GGQ, chain A; 159 mapped columns also have full sequence coverage. Eleven corresponding residues lack coordinates, 37 columns fall outside the construct, and eight are reference gaps. Missing/unmapped positions remain unscored. These are deposited coordinates, not newly generated folding predictions.

The offline viewer combines conservation, coverage, alignment, residue mapping and original metadata. Its data are embedded and its supporting tables, methods, citations and hashes are saved locally. The frozen v0.1.0 result is retained unchanged. Its 11 completed-result tests passed on the laptop; the broader existing local test set passed 26 tests. A previous Chrome launch was confirmed, but independent visual rendering inspection was blocked by browser-tool access. A presenter should check the local page before the demo.

Separately, event-cluster evidence establishes a real CUDA matrix operation on Spark30 and shared-storage reads on Spark29 and Spark30. This verifies infrastructure; it does not establish scientific acceleration or multi-node speedup.

**Next method, not a completed result:** ESM-2 8M masked-original-residue negative log-likelihood (NLL), one masked residue per example. The actual panel requires 6,305 examples and 415 scoring calls with per-sequence batch size 16. Leave-out aggregation reuses scores and uses the remaining sequence count for coverage. Independent GPU task shards are proposed; no NCCL/RDMA or distributed-model-capacity claim is made. Model staging and actual-model execution remain approval-gated.

**Unrun result placeholders:** actual-model pilot **NOT RUN**; masked scores **NOT RUN**; one-node timing **NOT RUN**; two-node timing/speedup **NOT RUN**. No embedding-dispersion or permutation result is claimed.

This is an unweighted, alignment-dependent convenience panel, not a protection, antigen-safety or significance claim. A separate demo overlay labels predicted processing, deposited assemblies and geometric contact proxies explicitly. UniProt attribution, PDB/primary-paper credit and original limitations are retained. No project license is selected; public GitHub visibility does not grant third-party redistribution rights. Organizer eligibility questions remain open.

New research runs stop Sunday, November 15, 2026 at **10:30 AM Central**. The noon submission and demo can use the completed CPU result even if model work never runs.

Evidence: `sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/` (viewer, summary, methods and tables); `findings/phase-b-results.json`; `findings/laptop-spark-integration.json`.
