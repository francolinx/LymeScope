"""Prepare deterministic manifests from existing inputs; never load a model."""
import csv
import hashlib
import json
from collections import defaultdict
from core import HERE, FROZEN, AA, digest, forward_calls, load_panel, object_hash, position_map, standard_positions, write_new

SETTINGS = {"precision": "float32", "autocast": False, "tf32": False,
            "deterministic_algorithms": True, "attention": "eager", "cpu_threads": 2}
TOLERANCES = {"log_probability_abs": 0.0001, "log_probability_rel": 0.00001,
              "policy": "abs(a-b) <= abs_tol + rel_tol*max(abs(a),abs(b)); exact task/identity coverage; hashes establish provenance, not float equality"}
CUTOFF = "2026-11-15T10:30:00-06:00"


def make_plan():
    from run_worker import source_identity
    sequences, alignment = load_panel()
    lock = json.loads((HERE / "model_lock.json").read_text())
    mapping = list(csv.DictReader((FROZEN / "alignment_to_structure.tsv").read_text().splitlines(), delimiter="\t"))
    fully_covered = [i+1 for i in range(218) if all(s[i] in AA for s in alignment.values())]
    observed = [int(r["alignment_column"]) for r in mapping if r["status"] == "observed"]
    intersection = sorted(set(fully_covered) & set(observed))
    assert (len(fully_covered), len(observed), len(intersection)) == (202, 162, 159)
    assert all(c not in observed and sum(s[c-1] in AA for s in alignment.values()) == 1 for c in (154, 173))
    tasks = {a: standard_positions(s) for a, s in sequences.items()}
    batch_size = 16
    counts = {a: forward_calls([len(p)], batch_size) for a, p in tasks.items()}
    shards = [[], []]
    loads = [0, 0]
    for a in sorted(tasks, key=lambda a: (-counts[a], a)):
        rank = min(range(2), key=lambda i: (loads[i], i))
        shards[rank].append(a)
        loads[rank] += counts[a]
    # Preserve frozen input order within each worker.
    shards = [[a for a in tasks if a in shard] for shard in shards]
    pilot = defaultdict(set)
    pilot[next(iter(sequences))].update([1, 38, 39, 200, 201, len(next(iter(sequences.values())))])
    for column in (154, 173):
        for a in alignment:
            inverse = {v: k for k, v in position_map(alignment[a]).items()}
            if column in inverse:
                pilot[a].add(inverse[column])
    pilot = {a: sorted(pilot[a]) for a in sequences if a in pilot}
    plan = {"schema_version": 1, "version": "0.2.0", "status": "PREPARED_NOT_EXECUTED",
            "method_source": "User-supplied Claude final contract plus accepted corrections; see CONTRACT.md",
            "approval_required": True, "new_research_cutoff": CUTOFF,
            "input_hashes": {p: digest(FROZEN / p) for p in ("inputs/input_sequences.fasta", "aligned.fasta", "inputs/sequence_metadata.tsv", "alignment_to_structure.tsv", "source/baseline.py", "analysis_manifest.json", "SHA256SUMS")},
            "sequence_sha256": {a: hashlib.sha256(s.encode('ascii')).hexdigest() for a, s in sequences.items()},
            "sequence_hash_definition": "SHA256 of exact ungapped ASCII sequence, no header/newline; identifiers retained as keys",
            "maximum_sequence_length": max(map(len, sequences.values())),
            "model_id": lock["model_id"], "model_revision": lock["revision"],
            "model_lock_sha256": digest(HERE / "model_lock.json"), "settings": SETTINGS,
            "primary_metric": "masked_original_residue_negative_log_probability",
            "column_sets": {"fully_covered": fully_covered, "mapped_observed_1GGQ_A": observed,
                            "fully_covered_and_mapped_observed": intersection,
                            "mapped_observed_incomplete": sorted(set(observed)-set(fully_covered)),
                            "alignment_only_low_coverage": [154, 173]},
            "analysis_sets": {"primary_comparison": "F: fully_covered", "structural_full_coverage": "MF: fully_covered_and_mapped_observed", "structural_descriptive": "M: mapped_observed_1GGQ_A"},
            "expected_physical_nodes": {"one": ["CIQ-CHI-SPARK30"], "two": ["CIQ-CHI-SPARK29", "CIQ-CHI-SPARK30"]},
            "source_sha256": source_identity(),
            "batch_size": batch_size, "tasks": tasks, "task_set_sha256": object_hash(tasks),
            "masked_examples": sum(map(len, tasks.values())), "expected_scoring_forward_calls": sum(counts.values()),
            "per_sequence_forward_calls": counts, "one_node_shards": [list(tasks)], "two_node_shards": shards,
            "two_node_scoring_calls": loads, "warmup_forward_calls_per_worker": 1,
            "pilot_tasks": pilot, "pilot_variants": [1, batch_size, batch_size],
            "pilot_repeat_scope": "Three passes on the same loaded eval-mode model: singleton, batched, repeated batched. Not three process launches.",
            "pilot_expected_forward_calls": sum(forward_calls([len(p) for p in pilot.values()], b) for b in (1, batch_size, batch_size)),
            "tolerances": TOLERANCES, "no_repeated_data_or_model_enlargement": True}
    plan["plan_sha256"] = object_hash(plan)
    return plan


def grouping_plan():
    rows = list(csv.DictReader((FROZEN / "inputs/sequence_metadata.tsv").read_text(encoding="utf-8").splitlines(), delimiter="\t"))
    groups = defaultdict(list)
    for row in rows:
        groups[row["taxon_id"]].append(row["accession"])
    return {"metadata_sha256": digest(FROZEN / "inputs/sequence_metadata.tsv"),
            "provenance_fields": ["accession", "organism", "taxon_id", "strain", "strain_provenance", "quality_flags"],
            "records": [{k: row[k] for k in ("accession", "organism", "taxon_id", "strain", "strain_provenance", "quality_flags")} for row in rows],
            "folds": [{"name": "leave-accession-" + r["accession"], "removed": [r["accession"]], "grouping": "accession"} for r in rows] +
                     [{"name": "leave-supplied-taxon-" + k, "removed": v, "grouping": "exact supplied taxon_id", "value": k} for k, v in sorted(groups.items())],
            "interpretation": "Taxon labels are not normalized species or independent biological replicates. These are explicit metadata sensitivity groups; unresolved strain labels are preserved. No significance tests."}


if __name__ == "__main__":
    write_new(HERE / "plans/workload.json", make_plan())
    write_new(HERE / "plans/grouping.json", grouping_plan())
