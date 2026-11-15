"""Independent audit of model masks, aggregate arithmetic and missing-structure semantics."""
import csv,collections,math
from common import *
def validate():
 panel=fasta(ROOT/'inputs/panel.fasta');aligned=fasta(ROOT/'inputs/aligned.fasta');scores=list(csv.DictReader((ROOT/'results/full_panel_v1/residue_nll.tsv').read_text().splitlines(),delimiter='\t'));assert len(scores)==6305 and len({r['task_id'] for r in scores})==6305;groups=collections.defaultdict(list);sequences=collections.defaultdict(list)
 for r in scores:
  key=r['accession'];pos=int(r['sequence_position']);col=int(r['alignment_column']);assert panel[key][pos-1]==aligned[key][col-1]==r['original_residue'];assert hashlib.sha256(panel[key].encode()).hexdigest()==r['sequence_sha256'];nll=float(r['nll_nats']);assert nll>=0 and math.isfinite(nll);groups[col].append(nll);sequences[key].append((pos,nll))
 for key,rows in sequences.items():assert sorted(pos for pos,nll in rows)==list(range(1,len(panel[key])+1))
 columns=list(csv.DictReader((ROOT/'results/full_panel_comparison_v2/column_comparison.tsv').read_text().splitlines(),delimiter='\t'));assert len(columns)==218;base={int(x['alignment_column']):x for x in csv.DictReader((ROOT/'inputs/baseline_alignment_to_structure.tsv').read_text().splitlines(),delimiter='\t')}
 for row in columns:
  col=int(row['alignment_column']);assert int(row['observed_residue_masks'])==len(groups[col]);assert math.isclose(math.fsum(groups[col])/len(groups[col]),float(row['mean_original_residue_nll_nats']),rel_tol=1e-14,abs_tol=1e-14);observed=base[col]['status']=='observed';assert (row['reference_1GGQ_assembly1_observation_status']=='observed')==observed
  if not observed:assert row['reference_1GGQ_assembly1_interchain_contact_4_5_A']==''
 seqsummary=list(csv.DictReader((ROOT/'results/full_panel_comparison_v2/sequence_summary.tsv').read_text().splitlines(),delimiter='\t'))
 for row in seqsummary:
  vals=[value for pos,value in sequences[row['accession']]];mean=math.fsum(vals)/len(vals);assert math.isclose(mean,float(row['mean_nll_nats']),rel_tol=1e-14,abs_tol=1e-14);assert math.isclose(math.exp(mean),float(row['masked_pseudo_perplexity']),rel_tol=1e-14,abs_tol=1e-14)
 t=json.loads((ROOT/'results/full_panel_v1/timings.json').read_text());assert t['scoring_masked_examples']==6305 and t['scoring_forward_passes']==sum((len(s)+7)//8 for s in panel.values())==805 and t['warmup_masked_examples']==24 and t['total_forward_passes']==808
 for item in json.loads((ROOT/'provenance/frozen_inputs.json').read_text())['files']:assert sha(ROOT/item['package_path'])==item['sha256']
 evidence=json.loads((ROOT/'results/laptop_evidence_v1.json').read_text());assert len(evidence['columns'])==218 and len(evidence['sequences'])==30 and len(evidence['experimental_1GGQ_dimer_CA'])==324
 for col in evidence['columns']:
  if col['reference_1GGQ_A_observation_status']!='observed':
   assert col['reference_1GGQ_A_contact_4_5_A'] is None and col['reference_1GGQ_A_calculated_monomer_sasa_A2'] is None and col['reference_1GGQ_A_calculated_dimer_sasa_A2'] is None and col['reference_1GGQ_A_calculated_delta_sasa_A2'] is None
  else:
   mono=col['reference_1GGQ_A_calculated_monomer_sasa_A2'];dim=col['reference_1GGQ_A_calculated_dimer_sasa_A2'];loss=col['reference_1GGQ_A_calculated_delta_sasa_A2'];assert mono>=dim-1e-9 and math.isclose(mono-dim,loss,rel_tol=1e-9,abs_tol=1e-9)
  assert sum(col['original_residue_counts'].values())==col['observed_residue_count']
 return {'status':'PASS','scored_masks':6305,'distinct_sequences':30,'columns_independently_aggregated':218,'sequence_mean_and_exp_checks':30,'forward_count_check':805,'reference_observed_columns':sum(r['reference_1GGQ_assembly1_observation_status']=='observed' for r in columns),'input_hashes_verified':True,'source_scores_sha256':sha(ROOT/'results/full_panel_v1/residue_nll.tsv'),'method':'Independent CSV arithmetic (math.fsum) and exact mapping checks; no additional model inference.'}
if __name__=='__main__':
 j=validate();write_json(ROOT/'results/full_panel_validation.json',j);print(json.dumps(j,indent=2))
