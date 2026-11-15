"""Validate model receipts before describing results; fixtures are not inference."""
import csv
import datetime
import json
import math
import time
from core import HERE, FROZEN, AA, digest, forward_calls, load_panel, object_hash, position_map, require, sequence_summary, write_new
from sensitivity import aggregate, leave_out, rank_comparison


def close_float(a, b, tolerances):
    return math.isfinite(a) and math.isfinite(b) and abs(a-b) <= (
        tolerances["log_probability_abs"] + tolerances["log_probability_rel"] * max(abs(a), abs(b)))


def deviations(left, right):
    require(left.keys() == right.keys() and left, "Deviation inventory mismatch")
    absolute = [abs(left[k]-right[k]) for k in left]
    relative = [abs(left[k]-right[k])/max(abs(left[k]), abs(right[k]))
                if max(abs(left[k]), abs(right[k])) else 0.0 for k in left]
    return {"max_absolute_error": max(absolute), "max_relative_error": max(relative),
            "relative_error_definition": "abs(a-b)/max(abs(a),abs(b)); zero if both zero"}


def validate_plan(plan):
    unhashed = {k: v for k, v in plan.items() if k != "plan_sha256"}
    require(object_hash(unhashed) == plan["plan_sha256"], "Plan identity mismatch")
    require(object_hash(plan["tasks"]) == plan["task_set_sha256"], "Task identity mismatch")
    require(digest(HERE / "model_lock.json") == plan["model_lock_sha256"], "Model lock identity mismatch")
    lock = json.loads((HERE / "model_lock.json").read_text())
    require((plan["model_id"], plan["model_revision"]) == (lock["model_id"], lock["revision"]), "Plan differs from pinned model")


def attach_reference(columns):
    """Reuse the original fixed-alignment mapping; never fill missing coordinates."""
    mapping = list(csv.DictReader((FROZEN / "alignment_to_structure.tsv").read_text().splitlines(), delimiter="\t"))
    require([int(r["alignment_column"]) for r in mapping] == [r["alignment_column"] for r in columns], "Reference column mapping mismatch")
    result = []
    for original, column in zip(mapping, columns):
        observed = original["status"] == "observed"
        result.append({"original_reference_mapping": original,
                       "alignment_column": column["alignment_column"],
                       "masked_mean_negative_log_probability": column["mean_negative_log_probability"] if observed else None,
                       "model_score_count": column["model_score_count"] if observed else 0,
                       "column_standard_residue_coverage": column["coverage"],
                       "full_coverage_model_eligible": observed and column["full_coverage_model_eligible"],
                       "coordinate_source": "pre-existing experimental 1GGQ A; original v0.1.0 mapping unchanged"})
    return result


def validate_rows(rows, tasks, sequences, alignment):
    expected = {(a, p) for a, positions in tasks.items() for p in positions}
    seen = set()
    for row in rows:
        a, pos = row["accession"], row["sequence_position"]
        key = (a, pos)
        require(type(pos) is int and key in expected and key not in seen, "Extra, duplicate or invalid scored position")
        seen.add(key)
        require(row["residue"] == sequences[a][pos-1] and row["residue"] in AA, "Scored residue identity mismatch")
        require(row["alignment_column"] == position_map(alignment[a])[pos], "Alignment mapping mismatch")
        require(row["token_offset"] == pos, "BOS token offset mismatch")
        value = row["log_probability"]
        require(type(value) in (int, float) and math.isfinite(value) and value <= 1e-6, "Invalid log probability")
        require(math.isclose(row["negative_log_probability"], -value, abs_tol=1e-12, rel_tol=0), "NLL mismatch")
    require(seen == expected, "Missing scored positions")


