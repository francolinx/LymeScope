"""Consume the published Spark adapter; never regenerate or edit scientific evidence."""
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / 'sparkprep/experiments/stretch_v0.2.0_20261115T072916Z'
COMMIT = 'aafe818a20ea025370cf4b65145a9684e80aaaef'
REVISION = 'c731040fcd8d73dceaa04b0a8e6329b345b0f5df'
CURRENT = 'results/full_panel_comparison_v2/column_comparison.tsv'
SASA_KEYS = tuple('reference_1GGQ_A_calculated_' + x + '_sasa_A2' for x in ('monomer', 'dimer', 'delta'))


class ScientificColumn(TypedDict):
    alignment_column: int
    coverage: float
    observed_residue_count: int
    original_residue_counts: dict[str, int]
    modal_fraction: float
    mean_masked_nll_nats: float
    agreement_minus_predictability_percentile: float | None
    reference_1GGQ_A_observation_status: str
    reference_1GGQ_A_contact_4_5_A: bool | None
    reference_1GGQ_A_calculated_monomer_sasa_A2: float | None
    reference_1GGQ_A_calculated_dimer_sasa_A2: float | None
    reference_1GGQ_A_calculated_delta_sasa_A2: float | None


class SequenceScore(TypedDict):
    accession: str
    sequence_sha256: str
    mask_count: int
    scored_positions: str
    mean_nll_nats: float
    masked_pseudo_perplexity: float


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path):
    return list(csv.DictReader(path.read_text(encoding='utf-8').splitlines(), delimiter='\t'))


def validate_evidence(evidence, context):
    require(evidence['schema'] == 'lymescope.personal_spark.evidence.v1', 'Unsupported adapter schema')
    require(evidence['model']['revision'] == REVISION, 'Model revision mismatch')
    require(evidence['recommended_files']['column_comparison'] == CURRENT, 'Only current v2 aggregate is eligible')
    require(evidence['method']['algorithm'] == 'singleton_mask_original_residue_nll_natural_log_full_vocab', 'Wrong scoring method')
    columns: list[ScientificColumn] = evidence['columns']
    sequences: list[SequenceScore] = evidence['sequences']
    require([c['alignment_column'] for c in columns] == list(range(1, 219)), 'Column inventory mismatch')
    observed = set(context['column_sets']['mapped_observed'])
    full = set(context['column_sets']['fully_covered'])
    for row, baseline in zip(columns, context['columns']):
        c = row['alignment_column']
        count = row['observed_residue_count']
        require(type(count) is int and count == baseline['contributing_sequences'], 'Contributor count mismatch')
        require(row['coverage'] == baseline['coverage'] == count / 30, 'Coverage mismatch')
        require(row['modal_fraction'] == baseline['modal_fraction'], 'Agreement mismatch')
        require(sum(row['original_residue_counts'].values()) == count, 'Residue counts mismatch')
        require(all(aa in 'ACDEFGHIKLMNPQRSTVWY' and type(n) is int and n > 0 for aa, n in row['original_residue_counts'].items()), 'Invalid residue counts')
        require(math.isfinite(row['mean_masked_nll_nats']) and row['mean_masked_nll_nats'] >= 0, 'Invalid NLL')
        contact = row['reference_1GGQ_A_contact_4_5_A']
        sasa = [row[k] for k in SASA_KEYS]
        if c not in observed:
            require(row['reference_1GGQ_A_observation_status'] == 'unobserved_or_unmapped', 'Unknown mapping mislabeled')
            require(contact is None and all(v is None for v in sasa), 'Unknown contact/SASA must remain null')
        else:
            require(row['reference_1GGQ_A_observation_status'] == 'observed', 'Observed mapping mismatch')
            require(type(contact) is bool, 'Observed contact must be boolean')
            require(all(type(v) in (int, float) and math.isfinite(v) and v >= 0 for v in sasa), 'Invalid calculated SASA')
            require(math.isclose(sasa[0] - sasa[1], sasa[2], abs_tol=1e-9), 'SASA loss differs from monomer minus dimer')
        rank = row['agreement_minus_predictability_percentile']
        require((rank is None) == (c not in full), 'Rank eligibility must use exactly F')
        if rank is not None:
            require(math.isfinite(rank) and -1 <= rank <= 1, 'Invalid descriptive rank')
    require(len(sequences) == len({s['accession'] for s in sequences}) == 30, 'Sequence inventory mismatch')
    require(sum(s['mask_count'] for s in sequences) == 6305, 'Wrong mask count')
    for seq in sequences:
        require(seq['scored_positions'] == '1..L all standard full-length natural residues', 'Undeclared score scope')
        require(math.isclose(math.exp(seq['mean_nll_nats']), seq['masked_pseudo_perplexity'], rel_tol=1e-12), 'Pseudo-perplexity mismatch')
    timing = evidence['personal_timing']
    require((timing['batch_size'], timing['scoring_masked_examples'], timing['scoring_forward_passes']) == (8, 6305, 805), 'Timing/call inventory mismatch')
    require(sum(math.ceil(s['mask_count'] / 8) for s in sequences) == 805, 'Per-sequence call accounting mismatch')
    require((timing['warmup_forward_passes'], timing['warmup_masked_examples'], timing['total_forward_passes']) == (3, 24, 808), 'Warm-up accounting mismatch')
    require(len(evidence['experimental_1GGQ_dimer_CA']) == 324, 'Experimental coordinate count mismatch')


