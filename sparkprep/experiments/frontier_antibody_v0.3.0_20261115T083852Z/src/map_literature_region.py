"""Project source-verified literature interval; never assign atom contacts from regional membership."""
from common import *

def run():
    source = json.loads((ROOT / 'inputs/8C1_literature_annotation.json').read_text())
    panel = fasta(ROOT / 'inputs/frozen_panel.fasta')
    aligned = fasta(ROOT / 'inputs/frozen_aligned.fasta')
    sequence = panel['Q07337']
    assert all((sequence[int(pos) - 1] == aa for pos, aa in source['identity_anchors'].items()))
    cols = [i for i, aa in enumerate(aligned['Q07337'], 1) if aa != '-']
    lo, hi = source['native_interval_Q07337']
    assert 1 <= lo <= hi <= len(sequence)
    result = [{'antibody': '8C1', 'source_doi': source['source_doi'], 'evidence_type': source['evidence_type'], 'Q07337_position': p, 'alignment_column': cols[p - 1], 'reference_aa': sequence[p - 1], 'antibody_contact_status': '', 'mapping_validation': 'Published K141/H142/T143/D144 anchors exactly match frozen Q07337; interval projected by frozen alignment', 'status': 'COMPLETED_LITERATURE_REGION_ONLY'} for p in range(lo, hi + 1)]
    write_tsv(ROOT / 'results/8C1_LITERATURE_REGION.tsv', result)
    write_json(ROOT / 'results/8C1_MAPPING_STATUS.json', {'status': 'COMPLETED_LITERATURE_REGION_ONLY', 'region_native_Q07337': [lo, hi], 'published_identity_anchors': source['identity_anchors'], 'contact_labels': 'NOT_ASSIGNED', 'primary_source': 'https://doi.org/' + source['source_doi'], 'later_deposition_notice': source['later_deposition_notice']})
if __name__ == '__main__':
    run()
