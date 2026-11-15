import unittest,sys,pathlib,math,csv,json
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'src'))
from common import *
from panel_sensitivity import stats
from dimer_context import contacts,transform
class ScienceTests(unittest.TestCase):
 def test_alignment_mapping_bijection(self):
  p=fasta(ROOT/'inputs/panel.fasta');a=fasta(ROOT/'inputs/aligned.fasta');rows=list(csv.DictReader((ROOT/'results/residue_alignment_mapping.tsv').read_text().splitlines(),delimiter='\t'))
  self.assertEqual(len(rows),6305);self.assertEqual(len({r['task_id'] for r in rows}),6305)
  for r in rows:self.assertEqual(p[r['accession']][int(r['sequence_position'])-1],r['original_residue']);self.assertEqual(a[r['accession']][int(r['alignment_column'])-1],r['original_residue'])
 def test_shard_partition(self):
  j=json.loads((ROOT/'results/shard_manifest.json').read_text());self.assertEqual(sum(j['two_node_masks']),6305);self.assertEqual(len(j['sequences']),30);self.assertEqual(set(x['two_node_shard'] for x in j['sequences']),{0,1})
 def test_sensitivity_defined_denominator(self):
  self.assertEqual(stats(['A','A','-'],0)['coverage'],2/3);self.assertEqual(stats(['A','A','-'],0)['modal_fraction'],1);self.assertIsNone(stats(['-'],0)['modal_fraction']);self.assertEqual(stats(['A','C'],0)['entropy_bits'],1)
 def test_cell_contacts_against_exhaustive_real_atoms(self):
  from cif_reader import parse_cif
  c=parse_cif(ROOT/'inputs/1GGQ.cif');atoms=cif_rows(c,'_atom_site');groups=[]
  for chain in ['A','B']:
   groups.append([{**a,'xyz':tuple(float(a['Cartn_'+k]) for k in ['x','y','z'])} for a in atoms if a['label_asym_id']==chain and a['label_atom_id']=='CA' and a['label_seq_id'] not in ['.','?']][:100])
  got={(r['left_label_seq_id'],r['right_label_seq_id']) for r in contacts(*groups)}
  expected={(a['label_seq_id'],b['label_seq_id']) for a in groups[0] for b in groups[1] if sum((x-y)**2 for x,y in zip(a['xyz'],b['xyz']))<=4.5**2};self.assertEqual(got,expected);self.assertTrue(got)
 def test_1g5z_symmetry(self):
  from cif_reader import parse_cif
  c=parse_cif(ROOT/'inputs/1G5Z.cif');op=cif_rows(c,'_pdbx_struct_oper_list')[1];p=(10.,20.,30.);self.assertEqual(transform(p,op),(54.158,-20.,30.));q=transform(transform(p,op),op)
  for a,b in zip(p,q):self.assertAlmostEqual(a,b)
 def test_frozen_input_hashes(self):
  for f in json.loads((ROOT/'provenance/frozen_inputs.json').read_text())['files']:self.assertEqual(sha(ROOT/f['package_path']),f['sha256'])
 def test_partial_pilot_cannot_masquerade_as_panel(self):
  from summarize_scores import run
  import tempfile
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaisesRegex(AssertionError,'Missing tasks'):run([ROOT/'results/pilot_v1/residue_nll.tsv'],pathlib.Path(tmp)/'uncreated')
 def test_comparison_rejects_two_matching_partial_panels(self):
  from compare_runs import compare
  p=ROOT/'results/pilot_v1/residue_nll.tsv'
  with self.assertRaisesRegex(AssertionError,'incomplete panel'):compare(p,p)
 def test_complete_model_results_independent_audit(self):
  from validate_full_results import validate
  result=validate();self.assertEqual(result['scored_masks'],6305);self.assertEqual(result['columns_independently_aggregated'],218)
 def test_unknown_structure_contact_is_never_false(self):
  rows=list(csv.DictReader((ROOT/'results/full_panel_comparison_v2/column_comparison.tsv').read_text().splitlines(),delimiter='\t'))
  self.assertEqual(sum(r['reference_1GGQ_assembly1_observation_status']=='observed' for r in rows),162)
  for row in rows:
   if row['reference_1GGQ_assembly1_observation_status']!='observed':self.assertEqual(row['reference_1GGQ_assembly1_interchain_contact_4_5_A'],'')
  self.assertEqual(rows[3]['reference_1GGQ_assembly1_interchain_contact_4_5_A'],'');self.assertEqual(rows[208]['reference_1GGQ_assembly1_interchain_contact_4_5_A'],'')
 def test_typed_evidence_structure_mapping(self):
  evidence=json.loads((ROOT/'results/laptop_evidence_v1.json').read_text());panel=fasta(ROOT/'inputs/panel.fasta');aligned=fasta(ROOT/'inputs/aligned.fasta');self.assertEqual(len(evidence['experimental_1GGQ_dimer_CA']),324)
  for atom in evidence['experimental_1GGQ_dimer_CA']:
   from dimer_context import AA
   pos=atom['sequence_position'];col=atom['alignment_column'];self.assertEqual(AA[atom['residue_name']],panel['Q07337'][pos-1]);self.assertEqual(panel['Q07337'][pos-1],aligned['Q07337'][col-1])
  self.assertIsNone(evidence['columns'][3]['reference_1GGQ_A_contact_4_5_A'])
 def test_average_rank_ties(self):
  from summarize_scores import rank
  self.assertEqual(rank([1,3,1,2]),[0.5,3.0,0.5,2.0])
 def test_calculated_sasa_analytical_spheres(self):
  from sasa_context import analytical_checks
  result=analytical_checks();self.assertLess(result['isolated_sphere_error_A2'],1e-10);self.assertLess(result['two_overlapping_spheres_max_abs_error_A2'],.15)
 def test_calculated_sasa_monotonicity_and_resolution(self):
  rows=list(csv.DictReader((ROOT/'results/sasa_dimer_context.tsv').read_text().splitlines(),delimiter='\t'));summary=json.loads((ROOT/'results/sasa_context_summary.json').read_text())
  for row in rows:self.assertGreaterEqual(float(row['delta_sasa_A2']),0);self.assertGreaterEqual(float(row['monomer_sasa_A2']),float(row['dimer_sasa_A2'])-1e-9)
  self.assertLess(summary['1GGQ_960_to_1920_relative_total_loss_difference'],.02)
  import math
  for calc in summary['calculations']:
   selected=[float(r['delta_sasa_A2']) for r in rows if r['pdb_id']==calc['pdb_id'] and int(r['sphere_points_per_atom'])==calc['sphere_points_per_atom']];self.assertAlmostEqual(math.fsum(selected),calc['total_sasa_loss_A2'],places=8)
class TorchMaskTests(unittest.TestCase):
 def test_mask_single_original_only(self):
  import torch
  from masked_nll import masked_batch
  ids=torch.tensor([[0,5,6,7,2]]);out=masked_batch(ids,[1,3],32)
  self.assertEqual(out.tolist(),[[0,32,6,7,2],[0,5,6,32,2]]);self.assertEqual(ids.tolist(),[[0,5,6,7,2]])
 def test_full_vocabulary_nll_known_uniform(self):
  import torch
  from masked_nll import original_nll
  logits=torch.zeros((2,5,33));out=original_nll(logits,torch.tensor([1,3]),torch.tensor([5,7]));self.assertTrue(torch.allclose(out,torch.full((2,),math.log(33)),atol=1e-6,rtol=0));logits[0,1,5]=2;got=original_nll(logits,torch.tensor([1,3]),torch.tensor([5,7]));self.assertAlmostEqual(got[0].item(),math.log(math.exp(2)+32)-2,places=6)
if __name__=='__main__':unittest.main()
