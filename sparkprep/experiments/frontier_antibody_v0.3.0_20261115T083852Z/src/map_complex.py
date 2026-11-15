"""Observed Fab–OspC atom contacts with exact construct/reference mapping. No model inference."""
import collections, re, math
import numpy as np
from scipy.spatial import cKDTree
from common import *
from cif_reader import parse_cif
AA = {'ALA': 'A', 'ARG': 'R', 'ASN': 'N', 'ASP': 'D', 'CYS': 'C', 'GLN': 'Q', 'GLU': 'E', 'GLY': 'G', 'HIS': 'H', 'ILE': 'I', 'LEU': 'L', 'LYS': 'K', 'MET': 'M', 'PHE': 'F', 'PRO': 'P', 'SER': 'S', 'THR': 'T', 'TRP': 'W', 'TYR': 'Y', 'VAL': 'V'}
SIDE = {'A': 'CB', 'R': 'CB CG CD NE CZ NH1 NH2', 'N': 'CB CG OD1 ND2', 'D': 'CB CG OD1 OD2', 'C': 'CB SG', 'Q': 'CB CG CD OE1 NE2', 'E': 'CB CG CD OE1 OE2', 'G': '', 'H': 'CB CG ND1 CD2 CE1 NE2', 'I': 'CB CG1 CG2 CD1', 'L': 'CB CG CD1 CD2', 'K': 'CB CG CD CE NZ', 'M': 'CB CG SD CE', 'F': 'CB CG CD1 CD2 CE1 CE2 CZ', 'P': 'CB CG CD', 'S': 'CB OG', 'T': 'CB OG1 CG2', 'W': 'CB CG CD1 CD2 NE1 CE2 CE3 CZ2 CZ3 CH2', 'Y': 'CB CG CD1 CD2 CE1 CE2 CZ OH', 'V': 'CB CG1 CG2'}

def expected_atoms(aa):
    return set('N CA C O'.split()) | set(SIDE[aa].split())

def transform(point, op):
    return [sum((float(op[f'matrix[{i}][{j}]']) * point[j - 1] for j in [1, 2, 3])) + float(op[f'vector[{i}]']) for i in [1, 2, 3]]

def choose_atoms(atomrows):
    grouped = collections.defaultdict(list)
    for a in atomrows:
        if a['pdbx_PDB_model_num'] != '1' or a['type_symbol'] in ['H', 'D'] or float(a['occupancy']) <= 0:
            continue
        grouped[a['label_asym_id'], a['label_seq_id']].append(a)
    out = []
    alt_audit = []
    for key, resatoms in grouped.items():
        occupancy = collections.defaultdict(float)
        for a in resatoms:
            if blank(a['label_alt_id']):
                occupancy[a['label_alt_id']] += float(a['occupancy'])
        preferred = sorted(occupancy, key=lambda k: (-occupancy[k], k))[0] if occupancy else ''
        chosen = {}
        for a in resatoms:
            if blank(a['label_alt_id']) not in ['', preferred]:
                continue
            name = a['label_atom_id']
            if name not in chosen or (float(a['occupancy']), not bool(blank(a['label_alt_id']))) > (float(chosen[name]['occupancy']), not bool(blank(chosen[name]['label_alt_id']))):
                chosen[name] = a
        out.extend(chosen.values())
        if occupancy:
            alt_audit.append({'asym_id': key[0], 'label_seq_id': key[1], 'selected_alt': preferred, 'alternates': dict(occupancy)})
    return (out, alt_audit)

def exact_construct_mapping(construct, natural):
    starts = [i for i in range(len(natural) - len(construct) + 1) if natural[i:i + len(construct)] == construct]
    if len(starts) != 1:
        raise ValueError(f'Construct must have one exact full-length substring match; found {starts}')
    return {label: starts[0] + label for label in range(1, len(construct) + 1)}

