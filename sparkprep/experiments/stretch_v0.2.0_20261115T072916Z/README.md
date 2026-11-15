# Personal-Spark OspC stretch checkpoint v0.2.1

Full frozen-panel ESM-2 masked-original-residue scoring is complete: 30 natural sequences, 6,305 masks, all 218 alignment columns. The pilot and original package remain preserved; the fixed v0.1.0 results were not modified. This release uses the same experiment directory identifier as the pilot.

Read REPORT.md for actual execution, SCIENCE_FINDINGS.md for interpretation, LAPTOP_HANDOFF.md for integration, and VENUE_CONTRACT.md for one-node/two-node reproduction. All 16 tests and the independent complete-data audit pass. Model weights are outside Git. No event cluster was contacted and no two-node benchmark is claimed.

Current data: results/full_panel_v1/ for raw model outputs, results/full_panel_comparison_v2/ for current aggregates (v1 retained but superseded for unknown-contact labeling), results/laptop_evidence_v1.json for the typed laptop adapter, results/joint_panel_sensitivity.tsv for fixed-panel perturbations, and results/sasa_dimer_context.tsv for separate CPU-calculated geometry. Agreement, NLL, contact, calculated SASA, antigenicity and protection are not interchangeable.

The figures full_panel_agreement_predictability, experimental_dimer_comparison and calculated_sasa_dimer_context are available as PNG and SVG under results/. The earlier panel_sensitivity_dimer_context figure has its original PLM-pending caption and remains a historical CPU checkpoint, not the current full-panel view. REPORT_PILOT.md / VENUE_CONTRACT_PILOT.md are also historical snapshots.

FILE_MANIFEST.json and SHA256SUMS list all eligible package files and exact bytes without recursive self-hashing. src/verify_package.py validates them offline and optionally verifies all six local model files. Source, inputs, tests, outputs, methods, attribution, approvals, timings, shard manifest and provenance are included; weights, Python bytecode and unrelated private inventories are excluded.
