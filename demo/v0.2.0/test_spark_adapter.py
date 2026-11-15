"""Integration acceptance tests on published data; no model inference."""
import copy
import json
import unittest
from build_overlay import build_context
from spark_adapter import EXPERIMENT, SASA_KEYS, load_evidence, validate_evidence


class SparkAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.context = build_context()
        cls.imported = load_evidence(cls.context)
        cls.evidence = cls.imported['evidence']

    def test_published_counts_and_current_aggregate(self):
        self.assertIn('full_panel_comparison_v2', self.imported['current_comparison'])
        self.assertEqual(sum(x['mask_count'] for x in self.evidence['sequences']), 6305)
        self.assertEqual(self.evidence['personal_timing']['scoring_forward_passes'], 805)
        self.assertEqual(self.imported['sensitivity']['panel_designs'], 239)
        self.assertEqual(self.imported['event_benchmark'], 'NOT_RUN')

    def test_unknown_is_not_false_or_zero(self):
        for column in (1, 154, 173, 209):
            row = self.evidence['columns'][column-1]
            self.assertIsNone(row['reference_1GGQ_A_contact_4_5_A'])
            self.assertTrue(all(row[k] is None for k in SASA_KEYS))
        self.assertIs(self.evidence['columns'][176]['reference_1GGQ_A_contact_4_5_A'], False)
        self.assertEqual(self.evidence['columns'][176][SASA_KEYS[2]], 0)

    def test_reject_loss_of_null_semantics(self):
        for key, value in [('reference_1GGQ_A_contact_4_5_A', False), (SASA_KEYS[2], 0)]:
            bad = copy.deepcopy(self.evidence)
            bad['columns'][153][key] = value
            with self.assertRaisesRegex(ValueError, 'must remain null'):
                validate_evidence(bad, self.context)

    def test_reject_superseded_aggregate(self):
        bad = copy.deepcopy(self.evidence)
        bad['recommended_files']['column_comparison'] = 'results/full_panel_comparison_v1/column_comparison.tsv'
        with self.assertRaisesRegex(ValueError, 'current v2'):
            validate_evidence(bad, self.context)

    def test_reject_incomplete_column_ranking(self):
        bad = copy.deepcopy(self.evidence)
        bad['columns'][153]['agreement_minus_predictability_percentile'] = 0
        with self.assertRaisesRegex(ValueError, 'Rank eligibility'):
            validate_evidence(bad, self.context)

    def test_reject_unbatched_call_estimate(self):
        bad = copy.deepcopy(self.evidence)
        bad['personal_timing']['scoring_forward_passes'] = 789
        with self.assertRaisesRegex(ValueError, 'call inventory'):
            validate_evidence(bad, self.context)

    def test_illustrative_values_and_sensitivity_match_saved_results(self):
        self.assertAlmostEqual(self.evidence['columns'][57]['mean_masked_nll_nats'], 3.9649845441182454)
        self.assertAlmostEqual(self.evidence['columns'][176]['mean_masked_nll_nats'], 4.011350917816162, places=5)
        self.assertAlmostEqual(self.imported['sensitivity']['full_panel_agreement_predictability_spearman_rho'], .13469642371821905)

    def test_rendered_payload_preserves_source_columns(self):
        saved = json.loads((__import__('pathlib').Path(__file__).parent/'context.json').read_text())
        self.assertEqual(saved['spark_science']['evidence'], self.evidence)


if __name__ == '__main__':
    unittest.main()
