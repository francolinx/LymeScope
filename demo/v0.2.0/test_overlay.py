"""Data-contract checks for the new overlay; not a browser-rendering test."""
import copy
import json
import math
import unittest
from build_overlay import FROZEN, _cif, assembly_one, build_context


class OverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_context()

    def test_population_sets_are_distinct(self):
        d = self.data["column_sets"]
        self.assertEqual([len(d[k]) for k in ("fully_covered", "mapped_observed", "intersection")], [202, 162, 159])
        self.assertEqual(set(d["intersection"]), set(d["fully_covered"]) & set(d["mapped_observed"]))

    def test_low_coverage_columns_never_gain_coordinates(self):
        for row in self.data["alignment_only"]:
            self.assertEqual(row["contributing_sequences"], 1)
            self.assertAlmostEqual(row["coverage"], 1/30)
            self.assertEqual(row["mapping_status"], "reference_gap")
            for reference in self.data["references"].values():
                self.assertFalse(any(r["alignment_column"] == row["column"] for r in reference["mapping"]))

    def test_cleavage_is_annotated_not_a_sequence_deletion(self):
        for annotation in self.data["annotations"].values():
            self.assertEqual((annotation["signal_start"], annotation["signal_end"], annotation["chain_start"]), (1, 18, 19))
            self.assertIn("not experimentally measured", annotation["evidence_note"])
        self.assertFalse(self.data["frozen_science_modified"])

    def test_assembly_validation_precedes_proxy(self):
        c = _cif.parse_cif(FROZEN / "inputs/reference_structures/1GGQ.cif")
        self.assertEqual(assembly_one(c)["polymer_chains"], ["A", "B"])
        bad = copy.deepcopy(c)
        bad["_pdbx_struct_oper_list.vector[1]"] = ["3.0"]
        with self.assertRaisesRegex(ValueError, "translation"): assembly_one(bad)

    def test_proxy_is_defined_only_on_observed_primary_coordinates(self):
        ref = self.data["references"]["1GGQ"]
        evaluated = 0
        for row in ref["mapping"]:
            value = row["nearest_other_chain_CA_A"]
            if row["xyz"] is None:
                self.assertIsNone(value)
                self.assertIsNone(row["CA_contact_proxy_within_8A"])
            else:
                self.assertTrue(math.isfinite(value) and value > 0)
                self.assertEqual(row["CA_contact_proxy_within_8A"], value <= 8)
                evaluated += 1
        self.assertEqual(evaluated, 162)
        self.assertIn("not measured solvent or antibody accessibility", ref["contact_proxy_status"])

    def test_secondary_reference_numbering_and_provenance(self):
        ref = self.data["references"]["1G5Z"]
        self.assertEqual(len(ref["mapping"]), 164)
        self.assertEqual([r["panel_sequence_position"] for r in ref["mapping"]], list(range(40, 204)))
        self.assertEqual([r["auth_residue_number"] for r in ref["mapping"]], list(map(str, range(40, 204))))
        self.assertEqual(ref["historical_deposited_correspondence"][0]["pdbx_db_accession"], "O31117")
        self.assertTrue(all(r["nearest_other_chain_CA_A"] is None for r in ref["mapping"]))

    def test_generated_data_matches_builder_and_published_spark_adapter(self):
        saved = json.loads((__import__('pathlib').Path(__file__).parent / "context.json").read_text())
        from spark_adapter import load_evidence
        expected = dict(self.data, spark_science=load_evidence(self.data), model_scoring='COMPLETED_PERSONAL_SPARK')
        from pathlib import Path
        expected['experimental_evidence'] = json.loads((Path(__file__).resolve().parents[2]/'docs/frontier_v0.3.0/experimental-evidence.json').read_text(encoding='utf-8'))
        self.assertEqual(saved, expected)
        self.assertEqual(saved['spark_science']['event_benchmark'], 'NOT_RUN')


if __name__ == "__main__":
    unittest.main(verbosity=2)
