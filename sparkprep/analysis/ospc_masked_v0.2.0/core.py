"""Offline contracts and scoring orchestration. Importing this module runs no model."""
from __future__ import annotations

import hashlib
import json
import math
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
FROZEN = HERE.parent / "ospc_comparison_v0.1.0" / "results_v0.1.0"
AA = frozenset("ACDEFGHIKLMNPQRSTVWY")
_baseline = types.ModuleType("lymescope_frozen_baseline")
_baseline_path = FROZEN / "source/baseline.py"
# Reuse the reviewed source without writing a __pycache__ into frozen evidence.
exec(compile(_baseline_path.read_bytes(), str(_baseline_path), "exec"), vars(_baseline))
read_fasta = _baseline.read_fasta
column_stats = _baseline.column_stats


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def object_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def write_new(path, value):
    """Never overwrite frozen evidence or an earlier result."""
    path = Path(path).resolve()
    require(not path.is_relative_to(FROZEN.parent.resolve()), "Refusing a write under frozen v0.1.0")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def load_panel():
    sequences = read_fasta(FROZEN / "inputs/input_sequences.fasta")
    alignment = read_fasta(FROZEN / "aligned.fasta")
    require(list(sequences) == list(alignment), "Identifier/order mismatch")
    require(len(sequences) == 30, "This version requires the frozen 30-sequence panel")
    require({len(s) for s in alignment.values()} == {218}, "Unexpected alignment dimensions")
    for accession, sequence in sequences.items():
        require(alignment[accession].replace("-", "") == sequence, "Ungapped sequence mismatch")
    return sequences, alignment


def position_map(aligned):
    """1-based ungapped position -> original 1-based alignment column."""
    return {position: column for position, column in enumerate(
        (i for i, residue in enumerate(aligned, 1) if residue != "-"), 1)}


def standard_positions(sequence, requested=None):
    positions = list(range(1, len(sequence) + 1)) if requested is None else list(requested)
    require(all(type(p) is int and 1 <= p <= len(sequence) for p in positions), "Invalid sequence position")
    require(len(set(positions)) == len(positions), "Duplicate sequence positions")
    return sorted(p for p in positions if sequence[p - 1] in AA)


def forward_calls(position_counts, batch_size):
    require(type(batch_size) is int and batch_size > 0, "Positive integer batch size required")
    require(all(type(n) is int and n >= 0 for n in position_counts), "Invalid position counts")
    return sum((n + batch_size - 1) // batch_size for n in position_counts)


def log_probability(logits, observed_id):
    """Stable log-softmax over the full model vocabulary; no AA renormalization."""
    require(bool(logits) and all(math.isfinite(v) for v in logits), "Nonfinite logits")
    require(0 <= observed_id < len(logits), "Observed token outside vocabulary")
    maximum = max(logits)
    return (logits[observed_id] - maximum) - math.log(math.fsum(math.exp(v - maximum) for v in logits))


def assert_token_offsets(sequence, token_ids, tokenizer):
    """Reject truncation, unexpected special tokens and off-by-one scoring."""
    require(len(token_ids) == len(sequence) + 2, "Expected exactly BOS + residues + EOS")
    require(token_ids[0] == tokenizer.cls_token_id and token_ids[-1] == tokenizer.eos_token_id, "BOS/EOS mismatch")
    residue_ids = tokenizer.convert_tokens_to_ids(list(sequence))
    require(token_ids[1:-1] == residue_ids, "Residue/token offsets disagree")
    forbidden = {tokenizer.cls_token_id, tokenizer.eos_token_id, tokenizer.pad_token_id, tokenizer.mask_token_id}
    require(not forbidden.intersection(residue_ids), "Special token inside biological sequence")
    for pos in standard_positions(sequence):
        require(residue_ids[pos - 1] != tokenizer.unk_token_id, "Standard residue mapped to UNK")


def score_sequence(accession, sequence, aligned, backend, batch_size, requested=None, phase="scoring"):
    """Backend receives one masked residue per example, same sequence per batch.

    Backend.predict returns log probabilities for exactly the requested observed
    tokens, never scores for BOS/EOS/padding/gaps. Fixture and real backends are
    intentionally separate. All timings/calls belong to the supplied phase.
    """
    require(aligned.replace("-", "") == sequence, "Sequence/alignment mismatch")
    require(phase in ("scoring", "warmup", "pilot"), "Unknown forward-call phase")
    forward_calls([], batch_size)
    positions = standard_positions(sequence, requested)
    columns = position_map(aligned)
    token_ids = backend.tokenizer.encode(sequence, add_special_tokens=True)
    assert_token_offsets(sequence, token_ids, backend.tokenizer)
    rows = []
    calls = 0
    for start in range(0, len(positions), batch_size):
        current = positions[start:start + batch_size]
        examples = []
        targets = []
        for pos in current:
            masked = list(token_ids)
            targets.append(masked[pos])  # BOS occupies offset 0; biological position is 1-based.
            masked[pos] = backend.tokenizer.mask_token_id
            require(masked.count(backend.tokenizer.mask_token_id) == 1, "Exactly one mask per example required")
            examples.append(masked)
        try:
            values = backend.predict(examples, current, targets, phase=phase)
        except Exception as error:
            if hasattr(backend, "failed_positions"):
                backend.failed_positions.append({"accession": accession, "positions": current,
                                                 "phase": phase, "error_type": type(error).__name__})
            raise
        calls += 1
        require(len(values) == len(current), "Backend returned wrong score count")
        for pos, value in zip(current, values):
            require(math.isfinite(value) and value <= 1e-6, "Invalid log probability")
            rows.append({"accession": accession, "sequence_position": pos, "token_offset": pos,
                         "alignment_column": columns[pos], "residue": sequence[pos - 1],
                         "log_probability": float(value), "negative_log_probability": -float(value)})
        if hasattr(backend, "successful_positions"):
            backend.successful_positions.append({"accession": accession, "positions": current, "phase": phase})
    require(calls == forward_calls([len(positions)], batch_size), "Forward-call count mismatch")
    return rows, {"phase": phase, "forward_calls": calls, "masked_examples": len(rows),
                  "scored_positions": positions, "batch_size": batch_size}


def sequence_summary(sequence, rows):
    positions = sorted(row["sequence_position"] for row in rows)
    require(len(set(positions)) == len(positions), "Duplicate scored positions")
    require(all(p in standard_positions(sequence) for p in positions), "Nonstandard scored position")
    mean = math.fsum(-r["log_probability"] for r in rows) / len(rows) if rows else None
    all_positions = standard_positions(sequence)
    scope = "all_observed_standard_residues" if positions == all_positions else "explicit_subset_of_observed_standard_residues"
    return {"scored_positions": positions, "scored_count": len(rows), "scope": scope,
            "sequence_length": len(sequence), "mean_negative_log_probability": mean,
            "pseudo_perplexity": math.exp(mean) if mean is not None and mean < 700 else None,
            "pseudo_perplexity_note": "exp(mean negative log probability) over the listed positions only"}
