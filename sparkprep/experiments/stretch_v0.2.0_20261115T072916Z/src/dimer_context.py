"""Experimental-coordinate heavy-atom contacts in deposited biological dimer assemblies.
No solvent-accessible area, epitope or protection inference is made.
"""
import collections,itertools,math,re
from common import *
from cif_reader import parse_cif
AA={'ALA':'A','ARG':'R','ASN':'N','ASP':'D','CYS':'C','GLN':'Q','GLU':'E','GLY':'G','HIS':'H','ILE':'I','LEU':'L','LYS':'K','MET':'M','PHE':'F','PRO':'P','SER':'S','THR':'T','TRP':'W','TYR':'Y','VAL':'V'}
def transform(xyz,op):return tuple(sum(float(op[f'matrix[{i}][{j}]'])*xyz[j-1] for j in [1,2,3])+float(op[f'vector[{i}]']) for i in [1,2,3])
def contacts(left,right,cutoff=4.5):
 cells=collections.defaultdict(list)
 for r in right:cells[tuple(math.floor(v/cutoff) for v in r['xyz'])].append(r)
 pairs={}
 for a in left:
  key=tuple(math.floor(v/cutoff) for v in a['xyz'])
  for dx,dy,dz in itertools.product([-1,0,1],repeat=3):
   for b in cells[(key[0]+dx,key[1]+dy,key[2]+dz)]:
    ds=sum((x-y)**2 for x,y in zip(a['xyz'],b['xyz']))
    if ds<=cutoff**2:
     pair=(a['label_seq_id'],b['label_seq_id']);distance=math.sqrt(ds)
     if pair not in pairs or distance<pairs[pair]['min_distance_A']:pairs[pair]={'left_label_seq_id':pair[0],'right_label_seq_id':pair[1],'left_auth_residue_number':a['auth_seq_id'],'right_auth_residue_number':b['auth_seq_id'],'left_aa':AA[a['label_comp_id']],'right_aa':AA[b['label_comp_id']],'min_distance_A':distance}
 return list(pairs.values())
