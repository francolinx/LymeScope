"""CPU-only Shrake-Rupley-style sampled SASA from existing experimental heavy-atom coordinates.
Original numerical implementation; uses existing numpy/scipy, not downloaded packages.
"""
import time,math,resource,collections
import numpy as np
from scipy.spatial import cKDTree
from common import *
from cif_reader import parse_cif
from dimer_context import transform,AA
RADII={'C':1.70,'N':1.55,'O':1.52,'S':1.80}
PROBE=1.40

def sphere_points(n):
 k=np.arange(n,dtype=np.float64);z=1-2*(k+0.5)/n;angle=k*(math.pi*(3-math.sqrt(5)));r=np.sqrt(1-z*z)
 return np.column_stack((r*np.cos(angle),r*np.sin(angle),z))

def atom_sasa(xyz,vdw,n_points=960,probe=PROBE):
 xyz=np.asarray(xyz,dtype=np.float64);expanded=np.asarray(vdw,dtype=np.float64)+probe;assert xyz.shape==(len(expanded),3);unit=sphere_points(n_points);tree=cKDTree(xyz);out=np.empty(len(xyz))
 for i,center in enumerate(xyz):
  points=unit*expanded[i]+center;visible=np.ones(n_points,dtype=bool)
  neighbors=tree.query_ball_point(center,expanded[i]+expanded.max())
  neighbors=[j for j in neighbors if j!=i and np.dot(xyz[j]-center,xyz[j]-center)<(expanded[i]+expanded[j])**2]
  neighbors.sort(key=lambda j:np.dot(xyz[j]-center,xyz[j]-center))
  for j in neighbors:
   idx=np.flatnonzero(visible)
   if not len(idx):break
   delta=points[idx]-xyz[j];visible[idx[np.einsum('ij,ij->i',delta,delta)<expanded[j]**2]]=False
  out[i]=4*math.pi*expanded[i]**2*visible.sum()/n_points
 return out

def analytical_checks():
 r=3.1;one=atom_sasa([[0,0,0]],[1.7],960);assert abs(one[0]-4*math.pi*r*r)<1e-10
 # Two identical expanded spheres at separation d: each loses cap area 2*pi*r*(r-d/2).
 d=3.;expected=4*math.pi*r*r-2*math.pi*r*(r-d/2);two=atom_sasa([[0,0,0],[d,0,0]],[1.7,1.7],8192)
 assert np.max(np.abs(two-expected))<.15, (two,expected)
 separated=atom_sasa([[0,0,0],[20,0,0]],[1.7,1.7],960);assert np.max(abs(separated-4*math.pi*r*r))<1e-10
 return {'isolated_sphere_error_A2':float(abs(one[0]-4*math.pi*r*r)),'two_overlapping_spheres_expected_each_A2':expected,'two_overlapping_spheres_max_abs_error_A2':float(np.max(abs(two-expected))),'nonoverlapping_spheres_error_A2':float(np.max(abs(separated-4*math.pi*r*r)))}

def assembly_atoms(code):
 c=parse_cif(ROOT/'inputs'/f'{code}.cif');ops={r['id']:r for r in cif_rows(c,'_pdbx_struct_oper_list')};pairs=[('A','1'),('B','1')] if code=='1GGQ' else [('A','1'),('A','2')];atoms=cif_rows(c,'_atom_site');out=[]
 for chain,operation in pairs:
  for a in atoms:
   if a['label_asym_id']!=chain or a['pdbx_PDB_model_num']!='1' or a['label_comp_id'] not in AA or a['label_seq_id'] in ['.','?'] or a['label_alt_id'] not in ['.','A'] or float(a['occupancy'])<=0 or a['type_symbol'] in ['H','D']:continue
   assert a['type_symbol'] in RADII,a['type_symbol'];out.append({'instance':chain+'@'+operation,'label_seq_id':a['label_seq_id'],'auth_residue_number':a['auth_seq_id'],'insertion_code':a['pdbx_PDB_ins_code'],'aa':AA[a['label_comp_id']],'element':a['type_symbol'],'xyz':transform(tuple(float(a['Cartn_'+k]) for k in ['x','y','z']),ops[operation])})
 return out

