"""Transparent column statistics and exact deposited-reference correspondence; no alignment algorithm."""
import collections
import pathlib
AA=set('ACDEFGHIKLMNPQRSTVWY')
THREE=dict(zip('ALA CYS ASP GLU PHE GLY HIS ILE LYS LEU MET ASN PRO GLN ARG SER THR VAL TRP TYR'.split(),'ACDEFGHIKLMNPQRSTVWY'))
def read_fasta(path):
 out={};key=None
 for line in pathlib.Path(path).read_text().splitlines():
  line=line.strip()
  if line.startswith('>'):
   key=line[1:].split()[0]
   if key in out:raise ValueError('Duplicate FASTA identifier: '+key)
   out[key]=''
  elif line:
   if key is None:raise ValueError('Sequence before FASTA header')
   out[key]+=line.upper()
 return out

def column_stats(chars):
 chars=list(chars);counts=collections.Counter(c for c in chars if c in AA);valid=sum(counts.values());gaps=sum(c=='-' for c in chars)
 # All tied modes retained; alphabetical first is a deterministic display convention.
 modes=sorted(c for c,n in counts.items() if n==max(counts.values())) if valid else []
 return {'most_frequent_aa':modes[0] if modes else None,'tied_modes':','.join(modes),'modal_fraction':max(counts.values())/valid if valid else None,'contributing_sequences':valid,'gap_count':gaps,'ambiguous_missing_count':len(chars)-valid-gaps,'total_sequences':len(chars),'coverage':valid/len(chars) if chars else None}

def cif_rows(c,category):
 keys=[k for k in c if k.startswith(category+'.')]
 return [dict(zip([k.split('.',1)[1] for k in keys],row)) for row in zip(*(c[k] for k in keys))] if keys else []

def clean_code(s):return '' if s in ['.','?'] else s

def reference_residues(c,sequence,chain='A',accession='Q07337'):
 refs=[r for r in cif_rows(c,'_struct_ref_seq') if r['pdbx_strand_id']==chain and r['pdbx_db_accession']==accession]
 if len(refs)!=1:raise ValueError('Expected exactly one reference range')
 ref=refs[0];lo,hi=int(ref['seq_align_beg']),int(ref['seq_align_end']);native=int(ref['db_align_beg'])
 if hi-lo!=int(ref['db_align_end'])-native:raise ValueError('Reference lengths disagree')
 atoms={}
 for r in cif_rows(c,'_atom_site'):
  if r['label_asym_id']==chain and r['label_atom_id']=='CA' and r['pdbx_PDB_model_num']=='1' and float(r['occupancy'])>0:
   key=int(r['label_seq_id'])
   if key in atoms:raise ValueError('Multiple CA conformers require explicit selection')
   atoms[key]=r
 unobs_rows={int(r['label_seq_id']):r for r in cif_rows(c,'_pdbx_unobs_or_zero_occ_residues') if r['label_asym_id']==chain and r['PDB_model_num']=='1'}
 unobs=set(unobs_rows)
 result=[]
 for r in cif_rows(c,'_pdbx_poly_seq_scheme'):
  if r['asym_id']!=chain:continue
  label=int(r['seq_id']);pos=native+label-lo if lo<=label<=hi else None;aa=THREE.get(r['mon_id'],'X');a=atoms.get(label)
  if pos is not None and sequence[pos-1]!=aa:raise ValueError(f'Reference sequence mismatch at {pos}: {aa} != {sequence[pos-1]}')
  if a and label in unobs:raise ValueError('Observed/unobserved residue contradiction')
  u=unobs_rows.get(label)
  if u and (u['auth_asym_id']!=r['pdb_strand_id'] or u['auth_seq_id']!=r['pdb_seq_num'] or u['auth_comp_id']!=r['mon_id'] or u['label_comp_id']!=r['mon_id'] or clean_code(u['PDB_ins_code'])!=clean_code(r['pdb_ins_code'])):raise ValueError('Unobserved-residue identity or numbering mismatch')
  if a and (a['label_comp_id']!=r['mon_id'] or a['auth_asym_id']!=r['pdb_strand_id'] or a['auth_seq_id']!=r['pdb_seq_num'] or clean_code(a['pdbx_PDB_ins_code'])!=clean_code(r['pdb_ins_code'])):raise ValueError('Atom/scheme residue identity or numbering mismatch')
  result.append({'pdb_id':'1GGQ','label_asym_id':chain,'auth_chain':r['pdb_strand_id'],'label_seq_id':label,'auth_residue_number':r['pdb_seq_num'],'insertion_code':clean_code(r['pdb_ins_code']),'residue_name':r['mon_id'],'aa':aa,'panel_accession':accession,'panel_sequence_position':pos,'has_observed_CA':bool(a),'listed_unobserved':label in unobs,'xyz':[float(a[k]) for k in ['Cartn_x','Cartn_y','Cartn_z']] if a else None,'mapping_status':'construct_extra_unmapped' if pos is None else 'unobserved' if not a else 'observed'})
 return result

def map_columns(aligned_reference,residues,stats):
 bypos={r['panel_sequence_position']:r for r in residues if r['panel_sequence_position'] is not None};pos=0;out=[]
 for col,aa in enumerate(aligned_reference,1):
  if aa!='-':pos+=1
  residue=bypos.get(pos) if aa!='-' else None
  if residue and residue['aa']!=aa:raise ValueError('Aligned residue differs from verified reference')
  status='reference_gap' if aa=='-' else 'outside_construct' if residue is None else residue['mapping_status']
  out.append({'alignment_column':col,'panel_accession':'Q07337','panel_sequence_position':pos if aa!='-' else None,'reference_aa':aa,'pdb_id':'1GGQ','auth_chain':'A','label_seq_id':residue['label_seq_id'] if residue else None,'auth_residue_number':residue['auth_residue_number'] if residue else None,'insertion_code':residue['insertion_code'] if residue else None,'status':status,'structure_modal_fraction':stats[col-1]['modal_fraction'] if status=='observed' else None,'structure_coverage':stats[col-1]['coverage'] if status=='observed' else None})
 return out
