"""Stable, allowlisted source + completed-results checkpoint; never overwrite a version."""
import pathlib,json,hashlib,tarfile,datetime,subprocess,sys,ast,io
P=pathlib.Path;workspace=P(__file__).resolve().parent.parent;name='lymescope_source_analysis_checkpoint_v0.1.0';stage=workspace/'exports'/name;archive=workspace/'exports'/(name+'.tar.gz');assert not stage.exists() and not archive.exists()
def sha(b):return hashlib.sha256(b).hexdigest()
# Load all source bytes once; compare again after packaging to reject concurrent mutation.
sources={}
for folder in [workspace/'scripts',workspace/'analysis/ospc_comparison_v0.1.0']:
 for p in sorted(folder.glob('*.py')):
  ast.parse(p.read_text());sources[str(p.relative_to(workspace))]=p.read_bytes()
source_analysis=workspace/'exports/lymescope_ospc_analysis_v0.1.0.tar.gz';completed=source_analysis.read_bytes();assert sha(completed)=='deae2140d0dc040169c71c0e7a1aa364ea80228ca08454a2507056b2ea8e0527'
frozen_path=workspace/'exports/lymescope_ospc_handoff_v0.1.0.tar.gz';frozen=frozen_path.read_bytes();assert sha(frozen)=='1ce0fff5a1b8d7d24ed6d70844f798484ac81231bcf2350ddcd8f6551ec1fa0f'
files={};prefix='lymescope_ospc_analysis_v0.1.0/'
with tarfile.open(fileobj=io.BytesIO(completed),mode='r:gz') as t:
 for line in t.extractfile(prefix+'SHA256SUMS').read().decode().splitlines():
  h,rel=line.split('  ',1);p=P(rel);assert not p.is_absolute() and '..' not in p.parts
  b=t.extractfile(prefix+rel).read();assert sha(b)==h;files['analysis/'+rel]=b
 files['analysis/SHA256SUMS']=t.extractfile(prefix+'SHA256SUMS').read()
# Cross-check the current completed directory is still exactly the verified result bytes.
result_dir=workspace/'analysis/ospc_comparison_v0.1.0/results_v0.1.0'
for rel,b in files.items():assert (result_dir/P(rel).relative_to('analysis')).read_bytes()==b
files.update(sources)
files['frozen/'+frozen_path.name]=frozen
files['frozen/'+frozen_path.name+'.sha256']=(sha(frozen)+'  '+frozen_path.name+'\n').encode()
files['provenance/runtime_inventory.json']=(workspace/'runtime_inventory.json').read_bytes()
files['provenance/process_snapshot.json']=(workspace/'exports/checkpoint_process_snapshot_before.json').read_bytes()
versions={}
for name_,cmd in [('python',[sys.executable,'--version']),('gcc',['gcc','--version']),('make',['make','--version']),('mafft',[str(workspace/'tools/mafft-7.525/bin/mafft'),'--version'])]:
 p=subprocess.run(cmd,capture_output=True,text=True,check=True);versions[name_]={'command':cmd,'output':p.stdout+p.stderr}
files['provenance/tool_versions.json']=(json.dumps(versions,indent=2)+'\n').encode()
readme='''# LymeScope source-and-analysis checkpoint v0.1.0

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
python3 scripts/reproduce_checkpoint_analysis.py \
  --mafft /absolute/path/to/mafft \
  --output /absolute/path/to/a/new-empty-output-directory
```

The replay refuses an existing output directory, runs --amino --localpair --maxiterate 1000 --thread 1 --inputorder, preserves identifiers/native input sequences, recomputes column statistics and the verified 1GGQ mapping, and compares alignment/statistics/mapping with the saved baseline. Differences stop the replay rather than labeling it equivalent. Successful replay writes reproduction_validation.json and an offline index.html. Reproduced numeric arrays must match before the original summary/display schema is reused; original methods remain as baseline provenance and the new command/time are recorded separately. Different builds/platforms may produce alignment differences requiring review. The saved original aligned FASTA hash includes descriptions/formatting; replay equality checks the parsed identifier/order/sequence arrays and numeric results, not just formatting.

## Running work / physical move

The recorded host check found no MAFFT/compiler/build processes or recognized project analysis scripts running. This is a point-in-time observation, not a shutdown or guarantee about unrelated processes. Final status is reported separately after checkpoint creation. No unrelated processes were killed; the Spark was not rebooted or shut down. Arrange physical movement/power handling yourself.
'''
files['README_CHECKPOINT.md']=readme.encode()
# Place original orchestration source in a distinct history subtree to avoid collision
# with completed analysis/source; the paths above are explicit and all are text scripts.
created=datetime.datetime.now(datetime.timezone.utc).isoformat()
metadata={'version':'v0.1.0','created_utc':created,'scope':'PERSONAL Spark source plus completed OspC baseline','completed_analysis_archive_sha256':sha(completed),'frozen_input_archive_sha256':sha(frozen),'completed_analysis_status':'30 sequences; 218 columns; 162 observed 1GGQ residues mapped; 11 saved passing tests','analysis_still_running_at_recorded_check':False,'snapshot_policy':'Verified immutable completed archive; current result bytes cross-checked; source bytes captured once and rechecked after packaging. No alignment or build restarted.','exclusions':['credentials','agent/config dot directories','transcripts','model weights','environments','download caches','compiled tool trees'],'files':[{'path':rel,'bytes':len(b),'sha256':sha(b)} for rel,b in sorted(files.items())]}
files['CHECKPOINT_MANIFEST.json']=(json.dumps(metadata,indent=2)+'\n').encode()
files['SHA256SUMS']=''.join(sha(b)+'  '+rel+'\n' for rel,b in sorted(files.items())).encode()
# Exclusive staging and archive creation; all paths are from this explicit allowlist.
stage.mkdir()
for rel,b in files.items():
 p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
with archive.open('xb') as f:
 with tarfile.open(fileobj=f,mode='w:gz') as t:
  for rel in sorted(files):t.add(stage/rel,arcname=stage.name+'/'+rel,recursive=False)
# Reject any source/result change during snapshot creation.
for rel,b in sources.items():assert (workspace/rel).read_bytes()==b,'Source changed while snapshotting: '+rel
assert source_analysis.read_bytes()==completed and frozen_path.read_bytes()==frozen
for rel,b in files.items():
 if rel.startswith('analysis/') and not rel.startswith('analysis/ospc_comparison_v0.1.0/'):
  original=result_dir/P(rel).relative_to('analysis')
  if original.is_file():assert original.read_bytes()==b,'Completed result changed: '+rel
with tarfile.open(archive) as t:
 names=t.getnames();assert len(names)==len(files)
 for rel,b in files.items():assert t.extractfile(stage.name+'/'+rel).read()==b
h=sha(archive.read_bytes())
with P(str(archive)+'.sha256').open('x') as f:f.write(h+'  '+archive.name+'\n')
receipt={'path':str(archive),'bytes':archive.stat().st_size,'sha256':h,'file_count':len(files),'stable_snapshot_verified':True,'input_archive_unchanged':True,'transfer_status':'NOT TRANSFERRED','publication_status':'No GitHub repository, branch or push; laptop owns publication'}
with P(str(archive)+'.receipt.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt,indent=2))
