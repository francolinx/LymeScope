"""Reference, namespace, geometry, missingness and numerical tests; no model inference or network."""
import unittest, pathlib, sys, csv, json, math, hashlib
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from common import fasta, sha
from map_complex import prepare, exact_construct_mapping, choose_atoms, expected_atoms
from build_site_table import union_observed
from exploratory_analysis import auc, metrics, fit_predict, design

class MappingTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.prepared = {code: prepare(code) for code in ['9BIF', '7UIJ']}
        cls.table = list(csv.DictReader((ROOT / 'EXPERIMENTAL_MAPPING.tsv').read_text().splitlines(), delimiter='\t'))

    def test_all_reused_input_bytes(self):
        for r in json.loads((ROOT / 'provenance/reused_inputs.json').read_text())['copies']:
            self.assertEqual(sha(ROOT / r['new_input_path']), r['sha256'])

    def test_all_official_source_hashes(self):
        for r in json.loads((ROOT / 'provenance/source_receipts.json').read_text()):
            self.assertEqual(sha(ROOT / r['file']), r['sha256'])
            self.assertEqual((ROOT / r['file']).stat().st_size, r['bytes'])

    def test_predeclaration_immutable(self):
        p = json.loads((ROOT / 'provenance/predeclaration.json').read_text())
        self.assertEqual(sha(ROOT / 'EXPERIMENT_QUESTION.md'), p['question_sha256'])
        self.assertEqual(p['primary_pdb'], '9BIF')
        self.assertEqual(p['L2_lambda'], 1.0)

    def test_exact_natural_construct_both_complexes(self):
        panel = fasta(ROOT / 'inputs/frozen_panel.fasta')
        record = json.loads((ROOT / 'inputs/Q07337_frozen_uniprot_record.json').read_text())
        self.assertEqual(panel['Q07337'], record['sequence']['value'])
        for code, (c, instances, mapping, scheme, columns, summary) in self.prepared.items():
            self.assertEqual(len(mapping), 164)
            self.assertEqual((mapping[1], mapping[164]), (38, 201))
            self.assertEqual(summary['construct_length'], 164)

    def test_reference_rejects_other_real_natural_sequence(self):
        panel = fasta(ROOT / 'inputs/frozen_panel.fasta')
        construct = panel['Q07337'][37:201]
        other = next((seq for key, seq in panel.items() if key != 'Q07337' and construct not in seq))
        with self.assertRaises(ValueError):
            exact_construct_mapping(construct, other)

    def test_label_author_namespaces(self):
        primary = self.prepared['9BIF'][1]
        secondary = self.prepared['7UIJ'][1]
        self.assertEqual([(i['label_chain'], i['auth_chains']) for i in primary if i['role'] == 'OspC'], [('C', ['A']), ('D', ['B'])])
        self.assertEqual([(i['label_chain'], i['auth_chains']) for i in secondary if i['role'] == 'OspC'], [('E', ['C']), ('F', ['D'])])

    def test_no_antigen_atoms_count_as_Fab(self):
        for code, (_, insts, *rest) in self.prepared.items():
            antigen = {i['instance'] for i in insts if i['role'] == 'OspC'}
            fab = {i['instance'] for i in insts if i['role'] == 'Fab'}
            self.assertFalse(antigen & fab)
            self.assertEqual((len(antigen), len(fab)), (2, 4))
            for r in csv.DictReader((ROOT / 'results' / f'{code}_FAB_CONTACT_PAIRS_5A.tsv').read_text().splitlines(), delimiter='\t'):
                self.assertIn(r['OspC_instance'], antigen)
                self.assertIn(r['Fab_instance'], fab)
                self.assertLessEqual(float(r['min_distance_A']), 5.0 + 1e-10)

    def test_missing_labels_not_negative_labels(self):
        for r in self.table:
            if r['complex_complete_copies'] != '2':
                self.assertEqual(r['strict_contact_union_4_5_A'], '')
            if r['complex_mapped_copies'] == '0':
                self.assertEqual(r['observed_contact_union_4_5_A'], '')
        self.assertEqual(union_observed([False, None]), None)
        self.assertEqual(union_observed([True, None]), True)
        self.assertFalse(union_observed([False, False]))

    def test_depositor_unobserved_records_match(self):
        from common import rows
        for code, (c, instances, *rest) in self.prepared.items():
            for inst in instances:
                expected = {int(r['seq_id']) for r in rows(c, '_pdbx_poly_seq_scheme') if r['asym_id'] == inst['label_chain']}
                seen = {int(a['label_seq_id']) for a in inst['atoms']}
                missing = {int(r['label_seq_id']) for r in rows(c, '_pdbx_unobs_or_zero_occ_residues') if r['PDB_model_num'] == '1' and r['label_asym_id'] == inst['label_chain']}
                self.assertEqual(expected - seen, missing)

    def test_strict_site_counts(self):
        for code, contacts in [('9BIF', 31), ('7UIJ', 25)]:
            rows = [r for r in self.table if r['pdb_id'] == code and r['strict_eligible'] == 'True']
            self.assertEqual(len(rows), 152)
            self.assertEqual(sum((r['strict_contact_union_4_5_A'] == 'True' for r in rows)), contacts)

    def test_contact_types_are_distinct(self):
        rows = [r for r in self.table if r['pdb_id'] == '9BIF' and r['strict_eligible'] == 'True']
        self.assertTrue(any((r['strict_contact_union_4_5_A'] == 'True' and r['reference_dimer_contact'] == 'False' for r in rows)))
        self.assertTrue(any((r['strict_contact_union_4_5_A'] == 'False' and r['reference_dimer_contact'] == 'True' for r in rows)))

    def test_coordinate_derived_distance_audit(self):
        audit = json.loads((ROOT / 'results/INDEPENDENT_GEOMETRY_AUDIT.json').read_text())
        self.assertEqual(sum((x['residue_distance_minima_checked'] for x in audit)), 625)
        for row in audit:
            self.assertLess(row['max_abs_distance_error_A'], 1e-10)
            self.assertTrue(row['all_fixed_cutoff_labels_match'])

    def test_alternate_selection_fixture(self):
        base = {'pdbx_PDB_model_num': '1', 'type_symbol': 'C', 'occupancy': '1', 'label_asym_id': 'test', 'label_seq_id': '1', 'label_atom_id': 'CA', 'label_alt_id': '.'}
        records = [base, {**base, 'label_atom_id': 'CB', 'label_alt_id': 'A', 'occupancy': '0.6'}, {**base, 'label_atom_id': 'CB', 'label_alt_id': 'B', 'occupancy': '0.4'}]
        atoms, audit = choose_atoms(records)
        self.assertEqual({a['label_alt_id'] for a in atoms}, {'.', 'A'})
        self.assertEqual(audit[0]['selected_alt'], 'A')

    def test_expected_canonical_heavy_atoms(self):
        self.assertEqual(expected_atoms('G'), {'N', 'CA', 'C', 'O'})
        self.assertIn('SG', expected_atoms('C'))
        self.assertEqual(len(expected_atoms('W')), 14)

    def test_literature_region_is_not_contacts(self):
        r = list(csv.DictReader((ROOT / 'results/8C1_LITERATURE_REGION.tsv').read_text().splitlines(), delimiter='\t'))
        self.assertEqual(len(r), 21)
        self.assertTrue(all((x['antibody_contact_status'] == '' for x in r)))
        self.assertEqual({int(x['Q07337_position']) for x in r}, set(range(130, 151)))

    def test_typed_adapter_nulls(self):
        data = json.loads((ROOT / 'results/FRONTIER_EVIDENCE.json').read_text())
        self.assertEqual(len(data['sites']), 436)
        for r in data['sites']:
            if r['complex_mapped_copies'] == 0:
                self.assertIsNone(r['strict_contact_union_4_5_A'])
        self.assertTrue(all((r['antibody_contact_status'] is None for r in data['literature_region_8C1'])))

