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


