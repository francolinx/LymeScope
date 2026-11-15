"""Collapse experimental copies to unique frozen alignment sites with explicit null/missingness."""
import collections, csv
from common import *

def truth(value):
    return None if value == '' else value == 'True'

def union_observed(values):
    return True if True in values else None if None in values else False

def build():
    panel = fasta(ROOT / 'inputs/frozen_panel.fasta')
    aligned = fasta(ROOT / 'inputs/frozen_aligned.fasta')
    cols = list(csv.DictReader((ROOT / 'inputs/frozen_column_comparison_v2.tsv').read_text().splitlines(), delimiter='\t'))
    ref = {int(r['alignment_column']): r for r in csv.DictReader((ROOT / 'inputs/frozen_reference_mapping.tsv').read_text().splitlines(), delimiter='\t')}
    sasa = {r['label_seq_id']: r for r in csv.DictReader((ROOT / 'inputs/frozen_sasa_dimer.tsv').read_text().splitlines(), delimiter='\t') if r['pdb_id'] == '1GGQ' and r['instance'] == 'A@1' and (r['sphere_points_per_atom'] == '1920')}
    raw = list(csv.DictReader((ROOT / 'inputs/frozen_residue_nll.tsv').read_text().splitlines(), delimiter='\t'))
    assert len(raw) == 6305 and len({x['task_id'] for x in raw}) == 6305
    q = {int(r['sequence_position']): r for r in raw if r['accession'] == 'Q07337'}
    assert len(q) == 210
    universe = [int(r['alignment_column']) for r in cols if float(r['coverage']) == 1 and ref[int(r['alignment_column'])]['status'] == 'observed']
    assert len(universe) == 159
    import numpy as np
    blocks = {int(col): b for b, part in enumerate(np.array_split(universe, 8)) for col in part}
    out = []
    gate_counts = {}
    for code, antibody in [('9BIF', 'B11'), ('7UIJ', 'B5')]:
        mapping = list(csv.DictReader((ROOT / 'results' / f'{code}_RESIDUE_MAPPING.tsv').read_text().splitlines(), delimiter='\t'))
        mapped = collections.defaultdict(list)
        for r in mapping:
            mapped[int(r['alignment_column'])].append(r)
        assert all((len(rs) == 2 for rs in mapped.values()))
        counter = collections.Counter()
        for c in cols:
            col = int(c['alignment_column'])
            r = ref[col]
            rs = mapped[col]
            native = int(r['panel_sequence_position']) if r['panel_sequence_position'] else None
            aa = r['reference_aa'] if native else ''
            complete = len(rs) == 2 and all((x['observation_status'] == 'COMPLETE_CANONICAL_HEAVY_ATOMS' for x in rs))
            reasons = []
            if float(c['coverage']) != 1:
                reasons.append('PANEL_COVERAGE_LT_30')
            if r['status'] != 'observed':
                reasons.append('REFERENCE_1GGQ_NOT_OBSERVED')
            if not rs:
                reasons.append('NO_EXACT_COMPLEX_CONSTRUCT_MAPPING')
            elif not complete:
                reasons.append('COMPLEX_COPY_MISSING_OR_INCOMPLETE_HEAVY_ATOMS')
            if rs:
                assert native is not None and all((int(x['Q07337_position']) == native and x['reference_aa'] == aa == panel['Q07337'][native - 1] for x in rs))
            geometry = sasa.get(r['label_seq_id']) if r['status'] == 'observed' else None
            if r['status'] == 'observed':
                assert geometry is not None and geometry['aa'] == aa
            for cut in ['4_0', '4_5', '5_0']:
                pass
            row = {'pdb_id': code, 'antibody': antibody, 'assembly_id': 1, 'alignment_column': col, 'Q07337_position': native if native else '', 'reference_aa': aa, 'full_panel_coverage': float(c['coverage']), 'reference_1GGQ_status': r['status'], 'complex_mapped_copies': len(rs), 'complex_observed_copies': sum((x['observed_heavy_atoms'] != '0' for x in rs)), 'complex_complete_copies': sum((x['observation_status'] == 'COMPLETE_CANONICAL_HEAVY_ATOMS' for x in rs)), 'complex_auth_chains': ','.join((x['auth_chain'] for x in rs)), 'complex_label_chains': ','.join((x['label_chain'] for x in rs)), 'strict_eligible': not reasons, 'exclusion_reasons': '|'.join(reasons), 'fixed_reference_block': blocks.get(col, ''), 'modal_fraction': float(c['modal_fraction']), 'mean_nll_nats': float(c['mean_original_residue_nll_nats']), 'signed_discordance': float(c['agreement_minus_predictability_percentile']) if c['agreement_minus_predictability_percentile'] else '', 'Q07337_nll_nats': float(q[native]['nll_nats']) if native else '', 'reference_dimer_contact': truth(c['reference_1GGQ_assembly1_interchain_contact_4_5_A']) if c['reference_1GGQ_assembly1_observation_status'] == 'observed' else '', 'reference_dimer_sasa_A2': float(geometry['dimer_sasa_A2']) if geometry else '', 'reference_dimerization_sasa_loss_A2': float(geometry['delta_sasa_A2']) if geometry else ''}
            for cut in ['4_0', '4_5', '5_0']:
                observed = union_observed([truth(x[f'observed_contact_{cut}_A']) for x in rs]) if rs else None
                row[f'observed_contact_union_{cut}_A'] = '' if observed is None else observed
                row[f'strict_contact_union_{cut}_A'] = observed if complete else ''
            out.append(row)
            if float(c['coverage']) == 1:
                counter['full_panel_columns'] += 1
                if r['status'] == 'observed':
                    counter['full_panel_and_reference_observed'] += 1
                    if rs:
                        counter['plus_exact_complex_mapping'] += 1
                        if complete:
                            counter['plus_complete_complex_copies'] += 1
            for reason in reasons:
                counter['exclusion_' + reason] += 1
        gate_counts[code] = dict(counter)
    write_tsv(ROOT / 'EXPERIMENTAL_MAPPING.tsv', out)
    write_json(ROOT / 'results/ELIGIBILITY_GATES.json', {'gate_counts': gate_counts, 'pre_antibody_universe_count': 159, 'blocks': {str(b): [col for col in universe if blocks[col] == b] for b in range(8)}})
    print(json.dumps(gate_counts, indent=2))
if __name__ == '__main__':
    build()
