"""Resolve depositor-listed missing residues and bound missing-Fab context without inventing contacts."""
import numpy as np
from scipy.spatial.distance import cdist
from common import *
from map_complex import prepare

def segments(values):
    out = []
    for value in sorted(values):
        if out and value == out[-1][-1] + 1:
            out[-1].append(value)
        else:
            out.append([value])
    return out

def audit(code):
    c, instances, *_ = prepare(code)
    antigen_xyz = np.array([a['xyz'] for inst in instances if inst['role'] == 'OspC' for a in inst['atoms']])
    reports = []
    for inst in instances:
        all_labels = {int(r['seq_id']) for r in rows(c, '_pdbx_poly_seq_scheme') if r['asym_id'] == inst['label_chain']}
        observed = {int(a['label_seq_id']) for a in inst['atoms']}
        missing = all_labels - observed
        declared = {int(r['label_seq_id']) for r in rows(c, '_pdbx_unobs_or_zero_occ_residues') if r['PDB_model_num'] == '1' and r['label_asym_id'] == inst['label_chain']}
        assert missing == declared, (code, inst['instance'], missing ^ declared)
        ca = {int(a['label_seq_id']): a for a in inst['atoms'] if a['label_atom_id'] == 'CA'}
        gaps = []
        for gap in segments(missing):
            adjacent = [max((n for n in ca if n < gap[0]), default=None), min((n for n in ca if n > gap[-1]), default=None)]
            flanks = []
            for label in adjacent:
                if label is None:
                    continue
                a = ca[label]
                distance = float(cdist(np.array([a['xyz']]), antigen_xyz).min()) if inst['role'] == 'Fab' else None
                flanks.append({'observed_label_seq_id': label, 'auth_residue_number': a['auth_seq_id'], 'minimum_flanking_CA_to_observed_OspC_heavy_atom_A': distance})
            gaps.append({'missing_label_range': [gap[0], gap[-1]], 'missing_count': len(gap), 'observed_flanks': flanks})
        reports.append({'instance': inst['instance'], 'auth_chains': inst['auth_chains'], 'role': inst['role'], 'construct_residues': len(all_labels), 'observed_residues': len(observed), 'missing_residues': len(missing), 'all_missing_match_depositor_unobserved_records': True, 'gaps': gaps})
    return {'pdb_id': code, 'status': 'COMPLETED', 'chains': reports, 'interpretation': 'Flanking distances describe known coordinates only; they do not reconstruct the missing residue or prove that an unmodeled loop cannot contact antigen. Noncontact labels mean no observed atom contact under the endpoint, not lack of binding potential.'}
if __name__ == '__main__':
    j = [audit(code) for code in ['9BIF', '7UIJ']]
    write_json(ROOT / 'results/MISSINGNESS_AUDIT.json', j)
    print(json.dumps(j, indent=2))
