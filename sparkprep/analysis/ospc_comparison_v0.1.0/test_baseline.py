import unittest
from baseline import column_stats,map_columns
class BaselineTests(unittest.TestCase):
 def test_identical(self):
  r=column_stats('AAAA');self.assertEqual((r['most_frequent_aa'],r['modal_fraction'],r['coverage']),( 'A',1,1))
 def test_variable_tie(self):
  r=column_stats('AACD');self.assertEqual(r['modal_fraction'],.5);self.assertEqual(column_stats('AC')['tied_modes'],'A,C')
 def test_gaps(self):
  r=column_stats('AA--');self.assertEqual((r['modal_fraction'],r['coverage'],r['gap_count']),(1,.5,2))
 def test_ambiguous_and_missing(self):
  r=column_stats('AX?B');self.assertEqual((r['contributing_sequences'],r['ambiguous_missing_count'],r['coverage']),(1,3,.25))
 def test_undefined(self):
  r=column_stats('--X?');self.assertIsNone(r['modal_fraction']);self.assertIsNone(r['most_frequent_aa']);self.assertEqual(r['coverage'],0)
 def test_mapping_insertion_and_unobserved(self):
  rs=[{'panel_sequence_position':1,'aa':'A','label_seq_id':2,'auth_residue_number':'38','insertion_code':'A','mapping_status':'observed'},{'panel_sequence_position':2,'aa':'C','label_seq_id':3,'auth_residue_number':'39','insertion_code':'','mapping_status':'unobserved'}]
  m=map_columns('A-C',rs,[column_stats('AA')]*3)
  self.assertEqual(m[0]['insertion_code'],'A');self.assertEqual(m[1]['status'],'reference_gap');self.assertIsNone(m[1]['structure_modal_fraction']);self.assertIsNone(m[2]['structure_modal_fraction'])
  with self.assertRaises(ValueError):map_columns('D-C',rs,[column_stats('AA')]*3)
if __name__=='__main__':unittest.main()

class FrozenReferenceTests(unittest.TestCase):
 def test_actual_frozen_reference_correspondence(self):
  import pathlib,json
  from cif_reader import parse_cif
  from baseline import read_fasta,reference_residues
  root=pathlib.Path(__file__).resolve().parent
  state=json.loads((root/'analysis_state.json').read_text());paths=state['manifest_paths'];inp=root/'frozen_inputs'
  seq=read_fasta(inp/paths['input_sequences.fasta'])['Q07337']
  residues=reference_residues(parse_cif(inp/paths['1GGQ.cif']),seq)
  self.assertEqual(len(residues),174);self.assertEqual(sum(r['has_observed_CA'] for r in residues),162)
  self.assertEqual(sum(r['panel_sequence_position'] is not None for r in residues),173)
  self.assertTrue(all(r['listed_unobserved']!=r['has_observed_CA'] for r in residues))
  self.assertEqual(len({(r['auth_chain'],r['auth_residue_number'],r['insertion_code']) for r in residues}),174)