def run():
 panel=fasta(ROOT/'inputs/panel.fasta');aligned=fasta(ROOT/'inputs/aligned.fasta');allrows=[];summaries=[];mapping=[]
 for code in ['1GGQ','1G5Z']:
  c=parse_cif(ROOT/'inputs'/f'{code}.cif');polys={r['entity_id']:re.sub(r'\s','',r['pdbx_seq_one_letter_code_can']) for r in cif_rows(c,'_entity_poly') if r['type']=='polypeptide(L)'}
  asym={r['id']:r['entity_id'] for r in cif_rows(c,'_struct_asym')};ops={r['id']:r for r in cif_rows(c,'_pdbx_struct_oper_list')};atoms=cif_rows(c,'_atom_site');assemblies={r['id']:r for r in cif_rows(c,'_pdbx_struct_assembly')}
  for aid,assembly in assemblies.items():
   if assembly['oligomeric_details']!='dimeric':continue
   instances=[]
   for gen in cif_rows(c,'_pdbx_struct_assembly_gen'):
    if gen['assembly_id']!=aid:continue
    expr=gen['oper_expression'];assert re.fullmatch(r'\d+(,\d+)*',expr),'Unsupported operator expression; do not guess'
    for chain in gen['asym_id_list'].split(','):
     if asym[chain] not in polys:continue
     for oid in expr.split(','):
      selected=[]
      for atom in atoms:
       if atom['label_asym_id']!=chain or atom['pdbx_PDB_model_num']!='1' or atom['type_symbol'] in ['H','D'] or float(atom['occupancy'])<=0 or atom['label_alt_id'] not in ['.','A']:continue
       if atom['label_comp_id'] not in AA or atom['label_seq_id'] in ['.','?']:continue
       atom=atom.copy();atom['xyz']=transform(tuple(float(atom['Cartn_'+v]) for v in ['x','y','z']),ops[oid]);selected.append(atom)
      instances.append({'instance':chain+'@'+oid,'label_chain':chain,'operator':oid,'atoms':selected,'polymer_sequence':polys[asym[chain]]})
   assert len(instances)==2,(code,aid,len(instances))
   left,right=instances;pairs=contacts(left['atoms'],right['atoms'])
   # Threshold sensitivity rather than declaring one cutoff biologically definitive.
   summary={'pdb_id':code,'assembly_id':aid,'assembly_details':assembly,'instances':[{'instance':i['instance'],'heavy_atoms':len(i['atoms'])} for i in instances],'residue_pairs_within_4_5_A':len(pairs),'left_contact_residues':len(set(p['left_label_seq_id'] for p in pairs)),'right_contact_residues':len(set(p['right_label_seq_id'] for p in pairs)),'pairs_at_4_0_A':sum(p['min_distance_A']<=4.0 for p in pairs),'pairs_at_5_0_A':len(contacts(left['atoms'],right['atoms'],5.0))}
   summaries.append(summary)
   for p in sorted(pairs,key=lambda p:(int(p['left_label_seq_id']),int(p['right_label_seq_id']))):allrows.append({'pdb_id':code,'assembly_id':aid,'left_instance':left['instance'],'right_instance':right['instance'],**p})
   for side,instance in [('left',left),('right',right)]:
    # Match the entire deposited construct exactly to a panel substring; 1GGQ includes initiating M and uses verified deposited correspondence instead.
    seq=instance['polymer_sequence'];matches=[]
    if code=='1GGQ':
     assert seq[0]=='M' and panel['Q07337'][37:]==seq[1:];matches=[('Q07337',36)] # label 2 -> native position 38
    else:
     for accession,natural in panel.items():
      start=natural.find(seq)
      if start>=0 and natural.find(seq,start+1)<0:matches.append((accession,start))
    labels=set(p[side+'_label_seq_id'] for p in pairs)
    for atom in instance['atoms']:
     label=int(atom['label_seq_id'])
     if atom['label_atom_id']!='CA':continue
     if not matches:mapping.append({'pdb_id':code,'assembly_id':aid,'instance':instance['instance'],'label_seq_id':label,'auth_residue_number':atom['auth_seq_id'],'aa':AA[atom['label_comp_id']],'contact_4_5_A':str(label) in labels,'panel_accession':'','sequence_position':'','alignment_column':'','status':'no_exact_whole_construct_panel_match'});continue
     for accession,offset in matches:
      pos=label+offset
      if pos<1 or pos>len(panel[accession]) or AA[atom['label_comp_id']]!=panel[accession][pos-1]:continue
      cols=[col for col,aa in enumerate(aligned[accession],1) if aa!='-'];mapping.append({'pdb_id':code,'assembly_id':aid,'instance':instance['instance'],'label_seq_id':label,'auth_residue_number':atom['auth_seq_id'],'aa':AA[atom['label_comp_id']],'contact_4_5_A':str(label) in labels,'panel_accession':accession,'sequence_position':pos,'alignment_column':cols[pos-1],'status':'exact_residue_identity_validated'})
 write_tsv(ROOT/'results/dimer_contacts.tsv',allrows);write_tsv(ROOT/'results/dimer_alignment_mapping.tsv',mapping)
 write_json(ROOT/'results/dimer_context_summary.json',{'method':'minimum interchain nonhydrogen atom distance <=4.5 A; model1, positive occupancy, alt . or A; deposited biological dimer assembly operators applied; waters/ions/nonprotein excluded','assemblies':summaries,'mapping_status_counts':dict(collections.Counter(r['status'] for r in mapping)),'limitations':['Contact counts are coordinate/construct/cutoff dependent and do not measure solvent-accessible surface area or buried area.','Missing residues are not classified as non-contact surface.','1GGQ dimers are alternative copies from one crystal, not independent biological replicates.','1G5Z symmetry-generated partner is explicitly transformed; no arbitrary asymmetric-unit pairing.','No mapped contact implies antigenicity, binding or protection.','1G5Z requires exact whole-construct natural sequence identity; historical accession correspondence alone is not accepted.']})
 print(json.dumps({'assemblies':summaries,'mapping_status_counts':dict(collections.Counter(r['status'] for r in mapping))},indent=2))
if __name__=='__main__':run()
