"""Standard-library fixtures only. These tests do NOT validate real inference."""
import copy
import datetime
import itertools
import json
import math
import tempfile
import unittest
from pathlib import Path
from core import (AA, FROZEN, assert_token_offsets, forward_calls, load_panel, log_probability,
                  object_hash, position_map, score_sequence, sequence_summary, standard_positions, write_new)
from ingest import close_float, compare_runs, deviations, validate_plan, validate_receipts, validate_rows
from planning import SETTINGS, TOLERANCES, grouping_plan, make_plan
from run_worker import authorize, source_identity
from sensitivity import aggregate, average_ranks, leave_out, rank_comparison


class FixtureTokenizer:
    cls_token_id, eos_token_id, pad_token_id, mask_token_id, unk_token_id = 0, 1, 2, 3, 4
    vocab = {aa: i for i, aa in enumerate(sorted(AA), 5)}

    def convert_tokens_to_ids(self, chars):
        return [self.vocab.get(c, self.unk_token_id) for c in chars]

    def encode(self, seq, add_special_tokens=True):
        return [self.cls_token_id] + self.convert_tokens_to_ids(seq) + [self.eos_token_id]


class FixtureBackend:
    """Artificial logits exercise orchestration, never a protein model."""
    def __init__(self):
        self.tokenizer = FixtureTokenizer()
        self.calls = []

    def predict(self, examples, offsets, targets, phase):
        self.calls.append((copy.deepcopy(examples), list(offsets), phase))
        for example, offset in zip(examples, offsets):
            assert example.count(self.tokenizer.mask_token_id) == 1
            assert example[offset] == self.tokenizer.mask_token_id
        return [log_probability([10000.0 + i / 10 for i in range(25)], target) for target in targets]


def fixture_run(plan, mode):
    sequences, alignment = load_panel()
    shards = plan["one_node_shards"] if mode == "one" else plan["two_node_shards"]
    lock = json.loads((Path(__file__).parent / "model_lock.json").read_text())
    receipts = []
    assignments = []
    for rank, assigned in enumerate(shards):
        rows = []
        for a in assigned:
            mapping = position_map(alignment[a])
            for pos in plan["tasks"][a]:
                value = -1 - (pos % 7) / 10
                rows.append({"accession": a, "sequence_position": pos, "token_offset": pos,
                             "alignment_column": mapping[pos], "residue": sequences[a][pos-1],
                             "log_probability": value, "negative_log_probability": -value})
        receipt = {"evidence_kind": "synthetic_fixture", "mode": mode, "rank": rank,
                   "plan_sha256": plan["plan_sha256"], "source_sha256": plan["source_sha256"],
                   "model_id": plan["model_id"], "model_revision": plan["model_revision"],
                   "settings": SETTINGS, "input_hashes": plan["input_hashes"], "batch_size": plan["batch_size"],
                   "sequence_sha256": plan["sequence_sha256"], "maximum_sequence_length": plan["maximum_sequence_length"], "failed_positions": [],
                   "assets": {"model.safetensors": lock["files"][0]["sha256"]}, "versions": {"fixture": "no libraries loaded"},
                   "runtime_settings": {**SETTINGS, "device": "cuda:0", "model_eval": True, "inference_mode": True},
                   "hardware": {"fixture": True},
                   "run_id": "SYNTHETIC_" + mode, "container_hostname": "FIXTURE_CONTAINER_" + str(rank),
                   "assigned_accessions": assigned, "rows": rows,
                   "forward_calls": {"scoring": forward_calls([len(plan["tasks"][a]) for a in assigned], plan["batch_size"]), "warmup": 1, "pilot": 0},
                   "timing": {"asset_verification_seconds": 0.1, "loading_seconds": 1, "model_transfer_seconds": 0.1,
                              "worker_until_receipt_seconds": 4,
                              "phases": {phase: {"host_to_device_seconds": 0.1, "compute_seconds": 1, "device_to_host_seconds": 0.1} for phase in ("scoring", "warmup")}}}
        receipts.append(receipt)
        receipt["successful_forward_calls"] = dict(receipt["forward_calls"])
        receipt["successful_masked_examples"] = {"scoring": len(rows), "pilot": 0, "warmup": 1}
        assignments.append({"rank": rank, "container_hostname": receipt["container_hostname"],
                            "container_id": "FIXTURE_ID_" + str(rank), "physical_node_id": plan["expected_physical_nodes"][mode][rank]})
    scheduler = {"source": "scheduler_export", "run_id": "SYNTHETIC_" + mode, "workflow_id": "FIXTURE_WORKFLOW", "job_id": "FIXTURE_JOB",
                 "ranks": assignments, "submitted_at": "2026-11-15T08:00:00-06:00", "started_at": "2026-11-15T08:00:01-06:00",
                 "finished_at": "2026-11-15T08:00:05-06:00", "export_completed_at": "2026-11-15T08:00:06-06:00"}
    scheduler.update(queued_at="2026-11-15T08:00:00-06:00", dequeued_at="2026-11-15T08:00:01-06:00",
                     startup_started_at="2026-11-15T08:00:01-06:00", startup_finished_at="2026-11-15T08:00:02-06:00")
    return receipts, scheduler


