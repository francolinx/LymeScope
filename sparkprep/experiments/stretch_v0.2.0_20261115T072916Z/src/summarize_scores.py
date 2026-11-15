"""Validate complete masked-score task coverage and export descriptive alignment-column comparison."""
import argparse,collections,math,statistics,csv
from common import *
def rank(values):
 order=sorted(range(len(values)),key=lambda i:values[i]);out=[0.]*len(values);i=0
 while i<len(order):
  j=i+1
  while j<len(order) and values[order[j]]==values[order[i]]:j+=1
  for k in order[i:j]:out[k]=(i+j-1)/2
  i=j
 return out
def run(paths,output):
 hashes={r['accession']:r['sequence_sha256'] for r in json.loads((ROOT/'results/shard_manifest.json').read_text())['sequences']}
 expected={r['task_id']:r for r in csv.DictReader((ROOT/'results/residue_alignment_mapping.tsv').read_text().splitlines(),delimiter='\t')};got={}
 for path in paths:
  for row in csv.DictReader(pathlib.Path(path).read_text().splitlines(),delimiter='\t'):
   task=row['task_id'];assert task in expected and task not in got,('Unexpected/duplicate task',task)
   e=expected[task];assert row['sequence_sha256']==hashes[row['accession']]
   for k in ['accession','sequence_position','alignment_column','original_residue']:assert row[k]==e[k],(task,k)
   value=float(row['nll_nats']);assert math.isfinite(value) and value>=0
   got[task]=row
 assert set(got)==set(expected),('Missing tasks',len(expected)-len(got))
 out=pathlib.Path(output);out.mkdir(parents=True,exist_ok=False)
 rows=list(got.values());rows.sort(key=lambda r:(int(expected[r['task_id']]['sequence_ordinal']),int(r['sequence_position'])))
 write_tsv(out/'residue_nll_merged.tsv',rows)
 sequence_summaries=[]
 for accession in hashes:
  vals=[float(row['nll_nats']) for row in rows if row['accession']==accession];mean_nll=statistics.mean(vals);sequence_summaries.append({'accession':accession,'sequence_sha256':hashes[accession],'mask_count':len(vals),'scored_positions':'1..L all standard full-length natural residues','mean_nll_nats':mean_nll,'masked_pseudo_perplexity':math.exp(mean_nll)})
 write_tsv(out/'sequence_summary.tsv',sequence_summaries)
 bycol=collections.defaultdict(list)
 for row in rows:bycol[int(row['alignment_column'])].append(row)
 sensitivity=list(csv.DictReader((ROOT/'results/panel_sensitivity.tsv').read_text().splitlines(),delimiter='\t'));contactrows=list(csv.DictReader((ROOT/'results/dimer_alignment_mapping.tsv').read_text().splitlines(),delimiter='\t'));reference_rows=[r for r in contactrows if r['pdb_id']=='1GGQ' and r['assembly_id']=='1' and r['instance']=='A@1' and r['panel_accession']=='Q07337' and r['alignment_column']]
 observed_reference={int(r['alignment_column']) for r in reference_rows};contacts={int(r['alignment_column']) for r in reference_rows if r['contact_4_5_A']=='True'}
 result=[]
 for s in sensitivity:
  col=int(s['alignment_column']);rs=bycol[col];scores=[float(r['nll_nats']) for r in rs];counts=collections.Counter(r['original_residue'] for r in rs);n=len(rs)
  result.append({**s,'observed_residue_masks':n,'mean_original_residue_nll_nats':statistics.mean(scores),'sd_original_residue_nll_nats':statistics.stdev(scores) if n>1 else '', 'empirical_entropy_nats':-sum((v/n)*math.log(v/n) for v in counts.values()),'reference_1GGQ_assembly1_observation_status':'observed' if col in observed_reference else 'unobserved_or_unmapped','reference_1GGQ_assembly1_interchain_contact_4_5_A':col in contacts if col in observed_reference else ''})
 full=[r for r in result if float(r['coverage'])==1];ag=rank([float(r['modal_fraction']) for r in full]);pred=rank([-r['mean_original_residue_nll_nats'] for r in full]);N=len(full)
 for i,r in enumerate(full):r.update(agreement_percentile_rank=ag[i]/(N-1),predictability_percentile_rank=pred[i]/(N-1),agreement_minus_predictability_percentile=(ag[i]-pred[i])/(N-1))
 for r in result:
  for key in ['agreement_percentile_rank','predictability_percentile_rank','agreement_minus_predictability_percentile']:r.setdefault(key,'')
 write_tsv(out/'column_comparison.tsv',result)
 summary={'tasks':len(rows),'columns':218,'fully_covered_columns_compared':202,'most_agreement_above_predictability':sorted(full,key=lambda r:r['agreement_minus_predictability_percentile'],reverse=True)[:10],'most_predictability_above_agreement':sorted(full,key=lambda r:r['agreement_minus_predictability_percentile'])[:10],'interpretation':'Percentile discordance is a descriptive ranking within these 202 fixed fully covered columns, not a p-value, biological mechanism or protection score. Mean NLL averages observed natural original-residue singleton-mask scores. No amino-acid-alphabet renormalization is performed.','limitations':['Panel composition/relatedness, precursor signal peptides, model training-set overlap and fixed alignment can affect both axes.','A 33-token model predictive distribution and 20-residue empirical distribution differ in support and conditioning; their magnitudes are not calibrated to each other.','Contact is separate from SASA, accessibility, antigenicity and protection.']}
 write_json(out/'divergence_summary.json',summary)
 print(json.dumps({'tasks':len(rows),'columns':len(result),'output':str(out)},indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--scores',nargs='+',required=True);p.add_argument('--output',required=True);a=p.parse_args();run(a.scores,a.output)
