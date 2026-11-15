"""Prepared execution entrypoint. Requires a separately approved, bounded receipt.

No downloads, fallback model, driver changes or cluster submission code exists.
"""
import argparse
import datetime
import json
import socket
import time
from pathlib import Path
from core import HERE, digest, load_panel, object_hash, require, score_sequence, write_new
from ingest import close_float, deviations, validate_plan, validate_rows
from runtime import HFBackend

SOURCE_FILES = ("core.py", "sensitivity.py", "runtime.py", "planning.py", "ingest.py", "run_worker.py", "launch_worker.sh")


def source_identity():
    return object_hash({name: digest(HERE / name) for name in SOURCE_FILES})


def authorize(plan, approval, mode, now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    require(now.tzinfo is not None, "Timezone-aware time required")
    require(now < datetime.datetime.fromisoformat(plan["new_research_cutoff"]), "Research cutoff reached; use CPU fallback")
    require(approval.get("approved") is True, "Execution requires a separate explicit approval")
    require(approval.get("plan_sha256") == plan["plan_sha256"], "Approval is for a different plan")
    require(approval.get("source_sha256") == source_identity(), "Approval is for different source code")
    require(approval.get("mode") == mode and approval.get("run_id"), "Approval scope/run identifier mismatch")
    require(approval.get("max_wall_seconds") == 300, "Require the five-minute worker cap")
    require(approval.get("max_nodes") == (2 if mode == "two" else 1), "Node bound mismatch")
    require(approval.get("model_revision") == plan["model_revision"], "Approval model revision mismatch")
    require(approval.get("downloads_allowed") is False, "Execution must remain offline")


def _run(plan, approval, mode, rank, model_dir, output_dir, pilot_path=None, state=None):
    started = time.perf_counter()
    validate_plan(plan)
    authorize(plan, approval, mode)
    require(plan["source_sha256"] == source_identity(), "Code differs from workload plan")
    require(not output_dir.resolve().is_relative_to((HERE.parent / "ospc_comparison_v0.1.0").resolve()), "Frozen output directory refused")
    sequences, alignment = load_panel()
    from core import FROZEN
    for name, expected in plan["input_hashes"].items():
        require(digest(FROZEN / name) == expected, "Frozen input changed")
    expected_file = output_dir / ("pilot.json" if mode == "pilot" else f"rank{rank}.json")
    require(not expected_file.exists(), "Refusing completed output overwrite")
    state.update(authorized=True, expected_file=expected_file)
    if mode == "pilot":
        require(rank == 0, "Pilot has one worker")
        tasks = plan["pilot_tasks"]
    else:
        require(pilot_path is not None, "Validated actual-model pilot receipt required before benchmark")
        pilot = json.loads(pilot_path.read_text())
        require(pilot["status"] == "ACTUAL_MODEL_PILOT_PASS" and pilot["evidence_kind"] == "actual_model", "Fixtures cannot unlock production")
        require(pilot["plan_sha256"] == plan["plan_sha256"] and pilot["source_sha256"] == source_identity(), "Pilot identity mismatch")
        require(pilot["tolerances"] == plan["tolerances"], "Pilot tolerance contract changed")
        shards = plan["one_node_shards"] if mode == "one" else plan["two_node_shards"]
        require(0 <= rank < len(shards), "Invalid rank")
        tasks = {a: plan["tasks"][a] for a in shards[rank]}
    state["tasks"] = tasks
    backend = HFBackend(model_dir, "cuda:0", plan["settings"])
    state["backend"] = backend
    backend.pilot_tolerances = plan["tolerances"]
    backend.deadline = min(started + 300, time.perf_counter() + max(0, (
        datetime.datetime.fromisoformat(plan["new_research_cutoff"]) - datetime.datetime.now(datetime.timezone.utc)).total_seconds()))
    if mode != "pilot":
        require(pilot["runtime_settings"] == backend.settings and pilot["versions"] == backend.versions,
                "Pilot and benchmark runtime settings/libraries differ")
        require(pilot["assets"] == {x["path"]: x["sha256"] for x in backend.assets["files"]}, "Pilot and benchmark assets differ")
        require(pilot["hardware"] == backend.hardware, "Pilot and benchmark hardware differ")
        require(pilot["batch_sizes"] == plan["pilot_variants"] and len(pilot["variants"]) == 3, "Pilot variants mismatch")
        require(pilot["sequence_sha256"] == plan["sequence_sha256"] and pilot["failed_positions"] == [], "Pilot sequence/failure inventory mismatch")
        for variant in pilot["variants"]:
            validate_rows(variant, plan["pilot_tasks"], sequences, alignment)
        left = {(r["accession"], r["sequence_position"]): r["log_probability"] for r in pilot["variants"][0]}
        for variant in pilot["variants"][1:]:
            right = {(r["accession"], r["sequence_position"]): r["log_probability"] for r in variant}
            require(all(close_float(left[k], right[k], plan["tolerances"]) for k in left), "Pilot numerical receipt mismatch")
        batch_first = {(r["accession"], r["sequence_position"]): r["log_probability"] for r in pilot["variants"][1]}
        require(all(close_float(batch_first[k], right[k], plan["tolerances"]) for k in batch_first), "Repeated pilot receipt mismatch")
        require(pilot["memory"]["inference_including_warmup"]["peak_allocated_bytes"] > 0, "Pilot memory evidence missing")
        require(pilot["forward_calls"] == {"scoring": 0, "pilot": plan["pilot_expected_forward_calls"], "warmup": 1}
                and pilot["successful_forward_calls"] == pilot["forward_calls"], "Pilot actual/successful forward counts mismatch")
        require(pilot["successful_masked_examples"] == {"scoring": 0, "pilot": 3*sum(map(len, plan["pilot_tasks"].values())), "warmup": 1}, "Pilot successful mask counts mismatch")
    first = next(iter(tasks))
    score_sequence(first, sequences[first], alignment[first], backend, 1, [tasks[first][0]], phase="warmup")
    if mode == "pilot":
        variants = []
        for batch in plan["pilot_variants"]:
            rows = []
            for a, positions in tasks.items():
                current, _ = score_sequence(a, sequences[a], alignment[a], backend, batch, positions, phase="pilot")
                rows.extend(current)
            validate_rows(rows, tasks, sequences, alignment)
            variants.append(rows)
        left = {(r["accession"], r["sequence_position"]): r["log_probability"] for r in variants[0]}
        comparisons = []
        for index, variant in enumerate(variants[1:], 1):
            right = {(r["accession"], r["sequence_position"]): r["log_probability"] for r in variant}
            require(left.keys() == right.keys(), "Pilot task mismatch")
            require(all(close_float(left[k], right[k], plan["tolerances"]) for k in left), "Serial/batched/repeated pilot tolerance failed")
            comparisons.append({"reference_variant": 0, "compared_variant": index, **deviations(left, right)})
        batched = {(r["accession"], r["sequence_position"]): r["log_probability"] for r in variants[1]}
        require(all(close_float(batched[k], right[k], plan["tolerances"]) for k in batched), "Repeated-batch tolerance failed")
        comparisons.append({"reference_variant": 1, "compared_variant": 2, **deviations(batched, right)})
        require(backend.calls["pilot"] == plan["pilot_expected_forward_calls"] and backend.calls["scoring"] == 0, "Pilot forward count mismatch")
        receipt = {"status": "ACTUAL_MODEL_PILOT_PASS", "evidence_kind": "actual_model", "plan_sha256": plan["plan_sha256"],
                   "source_sha256": source_identity(), "tolerances": plan["tolerances"], "tasks": tasks,
                   "variants": variants, "batch_sizes": plan["pilot_variants"],
                   "max_absolute_error": max(c["max_absolute_error"] for c in comparisons),
                   "max_relative_error": max(c["max_relative_error"] for c in comparisons),
                   "numerical_comparisons": comparisons, "repeat_scope": plan["pilot_repeat_scope"],
                   "float32_log_softmax_vs_float64_logsumexp_max_error": backend.pilot_log_softmax_max_error,
                   "interpretation": "Real-model serial/batched correctness pilot only; no scientific scaling result"}
    else:
        rows = []
        for a, positions in tasks.items():
            current, _ = score_sequence(a, sequences[a], alignment[a], backend, plan["batch_size"], positions)
            rows.extend(current)
        validate_rows(rows, tasks, sequences, alignment)
        receipt = {"schema_version": 1, "evidence_kind": "actual_model", "mode": mode, "rank": rank,
                   "plan_sha256": plan["plan_sha256"], "source_sha256": source_identity(),
                   "settings": plan["settings"], "input_hashes": plan["input_hashes"],
                   "batch_size": plan["batch_size"], "assigned_accessions": list(tasks), "rows": rows,
                   "pilot_receipt_sha256": digest(pilot_path)}
    receipt.update(run_id=approval["run_id"], container_hostname=socket.gethostname(),
                   model_id=plan["model_id"], model_revision=plan["model_revision"],
                   assets={x["path"]: x["sha256"] for x in backend.assets["files"]},
                   runtime_settings=backend.settings, versions=backend.versions,
                   hardware=backend.hardware,
                   sequence_sha256=plan["sequence_sha256"], maximum_sequence_length=plan["maximum_sequence_length"],
                   successful_position_inventory=backend.successful_positions, failed_positions=backend.failed_positions,
                   memory={"loading": backend.loading_memory, "inference_including_warmup": backend.memory()},
                   forward_calls={phase: backend.calls[phase] for phase in ("scoring", "pilot", "warmup")},
                   successful_forward_calls={phase: backend.successful_calls[phase] for phase in ("scoring", "pilot", "warmup")},
                   successful_masked_examples={phase: backend.examples[phase] for phase in ("scoring", "pilot", "warmup")},
                   timing={"asset_verification_seconds": backend.verification_seconds,
                           "loading_seconds": backend.load_seconds, "model_transfer_seconds": backend.model_transfer_seconds,
                           "phases": backend.timings, "worker_until_receipt_seconds": time.perf_counter() - started,
                           "scope": "Excludes queue, pre-worker shared-volume staging and receipt export; ingest scheduler lifecycle separately"})
    write_new(expected_file, receipt)


def run(plan, approval, mode, rank, model_dir, output_dir, pilot_path=None):
    state = {}
    try:
        _run(plan, approval, mode, rank, model_dir, output_dir, pilot_path, state)
    except Exception as error:
        if state.get("authorized"):
            backend = state.get("backend")
            failure = {"status": "ACTUAL_MODEL_FAILED_NO_SCIENTIFIC_RESULT", "run_id": approval["run_id"],
                       "plan_sha256": plan["plan_sha256"], "source_sha256": source_identity(),
                       "mode": mode, "rank": rank, "error_type": type(error).__name__,
                       "assigned_tasks": state.get("tasks", {}), "sequence_sha256": plan["sequence_sha256"],
                       "successful_position_inventory": backend.successful_positions if backend else [],
                       "failed_positions": backend.failed_positions if backend else [],
                       "actual_forward_calls": dict(backend.calls) if backend else {},
                       "successful_forward_calls": dict(backend.successful_calls) if backend else {},
                       "successful_masked_examples": dict(backend.examples) if backend else {},
                       "note": "A failed batch is listed separately; other uncompleted tasks remain unattempted/unaccounted. Process kill requires scheduler failure evidence; absence of a receipt never passes."}
            write_new(output_dir / f"failed-rank{rank}.json", failure)
        raise


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--mode", choices=("pilot", "one", "two"), required=True)
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--approval", type=Path, required=True)
    p.add_argument("--model-dir", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--pilot-receipt", type=Path)
    p.add_argument("--rank", type=int, default=0)
    a = p.parse_args()
    run(json.loads(a.plan.read_text()), json.loads(a.approval.read_text()), a.mode, a.rank,
        a.model_dir, a.output_dir, a.pilot_receipt)
