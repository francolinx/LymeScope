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
