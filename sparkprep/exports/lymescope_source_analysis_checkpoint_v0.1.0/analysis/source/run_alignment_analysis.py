"""Continue the existing prealignment task; fail rather than overwrite any completed run."""
import pathlib,json,csv,subprocess,os,hashlib,datetime,shutil,time,collections
from baseline import read_fasta,column_stats,reference_residues,map_columns,cif_rows,THREE
from cif_reader import parse_cif
P=pathlib.Path;root=P(__file__).resolve().parent;workspace=root.parents[1];state=json.loads((root/'analysis_state.json').read_text());paths=state['manifest_paths'];frozen=root/'frozen_inputs';out=root/'results_v0.1.0';out.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(P(p).read_bytes()).hexdigest()
def dump(name,obj):(out/name).write_text(json.dumps(obj,indent=2,allow_nan=False)+'\n')
def tsv(name,rows):
 with open(out/name,'x') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
archive=P(state['frozen_archive']);assert sha(archive)==state['frozen_archive_sha256']
manifest=json.load(open(frozen/'source_manifest.json'))
for a in manifest['artifacts']:
 assert sha(frozen/a['path'])==a['sha256'] and (frozen/a['path']).stat().st_size==a['bytes']
shutil.copytree(frozen,out/'inputs')
shutil.copyfile(root/'runtime_inventory_personal_spark.json',out/'runtime_inventory_personal_spark.json')
(out/'source').mkdir()
for name in ['baseline.py','cif_reader.py','test_baseline.py','inspect_reference.py','run_alignment_analysis.py']:
 shutil.copyfile(root/name,out/'source'/name)
shutil.copyfile(root/'panel_scope.json',out/'panel_scope.json');shutil.copyfile(root/'reference_inspection.json',out/'reference_inspection.json')
tool=workspace/'tools/mafft-7.525';exe=tool/'bin/mafft';env=os.environ.copy();env.pop('MAFFT_BINARIES',None);env['TMPDIR']=str(tool/'tmp');env['MAFFT_TMPDIR']=str(tool/'tmp')
version=subprocess.run([str(exe),'--version'],env=env,capture_output=True,text=True,check=True);toolversion=(version.stdout+version.stderr).strip();assert toolversion.startswith('v7.525 ')
(out/'tool_provenance').mkdir()
for file in ['build.log','install.log','install_dry_run.log','Makefile.original']:
 shutil.copyfile(tool/'logs'/file,out/'tool_provenance'/file)
