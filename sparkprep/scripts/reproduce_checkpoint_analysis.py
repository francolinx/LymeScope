"""Portable offline replay for the source-and-analysis checkpoint. Not run during checkpointing."""
import argparse,pathlib,sys,json,csv,hashlib,subprocess,os,shutil,datetime
P=pathlib.Path
parser=argparse.ArgumentParser();parser.add_argument('--mafft',required=True,type=P);parser.add_argument('--output',required=True,type=P);parser.add_argument('--checkpoint',type=P,default=P(__file__).resolve().parent.parent);args=parser.parse_args()
checkpoint=args.checkpoint.resolve();prior=checkpoint/'analysis';sys.path.insert(0,str(prior/'source'))
from baseline import read_fasta,column_stats,reference_residues,map_columns
from cif_reader import parse_cif
exe=args.mafft.resolve();version=subprocess.run([str(exe),'--version'],capture_output=True,text=True,check=True);v=(version.stdout+version.stderr).strip()
if not v.startswith('v7.525 '):raise SystemExit('For exact replay, MAFFT 7.525 is required; found '+v)
out=args.output.resolve();out.mkdir(exist_ok=False);(out/'tmp').mkdir();env=os.environ.copy();env.pop('MAFFT_BINARIES',None);env['TMPDIR']=str(out/'tmp');env['MAFFT_TMPDIR']=str(out/'tmp')
shutil.copytree(prior/'inputs',out/'inputs');shutil.copyfile(prior/'panel_scope.json',out/'panel_scope.json');shutil.copytree(prior/'source',out/'source',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
infile=out/'inputs/input_sequences.fasta';params=['--amino','--localpair','--maxiterate','1000','--thread','1','--inputorder'];cmd=[str(exe),*params,str(infile)]
with (out/'aligned.fasta').open('x') as stdout,(out/'mafft_stderr.log').open('x') as stderr:subprocess.run(cmd,stdout=stdout,stderr=stderr,cwd=out,env=env,check=True,timeout=300)
original=read_fasta(infile);aligned=read_fasta(out/'aligned.fasta');assert list(original)==list(aligned) and len(set(map(len,aligned.values())))==1
assert all(aligned[a].replace('-','')==s for a,s in original.items())
columns=[dict(alignment_column=i+1,**column_stats(s[i] for s in aligned.values())) for i in range(len(next(iter(aligned.values()))))]
residues=reference_residues(parse_cif(out/'inputs/reference_structures/1GGQ.cif'),original['Q07337']);mapping=map_columns(aligned['Q07337'],residues,columns)
for name,rows in [('conservation_coverage.tsv',columns),('alignment_to_structure.tsv',mapping)]:
 with (out/name).open('x') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
bylabel={r['label_seq_id']:r for r in mapping if r['label_seq_id'] is not None}
for r in residues:
 m=bylabel.get(r['label_seq_id']);r.update(alignment_column=m['alignment_column'] if m else None,modal_fraction=m['structure_modal_fraction'] if m else None,coverage=m['structure_coverage'] if m else None)
# Reuse display schema and metadata, replacing every computed quantity.
data=json.loads((prior/'viewer_data.json').read_text());data['columns']=columns;data['mapping']=mapping;data['structure_residues']=residues
for row in data['sequences']:row['aligned_sequence']=aligned[row['accession']]
prior_alignment=read_fasta(prior/'aligned.fasta');same_alignment=aligned==prior_alignment
same_stats=columns==json.loads((prior/'viewer_data.json').read_text())['columns'];same_mapping=mapping==json.loads((prior/'viewer_data.json').read_text())['mapping']
if not (same_alignment and same_stats and same_mapping):raise SystemExit('Replay differs from the saved baseline; raw replay files preserved. No viewer labeled equivalent was written. Investigate MAFFT/platform differences.')
# Same measured arrays justify retaining saved summary, with replay execution recorded separately.
(out/'viewer_data.json').write_text(json.dumps(data,indent=2)+'\n');(out/'structure_residues.json').write_text(json.dumps(residues,indent=2)+'\n')
flat=[{k:v for k,v in r.items() if k!='xyz'} for r in residues]
with (out/'structure_residues.tsv').open('x') as f:
 w=csv.DictWriter(f,fieldnames=list(flat[0]),delimiter='\t');w.writeheader();w.writerows(flat)
shutil.copyfile(prior/'METHOD_AND_LIMITATIONS.md',out/'METHOD_AND_LIMITATIONS.md')
shutil.copyfile(prior/'secondary_reference_check.json',out/'secondary_reference_check.json')
subprocess.run([sys.executable,str(out/'source/build_view.py')],check=True)
record={'replayed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd,'tool_version':v,'input_sha256':hashlib.sha256(infile.read_bytes()).hexdigest(),'aligned_fasta_sha256':hashlib.sha256((out/'aligned.fasta').read_bytes()).hexdigest(),'aligned_sequences_match_saved':same_alignment,'statistics_match_saved':same_stats,'mapping_matches_saved':same_mapping,'scope':'Offline CPU replay; no model, download or cluster access'}
(out/'reproduction_validation.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2))
