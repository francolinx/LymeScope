"""Independent full distance-matrix validation of KD-tree contact calculations and reference fold mapping."""
import collections, csv
import numpy as np
from scipy.spatial.distance import cdist
from common import *
from map_complex import prepare, AA
from cif_reader import parse_cif

def audit(code):
    c, instances, mapping, scheme, columns, summary = prepare(code)
    fab = [a for x in instances if x['role'] == 'Fab' for a in x['atoms']]
    fabxyz = np.array([a['xyz'] for a in fab])
    derived = list(csv.DictReader((ROOT / 'results' / f'{code}_RESIDUE_MAPPING.tsv').read_text().splitlines(), delimiter='\t'))
    lookup = {(r['OspC_instance'], int(r['label_seq_id'])): r for r in derived}
    maxerror = 0
    checked = 0
    for instance in [x for x in instances if x['role'] == 'OspC']:
        atoms = instance['atoms']
        xyz = np.array([a['xyz'] for a in atoms])
        minima = collections.defaultdict(lambda: float('inf'))
        for start in range(0, len(atoms), 128):
            ds = cdist(xyz[start:start + 128], fabxyz)
            mins = ds.min(axis=1)
            for a, value in zip(atoms[start:start + 128], mins):
                label = int(a['label_seq_id'])
                minima[label] = min(minima[label], float(value))
        for label, value in minima.items():
            r = lookup[instance['instance'], label]
            err = abs(value - float(r['min_observed_Fab_distance_A']))
            maxerror = max(maxerror, err)
            assert err < 1e-10
            for cut in [4.0, 4.5, 5.0]:
                key = 'observed_contact_' + f'{cut:.1f}'.replace('.', '_') + '_A'
                assert (r[key] == 'True') == (value <= cut), (code, label, key)
            checked += 1
    refc = parse_cif(ROOT / 'inputs/1GGQ_reference.cif')
    refscheme = {(r['asym_id'], r['seq_id']): r for r in rows(refc, '_pdbx_poly_seq_scheme')}
    refca = {}
    for a in rows(refc, '_atom_site'):
        if a['label_asym_id'] == 'A' and a['label_atom_id'] == 'CA' and (a['pdbx_PDB_model_num'] == '1') and (float(a['occupancy']) > 0):
            rs = refscheme['A', a['label_seq_id']]
            native = int(rs['pdb_seq_num'])
            refca[native] = (AA[a['label_comp_id']], np.array([float(a['Cartn_' + k]) for k in ['x', 'y', 'z']]))
    rmsds = []
    for inst in [x for x in instances if x['role'] == 'OspC']:
        pairs = []
        for a in inst['atoms']:
            if a['label_atom_id'] != 'CA':
                continue
            native = mapping[int(a['label_seq_id'])]
            if native not in refca:
                continue
            aa, refxyz = refca[native]
            assert aa == AA[a['label_comp_id']]
            pairs.append((np.array(a['xyz']), refxyz))
        X = np.array([a for a, b in pairs])
        Y = np.array([b for a, b in pairs])
        X -= X.mean(0)
        Y -= Y.mean(0)
        u, s, vt = np.linalg.svd(X.T @ Y)
        correction = np.eye(3)
        correction[-1, -1] = np.linalg.det(u @ vt)
        rot = u @ correction @ vt
        rmsd = float(np.sqrt(np.mean(np.sum((X @ rot - Y) ** 2, axis=1))))
        rmsds.append({'instance': inst['instance'], 'matched_CA': len(pairs), 'CA_RMSD_to_1GGQ_chain_A_A': rmsd, 'proper_rotation_determinant': float(np.linalg.det(rot))})
        assert rmsd < 3.0, 'Unexpected fold-coordinate mismatch; inspect mapping before analysis'
    return {'pdb_id': code, 'status': 'PASS', 'residue_distance_minima_checked': checked, 'max_abs_distance_error_A': maxerror, 'all_fixed_cutoff_labels_match': True, 'reference_superposition': rmsds, 'insertion_codes_in_selected_Fab_atoms': sorted({blank(a['pdbx_PDB_ins_code']) for a in fab if blank(a['pdbx_PDB_ins_code'])})}
if __name__ == '__main__':
    out = [audit(code) for code in ['9BIF', '7UIJ']]
    write_json(ROOT / 'results/INDEPENDENT_GEOMETRY_AUDIT.json', out)
    print(json.dumps(out, indent=2))
