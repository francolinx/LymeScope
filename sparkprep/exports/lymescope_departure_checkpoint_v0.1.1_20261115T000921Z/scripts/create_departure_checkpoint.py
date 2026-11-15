"""Reuse the verified completed checkpoint; add departure records, never analysis reruns."""
import pathlib,json,hashlib,tarfile,io,datetime,re,ast
P=pathlib.Path;root=P(__file__).resolve().parent.parent
now=datetime.datetime.now(datetime.timezone.utc);stamp=now.strftime('%Y%m%dT%H%M%SZ');name='lymescope_departure_checkpoint_v0.1.1_'+stamp;stage=root/'exports'/name;archive=root/'exports'/(name+'.tar.gz')
def sha(b):return hashlib.sha256(b).hexdigest()
prior=root/'exports/lymescope_source_analysis_checkpoint_v0.1.0.tar.gz';prior_bytes=prior.read_bytes();assert sha(prior_bytes)=='eb06c6e6f4b9ac6640519f4a7d9b59ab98e48830e08d43e091b43b6155fb990a'
frozen=root/'exports/lymescope_ospc_handoff_v0.1.0.tar.gz';frozen_bytes=frozen.read_bytes();frozen_hash=sha(frozen_bytes);assert frozen_hash=='1ce0fff5a1b8d7d24ed6d70844f798484ac81231bcf2350ddcd8f6551ec1fa0f';assert len(frozen_bytes)==264149
prefix='lymescope_source_analysis_checkpoint_v0.1.0/';files={}
with tarfile.open(fileobj=io.BytesIO(prior_bytes),mode='r:gz') as t:
 for line in t.extractfile(prefix+'SHA256SUMS').read().decode().splitlines():
  h,rel=line.split('  ',1);p=P(rel);assert not p.is_absolute() and '..' not in p.parts
  b=t.extractfile(prefix+rel).read();assert sha(b)==h
  if not rel.startswith('frozen/') and rel not in ['CHECKPOINT_MANIFEST.json','README_CHECKPOINT.md']:files[rel]=b
# Existing analysis artifacts are reused byte-for-byte. Refresh only explicitly named project source.
newsource={}
for p in sorted((root/'scripts').glob('*.py')):
 b=p.read_bytes();ast.parse(b);rel=str(p.relative_to(root));files[rel]=b;newsource[rel]=b