class NumericalTests(unittest.TestCase):

    def test_AUC_known_orders_and_ties(self):
        self.assertEqual(auc([0, 1], [0, 1]), 1.0)
        self.assertEqual(auc([0, 1], [1, 0]), 0.0)
        self.assertEqual(auc([0, 1], [0.5, 0.5]), 0.5)
        self.assertIsNone(auc([0, 0], [0, 1]))

    def test_metrics_analytical_constant(self):
        m = metrics([0, 1], [0.5, 0.5])
        self.assertAlmostEqual(m['brier'], 0.25)
        self.assertAlmostEqual(m['log_loss'], math.log(2))

    def test_intercept_MLE(self):
        x = np.empty((3, 0))
        p, fit = fit_predict(x, np.array([0.0, 1.0, 1.0]), np.empty((2, 0)), [])
        np.testing.assert_allclose(p, 2 / 3, atol=1e-10)

    def test_single_class_fails_explicitly(self):
        with self.assertRaises(ValueError):
            fit_predict(np.empty((3, 0)), np.zeros(3), np.empty((1, 0)), [])

    def test_primary_effect_recomputed_from_OOF(self):
        rows = list(csv.DictReader((ROOT / 'results/BLOCKED_OOF_PREDICTIONS.tsv').read_text().splitlines(), delimiter='\t'))
        a = json.loads((ROOT / 'ANALYSIS_RESULTS.json').read_text())['primary']
        briers = {}
        for model in ['B2', 'B3', 'B4']:
            selected = [r for r in rows if r['pdb_id'] == '9BIF' and r['cutoff_A'] == '4.5' and (r['model'] == model)]
            self.assertEqual(len(selected), 152)
            self.assertEqual(len({r['alignment_column'] for r in selected}), 152)
            brier = math.fsum(((float(r['oof_probability']) - float(r['observed_antibody_contact'] == 'True')) ** 2 for r in selected)) / 152
            briers[model] = brier
            self.assertAlmostEqual(brier, a['models'][model]['oof_metrics']['brier'], places=14)
        self.assertAlmostEqual(briers['B3'] - briers['B2'], a['primary_delta_oof_brier_B3_minus_B2'], places=14)

    def test_independent_optimizers_agree(self):
        a = json.loads((ROOT / 'results/INDEPENDENT_STATISTICS_AUDIT.json').read_text())
        self.assertEqual(a['fold_fits_checked'], 96)
        self.assertLess(a['max_probability_difference'], 1e-05)

    def test_training_only_standardization(self):
        table = [r for r in csv.DictReader((ROOT / 'EXPERIMENTAL_MAPPING.tsv').read_text().splitlines(), delimiter='\t') if r['pdb_id'] == '9BIF' and r['strict_eligible'] == 'True']
        x, names, cont = design(table, 'B2')
        y = np.array([r['strict_contact_union_4_5_A'] == 'True' for r in table], dtype=float)
        train = np.arange(100)
        test = np.arange(100, len(y))
        pred, info = fit_predict(x[train], y[train], x[test], cont)
        for j in cont:
            self.assertAlmostEqual(info['continuous_means'][j], x[train, j].mean())

    def test_numeric_fallback_preserves_fixed_objective(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        table = [r for r in csv.DictReader((ROOT / 'EXPERIMENTAL_MAPPING.tsv').read_text().splitlines(), delimiter='\t') if r['pdb_id'] == '9BIF' and r['strict_eligible'] == 'True']
        x, names, continuous = design(table, 'B1')
        y = np.array([r['strict_contact_union_4_5_A'] == 'True' for r in table], dtype=float)
        expected, _ = fit_predict(x, y, x, continuous)
        with patch('exploratory_analysis.minimize', return_value=SimpleNamespace(success=False, message='TEST_FORCED_NON_SUCCESS')):
            actual, info = fit_predict(x, y, x, continuous)
        np.testing.assert_allclose(actual, expected, atol=1e-05, rtol=0)
        self.assertEqual(info['solver_used'], 'Newton_fallback_same_objective')
        self.assertEqual(info['initial_solver_failure'], 'TEST_FORCED_NON_SUCCESS')

    def test_primary_unchanged_after_secondary_solver_recovery(self):
        old = json.loads((ROOT / 'provenance/ANALYSIS_BEFORE_SOLVER_RECOVERY.json').read_text())['primary']
        new = json.loads((ROOT / 'ANALYSIS_RESULTS.json').read_text())['primary']
        self.assertEqual(old['primary_delta_oof_brier_B3_minus_B2'], new['primary_delta_oof_brier_B3_minus_B2'])
        for name in old['models']:
            self.assertEqual(old['models'][name]['oof_metrics'], new['models'][name]['oof_metrics'])

    def test_fold_assignments_and_guards(self):
        a = json.loads((ROOT / 'ANALYSIS_RESULTS.json').read_text())['primary']
        rows = [r for r in csv.DictReader((ROOT / 'EXPERIMENTAL_MAPPING.tsv').read_text().splitlines(), delimiter='\t') if r['pdb_id'] == '9BIF' and r['strict_eligible'] == 'True']
        for fold in a['models']['B3']['folds']:
            test = [r for r in rows if int(r['fixed_reference_block']) == fold['block']]
            train = [r for r in rows if int(r['alignment_column']) < fold['train_guard_low'] or int(r['alignment_column']) > fold['train_guard_high']]
            self.assertEqual(len(train), fold['train_n'])
            self.assertEqual(len(test), fold['test_n'])
            self.assertFalse({r['alignment_column'] for r in train} & {r['alignment_column'] for r in test})
if __name__ == '__main__':
    unittest.main()