def validate_receipts(plan, receipts, mode, scheduler=None, allow_fixture=False):
    validate_plan(plan)
    for name, expected in plan["input_hashes"].items():
        require(digest(FROZEN / name) == expected, "Local frozen input identity mismatch")
    require(mode in ("one", "two"), "Benchmark mode required")
    shards = plan["one_node_shards"] if mode == "one" else plan["two_node_shards"]
    require(len(receipts) == len(shards), "Wrong worker count")
    require({r["rank"] for r in receipts} == set(range(len(shards))), "Missing or duplicate ranks")
    sequences, alignment = load_panel()
    all_rows = []
    runtime_identity = None
    run_ids = set()
    source_hashes = set()
    evidence_kinds = set()
    lock = json.loads((HERE / "model_lock.json").read_text())
    for receipt in receipts:
        require(receipt["evidence_kind"] == "actual_model" or (allow_fixture and receipt["evidence_kind"] == "synthetic_fixture"), "Fixture is not actual-model inference")
        evidence_kinds.add(receipt["evidence_kind"])
        require(receipt["plan_sha256"] == plan["plan_sha256"] and receipt["mode"] == mode, "Receipt plan/mode mismatch")
        require(receipt["source_sha256"] == plan["source_sha256"], "Receipt source differs from locked plan")
        require(receipt["model_id"] == plan["model_id"] and receipt["model_revision"] == plan["model_revision"], "Model identity mismatch")
        require(receipt["settings"] == plan["settings"] and receipt["batch_size"] == plan["batch_size"], "Settings mismatch")
        runtime = receipt["runtime_settings"]
        require(all(runtime.get(k) == v for k, v in plan["settings"].items()) and runtime.get("model_eval") is True
                and runtime.get("inference_mode") is True and runtime.get("device") == "cuda:0", "Inference settings mismatch")
        require(receipt["input_hashes"] == plan["input_hashes"], "Input identity mismatch")
        require(receipt["sequence_sha256"] == plan["sequence_sha256"] and receipt["maximum_sequence_length"] == plan["maximum_sequence_length"], "Sequence inventory mismatch")
        require(receipt["failed_positions"] == [], "Failed positions cannot produce complete scientific results")
        require(receipt["assets"]["model.safetensors"] == lock["files"][0]["sha256"], "Weight identity mismatch")
        identity = object_hash({"assets": receipt["assets"], "versions": receipt["versions"], "runtime": receipt["runtime_settings"], "hardware": receipt["hardware"]})
        require(runtime_identity is None or identity == runtime_identity, "Worker runtime/library/assets differ")
        runtime_identity = identity
        run_ids.add(receipt["run_id"])
        source_hashes.add(receipt["source_sha256"])
        assigned = shards[receipt["rank"]]
        tasks = {a: plan["tasks"][a] for a in assigned}
        require(receipt["assigned_accessions"] == assigned, "Shard assignment mismatch")
        validate_rows(receipt["rows"], tasks, sequences, alignment)
        require(receipt["forward_calls"]["scoring"] == forward_calls([len(p) for p in tasks.values()], plan["batch_size"]), "Actual forward-call count mismatch")
        require(receipt["successful_forward_calls"] == receipt["forward_calls"], "Unsuccessful model calls in receipt")
        require(receipt["successful_masked_examples"] == {"scoring": sum(map(len, tasks.values())), "pilot": 0, "warmup": 1}, "Successful mask counts mismatch")
        require(receipt["forward_calls"].get("pilot", 0) == 0 and receipt["forward_calls"]["warmup"] == 1, "Phase counts inconsistent")
        for key in ("asset_verification_seconds", "loading_seconds", "model_transfer_seconds", "worker_until_receipt_seconds"):
            require(math.isfinite(receipt["timing"][key]) and receipt["timing"][key] >= 0, "Invalid timing")
        for phase in ("scoring", "warmup"):
            for key in ("host_to_device_seconds", "compute_seconds", "device_to_host_seconds"):
                value = receipt["timing"]["phases"][phase][key]
                require(math.isfinite(value) and value >= 0, "Invalid phase timing")
        all_rows.extend(receipt["rows"])
    require(len(run_ids) == 1 and len(source_hashes) == 1 and len(evidence_kinds) == 1, "Mixed run/source/evidence identities")
    validate_rows(all_rows, plan["tasks"], sequences, alignment)
    require(scheduler is not None and scheduler["source"] == "scheduler_export", "Physical-node scheduler evidence required")
    require(scheduler["run_id"] == next(iter(run_ids)) and scheduler["workflow_id"] and scheduler["job_id"], "Scheduler identity mismatch")
    require(len(scheduler["ranks"]) == len(shards), "Wrong scheduler rank count")
    assignments = {r["rank"]: r for r in scheduler["ranks"]}
    require(set(assignments) == set(range(len(shards))), "Duplicate scheduler rank")
    nodes = set()
    for receipt in receipts:
        evidence = assignments[receipt["rank"]]
        require(evidence["container_hostname"] == receipt["container_hostname"] and evidence["container_id"], "Container-to-physical-node evidence mismatch")
        require(evidence["physical_node_id"], "Missing physical node")
        nodes.add(evidence["physical_node_id"])
    require(len(nodes) == len(shards), "Two workers must occupy two distinct physical nodes")
    require(nodes == set(plan["expected_physical_nodes"][mode]), "Unexpected physical event nodes")
    times = [datetime.datetime.fromisoformat(scheduler[k]) for k in ("submitted_at", "started_at", "finished_at", "export_completed_at")]
    require(all(t.tzinfo for t in times) and all(a <= b for a, b in zip(times, times[1:])), "Invalid workflow lifecycle times")
    timing = {"queue_and_staging_seconds": (times[1]-times[0]).total_seconds(),
              "job_wall_seconds": (times[2]-times[1]).total_seconds(),
              "export_seconds": (times[3]-times[2]).total_seconds(),
              "total_workflow_seconds": (times[3]-times[0]).total_seconds(),
              "worker_timings": [r["timing"] for r in sorted(receipts, key=lambda r: r["rank"])],
              "note": "Critical path is elapsed workflow wall time; do not sum worker times as elapsed time. Queue/staging may be confounded until separate scheduler events are available."}
    for phase, start_key, end_key in (("queue", "queued_at", "dequeued_at"), ("startup", "startup_started_at", "startup_finished_at")):
        begin, end = (datetime.datetime.fromisoformat(scheduler[k]) for k in (start_key, end_key))
        require(begin.tzinfo and end.tzinfo and times[0] <= begin <= end <= times[2], "Invalid queue/startup evidence")
        timing[phase+"_seconds"] = (end-begin).total_seconds()
    timing["phase_note"] = "Queue/startup intervals are measured scheduler intervals, may overlap other reported phases and must not be summed as total wall time."
    columns = aggregate(alignment, all_rows)
    eligible = [r["alignment_column"] for r in columns if r["full_coverage_model_eligible"]]
    return {"status": "VALIDATED_ACTUAL_MODEL" if evidence_kinds == {"actual_model"} else "FIXTURE_ONLY_NOT_SCIENCE",
            "mode": mode, "plan_sha256": plan["plan_sha256"], "runtime_identity": runtime_identity,
            "source_sha256": next(iter(source_hashes)), "run_id": next(iter(run_ids)), "rows": all_rows,
            "columns": columns, "reference_mapping": attach_reference(columns), "column_sets": plan["column_sets"],
            "physical_node_ids": sorted(nodes), "timing": timing,
            "sequence_summaries": {a: sequence_summary(s, [r for r in all_rows if r["accession"] == a]) for a, s in sequences.items()},
            "analysis_sets": plan["analysis_sets"],
            "conservation_vs_surprisal": {"analysis_set": "F: full-coverage columns", **rank_comparison(
                {r["alignment_column"]: r["modal_fraction"] for r in columns},
                {r["alignment_column"]: r["mean_negative_log_probability"] for r in columns}, eligible)}}