activity=(root/'exports/departure_activity_before.json').read_bytes();activity_obj=json.loads(activity)
assert not activity_obj['active_build_or_aligner_processes'] and not activity_obj['recognized_project_script_processes'] and not activity_obj['processes_with_open_writable_workspace_files']
files['provenance/departure_activity_before.json']=activity
files['provenance/git_status.json']=(json.dumps({'observed_utc':now.isoformat(),'workspace':str(root),'git_repository_detected':False,'observations':['Visible .git directory empty','git rev-parse failed: not a git repository'],'action':'No reset, delete, init, commit or push. No relevant local Git history was visible; existing laptop repository remains authoritative.'},indent=2)+'\n').encode()
files['provenance/frozen_input_handoff.json']=(json.dumps({'path':str(frozen),'bytes':len(frozen_bytes),'sha256':frozen_hash,'bundled':False,'reason':'Original retained separately; departure archive excludes old export archives. Actual scientific input files/manifests remain under analysis/inputs/.'},indent=2)+'\n').encode()
resume=f'''# Resume on PERSONAL Spark

Checkpoint {name}, prepared {now.isoformat()} on spark-6771 as darkstar90. Existing GitHub repository: https://github.com/francolinx/LymeScope. The Windows laptop worker owns repository import/publication. No GitHub publication or laptop transfer is assumed or was performed here.

## What works and what is complete

MAFFT v7.525 (2024/Mar/13) compiled from the official without-extensions source using existing gcc/make, with the entire installation under tools/mafft-7.525. The version/sanity checks passed. The actual frozen 30-sequence panel produced 218 alignment columns. Identifiers and ungapped sequences exactly match the input. 202 columns have full coverage; 76 are identical across the full analyzed panel. 16 columns contain gaps. Column modal conservation and coverage are saved separately. First-reference mapping scores 162 observed residues of pre-existing experimental 1GGQ chain A, with unmapped/unobserved positions unscored. Eleven recorded tests passed. The offline viewer rendered successfully.

Completed original workspace outputs:
`{root}/analysis/ospc_comparison_v0.1.0/results_v0.1.0/`

The previous prealignment files under its parent are historical; do not mistake their blocked-state reports for the completed result. In this checkpoint the completed result is under `analysis/`, including inputs/source_manifest.json, aligned.fasta, conservation_coverage.tsv, alignment_to_structure.tsv, structure_residues.*, viewer_data.json, index.html, scientific methods, attribution and tests.

## Unfinished work and blockers

No pending MAFFT installation, alignment or conservation/mapping task is known. No second-reference score map was generated. 1G5Z was independently verified: its earlier empty list was an absent optional unobserved-residue category; all 164 Cα residues are observed and the construct matches Q44717 positions 40–203. The portable replay entry point was syntax-checked but not run at departure, to avoid restarting/duplicating analysis.

No GPU model experiment, new fold, antigen ranking, universal representativeness or protection claim has been produced. Personal-Spark CUDA remained unavailable in the recorded inventory; three existing PyTorch environments could import torch but could not initialize CUDA, and Docker image inventory was blocked by socket permissions. These are not event-cluster results. No model or environment changes are authorized by this checkpoint.

Five primary strain fields remain unresolved/missing; 25 nonblank strain labels do not establish 25 distinct biological strains. Full methods/limitations are in analysis/METHOD_AND_LIMITATIONS.md. The full B31 catalog and full candidate pool are outside this compact checkpoint; the actual analyzed inputs and their provenance are included.

## Exact commands in this existing workspace

View the completed result by opening this file in a browser (no server):
`{root}/analysis/ospc_comparison_v0.1.0/results_v0.1.0/index.html`

Check saved results without realigning:

```bash
cd {root}/analysis/ospc_comparison_v0.1.0/results_v0.1.0
sha256sum -c SHA256SUMS
cd source
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest -v test_baseline test_results
```

Verify the existing MAFFT executable:

```bash
{root}/tools/mafft-7.525/bin/mafft --version
```

If intentionally resuming computation later, replay into a NEW output directory, preserving all existing results:

```bash
cd {root}
/usr/bin/python3 scripts/reproduce_checkpoint_analysis.py \\
  --checkpoint {stage} \\
  --mafft {root}/tools/mafft-7.525/bin/mafft \\
  --output {root}/analysis/replay_departure_{stamp}
```

This uses the checkpoint's actual input FASTA/CIFs, requires MAFFT 7.525, refuses an existing output directory, repeats the recorded CPU-only L-INS-i command, and compares parsed sequences/statistics/mapping with the saved baseline before writing an equivalent viewer. It performs no downloads/installations or GPU work. Do not run the historical export/freeze scripts just to view data; several intentionally refuse existing version names and expect the original workspace layout.

## Required paths and offline dependencies

- Python standard library: /usr/bin/python3 (Python 3.12.3 in recorded runtime); no new packages needed for baseline calculations/tests.
- MAFFT: {root}/tools/mafft-7.525/bin/mafft; helper files reside under that prefix's libexec/mafft. Invoke by full path; no global PATH/shell-profile changes.
- Build/source/version/hash information and gcc/make version strings are recorded in analysis/tool_provenance.json, analysis/tool_provenance/ and provenance/tool_versions.json. Compiled tools, environments and source-download caches are deliberately excluded.
- Offline viewing needs only a browser capable of JavaScript and Canvas. analysis/index.html embeds the measured data; no node_modules, CDN, external assets, local web server or network access is required. Text tables remain directly readable.

## Frozen input, handoff, history and activity

Keep the original input archive separately, unchanged:
`{frozen}`
Bytes: {len(frozen_bytes)}
SHA256: {frozen_hash}

No old export archives, recursive exports tree, .git, credentials, agent transcripts, weights, caches or environments are included in this departure checkpoint. The visible workspace .git directory is empty and Git did not recognize a repository; no relevant local history was visible. Nothing was reset or deleted. Preserve the laptop's existing Git history and root files when importing into its separate sparkprep/ directory.

The recorded host activity check found no active compiler/MAFFT/build processes, recognized project scripts or inspectable open writable workspace files. Some system process descriptors were unreadable; the snapshot is point-in-time, not a guarantee about all unrelated processes. No tasks were killed and no reboot/shutdown was performed. A final check is reported separately after packaging. The Spark is not automatically safe to unplug solely because an analysis task is idle; physical movement/power handling stays with the operator.
'''
# Exclusive workspace resume document, with timestamp if a prior departure document exists.
resume_path=root/'RESUME_ON_SPARK.md'
if resume_path.exists():
 if resume_path.read_bytes()!=resume.encode():resume_path=root/('RESUME_ON_SPARK_'+stamp+'.md')
with resume_path.open('xb') as f:f.write(resume.encode())
files['RESUME_ON_SPARK.md']=resume.encode()
files['README_CHECKPOINT.md']=f'''# LymeScope departure checkpoint v0.1.1

Prepared {now.isoformat()}; verified/reused prior source checkpoint SHA256 eb06c6e6f4b9ac6640519f4a7d9b59ab98e48830e08d43e091b43b6155fb990a. No scientific analysis/build was restarted. See RESUME_ON_SPARK.md for complete status and commands.

Open analysis/index.html directly for the completed measured comparison. analysis/ contains 30-sequence alignment, per-column conservation/coverage, 1GGQ mapping, reference coordinates/attribution, metadata, manifests, methods, tests and source. scripts/ and analysis/ospc_comparison_v0.1.0/*.py preserve project source/history. provenance/ retains runtime/tool versions, activity, Git observations and separate frozen-input identity.

The frozen input archive is NOT embedded; retain/copy it separately using provenance/frozen_input_handoff.json. Old archives, recursive exports trees, compiled tool trees, credentials, conversations, weights, caches, environments, node_modules and .git are excluded. Heuristic secret/path scan and isolated extraction validation are recorded; public-release review remains with the laptop worker.

Verify all files with `sha256sum -c SHA256SUMS` from this extracted directory. No transfer or publication occurred.
'''.encode()
# File/path allowlist plus high-confidence secret-pattern scan; never print matched values.
for rel in files:
 parts=P(rel).parts
 assert not any(p in {'.git','.aws','.ssh','.codex','.agents','node_modules','__pycache__','.venv','venv','exports','tools'} for p in parts),rel
 assert not rel.endswith(('.tar.gz','.tgz','.zip','.pyc','.safetensors','.pt','.pth','.pem','.key')),rel
