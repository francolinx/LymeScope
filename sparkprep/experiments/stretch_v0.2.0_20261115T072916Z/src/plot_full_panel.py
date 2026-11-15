"""Publication-style scientific figures from complete panel scores and existing experimental coordinates."""
from common import *
import collections,csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from matplotlib.colors import Normalize
from cif_reader import parse_cif
rows=list(csv.DictReader((ROOT/'results/full_panel_comparison_v2/column_comparison.tsv').read_text().splitlines(),delimiter='\t'));bycol={int(r['alignment_column']):r for r in rows};joint={int(r['alignment_column']):r for r in csv.DictReader((ROOT/'results/joint_panel_sensitivity.tsv').read_text().splitlines(),delimiter='\t')}
fig=plt.figure(figsize=(14,8.3),layout='constrained');gs=fig.add_gridspec(2,2,height_ratios=[2,1]);ax=fig.add_subplot(gs[0,:]);palette={'observed_contact':'#d97706','observed_noncontact':'#0f766e','unobserved':'#94a3b8'}
for state,label in [('observed_contact','Observed 1GGQ chain A: interchain contact'),('observed_noncontact','Observed 1GGQ chain A: no contact at 4.5 Å'),('unobserved','No observed 1GGQ chain A mapping')]:
 group=[r for r in rows if float(r['coverage'])==1 and (('unobserved' if r['reference_1GGQ_assembly1_observation_status']!='observed' else 'observed_contact' if r['reference_1GGQ_assembly1_interchain_contact_4_5_A']=='True' else 'observed_noncontact')==state)]
 ax.scatter([float(r['modal_fraction']) for r in group],[float(r['mean_original_residue_nll_nats']) for r in group],s=38,c=palette[state],alpha=.8,label=label,edgecolors='white',linewidths=.4)
sparse=[r for r in rows if float(r['coverage'])<1];ax.scatter([float(r['modal_fraction']) for r in sparse],[float(r['mean_original_residue_nll_nats']) for r in sparse],s=35,c='#cbd5e1',marker='x',label='Incomplete panel coverage (not ranked)')
for col,offset in [(134,(-120,-25)),(177,(-105,14)),(58,(-105,-17)),(129,(-90,-33)),(137,(-80,18))]:
 r=bycol[col];ax.annotate(f'column {col}',(float(r['modal_fraction']),float(r['mean_original_residue_nll_nats'])),xytext=offset,textcoords='offset points',fontsize=10,arrowprops={'arrowstyle':'-','color':'#475569'},bbox={'boxstyle':'round,pad=.2','fc':'white','ec':'#cbd5e1'})
ax.set_xlabel('Empirical sequence agreement (modal fraction; gaps excluded)');ax.set_ylabel('Mean masked-original-residue NLL (nats)\nLower = more predictable to ESM-2 8M');ax.set_xlim(.2,1.07);ax.set_ylim(bottom=0);ax.grid(alpha=.15);ax.legend(loc='upper left',fontsize=8);ax.set_title('Agreement and model predictability describe different features of this OspC panel',loc='left',fontsize=15,weight='bold')
bx=fig.add_subplot(gs[1,0]);cx=fig.add_subplot(gs[1,1]);selected=[177,58,129,137];colors=['#b45309','#ea580c','#0f766e','#0d9488']
for i,(col,color) in enumerate(zip(selected,colors)):
 r=bycol[col];j=joint[col];lo=float(j['half_panel_nll_min']);hi=float(j['half_panel_nll_max']);v=float(r['mean_original_residue_nll_nats']);bx.plot([lo,hi],[i,i],color=color,lw=5,solid_capstyle='round');bx.scatter([v],[i],c='white',edgecolors=color,zorder=3,s=45)
 lo=float(j['half_panel_discordance_min']);hi=float(j['half_panel_discordance_max']);v=float(j['original_agreement_minus_predictability_percentile']);cx.plot([lo,hi],[i,i],color=color,lw=5,solid_capstyle='round');cx.scatter([v],[i],c='white',edgecolors=color,zorder=3,s=45)
