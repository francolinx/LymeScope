# LymeScope demo — 4 minutes 30 seconds

Use the existing local viewer at `sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/index.html`. This is a duration script, not a change to the scheduled presentation time. Rehearse rendering manually before presenting; browser automation was unavailable. No live cluster or model execution is needed.

| Time | Show | Say |
|---|---|---|
| 0:00–0:35 | Viewer title and summary badges | “We compared 30 natural OspC sequences. This is a description of this panel, with a path back to every input and result. We are not claiming vaccine protection or newly predicted structures.” |
| 0:35–1:20 | Conservation and coverage plot; select column 154 | “Orange asks how frequently the modal amino acid appears among observed standard residues. Blue asks how many of the 30 sequences contribute. Here a modal fraction of one comes from just one sequence. Coverage prevents that from being mistaken for broad conservation.” |
| 1:20–2:05 | Alignment; inspect a full-coverage and a variable column | “There are 218 aligned columns, 202 fully covered and 76 identical at full coverage. The identifiers and ungapped sequences match the frozen panel. The alignment is fixed when we later remove rows; removing rows cannot turn an originally complete column into an incomplete one.” |
| 2:05–2:55 | Reference trace and unscored-position table | “This is experimental PDB 1GGQ chain A. We map 162 observed residues. Missing coordinates, positions outside the construct and reference gaps remain explicit. The trace is an illustration, not a molecular surface or a folding claim.” |
| 2:55–3:30 | Methods, metadata and saved file links | “The sampling labels and their limitations are preserved. These data, methods and outputs work offline. We can distinguish a completed result from a proposal and test the saved statistics without rerunning an experiment.” |
| 3:30–4:05 | Explain the prepared masked-scoring method; keep viewer open | “The next method measures the model log-probability of the actual residue while that one residue is masked. We batch examples, count real forward calls and reuse per-sequence scores for sampling sensitivity. Actual-model correctness and scaling are not yet demonstrated.” |
| 4:05–4:30 | Return to summary | “Our completed deliverable is the inspectable CPU baseline. CUDA and two-node shared storage were verified separately, but scientific speedup has not been measured. Model work is optional for this submission and stops at the 10:30 AM Central research cutoff.” |

## Evidence-dependent replacement slot

Keep these labels unless later approved runs produce validated receipts: **pilot NOT RUN; masked scores NOT RUN; one-node benchmark NOT RUN; two-node benchmark NOT RUN**. Do not substitute fixture outputs, projected speedups or a model's parameter count for measured inference.

If approved results arrive before the cutoff, replace only the 3:30–4:05 slot after ingestion verifies task coverage, physical nodes, matching inputs/settings, predeclared float tolerances and separated load/compute/transfer/workflow timings. A small workload may show no speedup; report that honestly.

## Fallback

If interactive rendering fails, open saved `summary.json`, `conservation_coverage.tsv` and `alignment_to_structure.tsv` from the completed result directory. Read the same facts, state the display limitation, and complete the demo. Do not repair drivers, fetch models or rerun science during the presentation.