def prepare(code, assembly='1'):
    c = parse_cif(ROOT / 'inputs' / f'{code}.cif')
    entities = {r['id']: r for r in rows(c, '_entity')}
    polys = {r['entity_id']: r for r in rows(c, '_entity_poly')}
    asym = {r['id']: r['entity_id'] for r in rows(c, '_struct_asym')}
    ops = {r['id']: r for r in rows(c, '_pdbx_struct_oper_list')}
    antigen = [eid for eid, e in entities.items() if e['type'] == 'polymer' and 'outer surface protein c' in e['pdbx_description'].lower()]
    antibody = [eid for eid, e in entities.items() if e['type'] == 'polymer' and 'fab' in e['pdbx_description'].lower()]
    assert len(antigen) == 1 and len(antibody) == 2, (code, antigen, antibody)
    panel = fasta(ROOT / 'inputs/frozen_panel.fasta')
    aligned = fasta(ROOT / 'inputs/frozen_aligned.fasta')
    record = json.loads((ROOT / 'inputs/Q07337_frozen_uniprot_record.json').read_text())
    assert record['sequence']['value'] == panel['Q07337']
    natural = panel['Q07337']
    construct = re.sub('\\s', '', polys[antigen[0]]['pdbx_seq_one_letter_code_can'])
    mapping = exact_construct_mapping(construct, natural)
    assert len(mapping) == 164 and min(mapping.values()) == 38 and (max(mapping.values()) == 201)
    for r in rows(c, '_struct_ref_seq'):
        if r['pdbx_db_accession'] == 'Q07337':
            assert int(r['seq_align_beg']) == 1 and int(r['seq_align_end']) == 164 and (int(r['db_align_beg']) == 38) and (int(r['db_align_end']) == 201)
    scheme = {(r['asym_id'], int(r['seq_id'])): r for r in rows(c, '_pdbx_poly_seq_scheme') if r['entity_id'] == antigen[0]}
    atoms, alt_audit = choose_atoms(rows(c, '_atom_site'))
    instances = []
    for gen in rows(c, '_pdbx_struct_assembly_gen'):
        if gen['assembly_id'] != assembly:
            continue
        expr = gen['oper_expression']
        assert re.fullmatch('\\d+(,\\d+)*', expr), ('Unsupported operator expression', expr)
        for chain in gen['asym_id_list'].split(','):
            entity = asym[chain]
            if entity not in antigen + antibody:
                continue
            for oid in expr.split(','):
                selected = []
                auth = set()
                for a in atoms:
                    if a['label_asym_id'] != chain:
                        continue
                    assert a['label_seq_id'] not in ['?', '.'] and a['label_comp_id'] in AA, (code, chain, a['label_comp_id'])
                    label = int(a['label_seq_id'])
                    auth.add(a['auth_asym_id'])
                    x = a.copy()
                    x['xyz'] = transform([float(a['Cartn_' + v]) for v in ['x', 'y', 'z']], ops[oid])
                    x['instance'] = chain + '@' + oid
                    selected.append(x)
                    if entity in antigen:
                        r = scheme[chain, label]
                        assert AA[a['label_comp_id']] == construct[label - 1] == natural[mapping[label] - 1] == AA[r['mon_id']]
                        assert a['auth_asym_id'] == r['pdb_strand_id']
                        assert blank(a['pdbx_PDB_ins_code']) == blank(r['pdb_ins_code'])
                        assert a['auth_seq_id'] == r['pdb_seq_num'], (code, chain, label, a['auth_seq_id'], r['pdb_seq_num'])
                instances.append({'instance': chain + '@' + oid, 'label_chain': chain, 'entity_id': entity, 'auth_chains': sorted(auth), 'role': 'OspC' if entity in antigen else 'Fab', 'entity_description': entities[entity]['pdbx_description'], 'atoms': selected, 'operator': ops[oid]})
    assert len([x for x in instances if x['role'] == 'OspC']) == 2 and len([x for x in instances if x['role'] == 'Fab']) == 4
    columns = [i for i, aa in enumerate(aligned['Q07337'], 1) if aa != '-']
    summary = {'pdb_id': code, 'assembly_id': assembly, 'entry_title': c.get('_struct.title'), 'method': c.get('_exptl.method'), 'resolution_A': c.get('_refine.ls_d_res_high'), 'revisions': rows(c, '_pdbx_audit_revision_history'), 'OspC_entity': antigen[0], 'Fab_entities': antibody, 'construct_length': len(construct), 'reference_accession': 'Q07337', 'native_range': [38, 201], 'exact_construct_sequence_sha256': hashlib.sha256(construct.encode()).hexdigest(), 'reference_sequence_sha256': hashlib.sha256(natural.encode()).hexdigest(), 'chain_instances': [{k: v for k, v in x.items() if k != 'atoms'} for x in instances], 'alt_selection_audit': alt_audit, 'atom_selection': 'model1; positive occupancy; no H/D; one occupancy-selected residue alt plus common atoms; canonical protein only; assembly roles from entity descriptions'}
    return (c, instances, mapping, scheme, columns, summary)

