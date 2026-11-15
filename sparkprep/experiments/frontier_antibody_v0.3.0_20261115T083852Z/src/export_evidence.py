"""Typed optional scientific handoff for laptop integration; no demo/UI edits."""
import csv
from common import *
from map_complex import prepare

def typed(row):
    out = {}
    bools = {'strict_eligible', 'observed_contact_union_4_0_A', 'observed_contact_union_4_5_A', 'observed_contact_union_5_0_A', 'strict_contact_union_4_0_A', 'strict_contact_union_4_5_A', 'strict_contact_union_5_0_A', 'reference_dimer_contact'}
    ints = {'assembly_id', 'alignment_column', 'Q07337_position', 'complex_mapped_copies', 'complex_observed_copies', 'complex_complete_copies', 'fixed_reference_block'}
    floats = {'full_panel_coverage', 'modal_fraction', 'mean_nll_nats', 'signed_discordance', 'Q07337_nll_nats', 'reference_dimer_sasa_A2', 'reference_dimerization_sasa_loss_A2'}
    for key, value in row.items():
        out[key] = None if value == '' else value == 'True' if key in bools else int(value) if key in ints else float(value) if key in floats else value
    return out

def export():
    table = [typed(r) for r in csv.DictReader((ROOT / 'EXPERIMENTAL_MAPPING.tsv').read_text().splitlines(), delimiter='\t')]
    coordinates = {}
    for code in ['9BIF', '7UIJ']:
        c, instances, mapping, scheme, columns, summary = prepare(code)
        points = []
        for inst in instances:
            for atom in inst['atoms']:
                if atom['label_atom_id'] != 'CA':
                    continue
                label = int(atom['label_seq_id'])
                native = mapping[label] if inst['role'] == 'OspC' else None
                points.append({'pdb_id': code, 'assembly_id': '1', 'instance': inst['instance'], 'entity_id': inst['entity_id'], 'entity_description': inst['entity_description'], 'role': inst['role'], 'label_chain': inst['label_chain'], 'auth_chain': atom['auth_asym_id'], 'label_seq_id': label, 'auth_residue_number': atom['auth_seq_id'], 'insertion_code': blank(atom['pdbx_PDB_ins_code']), 'residue_name': atom['label_comp_id'], 'Q07337_position': native, 'alignment_column': columns[native - 1] if native else None, 'xyz_A': atom['xyz']})
        coordinates[code] = points
    result = {'schema': 'lymescope.frontier.experimental_contact.v1', 'status': 'COMPLETED', 'parent_reference_commit': 'aafe818a20ea025370cf4b65145a9684e80aaaef', 'preregistration_commit': '79b6d77a4c489fd9e0827c23bbccbabacad819a3', 'source_receipts': json.loads((ROOT / 'provenance/source_receipts.json').read_text()), 'endpoint': 'Observed Fab/OspC heavy-atom contacts <=4.5 A in deposited biological assembly1; site union over two complete antigen copies for strict labels', 'sites': table, 'experimental_CA_coordinates': coordinates, 'primary_summary': {k: v for k, v in json.loads((ROOT / 'ANALYSIS_RESULTS.json').read_text())['primary'].items() if k not in ['models', 'descriptives']}, 'evidence_levels': {'9BIF': 'OFFICIAL_EXPERIMENTAL_COORDINATES_PLUS_EXACT_SEQUENCE_MAPPING_DERIVED_CONTACTS', '7UIJ': 'SECONDARY_OFFICIAL_EXPERIMENTAL_COORDINATES_PLUS_EXACT_SEQUENCE_MAPPING_DERIVED_CONTACTS', '8C1': 'LITERATURE_DEFINED_HDX_REGION_ONLY_NO_ATOM_CONTACT_LABELS'}, 'literature_region_8C1': [{**dict(r), 'antibody_contact_status': None, 'Q07337_position': int(r['Q07337_position']), 'alignment_column': int(r['alignment_column'])} for r in csv.DictReader((ROOT / 'results/8C1_LITERATURE_REGION.tsv').read_text().splitlines(), delimiter='\t')], 'display_rules': ['Namespace PDB, chain label, author chain, sequence position and alignment column independently.', 'Never draw links across missing label_seq_id gaps or between structures using chain names alone.', 'Null is unknown/excluded, not noncontact; false means no observed atom contact under the stated endpoint.', 'Full modeled footprint and strict analysis eligibility are different fields.', 'Contacts describe the deposited antibody complex, not general antigenicity, functional necessity or protective immunity.', 'The predeclared discordance-added model does not improve the primary blocked diagnostic; preserve the negative result.', '8C1 literature rows are regional annotation, never direct-contact labels.'], 'integration_scope': 'Optional scientific adapter only. Laptop owns the existing README/demo/submission; stable v0.2.1 remains independently usable.'}
    write_json(ROOT / 'results/FRONTIER_EVIDENCE.json', result)
    print(json.dumps({'site_rows': len(table), 'CA_points': {k: len(v) for k, v in coordinates.items()}, 'sha256': sha(ROOT / 'results/FRONTIER_EVIDENCE.json')}, indent=2))
if __name__ == '__main__':
    export()