for axis in [bx,cx]:axis.set_yticks(range(4),[f'column {c}' for c in selected]);axis.invert_yaxis();axis.grid(axis='x',alpha=.15)
bx.set_xlabel('Mean NLL across 200 real half-panels');cx.set_xlabel('Agreement rank − predictability rank');cx.axvline(0,color='#94a3b8',lw=1);cx.set_xlim(-1,1);bx.set_title('Panel-composition sensitivity (range, not CI)',loc='left',fontsize=11);cx.set_title('Direction persists in all 200 half-panels',loc='left',fontsize=11)
fig.supxlabel('30 natural sequences · 6,305 singleton masks · 218 fixed columns (202 fully covered). No protection, antigenicity or solvent-accessibility inference.',fontsize=9);fig.savefig(ROOT/'results/full_panel_agreement_predictability.png',dpi=180);fig.savefig(ROOT/'results/full_panel_agreement_predictability.svg');plt.close(fig)
# Experimental C-alpha traces, with gaps left disconnected. Both chains receive the same panel-column annotation.
c=parse_cif(ROOT/'inputs/1GGQ.cif');atoms=cif_rows(c,'_atom_site');mapping=list(csv.DictReader((ROOT/'results/dimer_alignment_mapping.tsv').read_text().splitlines(),delimiter='\t'));label_to_col={(r['instance'].split('@')[0],int(r['label_seq_id'])):int(r['alignment_column']) for r in mapping if r['pdb_id']=='1GGQ' and r['assembly_id']=='1' and r['alignment_column']};chains=collections.defaultdict(list)
for a in atoms:
 if a['label_asym_id'] in ['A','B'] and a['label_atom_id']=='CA' and a['pdbx_PDB_model_num']=='1' and float(a['occupancy'])>0:
  label=int(a['label_seq_id']);col=label_to_col.get((a['label_asym_id'],label));chains[a['label_asym_id']].append((label,tuple(float(a['Cartn_'+k]) for k in ['x','y','z']),col))
fig=plt.figure(figsize=(13.5,6.5),layout='constrained');allxyz=[xyz for chain in chains.values() for _,xyz,_ in chain];ranges=[(min(v[i] for v in allxyz),max(v[i] for v in allxyz)) for i in range(3)]
for n,(field,title,cmap,norm) in enumerate([('modal_fraction','Empirical panel agreement','viridis',Normalize(0,1)),('mean_original_residue_nll_nats','Mean masked-original-residue NLL','magma',Normalize(0,max(float(r['mean_original_residue_nll_nats']) for r in rows if r['reference_1GGQ_assembly1_observation_status']=='observed')))]):
 ax=fig.add_subplot(1,2,n+1,projection='3d')
 for chain,coords in chains.items():
  coords.sort();segments=[];vals=[]
  for (lab1,x1,col1),(lab2,x2,col2) in zip(coords,coords[1:]):
   if lab2!=lab1+1 or col1 is None or col2 is None:continue
   segments.append([x1,x2]);vals.append((float(bycol[col1][field])+float(bycol[col2][field]))/2)
  collection=Line3DCollection(segments,cmap=cmap,norm=norm,linewidths=3.5);collection.set_array(__import__('numpy').array(vals));ax.add_collection3d(collection)
  _,mid,_=coords[len(coords)//2];ax.text(*mid,f'chain {chain}',fontsize=9)
 for i,(lo,hi) in enumerate(ranges):getattr(ax,['set_xlim','set_ylim','set_zlim'][i])(lo-3,hi+3)
 ax.set_box_aspect([hi-lo for lo,hi in ranges]);ax.view_init(elev=18,azim=-50);ax.set_axis_off();ax.set_title(title,fontsize=13);fig.colorbar(collection,ax=ax,shrink=.6,pad=.01,label='Modal fraction' if n==0 else 'NLL (nats; lower is more predictable)')
fig.suptitle('Existing experimental OspC dimer 1GGQ, biological assembly 1',fontsize=16,weight='bold');fig.supxlabel('Cα traces with missing residues left disconnected. Colors project panel-column summaries onto the reference; they are not new structures, SASA, antigenicity or protection scores.',fontsize=9);fig.savefig(ROOT/'results/experimental_dimer_comparison.png',dpi=180);fig.savefig(ROOT/'results/experimental_dimer_comparison.svg');plt.close(fig)
