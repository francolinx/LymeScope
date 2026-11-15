# Resume on PERSONAL Spark

Checkpoint lymescope_departure_checkpoint_v0.1.1_20261115T000921Z, prepared 2026-11-15T00:09:21.424397+00:00 on spark-6771 as darkstar90. Existing GitHub repository: https://github.com/francolinx/LymeScope. The Windows laptop worker owns repository import/publication. No GitHub publication or laptop transfer is assumed or was performed here.

## What works and what is complete

MAFFT v7.525 (2024/Mar/13) compiled from the official without-extensions source using existing gcc/make, with the entire installation under tools/mafft-7.525. The version/sanity checks passed. The actual frozen 30-sequence panel produced 218 alignment columns. Identifiers and ungapped sequences exactly match the input. 202 columns have full coverage; 76 are identical across the full analyzed panel. 16 columns contain gaps. Column modal conservation and coverage are saved separately. First-reference mapping scores 162 observed residues of pre-existing experimental 1GGQ chain A, with unmapped/unobserved positions unscored. Eleven recorded tests passed. The offline viewer rendered successfully.

Completed original workspace outputs:
`/home/darkstar90/lymescope-sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/`

The previous prealignment files under its parent are historical; do not mistake their blocked-state reports for the completed result. In this checkpoint the completed result is under `analysis/`, including inputs/source_manifest.json, aligned.fasta, conservation_coverage.tsv, alignment_to_structure.tsv, structure_residues.*, viewer_data.json, index.html, scientific methods, attribution and tests.

## Unfinished work and blockers

No pending MAFFT installation, alignment or conservation/mapping task is known. No second-reference score map was generated. 1G5Z was independently verified: its earlier empty list was an absent optional unobserved-residue category; all 164 Cα residues are observed and the construct matches Q44717 positions 40–203. The portable replay entry point was syntax-checked but not run at departure, to avoid restarting/duplicating analysis.

No GPU model experiment, new fold, antigen ranking, universal representativeness or protection claim has been produced. Personal-Spark CUDA remained unavailable in the recorded inventory; three existing PyTorch environments could import torch but could not initialize CUDA, and Docker image inventory was blocked by socket permissions. These are not event-cluster results. No model or environment changes are authorized by this checkpoint.

Five primary strain fields remain unresolved/missing; 25 nonblank strain labels do not establish 25 distinct biological strains. Full methods/limitations are in analysis/METHOD_AND_LIMITATIONS.md. The full B31 catalog and full candidate pool are outside this compact checkpoint; the actual analyzed inputs and their provenance are included.

## Exact commands in this existing workspace

View the completed result by opening this file in a browser (no server):
`/home/darkstar90/lymescope-sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/index.html`

Check saved results without realigning:

```bash
cd /home/darkstar90/lymescope-sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0
sha256sum -c SHA256SUMS
cd source
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest -v test_baseline test_results
```

Verify the existing MAFFT executable:

```bash
/home/darkstar90/lymescope-sparkprep/tools/mafft-7.525/bin/mafft --version
```

If intentionally resuming computation later, replay into a NEW output directory, preserving all existing results:

```bash
cd /home/darkstar90/lymescope-sparkprep
/usr/bin/python3 scripts/reproduce_checkpoint_analysis.py \
  --checkpoint /home/darkstar90/lymescope-sparkprep/exports/lymescope_departure_checkpoint_v0.1.1_20261115T000921Z \
  --mafft /home/darkstar90/lymescope-sparkprep/tools/mafft-7.525/bin/mafft \
  --output /home/darkstar90/lymescope-sparkprep/analysis/replay_departure_20261115T000921Z
```

This uses the checkpoint's actual input FASTA/CIFs, requires MAFFT 7.525, refuses an existing output directory, repeats the recorded CPU-only L-INS-i command, and compares parsed sequences/statistics/mapping with the saved baseline before writing an equivalent viewer. It performs no downloads/installations or GPU work. Do not run the historical export/freeze scripts just to view data; several intentionally refuse existing version names and expect the original workspace layout.

## Required paths and offline dependencies

- Python standard library: /usr/bin/python3 (Python 3.12.3 in recorded runtime); no new packages needed for baseline calculations/tests.
- MAFFT: /home/darkstar90/lymescope-sparkprep/tools/mafft-7.525/bin/mafft; helper files reside under that prefix's libexec/mafft. Invoke by full path; no global PATH/shell-profile changes.
- Build/source/version/hash information and gcc/make version strings are recorded in analysis/tool_provenance.json, analysis/tool_provenance/ and provenance/tool_versions.json. Compiled tools, environments and source-download caches are deliberately excluded.
- Offline viewing needs only a browser capable of JavaScript and Canvas. analysis/index.html embeds the measured data; no node_modules, CDN, external assets, local web server or network access is required. Text tables remain directly readable.

## Frozen input, handoff, history and activity

Keep the original input archive separately, unchanged:
`/home/darkstar90/lymescope-sparkprep/exports/lymescope_ospc_handoff_v0.1.0.tar.gz`
Bytes: 264149
SHA256: 1ce0fff5a1b8d7d24ed6d70844f798484ac81231bcf2350ddcd8f6551ec1fa0f

No old export archives, recursive exports tree, .git, credentials, agent transcripts, weights, caches or environments are included in this departure checkpoint. The visible workspace .git directory is empty and Git did not recognize a repository; no relevant local history was visible. Nothing was reset or deleted. Preserve the laptop's existing Git history and root files when importing into its separate sparkprep/ directory.

The recorded host activity check found no active compiler/MAFFT/build processes, recognized project scripts or inspectable open writable workspace files. Some system process descriptors were unreadable; the snapshot is point-in-time, not a guarantee about all unrelated processes. No tasks were killed and no reboot/shutdown was performed. A final check is reported separately after packaging. The Spark is not automatically safe to unplug solely because an analysis task is idle; physical movement/power handling stays with the operator.