class ScoringTests(unittest.TestCase):
    def test_per_sequence_rounding(self):
        self.assertEqual(forward_calls([17, 17], 16), 4)
        self.assertNotEqual(forward_calls([17, 17], 16), math.ceil(34/16))
        for bad in (0, -1, 1.5):
            with self.assertRaises(ValueError): forward_calls([1], bad)

    def test_stable_log_softmax(self):
        self.assertAlmostEqual(log_probability([10000, 10000], 0), -math.log(2))
        self.assertAlmostEqual(log_probability([-10000, -10000], 0), -math.log(2))
        self.assertAlmostEqual(log_probability([10000, -10000], 1), -20000)
        with self.assertRaises(ValueError): log_probability([float("nan")], 0)

    def test_single_mask_offsets_and_no_gap_special_scores(self):
        backend = FixtureBackend()
        rows, counts = score_sequence("FIXTURE", "ACXDE", "A-CXDE", backend, 3)
        self.assertEqual([r["sequence_position"] for r in rows], [1, 2, 4, 5])
        self.assertEqual([r["alignment_column"] for r in rows], [1, 3, 5, 6])
        self.assertEqual(counts["forward_calls"], 2)
        self.assertEqual([len(x[0]) for x in backend.calls], [3, 1])
        self.assertEqual({r["residue"] for r in rows}, set("ACDE"))

    def test_warmup_and_pilot_are_separate_calls(self):
        backend = FixtureBackend()
        for phase in ("warmup", "pilot", "scoring"):
            _, counts = score_sequence("FIXTURE", "AC", "AC", backend, 2, phase=phase)
            self.assertEqual(counts["phase"], phase)
        self.assertEqual([x[2] for x in backend.calls], ["warmup", "pilot", "scoring"])

    def test_offset_assertions_reject_bos_eos_truncation_and_padding(self):
        tokenizer = FixtureTokenizer()
        good = tokenizer.encode("AC")
        for bad in (good[:-1], [1]+good[1:], good[:2]+[2]+good[3:], good[1:]+[1]):
            with self.assertRaises(ValueError): assert_token_offsets("AC", bad, tokenizer)

    def test_subset_pseudoperplexity_label_and_exact_positions(self):
        rows, _ = score_sequence("FIXTURE", "ACDE", "ACDE", FixtureBackend(), 16, [2, 4])
        summary = sequence_summary("ACDE", rows)
        self.assertEqual(summary["scope"], "explicit_subset_of_observed_standard_residues")
        self.assertEqual(summary["scored_positions"], [2, 4])
        self.assertAlmostEqual(summary["pseudo_perplexity"], math.exp(summary["mean_negative_log_probability"]))
        with self.assertRaises(ValueError): standard_positions("AC", [1, 1])

    def test_nonfinite_backend_score_rejected(self):
        backend = FixtureBackend()
        backend.predict = lambda *a, **k: [float("nan")]
        with self.assertRaises(ValueError): score_sequence("FIXTURE", "A", "A", backend, 1)

    def test_results_are_append_only_and_frozen_writes_refused(self):
        with self.assertRaises(ValueError): write_new(FROZEN / "NEVER_WRITE.json", {})
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "fixture.json"
            write_new(p, {"fixture": True})
            with self.assertRaises(FileExistsError): write_new(p, {})


