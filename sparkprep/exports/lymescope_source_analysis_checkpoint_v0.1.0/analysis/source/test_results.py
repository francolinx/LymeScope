import unittest,pathlib,json,csv
from baseline import read_fasta,column_stats,reference_residues,map_columns
from cif_reader import parse_cif
ROOT=pathlib.Path(__file__).resolve().parent.parent
class ScientificResultsTests(unittest.TestCase):
 def setUp(self):self.d=json.loads((ROOT/'viewer_data.json').read_text())
 def test_roundtrip_and_identifiers(self):
  inp=read_fasta(ROOT/'inputs/input_sequences.fasta');aligned=read_fasta(ROOT/'aligned.fasta')
  self.assertEqual(list(inp),list(aligned));self.assertEqual(len(inp),30)
  for a,s in aligned.items():self.assertEqual(s.replace('-',''),inp[a])
 def test_all_saved_statistics(self):
  seqs=[r['aligned_sequence'] for r in self.d['sequences']]
  self.assertEqual(len(set(map(len,seqs))),1)
  for i,row in enumerate(self.d['columns']):
   expected=column_stats(s[i] for s in seqs)
   for k,v in expected.items():self.assertEqual(row[k],v)
   self.assertEqual(row['alignment_column'],i+1)
   self.assertEqual(row['contributing_sequences']+row['gap_count']+row['ambiguous_missing_count'],30)
 def test_real_structure_mapping(self):
  seqs=read_fasta(ROOT/'aligned.fasta');original=read_fasta(ROOT/'inputs/input_sequences.fasta')
  c=parse_cif(ROOT/'inputs/reference_structures/1GGQ.cif')
  residues=reference_residues(c,original['Q07337']);expected=map_columns(seqs['Q07337'],residues,self.d['columns'])
  self.assertEqual(expected,self.d['mapping'])
  observed=[r for r in expected if r['status']=='observed'];self.assertEqual(len(observed),162)
  self.assertEqual(len({(r['auth_chain'],r['auth_residue_number'],r['insertion_code']) for r in observed}),162)
  for r in expected:
   if r['status']!='observed':self.assertIsNone(r['structure_modal_fraction']);self.assertIsNone(r['structure_coverage'])
 def test_secondary_empty_category_explanation(self):
  s=json.loads((ROOT/'secondary_reference_check.json').read_text());self.assertEqual(s['observed_CA_residues'],164);self.assertFalse(s['unobserved_category_present']);self.assertFalse(s['scores_mapped']);self.assertEqual(s['exact_construct_matches'][0]['accession'],'Q44717')
 def test_saved_tsv_matches_viewer(self):
  rows=list(csv.DictReader((ROOT/'conservation_coverage.tsv').read_text().splitlines(),delimiter='\t'));self.assertEqual(len(rows),len(self.d['columns']))
  for a,b in zip(rows,self.d['columns']):
   self.assertEqual(int(a['alignment_column']),b['alignment_column']);self.assertEqual(float(a['coverage']),b['coverage']);self.assertEqual(float(a['modal_fraction']),b['modal_fraction'])
if __name__=='__main__':unittest.main()