patterns={'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----','aws_access_key':rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b','github_token':rb'\bgh[pousr]_[A-Za-z0-9]{30,}\b','github_fine_grained_token':rb'github_pat_[A-Za-z0-9_]{40,}','slack_token':rb'\bxox[baprs]-[A-Za-z0-9-]{20,}','literal_secret_assignment':rb'''(?i)\b(?:api_key|api_token|access_token|client_secret|password)\b\s*[:=]\s*["'][A-Za-z0-9_+/=-]{12,}["']'''}
findings=[]
for rel,b in files.items():
 for label,pattern in patterns.items():
  if re.search(pattern,b):findings.append({'path':rel,'rule':label})
assert not findings,findings
scan={'checked_utc':now.isoformat(),'files_scanned':len(files),'path_policy':'Explicit verified result/source allowlist; no excluded directories or archive/weight/key extensions.','content_rules':list(patterns),'findings':findings,'limitations':'Heuristic path/content check, not proof that no sensitive information could exist. No excluded credentials/configuration files were opened; only selected payload scanned. Review for public release remains required.'}
files['SECRET_SCAN.json']=(json.dumps(scan,indent=2)+'\n').encode()
files['CONTENTS.txt']=''.join(f'{len(b):>10}  {rel}\n' for rel,b in sorted(files.items())).encode()
metadata={'version':'v0.1.1','timestamp_utc':now.isoformat(),'status':'Stable departure checkpoint of completed scientific outputs; no analysis rerun','reused_checkpoint_sha256':sha(prior_bytes),'frozen_input_retained_separately':{'path':str(frozen),'bytes':len(frozen_bytes),'sha256':frozen_hash},'excluded_embedded_old_archives':True,'unfinished':'See RESUME_ON_SPARK.md; no pending alignment/build. GPU unavailable in recorded inventory; no model work authorized.','files':[{'path':rel,'bytes':len(b),'sha256':sha(b)} for rel,b in sorted(files.items())]}
files['CHECKPOINT_MANIFEST.json']=(json.dumps(metadata,indent=2)+'\n').encode();files['SHA256SUMS']=''.join(sha(b)+'  '+rel+'\n' for rel,b in sorted(files.items())).encode()
assert not stage.exists() and not archive.exists();stage.mkdir()
for rel,b in files.items():p=stage/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
with archive.open('xb') as f:
 with tarfile.open(fileobj=f,mode='w:gz') as t:
  for rel in sorted(files):t.add(stage/rel,arcname=name+'/'+rel,recursive=False)
# Safe extraction into a NEW isolated workspace directory; reject links/devices/traversal.
extract=root/'exports'/('departure_extraction_check_'+stamp);extract.mkdir(exist_ok=False)
with tarfile.open(archive) as t:
 members=t.getmembers();assert len(members)==len(files)
 for m in members:
  pp=P(m.name);assert m.isfile() and not pp.is_absolute() and '..' not in pp.parts and pp.parts[0]==name
  dest=extract/pp;dest.parent.mkdir(parents=True,exist_ok=True)
  with dest.open('xb') as f:f.write(t.extractfile(m).read())
 for rel,b in files.items():assert (extract/name/rel).read_bytes()==b
for rel,b in newsource.items():assert (root/rel).read_bytes()==b,'Source changed during packaging'
assert prior.read_bytes()==prior_bytes and frozen.read_bytes()==frozen_bytes
validation={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'file_count':len(files),'all_file_bytes_and_hashes_match':True,'safe_extraction_directory':str(extract/name),'members_regular_files_only':True,'links_devices_traversal':False,'secret_scan_findings':0,'analysis_rerun':False,'frozen_input_unchanged':True}
with P(str(archive)+'.validation.json').open('x') as f:json.dump(validation,f,indent=2);f.write('\n')
h=sha(archive.read_bytes())
with P(str(archive)+'.sha256').open('x') as f:f.write(h+'  '+archive.name+'\n')
with P(str(archive)+'.contents.txt').open('x') as f:f.write(''.join(f'{len(b):>10}  {rel}\n' for rel,b in sorted(files.items())))
receipt={'path':str(archive),'bytes':archive.stat().st_size,'sha256':h,'file_count':len(files),'safe_extraction_verified':True,'secret_scan_findings':0,'resume_document':str(resume_path),'frozen_input':{'path':str(frozen),'bytes':len(frozen_bytes),'sha256':frozen_hash},'transfer_or_push':'NOT PERFORMED'}
with P(str(archive)+'.receipt.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt,indent=2))
