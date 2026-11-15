import csv,collections
from common import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
s=list(csv.DictReader((ROOT/'results/panel_sensitivity.tsv').read_text().splitlines(),delimiter='\t'));m=list(csv.DictReader((ROOT/'results/dimer_alignment_mapping.tsv').read_text().splitlines(),delimiter='\t'))
x=[int(r['alignment_column']) for r in s];y=[float(r['modal_fraction']) for r in s];low=[float(r['half_panel_min']) for r in s];high=[float(r['half_panel_max']) for r in s]
fig,(ax,bx)=plt.subplots(2,1,figsize=(13,6.8),sharex=True,gridspec_kw={'height_ratios':[2.4,1.2]},layout='constrained');fig.patch.set_facecolor('#f8fafc')
ax.fill_between(x,low,high,color='#67b5b4',alpha=.38,label='Range across 200 real 15-sequence subpanels');ax.plot(x,y,lw=1.3,color='#155e75',label='Original 30-sequence modal fraction')
for r in s:
 if float(r['coverage'])<1:ax.axvspan(int(r['alignment_column'])-.5,int(r['alignment_column'])+.5,color='#94a3b8',alpha=.2)
ax.set_ylim(0,1.04);ax.set_ylabel('Observed-residue modal fraction');ax.legend(loc='lower left',fontsize=8);ax.set_title('OspC: sequence agreement depends on which natural sequences are sampled',loc='left',weight='bold',fontsize=14);ax.grid(alpha=.15)
groups=[('1GGQ','1','A@1','1GGQ dimer 1 · Q07337'),('1GGQ','2','C@1','1GGQ dimer 2 · Q07337'),('1G5Z','1','A@1','1G5Z symmetry dimer · Q44717')]
for n,(pdb,assembly,inst,label) in enumerate(groups):
 rows=[r for r in m if r['pdb_id']==pdb and r['assembly_id']==assembly and r['instance']==inst and r['alignment_column']];observed=[int(r['alignment_column']) for r in rows];contact=[int(r['alignment_column']) for r in rows if r['contact_4_5_A']=='True'];bx.scatter(observed,[n]*len(observed),marker='s',s=14,color='#d1d5db');bx.scatter(contact,[n]*len(contact),marker='s',s=14,color='#d97706')
bx.set_yticks(range(3),[g[3] for g in groups],fontsize=9);bx.set_xlabel('Frozen alignment column (1-based)');bx.set_xlim(.5,218.5);bx.set_ylim(2.7,-.7);bx.set_title('Orange: experimental-coordinate interchain contacts ≤4.5 Å. Gray: observed residues.',loc='left',fontsize=10);bx.grid(axis='x',alpha=.15)
fig.supxlabel('Fixed alignment; sensitivity range is not a confidence interval. Contacts are not solvent accessibility, antigenicity, or protection. PLM scoring pending.',fontsize=9)
fig.savefig(ROOT/'results/panel_sensitivity_dimer_context.png',dpi=180);fig.savefig(ROOT/'results/panel_sensitivity_dimer_context.svg');plt.close(fig)
