# LymeScope source-and-analysis checkpoint v0.1.0

Stable snapshot of the latest COMPLETED OspC comparison. The source data archive remains frozen and byte-identical. No analysis was restarted or duplicated to create this checkpoint. No model/GPU or event-cluster work was performed, no GitHub repository or branch was created/pushed, and no transfer has occurred. Laptop worker owns publication.

## Inventory

- analysis/: completed 30-sequence, 218-column MAFFT alignment; conservation/coverage tables; first-reference mapping to 162 observed residues of pre-existing experimental 1GGQ chain A; secondary 1G5Z check; offline viewer; tests; exact commands/tool provenance; limitations; input manifests, reference structures and scientific evidence.
- scripts/: project data preparation, inventory, handoff, analysis-start and checkpoint scripts, plus a portable replay entry point. Historical packaging scripts retain original workspace assumptions and exclusive output/version guards.
- analysis/ospc_comparison_v0.1.0/*.py: original prealignment and orchestration source retained as source history only. These files are NOT the location of the current completed outputs. The completed outputs and maintained portable baseline/tests are under top-level analysis/ and analysis/source/.
- frozen/lymescope_ospc_handoff_v0.1.0.tar.gz: unchanged frozen input archive and its checksum.
- provenance/: personal-Spark runtime inventory, exact Python/gcc/make/MAFFT version strings, read-only host process snapshot and snapshot metadata.
- CHECKPOINT_MANIFEST.json and SHA256SUMS: byte sizes, hashes and snapshot status.

Credentials, dot-directory agent/configuration files, transcripts, environments, model weights, download caches and compiled tool installations are excluded by explicit file allowlist. MAFFT's source URL/hash/version, configured installation paths, native helper hashes, license and build/install logs are recorded as text under analysis/tool_provenance*. No compiled MAFFT tree or downloaded source tarball is included.

## Verify and view (no installation required)

Verify the archive using its adjacent .tar.gz.sha256 file. Extract into an empty destination. From the extracted checkpoint directory run:

```bash
sha256sum -c SHA256SUMS
```

Open analysis/index.html directly in a local browser; it has embedded measured data and needs no server or network. Scientific methods, actual findings, limitations and input/output hashes are in analysis/METHOD_AND_LIMITATIONS.md. Conservation is only within this analyzed convenience panel; 30 distinct sequences do not establish 30 distinct strains. Coverage and modal fraction have separate denominators. No scores are assigned to unmapped/unobserved structure residues, and experimental B-factors are not prediction confidence.

Existing tests use Python's standard library:

```bash
cd analysis/source
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_baseline test_results
```

The saved analysis/tests.log records 11 passing tests from the completed run. No scientific computation was rerun for snapshotting. The new portable replay script was syntax-checked, not executed during checkpoint creation.

## Reproduce in a NEW output directory

An existing MAFFT 7.525 executable is required for alignment; use its absolute path. Do not invoke the historical package/install scripts blindly. MAFFT installation/source information is in analysis/tool_provenance.json. The original isolated installation is /home/darkstar90/lymescope-sparkprep/tools/mafft-7.525; it is not included. On a new machine, installing MAFFT is a separate action requiring that machine's authorization. No install or download is needed to view or test the saved baseline.

From the extracted checkpoint root, after an appropriate MAFFT 7.525 executable exists:

```bash
python3 scripts/reproduce_checkpoint_analysis.py   --mafft /absolute/path/to/mafft   --output /absolute/path/to/a/new-empty-output-directory
```

The replay refuses an existing output directory, runs --amino --localpair --maxiterate 1000 --thread 1 --inputorder, preserves identifiers/native input sequences, recomputes column statistics and the verified 1GGQ mapping, and compares alignment/statistics/mapping with the saved baseline. Differences stop the replay rather than labeling it equivalent. Successful replay writes reproduction_validation.json and an offline index.html. Reproduced numeric arrays must match before the original summary/display schema is reused; original methods remain as baseline provenance and the new command/time are recorded separately. Different builds/platforms may produce alignment differences requiring review. The saved original aligned FASTA hash includes descriptions/formatting; replay equality checks the parsed identifier/order/sequence arrays and numeric results, not just formatting.

## Running work / physical move

The recorded host check found no MAFFT/compiler/build processes or recognized project analysis scripts running. This is a point-in-time observation, not a shutdown or guarantee about unrelated processes. Final status is reported separately after checkpoint creation. No unrelated processes were killed; the Spark was not rebooted or shut down. Arrange physical movement/power handling yourself.
