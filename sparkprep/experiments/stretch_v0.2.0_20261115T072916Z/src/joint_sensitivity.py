"""Reuse computed independent sequence scores across fixed real-panel subsets; no new inference."""
import collections,csv,statistics,math
from common import *
from summarize_scores import rank

def correlation(a,b):
 ma=statistics.mean(a);mb=statistics.mean(b);den=math.sqrt(sum((x-ma)**2 for x in a)*sum((x-mb)**2 for x in b))
 return sum((x-ma)*(y-mb) for x,y in zip(a,b))/den if den else None

def run():
 scores=list(csv.DictReader((ROOT/'results/full_panel_v1/residue_nll.tsv').read_text().splitlines(),delimiter='\t'));columns=list(csv.DictReader((ROOT/'results/full_panel_comparison_v2/column_comparison.tsv').read_text().splitlines(),delimiter='\t'));full=[r for r in columns if float(r['coverage'])==1];colids=[int(r['alignment_column']) for r in full];data=collections.defaultdict(dict)
 for r in scores:data[int(r['alignment_column'])][r['accession']]=(r['original_residue'],float(r['nll_nats']))
 original={int(r['alignment_column']):float(r['agreement_minus_predictability_percentile']) for r in full};records={col:collections.defaultdict(list) for col in colids};designs=json.loads((ROOT/'results/panel_designs.json').read_text());bydesign=[]
 for design in designs:
  means=[];agreement=[]
  for col in colids:
   subset=[data[col][k] for k in design['included']];counts=collections.Counter(aa for aa,nll in subset);agreement.append(max(counts.values())/len(subset));means.append(statistics.mean(nll for aa,nll in subset))
  ra=rank(agreement);rp=rank([-v for v in means]);deltas=[(a-b)/(len(colids)-1) for a,b in zip(ra,rp)]
  for col,mean,delta in zip(colids,means,deltas):records[col][design['kind']].append((mean,delta))
  bydesign.append({'design_id':design['id'],'kind':design['kind'],'sample_size':len(design['included']),'agreement_predictability_spearman_rho':correlation(ra,rp)})
 out=[]
 for row in full:
  col=int(row['alignment_column']);result={'alignment_column':col,'original_agreement_minus_predictability_percentile':original[col]}
  for kind,values in records[col].items():
   means=[v[0] for v in values];deltas=[v[1] for v in values];result.update({kind+'_nll_min':min(means),kind+'_nll_max':max(means),kind+'_discordance_min':min(deltas),kind+'_discordance_max':max(deltas),kind+'_same_direction_fraction':sum((v>0)==(original[col]>0) for v in deltas if v!=0)/len(deltas) if original[col]!=0 else ''})
  out.append(result)
 write_tsv(ROOT/'results/joint_panel_sensitivity.tsv',out);write_tsv(ROOT/'results/joint_design_summary.tsv',bydesign)
 base_rho=correlation(rank([float(r['modal_fraction']) for r in full]),rank([-float(r['mean_original_residue_nll_nats']) for r in full]))
 examples=[]
 for col in [177,58,129,137,4,209]:
  row=columns[col-1];j=next(x for x in out if x['alignment_column']==col);examples.append({'alignment_column':col,'modal_fraction':float(row['modal_fraction']),'mean_nll_nats':float(row['mean_original_residue_nll_nats']),'observation_status':row['reference_1GGQ_assembly1_observation_status'],'interchain_contact_4_5_A':row['reference_1GGQ_assembly1_interchain_contact_4_5_A'],**j})
 summary={'source_scores_sha256':sha(ROOT/'results/full_panel_v1/residue_nll.tsv'),'fixed_full_coverage_columns':202,'panel_designs':len(designs),'additional_model_forward_passes':0,'full_panel_agreement_predictability_spearman_rho':base_rho,'half_panel_rho_min':min(r['agreement_predictability_spearman_rho'] for r in bydesign if r['kind']=='half_panel'),'half_panel_rho_max':max(r['agreement_predictability_spearman_rho'] for r in bydesign if r['kind']=='half_panel'),'examples':examples,'interpretation':['These are descriptive rank comparisons and panel-composition sensitivity, not p-values or population confidence intervals.','A zero rank-discordance is not counted as maintaining a positive/negative direction.','The same precomputed per-sequence conditional score is valid across panel subsets because ESM sees each sequence independently; empirical frequencies and column mean scores are recomputed for each subset.','Subsets overlap, columns are correlated and phylogeny is not corrected.']}
 write_json(ROOT/'results/joint_sensitivity_summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