def compare_runs(one, two, plan, allow_fixture=False):
    validate_plan(plan)
    sequences, alignment = load_panel()
    validate_rows(one["rows"], plan["tasks"], sequences, alignment)
    validate_rows(two["rows"], plan["tasks"], sequences, alignment)
    actual = one["status"] == two["status"] == "VALIDATED_ACTUAL_MODEL"
    fixture = one["status"] == two["status"] == "FIXTURE_ONLY_NOT_SCIENCE"
    require(actual or (allow_fixture and fixture), "Actual model validation required")
    require(one["mode"] == "one" and two["mode"] == "two", "Expected matched one/two-node runs")
    require(one["plan_sha256"] == two["plan_sha256"] == plan["plan_sha256"], "Different benchmark tasks")
    require(one["runtime_identity"] == two["runtime_identity"] and one["source_sha256"] == two["source_sha256"] == plan["source_sha256"], "Different benchmark runtimes/source")
    left = {(r["accession"], r["sequence_position"]): r["log_probability"] for r in one["rows"]}
    right = {(r["accession"], r["sequence_position"]): r["log_probability"] for r in two["rows"]}
    require(left.keys() == right.keys(), "Task coverage differs")
    errors = [abs(left[k]-right[k]) for k in left]
    require(all(close_float(left[k], right[k], plan["tolerances"]) for k in left), "Predeclared numerical tolerance failed")
    denominator = two["timing"]["total_workflow_seconds"]
    return {"status": "MATCHED_PILOT_COMPARISON" if actual else "FIXTURE_ONLY_NOT_SCIENCE", "tasks_compared": len(left), "max_absolute_log_probability_error": max(errors),
            "numerical_deviations": deviations(left, right),
            "tolerances": plan["tolerances"], "one_node_timing": one["timing"], "two_node_timing": two["timing"],
            "total_workflow_speedup": one["timing"]["total_workflow_seconds"] / denominator if denominator > 0 else None,
            "time_to_analyzed_result_speedup": (one["timing"]["time_to_analyzed_result_seconds"]/two["timing"]["time_to_analyzed_result_seconds"])
                if one["timing"].get("time_to_analyzed_result_seconds") is not None and two["timing"].get("time_to_analyzed_result_seconds", 0) > 0 else None,
            "interpretation": "One pair is a descriptive pilot, not a scaling law or significance claim. No speedup is required."}


