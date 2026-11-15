"""Build a navigable claim index from saved results; no scientific inference."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP = 'sparkprep/experiments/stretch_v0.2.0_20261115T072916Z'
FROZEN = 'sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0'
SPARK_COMMIT = 'aafe818a20ea025370cf4b65145a9684e80aaaef'
BASELINE_COMMIT = '8058846c05d4dccd60117dd29ef784af43570418'


def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


def build():
    frozen = read(FROZEN+'/viewer_data.json')
    adapter = read(EXP+'/results/laptop_evidence_v1.json')
    timing = adapter['personal_timing']
    sensitivity = read(EXP+'/results/joint_sensitivity_summary.json')
    contacts = read(EXP+'/results/dimer_context_summary.json')
    sasa = next(x for x in adapter['calculated_sasa_method']['calculations'] if x['pdb_id']=='1GGQ' and x['sphere_points_per_atom']==1920)
    inventory = read('docs/frontier_v0.3.0/experimental-evidence.json')
    claims = []

    def add(identifier, assertion, level, paths, method, limitations, metrics=None, refs=(), status='VERIFIED_SAVED_EVIDENCE'):
        sources=[]
        for path in paths:
            raw=(ROOT/path).read_bytes()
            sources.append({'path':path,'sha256':hashlib.sha256(raw).hexdigest(), 'bytes':len(raw),
                            'commit':SPARK_COMMIT if path.startswith(EXP) else BASELINE_COMMIT if path.startswith(FROZEN) else None})
        claims.append({'claim_id':identifier,'assertion':assertion,'evidence_level':level,'sources':sources,
                       'method':method,'run_id':'stretch_v0.2.0_20261115T072916Z/full_panel_v1' if level=='PERSONAL_SPARK_COMPUTATION' else None,
                       'primary_references':list(refs),'interpretation_limitations':limitations,
                       'verification_status':status,'metrics':metrics or {}})

    add('C01','CDC distinguishes more than 80,000 annually reported Lyme cases from a claims-based estimate of 476,000 people diagnosed and treated.','PUBLIC_HEALTH_SOURCE',[],
        'Primary CDC surveillance page checked November 15, 2026.','Different measures; neither is an exact infection count. Claims estimates may overcount; surveillance has underreporting/misclassification.',
        refs=['https://www.cdc.gov/lyme/data-research/facts-stats/'],status='PRIMARY_RECORD_VERIFIED')
    full=[c['alignment_column'] for c in frozen['columns'] if c['coverage']==1]
    mapped=[m['alignment_column'] for m in frozen['mapping'] if m['status']=='observed']
    add('C02','The selected panel has 30 natural sequences, 218 fixed columns, F=202 fully covered, M=162 observed mapped columns, and MF=159.','FROZEN_BASELINE',[FROZEN+'/viewer_data.json'],
        'Saved coverage and explicit coordinate-status mapping.','Selected related sequences; not universal conservation or independent residue samples.',
        {'sequences':30,'columns':len(frozen['columns']),'F':len(full),'M':len(mapped),'MF':len(set(full)&set(mapped)),'M_minus_F':sorted(set(mapped)-set(full))})
    add('C03','Columns 154 and 173 each have modal agreement 1.0 from one of 30 observations and no reference coordinate.','FROZEN_BASELINE',[FROZEN+'/viewer_data.json'],
        'Observed standard-residue fraction; gaps excluded from agreement and retained in coverage.','The percentage is correctly calculated from one observation; that is insufficient support for broad conservation in this panel.',
        {str(c):{'count':adapter['columns'][c-1]['observed_residue_count'],'coverage':adapter['columns'][c-1]['coverage'],'modal_fraction':adapter['columns'][c-1]['modal_fraction'],'contact':adapter['columns'][c-1]['reference_1GGQ_A_contact_4_5_A']} for c in (154,173)})
    add('C04','The personal Spark completed 6,305 original-residue masks in 805 scoring forwards at per-sequence batch size 8.','PERSONAL_SPARK_COMPUTATION',[EXP+'/results/full_panel_v1/timings.json',EXP+'/results/full_panel_validation.json'],
        'One mask per example; sum of per-sequence ceil(length/batch size); actual successful calls recorded.','Three warm-up forwards / 24 examples are additional, not scientific rows.',
        {k:timing[k] for k in ['scoring_masked_examples','scoring_forward_passes','batch_size','warmup_forward_passes','warmup_masked_examples','total_forward_passes']})
    add('C05','Personal GB10 warm scoring took 9.909294 seconds; load/transfer took 0.313129 seconds.','PERSONAL_SPARK_COMPUTATION',[EXP+'/results/full_panel_v1/timings.json'],
        'Synchronized GPU scoring and separate load/transfer receipt.','One personal-host run, not a matched venue benchmark. Process wall starts after imports; OS page cache uncontrolled.',
        {k:timing[k] for k in ['host','device','warm_scoring_wall_s','model_load_and_cuda_transfer_s','first_forward_after_load_s','end_to_end_wall_s','peak_gpu_allocated_bytes','peak_gpu_reserved_bytes']})
    add('C06','The primary score is masked-original-residue NLL under pinned ESM-2 8M, using all 33 vocabulary logits.','METHOD_AND_PROVENANCE',[EXP+'/provenance/method_contract.json',EXP+'/provenance/model_download_receipt.json'],
        'Natural-log softmax, eval/inference mode, fp32/eager, TF32 disabled, one masked original residue; exact token/mapping assertions.','Neither empirical conservation nor entropy, mutation effect, function, immunogenicity or an autoregressive sequence likelihood.',
        {'model':adapter['model']['model_id'],'revision':adapter['model']['revision'],'score_sha256':adapter['source_scores_sha256']},refs=['https://huggingface.co/facebook/esm2_t6_8M_UR50D','https://doi.org/10.1126/science.ade2574'])
    add('C07','Agreement versus predictability has descriptive Spearman rho 0.134696 across F=202; 239 overlapping fixed-alignment subsets assess sensitivity.','PERSONAL_SPARK_COMPUTATION',[EXP+'/results/joint_sensitivity_summary.json',EXP+'/results/full_panel_comparison_v2/column_comparison.tsv'],
        'Common full-coverage column set, average tied ranks; reuse unchanged per-sequence scores.','Overlapping subsets are not independent replicates or a population confidence interval; no significance claim.',
        {k:sensitivity[k] for k in ['full_panel_agreement_predictability_spearman_rho','panel_designs','fixed_full_coverage_columns','additional_model_forward_passes','half_panel_rho_min','half_panel_rho_max']})
    add('C08','Columns 177 and 129 illustrate high agreement/high NLL versus lower agreement/lower NLL.','PERSONAL_SPARK_COMPUTATION',[EXP+'/results/laptop_evidence_v1.json'],
        'Column mean NLL among observed original residues, shown beside empirical residue counts.','Illustrative selected positions, not an antibody-binding or biological-function prediction.',
        {str(c):adapter['columns'][c-1] for c in (177,129)})
    add('C09','1GGQ assembly 1 has 118 interchain heavy-atom residue pairs within 4.5 Å and 51 contacting residues per partner.','COMPUTED_EXPERIMENTAL_GEOMETRY',[EXP+'/results/dimer_context_summary.json',EXP+'/results/dimer_contacts.tsv'],
        contacts['method'],'OspC–OspC dimer contacts, not antibody contacts. Cutoff/construct dependent; missing coordinates are unknown.',
        contacts['assemblies'][0],refs=['https://www.rcsb.org/structure/1GGQ','https://doi.org/10.1093/emboj/20.5.971'])
    add('C10','1GGQ calculated total SASA loss is 4,081.16 Å²; mean partner interface area is half, 2,040.58 Å².','CALCULATED_SASA',[EXP+'/results/sasa_context_summary.json',EXP+'/results/sasa_dimer_context.tsv'],
        'Heavy-atom Shrake–Rupley-style Fibonacci sampling, stated element radii, 1.40 Å probe, 1,920 points/atom.','Static incomplete constructs; no physiological/antibody accessibility measurement or exposed/buried classification.',sasa)
    add('C11','The second reference 1G5Z uses an explicitly transformed symmetry partner and an exact Q44717 construct correspondence.','COMPUTED_EXPERIMENTAL_GEOMETRY',[EXP+'/results/dimer_alignment_mapping.tsv',EXP+'/results/dimer_context_summary.json'],
        'Whole-construct sequence identity and deposited assembly operators.','Residue numbering is not transferred by accession metadata alone. Separate structure, not a new model-generated fold.',
        contacts['assemblies'][2],refs=['https://www.rcsb.org/structure/1G5Z','https://doi.org/10.1074/jbc.M010062200'])
    add('C12','Current v2 unknown/unobserved contacts and SASA remain null, distinct from observed false and calculated zero.','DATA_SEMANTICS',[EXP+'/results/laptop_evidence_v1.json',EXP+'/provenance/analysis_corrections.json'],
        'Typed adapter and explicit coordinate status; v2 supersedes the earlier false labels.','The schema suffix evidence.v1 does not mean the superseded comparison_v1 aggregate.')
    add('C13','CIQ Fuzzball ran a CUDA calculation on Spark30 and verified identical stored bytes on Spark29 and Spark30.','EVENT_INFRASTRUCTURE',[ 'findings/phase-b-results.json'],
        'Saved CUDA and shared-NFS write/read receipts with physical-node attribution.','Infrastructure proof, not the scientific throughput benchmark. Vendor/backend identity is not established by identical-byte reads alone.',
        {'cuda':'PASS','shared_storage':'PASS','event_scientific_benchmark':'NOT_RUN'})
    add('C14','The matched event scientific one-node/two-node comparison is prepared but NOT RUN.','PLANNED_WORKFLOW',['workflows/ospc-spark-v0.2.1/trial.HOLD.json'],
        'Spark30 all tasks, then concurrent Spark29/Spark30 shards; identical batch-8 protocol.','Authorization, staging, runtime, placement and venue pilots are gates. No measured speedup.',
        {'one_node_masks':6305,'two_node_masks':[3156,3149],'one_node_calls':805,'two_node_calls':[403,402],'speedup':None},status='NOT_RUN')
    add('C15','Published B11/9BIF, B5/7UIJ and the 8C1 study supply independent experimental context; no antibody residue overlay is yet imported.','PUBLISHED_EXPERIMENTAL_CONTEXT',['docs/frontier_v0.3.0/experimental-evidence.json'],
        'Official PDB metadata and primary paper records checked; educational source card only.','Published numbering requires validated chain/sequence/alignment mapping. Homodimer contacts are not antibody contacts.',
        {'mapping_status':inventory['mapping_status'],'mapped_contact_positions':inventory['mapped_antibody_contact_positions']},
        refs=[s['primary_reference'] for s in inventory['sources']],status='SOURCE_VERIFIED_MAPPING_PENDING')
    add('C16','The animations use saved alignment/coordinates and rigid camera motion; they are not new predicted structures or dynamics.','PRESENTATION_OF_SAVED_EVIDENCE',['demo/v0.2.0/assets/manifest.json'],
        'Original Pillow/NumPy renders, static alternatives, source hashes and decoded-frame checks.','The legacy dimer amber color is a separate 8 Å Cα proxy (49 residues/chain), not the 4.5 Å heavy-atom field. Browser playback requires its own check.')
    add('C17','The published personal-Spark experiment reports sixteen passing tests and an independent full-result arithmetic audit.','PUBLISHED_VALIDATION',[EXP+'/provenance/tests_full_release.log',EXP+'/results/full_panel_validation.json'],
        'Saved runtime test receipt plus independent CSV arithmetic, task identity and mapping checks.','Laptop offline fixtures do not validate new real-model inference; local runtime limitations are reported separately.',{'published_tests_passed':16})
    document={'schema':'lymescope.claim_index.v1','publication_scope':'feature/ospc-masked-scoring-v0.2.0',
              'scientific_source_commit':SPARK_COMMIT,'baseline_commit':BASELINE_COMMIT,'claims':claims,
              'rule':'Every claim identifies measurement level, source bytes, method and limits. Pending work is not a result.'}
    (ROOT/'docs/claim-index.json').write_text(json.dumps(document,indent=2,ensure_ascii=False,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
    md=['# LymeScope claim index','','Machine-readable companion: [claim-index.json](claim-index.json). Generated from saved evidence; no new inference.','']
    for c in claims:
        md += ['## '+c['claim_id'],'',c['assertion'],'',f"**Level:** {c['evidence_level']} · **Status:** {c['verification_status']}",'',c['method'],'', '**Limits:** '+c['interpretation_limitations'],'']
        for s in c['sources']:
            md += [f"- [{s['path']}](../{s['path']}) · SHA256 `{s['sha256']}`"]
        for i,url in enumerate(c['primary_references'],1):md += [f'- [Primary source {i}]({url})']
        md+=['']
    (ROOT/'docs/claim-index.md').write_text('\n'.join(md).rstrip()+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'claims':len(claims),'source_commit':SPARK_COMMIT}))


if __name__=='__main__':build()
