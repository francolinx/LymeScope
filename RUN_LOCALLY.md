# View saved LymeScope results

## Completed personal-Spark analysis

Open [sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/index.html](sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/index.html) directly in Chrome or Edge. Keep the completed results directory intact. Its data and viewer code are embedded; the scientific tables and method notes are linked locally. No server, package installation, cluster connection, model download or new alignment run is needed.

The laptop fast-forwarded reviewed recovery commit `55fcd984554eb12d7a62bd42d42675863fe0f2ea`. File existence, embedded JSON equality and seven local links passed. Chrome opened the viewer and its OspC window title was read back, but rendering was not inspected because the computer-use tool denied Chrome access. Do not treat launch acceptance or the earlier Spark browser receipt as a new laptop rendering check.

Run the existing tests with the installed Python from the repository root:

```powershell
python -B -m unittest discover -s tests -v
Push-Location sparkprep/analysis/ospc_comparison_v0.1.0
python -B -m unittest -v test_baseline
Pop-Location
Push-Location sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/source
python -B -m unittest -v test_baseline test_results
Pop-Location
```

These passed 8, 7 and 11 tests respectively with Python 3.14.4. Importer discovery avoids overwriting the historical test receipt; synthetic fixtures are retained in ignored directories. The earlier baseline emits two unclosed-file resource warnings. The completed suite verifies saved statistics, sequence round trips, TSV/JSON agreement and deposited-structure correspondence without rerunning MAFFT.

The [laptop integration receipt](findings/laptop-spark-integration.json) records all existing checksum-list and JSON-manifest checks: no mismatches among included files. Four absent original archive/sidecar paths are explained by the existing recovery audit. All 54 entries in the completed viewer's `SHA256SUMS` pass. Scientific outputs and original manifests remain unchanged; do not regenerate them just to update status documentation.

The separate [portable infrastructure viewer](portable_results/index.html) and its 47-file manifest remain unchanged. Its older saved README/handoff copies describe the departure checkpoint.

Private timestamped ZIP/Git-bundle backups and final publication readbacks are stored under `C:\Users\franc\Projects\LymeScope-recovery`. Original excluded archives on the personal Spark are outside this laptop backup's scope.

## Historical infrastructure-viewer and transfer instructions

The remaining instructions are retained from the departure checkpoint. Statements about absent scientific outputs and the blocked SSH transfer below are historical; the reviewed extracted recovery is now local. No transfer or importer run is needed to open the completed results above.

Open **[portable_results/index.html](portable_results/index.html)** in Chrome or Edge. It is labeled **“Saved results from completed cluster runs.”** Keep the whole `portable_results` directory together when copying it.

The viewer is a static local HTML file with inline styling. It requires no Fuzzball connection, remote model endpoint, shared volume, notebook, JavaScript package, Python server, internet connection or web font. Its content-security policy prohibits scripts and network connections. Local evidence links open the saved files.

The bundle now contains three completed infrastructure workflows: driver smoke, a real PyTorch CUDA operation with persistent NFS writing, and two-node shared-storage verification. All passed. No protein-analysis output, reference-structure bundle or scientific timing pair has been produced.

To verify the portable manifest using the laptop's existing Python:
```powershell
@'
from pathlib import Path
import hashlib, json
root=Path("portable_results")
m=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
for item in m["files"]:
    p=root/item["path"]
    assert p.is_file(), str(p)
    assert hashlib.sha256(p.read_bytes()).hexdigest()==item["sha256"], str(p)
print("PASS: all listed portable files exist and match SHA256")
'@ | python -
```

To export newly retrieved and reviewed evidence, first add only the exact small files and real result metadata to `findings/result-export-index.json`, then run:
```powershell
python scripts/export_saved_results.py
```
The exporter uses an explicit file allowlist, refuses files above 2 MiB until reviewed, hashes copied files, and performs no network or cluster calls. Do not add tokens, authentication files, model weights, entire dataset directories or unrelated team data. Keep pre-existing reference structures labeled separately from generated structures. Never register a proposal as a completed run.

Before departure, verify the manifest, open the viewer, open its evidence links, and check every expected scientific output exists. Use the final 15 minutes of actual node access for this check with cluster requests disabled. No Windows network or security changes are needed. Record missing outputs honestly.

Initial browser check passed on November 14 at approximately 5:10 PM Central using a separate headless Chrome profile, page `connect-src 'none'` and process-only DNS blocking. Windows networking was unchanged. See `findings/local-viewer-validation.json` and `findings/saved-results-viewer.png`. A regular local browser is the only viewing dependency; Python is needed only to regenerate or verify the bundle.


## Frozen personal-Spark handoff: transfer currently blocked

Strict SSH host-key verification failed for spark-6771. No file was imported. First independently verify the host's ED25519 fingerprint and establish the trusted known-host entry. Do not bypass this step. Then retry this exact transfer to the recovery directory outside the Git repository:

```powershell
scp -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 darkstar90@spark-6771:/home/darkstar90/lymescope-sparkprep/exports/lymescope_ospc_handoff_v0.1.0.tar.gz "C:\Users\franc\Projects\LymeScope-recovery\lymescope_ospc_handoff_v0.1.0.tar.gz"
Get-FileHash -Algorithm SHA256 "C:\Users\franc\Projects\LymeScope-recovery\lymescope_ospc_handoff_v0.1.0.tar.gz"
```

Require exactly 264149 bytes and SHA256 `1ce0fff5a1b8d7d24ed6d70844f798484ac81231bcf2350ddcd8f6551ec1fa0f`. Inspect archive contents before safe extraction. The current importer accepts directories/ZIP only, not tar.gz. Preserve the original and reconcile the actual manifest with scientific_bundle_contract.json before importing. Never execute imported scripts without inspection.

After safe extraction into a new directory and actual schema review:

    python scripts/import_scientific_bundle.py "C:\path\to\reviewed-extracted-bundle"
    python scripts/import_scientific_bundle.py "C:\path\to\reviewed-extracted-bundle" --import-to scientific_inputs

These commands validate/import locally only. They do not approve or submit a scientific job. No actual scientific command is fixed yet. Keep personal-Spark outputs distinct from event-cluster outputs.

## Recovery

Timestamped recovery ZIP and Git bundle are saved outside this repository under C:\Users\franc\Projects\LymeScope-recovery. The adjacent receipt records exact paths, SHA256 values and commit. Verify the ZIP hash, test its archive integrity and run `git bundle verify` from a Git repository before restoring. Keep the portable_results directory intact. No credential stores or browser profiles belong in these backups.

Departure browser recheck passed at approximately 6:05 PM Central: real infrastructure cards, all 17 local evidence links, and all 44 then-current manifest files. Cluster connections and process DNS were disabled; Windows networking was unchanged. See findings/departure-viewer-validation.json. Later additions are local handoff/evidence documents only.