def run():
 start=time.perf_counter();checks=analytical_checks();results=[];summaries=[]
 for code,resolutions in [('1GGQ',[480,960,1920]),('1G5Z',[960])]:
  atoms=assembly_atoms(code);xyz=np.array([a['xyz'] for a in atoms]);vdw=np.array([RADII[a['element']] for a in atoms]);instances=list(dict.fromkeys(a['instance'] for a in atoms));assert len(instances)==2;ids=np.array([a['instance'] for a in atoms])
  for n in resolutions:
   tick=time.perf_counter();dimer=atom_sasa(xyz,vdw,n);monomer=np.empty(len(atoms))
   for instance in instances:
    subset=np.flatnonzero(ids==instance);monomer[subset]=atom_sasa(xyz[subset],vdw[subset],n)
   assert np.min(monomer-dimer)>-1e-9;loss=monomer-dimer;grouped=collections.defaultdict(lambda:[0.,0.,0.])
   for i,a in enumerate(atoms):
    key=(a['instance'],a['label_seq_id'],a['auth_residue_number'],a['insertion_code'],a['aa']);grouped[key][0]+=monomer[i];grouped[key][1]+=dimer[i];grouped[key][2]+=loss[i]
   for (inst,label,auth,ins,aa),(mono,dim,delta) in grouped.items():results.append({'pdb_id':code,'assembly_id':1,'instance':inst,'label_seq_id':label,'auth_residue_number':auth,'insertion_code':ins,'aa':aa,'sphere_points_per_atom':n,'monomer_sasa_A2':mono,'dimer_sasa_A2':dim,'delta_sasa_A2':delta})
   summaries.append({'pdb_id':code,'assembly_id':1,'sphere_points_per_atom':n,'heavy_atoms':len(atoms),'monomer_sasa_sum_A2':float(monomer.sum()),'dimer_sasa_A2':float(dimer.sum()),'total_sasa_loss_A2':float(loss.sum()),'mean_partner_interface_area_A2':float(loss.sum()/2),'elapsed_s':time.perf_counter()-tick})
   assert time.perf_counter()-start<180,'CPU geometry time bound exceeded'
 # Quantify, rather than assume, discretization sensitivity for the main reference.
 a=next(x for x in summaries if x['pdb_id']=='1GGQ' and x['sphere_points_per_atom']==960);b=next(x for x in summaries if x['pdb_id']=='1GGQ' and x['sphere_points_per_atom']==1920);relative=abs(a['total_sasa_loss_A2']-b['total_sasa_loss_A2'])/b['total_sasa_loss_A2'];assert relative<.02,relative
 lo={(r['instance'],r['label_seq_id']):r for r in results if r['pdb_id']=='1GGQ' and r['sphere_points_per_atom']==960};hi={(r['instance'],r['label_seq_id']):r for r in results if r['pdb_id']=='1GGQ' and r['sphere_points_per_atom']==1920};differences=[abs(lo[k]['delta_sasa_A2']-hi[k]['delta_sasa_A2']) for k in hi];write_tsv(ROOT/'results/sasa_dimer_context.tsv',results)
 summary={'method':'Independent Shrake-Rupley-style Fibonacci sphere surface sampling, heavy-atom element radii, probe 1.40 A. SASA is the area swept by probe centers, not molecular/solvent-excluded surface.','vdw_radii_A':RADII,'coordinates':'Existing experimental biological dimer assembly1; identical atom selections for monomer and dimer; missing atoms/residues are not reconstructed. Model1, positive occupancy, alt . or A, canonical protein residues only; waters/ions omitted.','analytical_tests':checks,'calculations':summaries,'1GGQ_960_to_1920_relative_total_loss_difference':relative,'1GGQ_960_to_1920_max_residue_delta_difference_A2':max(differences),'elapsed_total_s':time.perf_counter()-start,'process_max_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'additional_model_forward_passes':0,'interpretation':['Total SASA loss = SASA_A + SASA_B - SASA_AB. Mean partner interface area is half that total; both reported to avoid convention ambiguity.','This is calculated geometric accessible area for incomplete static crystal constructs, not experimental solvent exposure or physiological accessibility.','A heavy-atom contact cutoff and sampled area burial measure different things; neither implies antigenicity or protection.','No relative SASA normalization or exposed/buried classification threshold is introduced.','Point sampling, orientation, radii, probe, missing residues/atoms and conformational state affect results. 1G5Z has only a single sampling resolution here.'],'references':['https://doi.org/10.1016/0022-2836(73)90011-9','https://biopython.org/docs/dev/api/Bio.PDB.SASA.html']}
 write_json(ROOT/'results/sasa_context_summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