def map_one(code):
    c, instances, mapping, scheme, columns, summary = prepare(code)
    ab = [a for x in instances if x['role'] == 'Fab' for a in x['atoms']]
    assert ab
    tree = cKDTree(np.array([a['xyz'] for a in ab]))
    recordrows = []
    residuepairs = {}
    atom_contacts = []
    for inst in [x for x in instances if x['role'] == 'OspC']:
        bylabel = collections.defaultdict(list)
        for a in inst['atoms']:
            bylabel[int(a['label_seq_id'])].append(a)
        for label, native in mapping.items():
            rs = scheme[inst['label_chain'], label]
            aa = AA[rs['mon_id']]
            selected = bylabel[label]
            present = {a['label_atom_id'] for a in selected}
            missing = sorted(expected_atoms(aa) - present)
            contacts = {cut: False for cut in [4.0, 4.5, 5.0]}
            minimum = None
            partner_res = set()
            for a in selected:
                distance, j = tree.query(a['xyz'])
                minimum = float(distance) if minimum is None else min(minimum, float(distance))
                for cutoff in contacts:
                    if distance <= cutoff:
                        contacts[cutoff] = True
                for j in tree.query_ball_point(a['xyz'], 5.0):
                    b = ab[j]
                    dist = math.sqrt(sum(((u - v) ** 2 for u, v in zip(a['xyz'], b['xyz']))))
                    if dist > 5.0 + 1e-10:
                        continue
                    key = (inst['instance'], label, b['instance'], b['label_seq_id'])
                    partner_res.add((b['instance'], b['label_seq_id']))
                    row = {'pdb_id': code, 'assembly_id': '1', 'OspC_instance': inst['instance'], 'OspC_auth_chain': rs['pdb_strand_id'], 'OspC_label_seq_id': label, 'OspC_auth_residue_number': rs['pdb_seq_num'], 'OspC_insertion_code': blank(rs['pdb_ins_code']), 'Q07337_position': native, 'alignment_column': columns[native - 1], 'OspC_aa': aa, 'Fab_instance': b['instance'], 'Fab_auth_chain': b['auth_asym_id'], 'Fab_label_seq_id': b['label_seq_id'], 'Fab_auth_residue_number': b['auth_seq_id'], 'Fab_insertion_code': blank(b['pdbx_PDB_ins_code']), 'Fab_residue_name': b['label_comp_id'], 'min_distance_A': dist, 'OspC_atom_at_min': a['label_atom_id'], 'Fab_atom_at_min': b['label_atom_id']}
                    if key not in residuepairs or dist < residuepairs[key]['min_distance_A']:
                        residuepairs[key] = row
            recordrows.append({'pdb_id': code, 'assembly_id': '1', 'OspC_instance': inst['instance'], 'label_chain': inst['label_chain'], 'auth_chain': rs['pdb_strand_id'], 'label_seq_id': label, 'auth_residue_number': rs['pdb_seq_num'], 'insertion_code': blank(rs['pdb_ins_code']), 'Q07337_position': native, 'alignment_column': columns[native - 1], 'reference_aa': aa, 'mapping_status': 'EXACT_CONSTRUCT_AND_ATOM_IDENTITY', 'observation_status': 'UNOBSERVED' if not selected else 'COMPLETE_CANONICAL_HEAVY_ATOMS' if not missing else 'INCOMPLETE_CANONICAL_HEAVY_ATOMS', 'observed_heavy_atoms': len(present), 'expected_heavy_atoms': len(expected_atoms(aa)), 'missing_atom_names': ','.join(missing), 'observed_contact_4_0_A': contacts[4.0] if selected else '', 'observed_contact_4_5_A': contacts[4.5] if selected else '', 'observed_contact_5_0_A': contacts[5.0] if selected else '', 'strict_contact_4_5_A': contacts[4.5] if selected and (not missing) else '', 'min_observed_Fab_distance_A': minimum if minimum is not None else ''})
    pairs = sorted(residuepairs.values(), key=lambda r: (r['OspC_instance'], r['OspC_label_seq_id'], r['Fab_instance'], int(r['Fab_label_seq_id'])))
    write_tsv(ROOT / 'results' / f'{code}_RESIDUE_MAPPING.tsv', recordrows)
    write_tsv(ROOT / 'results' / f'{code}_FAB_CONTACT_PAIRS_5A.tsv', pairs)
    summary['observation_counts'] = dict(collections.Counter((r['observation_status'] for r in recordrows)))
    summary['contact_positions_by_cutoff'] = {str(cut): len({r['alignment_column'] for r in recordrows if r[f'observed_contact_{str(cut).replace('.', '_')}_A'] is True}) for cut in [4.0, 4.5, 5.0]}
    write_json(ROOT / 'results' / f'{code}_MAPPING_STATUS.json', summary)
    return summary
if __name__ == '__main__':
    for code in ['9BIF', '7UIJ']:
        s = map_one(code)
        print(json.dumps({k: v for k, v in s.items() if k not in ['chain_instances', 'alt_selection_audit']}, indent=2))
