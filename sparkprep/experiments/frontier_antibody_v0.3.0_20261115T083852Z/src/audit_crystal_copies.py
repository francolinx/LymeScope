"""Posthoc geometric reliability audit of all deposited 9BIF copies; primary assembly stays fixed."""
import collections
import numpy as np
from scipy.spatial import cKDTree
from common import *
from map_complex import prepare, expected_atoms, AA

def audit():
    data = []
    assemblies = []
    strict_sets = []
    contact_sets = []
    for aid in ['1', '2', '3', '4']:
        c, instances, mapping, scheme, columns, summary = prepare('9BIF', aid)
        ab = np.array([a['xyz'] for inst in instances if inst['role'] == 'Fab' for a in inst['atoms']])
        tree = cKDTree(ab)
        site = collections.defaultdict(list)
        for inst in [x for x in instances if x['role'] == 'OspC']:
            bylabel = collections.defaultdict(list)
            for atom in inst['atoms']:
                bylabel[int(atom['label_seq_id'])].append(atom)
            for label, native in mapping.items():
                selected = bylabel[label]
                aa = AA[scheme[inst['label_chain'], label]['mon_id']]
                complete = expected_atoms(aa) <= {a['label_atom_id'] for a in selected}
                dist = float(tree.query(np.array([a['xyz'] for a in selected]))[0].min()) if selected else None
                site[columns[native - 1]].append({'complete': complete, 'contact': dist <= 4.5 if dist is not None else None})
        strict = {col for col, rs in site.items() if all((r['complete'] for r in rs))}
        positive = {col for col, rs in site.items() if any((r['contact'] is True for r in rs))}
        strict_sets.append(strict)
        contact_sets.append(positive)
        assemblies.append({'assembly_id': aid, 'strict_observed_construct_sites': len(strict), 'observed_contact_union_positions': len(positive), 'strict_contact_positions': len(strict & positive), 'observed_contact_columns': sorted(positive)})
        for col, rs in sorted(site.items()):
            data.append({'pdb_id': '9BIF', 'assembly_id': aid, 'alignment_column': col, 'all_OspC_copies_complete': col in strict, 'observed_contact_union_4_5_A': True if any((r['contact'] is True for r in rs)) else '' if any((r['contact'] is None for r in rs)) else False})
    common = set.intersection(*strict_sets)
    agreement = []
    for i in range(4):
        for j in range(i + 1, 4):
            a = contact_sets[i] & common
            b = contact_sets[j] & common
            agreement.append({'assembly_pair': [str(i + 1), str(j + 1)], 'common_complete_sites': len(common), 'contact_intersection': len(a & b), 'contact_union': len(a | b), 'jaccard_on_common_complete': len(a & b) / len(a | b) if a | b else None, 'disagreeing_alignment_columns': sorted(a ^ b)})
    out = {'status': 'COMPLETED_POSTHOC_GEOMETRY_QUALITY_AUDIT', 'primary_assembly_unchanged': '1', 'no_refitting': True, 'assemblies': assemblies, 'common_complete_sites_all_four': len(common), 'pairwise_contact_agreement': agreement, 'limitations': ['Crystal copies are correlated structural observations, not independent biological replicates.', 'This is a reliability audit of coordinate-derived contact labels, not a new optimized endpoint or a model-performance selection.']}
    write_tsv(ROOT / 'results/9BIF_CRYSTAL_COPY_CONTACTS.tsv', data)
    write_json(ROOT / 'results/9BIF_CRYSTAL_COPY_AUDIT.json', out)
    print(json.dumps(out, indent=2))
if __name__ == '__main__':
    audit()
