from pathlib import Path
from datetime import datetime
import json
now=datetime.now().astimezone().strftime("%I:%M %p Central")
Path("milestones.md").write_text(f"""# LymeScope checkpoints — November 14, 2026

Last checked: **{now}**. Actual organizer node-access cutoff remains **unknown and may be earlier** than the 7:30 PM departure target. No overnight event-node access is assumed.

| Target (Central) | Status | Evidence / next requirement |
|---|---|---|
| 5:15 PM — smoke evidence | DONE at 5:02 PM | findings/gpu-smoke-run.json; original successful run preserved, never repeated. |
| 5:45 PM — GPU runtime and durable path | DONE by 5:38 PM | findings/phase-b-results.json: CUDA, persistent write, Spark29 read and Spark30 read all PASS; reports exported and verified. |
| 6:15 PM — first real protein output | BLOCKED | Actual compact input bundle and scientific method from personal-Spark session are not on this laptop. Importer/contract ready. |
| 6:50 PM — identical-workload one/two-node pilot | NOT STARTED | Requires meaningful successful science with identical input/settings. Storage verification is not a scientific benchmark. |
| 7:10 PM — inspectable demo | IN PROGRESS | portable_results/index.html displays actual infrastructure results offline; no scientific output yet. |
| 7:30 PM — backup/departure | IN PROGRESS | Incremental reports/logs/workflows/hashes saved. Final departure validation remains required. |

No target has been missed as of this checkpoint. Reserve the final **45 minutes of actual access** for export/validation and its final **15 minutes** for saved-results viewing with cluster requests disabled. If access lasts to 7:30 PM, begin at 6:45 and 7:15 PM. Shift earlier with an earlier cutoff. The 6:50 pilot must finish before the export reserve or be marked incomplete.

Completed workflows:
- Smoke: 79a4aa69-4307-4184-9764-84b915f58579
- CUDA/write: 2f5d31fa-223c-4f5f-8df4-721fee85309a
- Two-node read: 9d279ac6-741f-48b1-88c3-1a61a0a56aa6

All finished with exit 0. **No submitted workflow remains running.** Phase B used two submissions, one new persistent 1 GiB NFS volume, and two temporary report volumes within 16 MiB each. No packages, weights or datasets were downloaded; both images reported cache hits. MCP remains read-only.

Scientific preparation: scripts/import_scientific_bundle.py and scientific_bundle_contract.json; eight synthetic importer tests passed (findings/scientific-importer-tests.json). Test fixtures are not data or scientific results. Preserve Claude's method/data handoff and the original personal-Spark bundle when supplied.
""",encoding="utf-8")
p=Path("RUN_LOCALLY.md"); s=p.read_text(encoding="utf-8")
s=s.replace("The current bundle contains one real **setup test**, not a protein-analysis result. PyTorch calculation, real protein inputs/outputs, reference structures and one/two-node pilot evidence are explicitly missing.","The bundle now contains three completed infrastructure workflows: driver smoke, a real PyTorch CUDA operation with persistent NFS writing, and two-node shared-storage verification. All passed. No protein-analysis output, reference-structure bundle or scientific timing pair has been produced.")
s+=r"""

## Import the future personal-Spark bundle

Source session: darkstar90@spark-6771; workspace: /home/darkstar90/lymescope-sparkprep. That is not a local Windows path. This session has not connected to it or transferred its files.

After an actual compact directory/ZIP has been transferred to this laptop, run from the LymeScope workspace:

    python scripts/import_scientific_bundle.py "C:\path\to\actual-bundle.zip"
    python scripts/import_scientific_bundle.py "C:\path\to\actual-bundle.zip" --import-to scientific_inputs

The first command validates only. The second creates a new manifest-identified local directory and byte-verifies the copy; it refuses to overwrite. Follow scientific_bundle_contract.json for FASTA IDs/accessions, source metadata, pre-existing reference labels, file sizes and SHA256 fields. No sample protein data is supplied.

The importer makes no network or cluster calls. It rejects traversal paths, links, case collisions, unlisted files, corrupt hashes, inconsistent sequence metadata and invalid residues. Limits: 20 MiB/file, 100 MiB total. Missing structures are explicit. Validation does not establish biological relevance or source-license suitability.

findings/next-scientific-run-proposal.json records a limited one-run resource envelope. It remains on hold until the exact real inputs and scientific command are available. No scientific upload or submission is authorized.
"""
p.write_text(s,encoding="utf-8")
Path("NEXT_SESSION.md").write_text("""# LymeScope handoff

Event node access will not be available overnight. Actual organizer cutoff is unknown; an earlier cutoff supersedes 7:30 PM Central November 14 departure. Access loss does not imply that nodes are powered off.

## Completed work with evidence

- Original smoke 79a4aa69-4307-4184-9764-84b915f58579 finished at 5:02 PM, exit 0. Never rerun; original report and hash preserved.
- CUDA/write workflow 2f5d31fa-223c-4f5f-8df4-721fee85309a, job 434b8807-bc70-527b-ad12-26896e66a050, finished at 5:36:27 PM, exit 0, on CIQ-CHI-SPARK30 (192.168.99.39/7331).
- Real CUDA matrix multiplication: 32x32 float32 all-ones matrices on cuda:0, synchronization, exact correctness checks, sum 32768. Python 3.12.3; PyTorch 2.10.0a0+b558c986e8.nv25.11; runtime CUDA 13.0; driver 580.173.02; GB10. Registry image metadata specifies CUDA 13.0.2.006. Evidence: findings/phase-b-writer-run.json.
- Created team15/lymescope-project: persistent NFS, exactly 1 GiB, group GID 100056 matching team15. No resize or permissions changes. Evidence: findings/phase-b-volume.json.
- Unique file: /project/verification/phase-b-20261114T173521-7908c2da/sentinel.txt; 78 bytes; SHA256 39fdbdc8e6d379b229fbab22b10b75fb803d6a257df97604adebe9a2d9be870d.
- Reader workflow 9d279ac6-741f-48b1-88c3-1a61a0a56aa6, job efeba751-fe73-540e-a992-a6d0e8c2cbcf, finished exit 0. Rank 0/container storage-two-node-read-0 maps to Spark30; rank 1/container storage-two-node-read-1 to Spark29 (192.168.99.38/7331). Scheduler Hosts and head ContainerId establish this mapping; both receipts match expected bytes/hash. Evidence: findings/phase-b-reader-run.json.
- Label: **two-node shared-storage verification**. Not GPU scaling, RDMA or a scientific benchmark. A roughly 30-second wait for the worker receipt occurred; cause not diagnosed.
- Both images reported cache hits. Public OCI metadata exposed the ARM64 PyTorch variant and digests; Fuzzball did not expose its executed OCI digest. Do not assert that current registry digest equals cached-image digest.
- Reports, logs, stages and exact workflows are local and in portable_results; digest verification passed. Summary: findings/phase-b-results.json. Manifest: portable_results/manifest.json.
- Exactly one persistent volume, two temporary report volumes and two Phase B submissions. **No tracked job remains running.** MCP is read-only.

## Laptop-only work possible overnight

- View actual infrastructure results in portable_results/index.html without cluster calls, endpoint or notebook.
- Receive the actual compact protein bundle from darkstar90@spark-6771, /home/darkstar90/lymescope-sparkprep. Its files are not automatically local, and this session has not contacted that host.
- Preserve Claude's method/data-contract work and the original received files. Reconcile with scientific_bundle_contract.json; adapt the local importer if the agreed contract differs.
- Validate/import a local directory/ZIP using scripts/import_scientific_bundle.py. It checks sizes, hashes, safe paths, FASTA IDs/residues, accessions, sources and pre-existing reference labels. Eight synthetic tests pass; fixtures are not scientific data.
- Prepare exact scientific commands, selected input IDs, output contract and evidence cards from the real manifest. Do not fabricate missing sequences, structures, model settings or results.
- Inspect portable provenance/hashes and improve the viewer with actual exported outputs, keeping setup runs separate from science.

## Work needing future node access — availability unknown

- findings/next-scientific-run-proposal.json is HOLD: one future manifest-locked run, team15, 1 GPU/2 CPU/16 GiB/2m, verified nvcr.io/nvidia/pytorch:25.11-py3, existing NFS, up to 5 MiB selected input upload and 1 MiB output egress, no weights/package downloads. Exact command and input manifest hash are missing; this is not approval-ready.
- After real data/method arrive, author and validate the exact workflow and obtain specific approval before upload/submission. Explicitly bound any other image, package or model requirement.
- After meaningful science succeeds, prepare an identical-workload one/two-node pilot. Verify both physical nodes. One timing pair is a pilot; preserve partial comparisons honestly.
- Shared datasets inspection remains HOLD pending supported enforced read-only mounting. It was not executed.
- NFS availability after event access is unknown. Export all essential outputs immediately.
- Reserve final 45 minutes of actual access for export/validation; final 15 for local viewing with cluster requests disabled. For 7:30 departure, start 6:45 and 7:15 only if access remains. No overnight workers, tunnels or remote-access assumptions.
""",encoding="utf-8")
p=Path("findings/result-export-index.json"); idx=json.loads(p.read_text())
name="findings/next-scientific-run-proposal.json"
if not any(x["path"]==name for x in idx["evidence_files"]):
    idx["evidence_files"].append({"path":name,"classification":"unexecuted_proposal","provenance":"Bounded resource envelope on hold for real manifest and scientific command"})
p.write_text(json.dumps(idx,indent=2)+"\n")
print("Milestones and handoff updated.")

