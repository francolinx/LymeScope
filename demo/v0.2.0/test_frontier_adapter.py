"""Offline import regression tests; saved experiments are not new inference."""
import copy
import json
import unittest
from pathlib import Path
from frontier_adapter import COMMIT, EXPERIMENT, load_evidence, validate

ROOT = Path(__file__).resolve().parents[2]


class FrontierAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = json.loads((EXPERIMENT / 'results/FRONTIER_EVIDENCE.json').read_text(encoding='utf-8'))
        cls.columns = json.loads((ROOT / 'sparkprep/experiments/stretch_v0.2.0_20261115T072916Z/results/laptop_evidence_v1.json').read_text(encoding='utf-8'))['columns']
        cls.loaded = load_evidence(cls.columns)

    def test_imported_negative_result_matches_original_metric_table(self):
        self.assertEqual(self.loaded['source_commit'], COMMIT)
        metrics = self.loaded['primary_metrics']
        self.assertAlmostEqual(metrics['B2']['brier'], 0.1686336055872799, places=14)
        self.assertAlmostEqual(metrics['B3']['brier'], 0.1740219332031673, places=14)
        self.assertLess(metrics['B3']['auroc'], metrics['B2']['auroc'])
        self.assertEqual(self.loaded['additional_model_calls'], 0)

    def test_observed_contact_and_strict_eligibility_remain_separate(self):
        b11 = self.loaded['complexes']['9BIF']
        self.assertEqual((b11['eligible_contact_count'], b11['eligible_count'], b11['observed_contact_count']), (31,152,32))
        self.assertTrue(b11['sites'][74]['observed_contact_union_4_5_A'])
        self.assertFalse(b11['sites'][74]['strict_eligible'])
        self.assertIsNone(b11['sites'][153]['observed_contact_union_4_5_A'])
        b5 = self.loaded['complexes']['7UIJ']
        self.assertNotEqual([s['alignment_column'] for s in b11['sites'] if s['strict_eligible']],
                            [s['alignment_column'] for s in b5['sites'] if s['strict_eligible']])

    def test_reject_unknown_converted_to_false(self):
        data = copy.deepcopy(self.source)
        data['sites'][153]['observed_contact_union_4_5_A'] = False
        with self.assertRaisesRegex(ValueError, 'Unmapped contact'):
            validate(data, self.columns)

    def test_reject_cross_complex_namespace_and_duplicate_column(self):
        for key, value in [('assembly_id', 2), ('alignment_column', 2)]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.source); data['sites'][0][key] = value
                with self.assertRaises(ValueError): validate(data, self.columns)

    def test_reject_reused_nll_or_geometry_changes(self):
        for key, value in [('mean_nll_nats', 0.0), ('reference_dimer_sasa_A2', 0.0)]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.source); data['sites'][0][key] = value
                with self.assertRaisesRegex(ValueError, 'Reused v2 field'):
                    validate(data, self.columns)

    def test_literature_region_cannot_be_promoted_to_contacts(self):
        data = copy.deepcopy(self.source)
        data['literature_region_8C1'][0]['antibody_contact_status'] = True
        with self.assertRaisesRegex(ValueError, 'literature-only'): validate(data, self.columns)

    def test_reject_positive_relabeling_of_primary_result(self):
        data = copy.deepcopy(self.source)
        data['primary_summary']['primary_delta_oof_brier_B3_minus_B2'] *= -1
        with self.assertRaisesRegex(ValueError, 'Negative primary result'): validate(data, self.columns)


if __name__ == '__main__': unittest.main(verbosity=2)