class SensitivityTests(unittest.TestCase):
    alignment = {"a": "AA-A", "b": "AA-C", "c": "ACA-", "d": "ACAA"}

    def test_full_coverage_invariant_all_nonempty_subsets(self):
        original = aggregate(self.alignment)
        for count in range(1, 4):
            for removed in itertools.combinations(self.alignment, count):
                fold = leave_out(self.alignment, [], removed, {"test": "fixture"})
                for a, b in zip(original, fold["columns"]):
                    if a["full_coverage"]: self.assertEqual(b["coverage"], 1)
                    if a["full_coverage"] and a["modal_fraction"] == 1:
                        self.assertEqual(b["modal_fraction"], 1)  # Mathematical invariant, not robustness evidence.
                    self.assertEqual(b["total_sequences"], 4-count)
                self.assertEqual(fold["additional_model_forward_calls"], 0)

    def test_incomplete_coverage_and_newly_apparent_conservation(self):
        fold = leave_out(self.alignment, [], ["a", "b"], {"original_groups": ["fixture"]})
        self.assertEqual(fold["columns"][2]["coverage"], 1)
        self.assertEqual(fold["changes"][2]["coverage_change_at_originally_incomplete_column"], .5)
        self.assertTrue(fold["changes"][1]["newly_apparent_full_coverage_conservation"])
        self.assertEqual(fold["grouping_provenance"], {"original_groups": ["fixture"]})
        self.assertEqual(fold["rank_comparisons"]["conservation"]["common_eligible_columns"], [1, 2])

    def test_gapped_column_aggregate_is_descriptive_only(self):
        rows = [{"accession": "c", "alignment_column": 3, "log_probability": -2}]
        columns = aggregate(self.alignment, rows)
        self.assertEqual(columns[2]["mean_negative_log_probability"], 2)
        self.assertEqual(columns[2]["model_score_count"], 1)
        self.assertFalse(columns[2]["full_coverage_model_eligible"])

    def test_average_ties_common_population_and_undefined_correlation(self):
        self.assertEqual(average_ranks([1, 1, 4]), [1.5, 1.5, 3])
        comparison = rank_comparison({1: 1, 2: 1, 3: 9}, {1: 2, 2: 2, 3: 8}, [1, 2, 3])
        self.assertAlmostEqual(comparison["spearman_rho"], 1)
        self.assertIsNone(rank_comparison({1: 1}, {1: 2}, [1])["spearman_rho"])
        self.assertNotIn("p_value", comparison)

    def test_score_reuse_ignores_removed_sequences_without_mutation(self):
        rows = [{"accession": a, "alignment_column": 1, "log_probability": -i-1} for i, a in enumerate(self.alignment)]
        before = copy.deepcopy(rows)
        fold = leave_out(self.alignment, rows, ["a"], {"fixture": True})
        self.assertEqual(fold["columns"][0]["mean_negative_log_probability"], 3)
        self.assertEqual(rows, before)


class IngestionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = make_plan()

    def validate_fixture(self, receipts, scheduler, mode="one"):
        return validate_receipts(self.plan, receipts, mode, scheduler, allow_fixture=True)

    def test_plan_exact_task_coverage_and_balanced_shards(self):
        validate_plan(self.plan)
        changed = copy.deepcopy(self.plan)
        changed["model_lock_sha256"] = "wrong"
        changed["plan_sha256"] = object_hash({k: v for k, v in changed.items() if k != "plan_sha256"})
        with self.assertRaisesRegex(ValueError, "Model lock"):
            validate_plan(changed)
        sequences, _ = load_panel()
        self.assertEqual(self.plan["masked_examples"], sum(len(s) for s in sequences.values()))
        first, second = map(set, self.plan["two_node_shards"])
        self.assertFalse(first & second)
        self.assertEqual(first | second, set(sequences))
        self.assertEqual(sum(self.plan["two_node_scoring_calls"]), self.plan["expected_scoring_forward_calls"])
        sets = self.plan["column_sets"]
        self.assertEqual([len(sets[k]) for k in ("fully_covered", "mapped_observed_1GGQ_A", "fully_covered_and_mapped_observed")], [202, 162, 159])
        self.assertEqual(sets["alignment_only_low_coverage"], [154, 173])
        self.assertEqual(sets["mapped_observed_incomplete"], [75, 86, 119])
        self.assertEqual(self.plan["pilot_variants"], [1, 16, 16])
        self.assertEqual(self.plan["pilot_expected_forward_calls"], 14)

    def test_fixture_cannot_be_ingested_as_actual_model(self):
        receipts, scheduler = fixture_run(self.plan, "one")
        with self.assertRaisesRegex(ValueError, "Fixture"):
            validate_receipts(self.plan, receipts, "one", scheduler)
        result = self.validate_fixture(receipts, scheduler)
        self.assertEqual(result["status"], "FIXTURE_ONLY_NOT_SCIENCE")
        self.assertEqual(len(result["conservation_vs_surprisal"]["common_eligible_columns"]), 202)

    def test_reference_missing_and_unmapped_states_remain_unscored(self):
        receipts, scheduler = fixture_run(self.plan, "one")
        result = self.validate_fixture(receipts, scheduler)
        scored = [r for r in result["reference_mapping"] if r["masked_mean_negative_log_probability"] is not None]
        self.assertEqual(len(scored), 162)
        self.assertTrue(all(r["original_reference_mapping"]["status"] == "observed" for r in scored))
        for row in result["reference_mapping"]:
            if row["original_reference_mapping"]["status"] != "observed":
                self.assertIsNone(row["masked_mean_negative_log_probability"])
                self.assertFalse(row["full_coverage_model_eligible"])

    def test_missing_duplicate_corrupt_and_extra_scores_rejected(self):
        receipts, scheduler = fixture_run(self.plan, "one")
        for mutate in (lambda r: r[0]["rows"].pop(),
                       lambda r: r[0]["rows"].append(copy.deepcopy(r[0]["rows"][0])),
                       lambda r: r[0]["rows"][0].update(token_offset=0),
                       lambda r: r[0]["rows"][0].update(residue="-"),
                       lambda r: r[0]["rows"][0].update(log_probability=float("inf")),
                       lambda r: r[0]["rows"][0].update(alignment_column=999)):
            bad = copy.deepcopy(receipts); mutate(bad)
            with self.assertRaises(ValueError): self.validate_fixture(bad, scheduler)

    def test_settings_model_inputs_and_counts_are_enforced(self):
        receipts, scheduler = fixture_run(self.plan, "one")
        for mutate in (lambda r: r[0].update(model_revision="wrong"),
                       lambda r: r[0].update(source_sha256="unplanned_source"),
                       lambda r: r[0].update(sequence_sha256={}),
                       lambda r: r[0].update(failed_positions=[{"position": 1}]),
                       lambda r: r[0].update(input_hashes={}),
                       lambda r: r[0]["forward_calls"].update(scoring=1),
                       lambda r: r[0]["runtime_settings"].update(model_eval=False),
                       lambda r: r[0]["successful_masked_examples"].update(scoring=1),
                       lambda r: r[0]["forward_calls"].update(warmup=0)):
            bad = copy.deepcopy(receipts); mutate(bad)
            with self.assertRaises(ValueError): self.validate_fixture(bad, scheduler)

    def test_two_distinct_physical_nodes_and_hostname_mapping_required(self):
        receipts, scheduler = fixture_run(self.plan, "two")
        result = self.validate_fixture(receipts, scheduler, "two")
        self.assertEqual(len(result["physical_node_ids"]), 2)
        for mutate in (lambda s: s["ranks"][1].update(physical_node_id=s["ranks"][0]["physical_node_id"]),
                       lambda s: s["ranks"][0].update(physical_node_id="UNEXPECTED_NODE"),
                       lambda s: s["ranks"][0].update(container_hostname="WRONG")):
            bad = copy.deepcopy(scheduler); mutate(bad)
            with self.assertRaises(ValueError): self.validate_fixture(receipts, bad, "two")

    def test_float_tolerance_comparison_not_hash_equality(self):
        a, sa = fixture_run(self.plan, "one"); b, sb = fixture_run(self.plan, "two")
        one = self.validate_fixture(a, sa); two = self.validate_fixture(b, sb, "two")
        with self.assertRaises(ValueError): compare_runs(one, two, self.plan)
        two["rows"][0]["log_probability"] += 1e-6
        two["rows"][0]["negative_log_probability"] = -two["rows"][0]["log_probability"]
        report = compare_runs(one, two, self.plan, allow_fixture=True)
        self.assertEqual(report["status"], "FIXTURE_ONLY_NOT_SCIENCE")
        two["rows"][0]["log_probability"] += .1
        two["rows"][0]["negative_log_probability"] = -two["rows"][0]["log_probability"]
        with self.assertRaises(ValueError): compare_runs(one, two, self.plan, allow_fixture=True)
        self.assertFalse(close_float(float("nan"), 0, TOLERANCES))
        self.assertEqual(deviations({1: 0}, {1: 0})["max_relative_error"], 0)
        self.assertAlmostEqual(deviations({1: -1}, {1: -2})["max_relative_error"], .5)

    def test_failed_and_successful_position_inventory(self):
        backend = FixtureBackend()
        backend.failed_positions = []; backend.successful_positions = []
        original = backend.predict
        def fail_second(*args, **kwargs):
            if backend.calls: raise RuntimeError("deliberate fixture failure")
            return original(*args, **kwargs)
        backend.predict = fail_second
        with self.assertRaises(RuntimeError): score_sequence("FIXTURE", "ACD", "ACD", backend, 2)
        self.assertEqual(backend.successful_positions, [{"accession": "FIXTURE", "positions": [1, 2], "phase": "scoring"}])
        self.assertEqual(backend.failed_positions[0]["positions"], [3])

    def test_group_provenance_keeps_supplied_metadata(self):
        groups = grouping_plan()
        self.assertEqual(len(groups["records"]), 30)
        self.assertEqual(len(groups["folds"]), 40)
        self.assertEqual(sum(not r["strain"] for r in groups["records"]), 5)
        self.assertIn("not normalized", groups["interpretation"])

    def test_cutoff_and_execution_approval(self):
        before = datetime.datetime.fromisoformat("2026-11-15T10:29:00-06:00")
        with self.assertRaises(ValueError): authorize(self.plan, {}, "pilot", before)
        approval = {"approved": True, "plan_sha256": self.plan["plan_sha256"], "source_sha256": source_identity(),
                    "mode": "pilot", "run_id": "FIXTURE_APPROVAL_TEST", "max_wall_seconds": 300,
                    "max_nodes": 1, "model_revision": self.plan["model_revision"], "downloads_allowed": False}
        authorize(self.plan, approval, "pilot", before)
        with self.assertRaisesRegex(ValueError, "cutoff"):
            authorize(self.plan, approval, "pilot", datetime.datetime.fromisoformat(self.plan["new_research_cutoff"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
