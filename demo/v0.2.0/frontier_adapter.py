"""Read the pinned antibody experiment; no inference, fitting or coordinate edits."""
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import TypedDict

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / 'sparkprep/experiments/frontier_antibody_v0.3.0_20261115T083852Z'
COMMIT = '82fb8b53018ba4012ccebf02a29efa87b892f6ed'


class ContactSite(TypedDict):
    pdb_id: str
    assembly_id: int
    alignment_column: int
    Q07337_position: int | None
    observed_contact_union_4_5_A: bool | None
    strict_contact_union_4_5_A: bool | None
    strict_eligible: bool
    reference_dimer_contact: bool | None
    reference_dimer_sasa_A2: float | None


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(evidence, columns):
    require(evidence['schema'] == 'lymescope.frontier.experimental_contact.v1', 'Unknown frontier schema')
    require(evidence['status'] == 'COMPLETED', 'Incomplete frontier evidence')
    require(len(evidence['sites']) == 436, 'Expected two separate 218-column maps')
    complexes = {}
    for code, antibody, contacts, observed_contacts in [('9BIF', 'B11', 31, 32), ('7UIJ', 'B5', 25, 27)]:
        sites: list[ContactSite] = [s for s in evidence['sites'] if s['pdb_id'] == code]
        require([s['alignment_column'] for s in sites] == list(range(1, 219)), 'Duplicate/missing alignment columns')
        for site, column in zip(sites, columns):
            require(site['assembly_id'] == 1 and site['antibody'] == antibody, 'Complex namespace mismatch')
            for key in ('observed_contact_union_4_5_A', 'strict_contact_union_4_5_A', 'reference_dimer_contact'):
                require(site[key] is None or type(site[key]) is bool, 'Contact must be boolean or null')
            if site['complex_mapped_copies'] == 0:
                require(site['observed_contact_union_4_5_A'] is None, 'Unmapped contact must remain null')
            if site['complex_complete_copies'] != 2:
                require(site['strict_contact_union_4_5_A'] is None, 'Incomplete strict contact must remain null')
            if site['strict_eligible']:
                require(site['full_panel_coverage'] == 1 and site['reference_1GGQ_status'] == 'observed'
                        and site['complex_complete_copies'] == 2, 'Invalid strict eligibility')
            for left, right in [('modal_fraction', 'modal_fraction'), ('full_panel_coverage', 'coverage'),
                                ('mean_nll_nats', 'mean_masked_nll_nats'),
                                ('reference_dimer_contact', 'reference_1GGQ_A_contact_4_5_A'),
                                ('reference_dimer_sasa_A2', 'reference_1GGQ_A_calculated_dimer_sasa_A2')]:
                # Exact saved inputs, including nulls; no numerical recomputation here.
                require(site[left] == column[right], f'Reused v2 field differs: {left}')
        eligible = [s for s in sites if s['strict_eligible']]
        require(len(eligible) == 152, 'Eligible count mismatch')
        require(sum(s['strict_contact_union_4_5_A'] is True for s in eligible) == contacts, 'Strict contact count mismatch')
        require(sum(s['observed_contact_union_4_5_A'] is True for s in sites) == observed_contacts, 'Observed contact count mismatch')
        complexes[code] = {'antibody': antibody, 'sites': sites, 'eligible_count': len(eligible),
                           'eligible_contact_count': contacts, 'observed_contact_count': observed_contacts}
    region = evidence['literature_region_8C1']
    require(len(region) == 21 and all(r['antibody_contact_status'] is None for r in region), '8C1 must remain literature-only')
    require([r['Q07337_position'] for r in region] == list(range(130, 151)), '8C1 native interval mismatch')
    require(evidence['primary_summary']['primary_delta_oof_brier_B3_minus_B2'] > 0, 'Negative primary result must remain visible')
    return complexes


def load_evidence(columns):
    manifest = json.loads((EXPERIMENT / 'FILE_MANIFEST.json').read_text(encoding='utf-8'))
    files = {r['path']: r for r in manifest['files']}
    consumed = ('results/FRONTIER_EVIDENCE.json', 'results/COMPARISON_METRICS.tsv',
                'results/FRONTIER_EXPERIMENT.svg', 'results/FRONTIER_EXPERIMENT.png')
    for name in consumed:
        raw = (EXPERIMENT / name).read_bytes()
        require(len(raw) == files[name]['bytes'] and hashlib.sha256(raw).hexdigest() == files[name]['sha256'], f'Changed frontier source: {name}')
    evidence = json.loads((EXPERIMENT / consumed[0]).read_text(encoding='utf-8'))
    complexes = validate(evidence, columns)
    with (EXPERIMENT / consumed[1]).open(encoding='utf-8', newline='') as handle:
        rows = list(csv.DictReader(handle, delimiter='\t'))
    metrics = {r['model']: {'brier': float(r['OOF_Brier']), 'auroc': float(r['OOF_AUROC'])}
               for r in rows if r['pdb_id'] == '9BIF' and float(r['cutoff_A']) == 4.5}
    delta = metrics['B3']['brier'] - metrics['B2']['brier']
    require(math.isclose(delta, evidence['primary_summary']['primary_delta_oof_brier_B3_minus_B2'], abs_tol=1e-15), 'Primary metric mismatch')
    return {'schema': 'lymescope.frontier_presentation.v1', 'source_commit': COMMIT,
            'source_manifest_sha256': hashlib.sha256((EXPERIMENT / 'FILE_MANIFEST.json').read_bytes()).hexdigest(),
            'sources': [files[name] for name in consumed], 'endpoint': evidence['endpoint'],
            'primary_summary': evidence['primary_summary'], 'primary_metrics': metrics,
            'complexes': complexes, 'literature_region_8C1': evidence['literature_region_8C1'],
            'display_rules': evidence['display_rules'], 'additional_model_calls': 0,
            'hypothesis_support': 'NOT_SUPPORTED_BY_PREDECLARED_DIAGNOSTIC'}