core=tool/'source/mafft-7.525-without-extensions/core'
shutil.copyfile(core/'Makefile',out/'tool_provenance/Makefile.configured');shutil.copyfile(core.parent/'license',out/'tool_provenance/MAFFT_LICENSE')
source_archive=tool/'source/mafft-7.525-without-extensions-src.tgz'
provenance={'official_source_url':'https://mafft.cbrc.jp/alignment/software/mafft-7.525-without-extensions-src.tgz','retrieved_utc':datetime.datetime.fromtimestamp(source_archive.stat().st_mtime,datetime.timezone.utc).isoformat(),'source_archive_bytes':source_archive.stat().st_size,'source_archive_sha256':sha(source_archive),'installation_prefix':str(tool),'executable':str(exe),'version':toolversion,'version_command':[str(exe),'--version'],'executable_sha256':sha(exe),'build_command':['make','-j2'],'install_command':['make','install'],'build_cwd':str(core),'configured_makefile_sha256':sha(core/'Makefile'),'installed_files':[{'path':str(p.relative_to(tool)),'bytes':p.stat().st_size,'sha256':sha(p)} for folder in ['bin','libexec','share'] for p in sorted((tool/folder).rglob('*')) if p.is_file()],'environment_overrides':{'MAFFT_BINARIES':'unset for subprocess only','TMPDIR':env['TMPDIR'],'MAFFT_TMPDIR':env['MAFFT_TMPDIR']},'no_global_environment_changes':True}
dump('tool_provenance.json',provenance)
# Sanity fixture validates identifiers, amino acid preservation, and known trivial alignment.
san=out/'sanity_input.fasta';san.write_text('>sanity_A\nACDEFGHIKLMNPQRSTVWY\n>sanity_B\nACDEFGHIKLMNPQRSTVWY\n>sanity_C\nACDEFGHIKLMNPQRSTVWY\n')
params=['--amino','--localpair','--maxiterate','1000','--thread','1','--inputorder']
cmd=[str(exe),*params,str(san)]
v=subprocess.run(cmd,env=env,cwd=out,capture_output=True,text=True,timeout=60);(out/'sanity_aligned.fasta').write_text(v.stdout);(out/'sanity_stderr.log').write_text(v.stderr);assert v.returncode==0
sanseq=read_fasta(out/'sanity_aligned.fasta');assert sanseq==read_fasta(san)
dump('sanity_check.json',{'command':cmd,'returncode':v.returncode,'passed':True,'identical_sequence_fixture':'3 sequences, 20 standard amino acids each; identifiers and exact sequences preserved','input_sha256':sha(san),'output_sha256':sha(out/'sanity_aligned.fasta')})
infile=(out/'inputs'/paths['input_sequences.fasta']).resolve();original=read_fasta(infile);metadata=list(csv.DictReader(open(out/'inputs'/paths['sequence_metadata.tsv']),delimiter='\t'));assert list(original)==[r['accession'] for r in metadata];assert len(original)==30
cmd=[str(exe),*params,str(infile)];start=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic()
with open(out/'aligned.fasta','x') as stdout,open(out/'mafft_stderr.log','x') as stderr:
 v=subprocess.run(cmd,env=env,cwd=out,stdout=stdout,stderr=stderr,timeout=300)
elapsed=time.monotonic()-t;assert v.returncode==0,f'MAFFT failed: {v.returncode}'
aligned=read_fasta(out/'aligned.fasta');assert list(aligned)==list(original);assert len({len(s) for s in aligned.values()})==1
for a,s in aligned.items():assert s.replace('-','')==original[a],a
columns=len(next(iter(aligned.values())));stats=[dict(alignment_column=i+1,**column_stats(s[i] for s in aligned.values())) for i in range(columns)]
assert all(r['contributing_sequences']+r['gap_count']+r['ambiguous_missing_count']==30 for r in stats)
tsv('conservation_coverage.tsv',stats)
c=parse_cif(out/'inputs'/paths['1GGQ.cif']);res=reference_residues(c,original['Q07337']);mapping=map_columns(aligned['Q07337'],res,stats);assert len(mapping)==columns
assert sum(r['status']=='observed' for r in mapping)==162
mapped=[r for r in mapping if r['status']=='observed'];assert len({(r['auth_chain'],r['auth_residue_number'],r['insertion_code']) for r in mapped})==162
assert all(r['structure_modal_fraction'] is None and r['structure_coverage'] is None for r in mapping if r['status']!='observed')
tsv('alignment_to_structure.tsv',mapping)
bylabel={r['label_seq_id']:r for r in mapping if r['label_seq_id'] is not None}
for r in res:
 m=bylabel.get(r['label_seq_id']);r.update(alignment_column=m['alignment_column'] if m else None,modal_fraction=m['structure_modal_fraction'] if m else None,coverage=m['structure_coverage'] if m else None)
