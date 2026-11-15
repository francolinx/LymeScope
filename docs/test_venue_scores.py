"""CPU-only saved-data/fixture checks; never actual venue inference."""
import csv
import math
import tempfile
import unittest
from pathlib import Path
from compare_venue_scores import PACKAGE,compare,deviations,published


class VenueAcceptanceTests(unittest.TestCase):
    def test_saved_6305_scores_against_saved_v2_merge(self):
        result=compare(PACKAGE/'results/full_panel_v1/residue_nll.tsv',PACKAGE/'results/full_panel_comparison_v2/residue_nll_merged.tsv')
        self.assertEqual(result['task_count'],6305)
        self.assertEqual(result['max_absolute_deviation_nats'],0)
        self.assertEqual(result['max_relative_deviation'],0)
        self.assertIsNone(result['event_speedup'])

    def test_relative_errors_and_zero_denominator_are_explicit(self):
        result=deviations([(2.,2.00001),(0.,0.),(0.,0.00001)])
        self.assertIsNone(result['max_relative_deviation'])
        self.assertEqual(result['undefined_or_overflow_relative_count'],1)
        self.assertEqual(result['equal_zero_reference_count'],1)
        self.assertAlmostEqual(result['max_finite_relative_deviation'],0.000005)

    def test_nonfinite_negative_or_out_of_tolerance_fail(self):
        for pair in [(1,math.nan),(math.inf,1),(1,-1),(1,1.01)]:
            with self.subTest(pair=pair),self.assertRaises(ValueError):deviations([pair])

    def test_partial_pilot_is_not_accepted(self):
        reference=PACKAGE/'results/pilot_v1/residue_nll.tsv'
        rows=list(published.load(reference).values())
        with tempfile.TemporaryDirectory(prefix='lymescope-venue-fixture-') as temp:
            candidate=Path(temp)/'partial.tsv'
            with candidate.open('w',newline='') as handle:
                writer=csv.DictWriter(handle,fieldnames=rows[0],delimiter='\t');writer.writeheader();writer.writerows(rows[:-1])
            with self.assertRaisesRegex(ValueError,'coverage'):compare(reference,candidate,pilot=True)

    def test_matching_but_corrupted_reference_identity_is_rejected(self):
        reference=PACKAGE/'results/pilot_v1/residue_nll.tsv'
        rows=list(published.load(reference).values());rows[0]['original_residue']='A'
        with tempfile.TemporaryDirectory(prefix='lymescope-venue-fixture-') as temp:
            candidate=Path(temp)/'wrong-identity.tsv'
            with candidate.open('w',newline='') as handle:
                writer=csv.DictWriter(handle,fieldnames=rows[0],delimiter='\t');writer.writeheader();writer.writerows(rows)
            with self.assertRaisesRegex(ValueError,'frozen identity'):compare(candidate,candidate,pilot=True)


if __name__=='__main__':unittest.main(verbosity=2)
