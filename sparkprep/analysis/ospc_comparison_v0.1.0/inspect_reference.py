import pathlib,json,csv
from baseline import read_fasta,reference_residues,cif_rows
from cif_reader import parse_cif
P=pathlib.Path;root=P(__file__).resolve().parent;state=json.loads((root/'analysis_state.json').read_text());paths=state['manifest_paths'];inp=root/'frozen_inputs';seq=read_fasta(inp/paths['input_sequences.fasta']);inspections=[]
for code in ['1GGQ','1G5Z']:
 c=parse_cif(inp/paths[code+'.cif']);d=json.load(open(inp/paths[code+'.json']))
 inspections.append({'pdb_id':code,'title':d['struct']['title'],'resolution_A':d['rcsb_entry_info']['resolution_combined'],'source':'PRE-EXISTING experimental X-ray coordinates, not project-generated folding','reference_ranges':cif_rows(c,'_struct_ref_seq'),'assembly_definitions':cif_rows(c,'_pdbx_struct_assembly'),'unobserved_residues':cif_rows(c,'_pdbx_unobs_or_zero_occ_residues')})
c=parse_cif(inp/paths['1GGQ.cif']);res=reference_residues(c,seq['Q07337']);assert len(res)==174;assert sum(r['has_observed_CA'] for r in res)==162
assert sum(r['listed_unobserved'] for r in res)==12
assert all(r['has_observed_CA']!=r['listed_unobserved'] for r in res)
assert len({(r['auth_chain'],r['auth_residue_number'],r['insertion_code']) for r in res})==174
(root/'reference_residues.json').write_text(json.dumps(res,indent=2)+'\n')
flat=[{k:v for k,v in r.items() if k!='xyz'} for r in res]
with open(root/'reference_residues.tsv','w') as f:
 w=csv.DictWriter(f,fieldnames=list(flat[0]),delimiter='\t');w.writeheader();w.writerows(flat)
summary={'selected':'1GGQ label/auth chain A; model 1; positive-occupancy CA atoms','reason':'B31 reference Q07337 is present in the frozen panel. CIF native positions 38–210 match all 173 residues exactly; additional initiating methionine is excluded from native mapping. No alignment inference is required for this deposited correspondence. 1G5Z is retained as an alternative but its historical accession mapping is not used.','construct_residues':174,'native_residues_verified':173,'observed_CA_residues':162,'unobserved_residues':12,'native_unobserved_positions':[r['panel_sequence_position'] for r in res if not r['has_observed_CA'] and r['panel_sequence_position'] is not None],'construct_extra_labels':[r['label_seq_id'] for r in res if r['panel_sequence_position'] is None],'observed_auth_range':[r['auth_residue_number'] for r in res if r['has_observed_CA']][::161],'nonblank_insertion_codes':[r['insertion_code'] for r in res if r['insertion_code']],'mapping_validation':'All observed CA atom residue names, author chains/numbers and insertion codes match the polymer scheme. Unobserved list and absence of CA agree for every construct residue. No B-factors used as confidence.','inspected_entries':inspections}
(root/'reference_inspection.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k!='inspected_entries'},indent=2))