dump('structure_residues.json',res);tsv('structure_residues.tsv',[{k:v for k,v in r.items() if k!='xyz'} for r in res])
# Independently verify secondary-reference observation category, not a second scoring map.
c2=parse_cif(out/'inputs'/paths['1G5Z.cif']);scheme=[r for r in cif_rows(c2,'_pdbx_poly_seq_scheme') if r['asym_id']=='A'];s2=''.join(THREE[r['mon_id']] for r in scheme)
ca={int(r['label_seq_id']) for r in cif_rows(c2,'_atom_site') if r['label_asym_id']=='A' and r['label_atom_id']=='CA' and r['pdbx_PDB_model_num']=='1' and float(r['occupancy'])>0};assert len(scheme)==len(ca)==164;assert ca==set(range(1,165))
matching=[{'accession':a,'start_1based':s.find(s2)+1,'end_1based':s.find(s2)+len(s2)} for a,s in original.items() if s2 in s];assert matching==[{'accession':'Q44717','start_1based':40,'end_1based':203}]
dump('secondary_reference_check.json',{'pdb_id':'1G5Z','chain':'A','scheme_residues':len(scheme),'observed_CA_residues':len(ca),'unobserved_category_present':any(k.startswith('_pdbx_unobs_or_zero_occ_residues.') for k in c2),'empty_list_explanation':'The prior [] was an absent optional unobserved-residue category, not missing atom coordinates. All 164 scheme residues have positive-occupancy CA atoms in model 1.','exact_construct_matches':matching,'historical_CIF_accession':'O31117 retained as supplied; no invented renumbering','scores_mapped':False,'reason':'First scored reference is 1GGQ chain A.'})
seqvalidation=[{'accession':a,'original_length':len(original[a]),'aligned_length':len(s),'gap_count':s.count('-'),'original_sequence_sha256':hashlib.sha256(original[a].encode()).hexdigest(),'ungapped_aligned_sequence_sha256':hashlib.sha256(s.replace('-','').encode()).hexdigest(),'identifier_preserved':True,'sequence_preserved':True} for a,s in aligned.items()];tsv('sequence_validation.tsv',seqvalidation)
dump('alignment_run.json',{'started_utc':start,'elapsed_seconds':elapsed,'returncode':v.returncode,'command':cmd,'parameters':params,'tool_version':toolversion,'input_fasta_sha256':sha(infile),'frozen_archive_sha256':sha(archive),'output_aligned_fasta_sha256':sha(out/'aligned.fasta'),'sequence_count':len(aligned),'alignment_columns':columns,'included_accessions':list(aligned),'identifier_order_preserved':True,'ungapped_sequences_equal_inputs':True,'CPU_only':True,'MAFFT_strategy':'L-INS-i (--localpair --maxiterate 1000); amino acid; 1 thread'})
summary={'sequence_count':30,'alignment_columns':columns,'fully_observed_columns':sum(r['contributing_sequences']==30 for r in stats),'columns_with_gaps':sum(r['gap_count']>0 for r in stats),'ambiguous_missing_residues':sum(r['ambiguous_missing_count'] for r in stats),'undefined_columns':sum(r['modal_fraction'] is None for r in stats),'all_observed_residues_identical_columns':sum(r['modal_fraction']==1 for r in stats),'fully_covered_identical_columns':sum(r['modal_fraction']==1 and r['contributing_sequences']==30 for r in stats),'coverage_min':min(r['coverage'] for r in stats),'mean_modal_fraction':sum(r['modal_fraction'] for r in stats if r['modal_fraction'] is not None)/sum(r['modal_fraction'] is not None for r in stats),'observed_structure_residues_scored':len(mapped),'structure_mapping_status_counts':dict(collections.Counter(r['status'] for r in mapping)),'interpretation':'Conserved within this analyzed panel only; unweighted, alignment-dependent descriptive baseline. Not universally representative or evidence of protection.'}
dump('summary.json',summary)
viewer={'status':'measured_alignment_baseline','summary':summary,'scope':json.loads((out/'panel_scope.json').read_text()),'alignment_run':json.loads((out/'alignment_run.json').read_text()),'sequences':[{'accession':a,'aligned_sequence':s,'metadata':metadata[i]} for i,(a,s) in enumerate(aligned.items())],'columns':stats,'mapping':mapping,'structure_residues':res,'coordinate_label':'PRE-EXISTING experimental 1GGQ chain A, model 1; C-alpha trace, not newly generated folding','score_definition':'Modal standard-amino-acid count / all observed standard residues; coverage is standard residues / 30; undefined fractions are null; missing structure positions unscored. Experimental B-factors are not used.'}
dump('viewer_data.json',viewer)
assert sha(archive)==state['frozen_archive_sha256']
print(json.dumps(summary,indent=2));print('Saved scientific results:',out)