def load_evidence(context):
    adapter = EXPERIMENT / 'results/laptop_evidence_v1.json'
    evidence = json.loads(adapter.read_text(encoding='utf-8'))
    validate_evidence(evidence, context)
    # Byte identities are provenance, not floating-point equivalence tests.
    raw = EXPERIMENT / evidence['recommended_files']['residue_scores']
    require(sha(raw) == evidence['source_scores_sha256'], 'Raw score hash mismatch')
    frozen = ROOT / 'sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0'
    for item in evidence['source_input_hashes']['files']:
        require(sha(frozen / item['source_relative_to_frozen_results']) == item['sha256'], 'Frozen input identity mismatch')
    current = read_tsv(EXPERIMENT / CURRENT)
    require(len(current) == 218, 'Current comparison must contain 218 columns')
    for row, actual in zip(evidence['columns'], current):
        require(row['alignment_column'] == int(actual['alignment_column']), 'Comparison column mismatch')
        require(row['mean_masked_nll_nats'] == float(actual['mean_original_residue_nll_nats']), 'NLL differs from v2 comparison')
        contact = actual['reference_1GGQ_assembly1_interchain_contact_4_5_A']
        require(contact in ('', 'True', 'False'), 'Unexpected contact encoding')
        require(row['reference_1GGQ_A_contact_4_5_A'] is {'': None, 'True': True, 'False': False}[contact], 'Contact differs from v2 comparison')
    summary = json.loads((EXPERIMENT / 'results/joint_sensitivity_summary.json').read_text())
    require(summary['panel_designs'] == 239 and summary['additional_model_forward_passes'] == 0, 'Sensitivity provenance mismatch')
    used = ['results/laptop_evidence_v1.json', CURRENT, 'results/joint_sensitivity_summary.json',
            'results/full_panel_v1/residue_nll.tsv', 'results/full_panel_v1/timings.json',
            'results/full_panel_agreement_predictability.png', 'results/experimental_dimer_comparison.png',
            'results/calculated_sasa_dimer_context.png']
    return {'evidence': evidence, 'sensitivity': summary, 'source_commit': COMMIT,
            'source_branch': 'feat/ospc-esm2-spark-pilot', 'release': 'v0.2.1',
            'current_comparison': CURRENT, 'source_hashes': {f: sha(EXPERIMENT / f) for f in used},
            'source_url': f'https://github.com/francolinx/LymeScope/tree/{COMMIT}/' + EXPERIMENT.relative_to(ROOT).as_posix(),
            'event_benchmark': 'NOT_RUN'}