def ingest_files(plan_path, receipt_paths, scheduler_path, mode, output, groups_path):
    started = time.perf_counter()
    plan = json.loads(plan_path.read_text())
    result = validate_receipts(plan, [json.loads(p.read_text()) for p in receipt_paths], mode, json.loads(scheduler_path.read_text()))
    result["ingestion_provenance"] = {"plan_file_sha256": digest(plan_path), "scheduler_evidence_sha256": digest(scheduler_path),
                                      "receipt_file_sha256": {p.name: digest(p) for p in receipt_paths}, "grouping_file_sha256": digest(groups_path)}
    _, alignment = load_panel()
    groups = json.loads(groups_path.read_text())
    require(groups["metadata_sha256"] == plan["input_hashes"]["inputs/sequence_metadata.tsv"], "Grouping provenance mismatch")
    result["sensitivity"] = [leave_out(alignment, result["rows"], f["removed"],
                                      {"fold": f, "metadata_sha256": groups["metadata_sha256"], "records": groups["records"]}) for f in groups["folds"]]
    result["timing"]["merge_and_analysis_seconds"] = time.perf_counter()-started
    result["timing"]["time_to_analyzed_result_seconds"] = result["timing"]["total_workflow_seconds"]+result["timing"]["merge_and_analysis_seconds"]
    result["timing"]["merge_scope"] = "Local validation, merging, summaries and sensitivity; excludes final JSON serialization and manual delay after export"
    write_new(output, result)


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--receipts", type=Path, nargs="+", required=True)
    p.add_argument("--scheduler", type=Path, required=True)
    p.add_argument("--groups", type=Path, required=True)
    p.add_argument("--mode", choices=("one", "two"), required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    ingest_files(a.plan, a.receipts, a.scheduler, a.mode, a.output, a.groups)
