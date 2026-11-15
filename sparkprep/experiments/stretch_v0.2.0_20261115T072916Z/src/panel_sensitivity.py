"""Fixed-alignment perturbation of observed natural panel; no realignment or synthetic sequences."""
import collections,math,random,statistics,csv
from common import *
def stats(seqs,col):
 counts=collections.Counter(s[col] for s in seqs if s[col]!='-');n=sum(counts.values())
 return {'coverage':n/len(seqs),'modal_fraction':max(counts.values())/n if n else None,'entropy_bits':-sum((v/n)*math.log2(v/n) for v in counts.values()) if n else None,'modal_residues':''.join(sorted(k for k,v in counts.items() if v==max(counts.values()))) if n else ''}
def run():
 panel=fasta(ROOT/'inputs/panel.fasta');aligned=fasta(ROOT/'inputs/aligned.fasta');assert len(panel)==len(aligned)==30;assert set(panel)==set(aligned);assert len(set(panel.values()))==30
 ids=list(aligned);seqs=list(aligned.values());L=len(seqs[0]);assert L==218 and all(len(s)==L for s in seqs)
 for k,s in aligned.items():assert s.replace('-','')==panel[k]
 base=[stats(seqs,c) for c in range(L)];assert sum(x['coverage']==1 for x in base)==202;assert sum(x['coverage']==1 and x['modal_fraction']==1 for x in base)==76
 designs=[]
 for k in ids:designs.append({'id':'loo_'+k,'kind':'leave_one_out','included':[i for i in ids if i!=k]})
 # Hash-ranked subsamples avoid dependence on Python PRNG implementation. 200 reproducible real 15-sequence panels.
 for seed in range(200):
  chosen=sorted(ids,key=lambda k:hashlib.sha256(f'LymeScope-halfpanel-v1:{seed}:{k}'.encode()).hexdigest())[:15]
  designs.append({'id':f'half_{seed:03}','kind':'half_panel','included':sorted(chosen)})
 metadata={r['accession']:r for r in csv.DictReader((ROOT/'inputs/sequence_metadata.tsv').open(),delimiter='\t')}
 groups=collections.defaultdict(list)
 for k in ids:
  # Stable species-level display grouping; strip infraspecific parenthetical annotations, not phylogenetic inference.
  group=metadata[k]['organism'].split(' (')[0];groups[group].append(k)
 for species,members in sorted(groups.items()):
  included=[k for k in ids if k not in members]
  if included:designs.append({'id':'drop_group_'+species,'kind':'leave_organism_group_out','included':included,'removed':members})
 measures={d['id']:[stats([aligned[k] for k in d['included']],c) for c in range(L)] for d in designs};out=[]
 for c,b in enumerate(base):
  row={'alignment_column':c+1,**b}
  for kind in ['leave_one_out','half_panel','leave_organism_group_out']:
   vals=[measures[d['id']][c]['modal_fraction'] for d in designs if d['kind']==kind and measures[d['id']][c]['modal_fraction'] is not None]
   row.update({kind+'_min':min(vals) if vals else '',kind+'_max':max(vals) if vals else '',kind+'_range':max(vals)-min(vals) if vals else '',kind+'_defined_panels':len(vals)})
  out.append(row)
 write_tsv(ROOT/'results/panel_sensitivity.tsv',out);write_json(ROOT/'results/panel_designs.json',designs)
 # Exact per-residue mapping: one row per original natural residue; gaps produce no scoring task.
 mapping=[];seqmanifest=[]
 for ordinal,k in enumerate(ids):
  pos=0
  for col,aa in enumerate(aligned[k],1):
   if aa=='-':continue
   pos+=1;mapping.append({'sequence_ordinal':ordinal,'accession':k,'sequence_position':pos,'alignment_column':col,'original_residue':aa,'token_position_expected':pos,'task_id':f'{k}:{pos}'})
  seqmanifest.append({'accession':k,'sequence_ordinal':ordinal,'length':pos,'sequence_sha256':hashlib.sha256(panel[k].encode()).hexdigest(),'one_node_shard':0,'two_node_shard':ordinal%2})
 write_tsv(ROOT/'results/residue_alignment_mapping.tsv',mapping)
 write_json(ROOT/'results/shard_manifest.json',{'schema_version':'1.0','assignment':'FASTA alignment order sequence ordinal modulo node count; one task per non-gap original residue; each task has exactly one masked position','task_count':len(mapping),'sequence_count':30,'one_node_masks':[len(mapping)],'two_node_masks':[sum(x['length'] for x in seqmanifest if x['two_node_shard']==s) for s in [0,1]],'sequences':seqmanifest})
 summary={'alignment_columns':L,'sequence_count':30,'residue_mask_tasks':len(mapping),'full_coverage_columns':202,'fully_covered_identical_columns':76,'organism_groups':dict(groups),'design_counts':dict(collections.Counter(d['kind'] for d in designs)),'mean_loo_range':statistics.mean(r['leave_one_out_range'] for r in out),'max_loo_range':max(r['leave_one_out_range'] for r in out),'columns_halfpanel_range_ge_0_2':sum(r['half_panel_range']>=0.2-1e-12 for r in out),'columns_undefined_in_any_halfpanel':sum(r['half_panel_defined_panels']<200 for r in out),'largest_halfpanel_ranges':sorted(out,key=lambda r:r['half_panel_range'],reverse=True)[:12],'limitations':['Panel selected rather than probability sampled; perturbation ranges are sensitivity summaries, not population confidence intervals.','Alignment is fixed; this does not measure realignment uncertainty.','Gap-containing columns use observed-residue denominator; coverage reported independently.','Organism text groups are metadata groups, not independent clades or verified strains.','No PLM scores used or inferred in this computation.']}
 write_json(ROOT/'results/panel_sensitivity_summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ['largest_halfpanel_ranges','organism_groups']},indent=2))
if __name__=='__main__':run()
