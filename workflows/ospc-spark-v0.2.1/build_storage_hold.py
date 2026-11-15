"""Prepare an inert v4 workflow and exact byte plan; never submit or upload."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
COMMIT='aafe818a20ea025370cf4b65145a9684e80aaaef'
PACKAGE='sparkprep/experiments/stretch_v0.2.0_20261115T072916Z'
RUN='venue-v021-20261115T140000Z'


def build():
    # In-memory deterministic archive sizing only: nothing is written/uploaded.
    payload=subprocess.check_output(['git','archive','--format=tar',COMMIT,PACKAGE],cwd=ROOT)
    with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
        science_files=[x for x in archive.getmembers() if x.isfile()]
        if not all(x.name.startswith(PACKAGE+'/') for x in science_files):raise ValueError('Unexpected archive scope')
    model=json.loads((ROOT/PACKAGE/'provenance/model_transfer_bundle_receipt.json').read_text())
    model_files=json.loads((ROOT/PACKAGE/'provenance/model_download_receipt.json').read_text())['files']
    plan={'schema':'lymescope.shared_storage_plan.v1','status':'HOLD_NOT_SUBMITTED',
        'scientific_commit':COMMIT,'package_path':PACKAGE,'run_id':RUN,
        'provisioner':'team15','volume':'lymescope-project',
        'volume_id':'01a1dc69-7808-7695-b6d3-f8a3f6e5a437',
        'provisioner_id_from_historical_volume':'4dfde680-0cc5-3488-9376-7cf20605b12f',
        'vast_backend':'UNVERIFIED','live_volume_readback':'TIMEOUT',
        'object_prefix':'fb://group/lymescope/ospc-v0.2.1/'+RUN,
        'volume_root':'/project/ospc-v0.2.1/'+RUN,
        'science':{'archive_bytes':len(payload),'archive_sha256':hashlib.sha256(payload).hexdigest(),
            'expanded_bytes':sum(x.size for x in science_files),'regular_files':len(science_files)},
        'model':{'archive_bytes':model['bytes'],'archive_sha256':model['sha256'],
            'expanded_bytes':model['six_file_uncompressed_payload_bytes'],'revision':model['model_revision'],
            'file_names':[x['name'] for x in model_files],'files':model_files},
        'output_and_receipt_budget_bytes':32*1024**2,'incremental_reservation_bytes':128*1024**2,
        'historical_quota_bytes':1024**3,'current_used_bytes':None,'current_free_quota_bytes':None,
        'scientific_jobs_submitted':0,'staging_jobs_submitted':0,'archive_written':False}
    plan['peak_payload_plus_output_budget_bytes']=sum(plan[k]['archive_bytes']+plan[k]['expanded_bytes'] for k in ('science','model'))+plan['output_and_receipt_budget_bytes']
    plan['peak_quota_percent']=100*plan['peak_payload_plus_output_budget_bytes']/plan['historical_quota_bytes']
    encoded=json.dumps(plan,indent=2)+'\n'
    (HERE/'storage-plan.HOLD.json').write_text(encoded,encoding='utf-8',newline='\n')
    worker=(HERE/'stage_shared.py').read_text(encoding='utf-8')
    lines=['# HOLD: no workflow submission or uploads authorized.','version: v4','files:','  storage-plan.json: |']
    lines+=['    '+x for x in encoded.splitlines()]+['  stage_shared.py: |']
    lines+=['    '+x if x else '' for x in worker.splitlines()]
    lines+=['volumes:','  project:','    use: team15','    name: lymescope-project',
        '    # Ingress is DISABLED: it runs before jobs, so a job guard alone cannot stop it.',
        '    # After approval, enable the following block in a NEW reviewed execution copy.',
        '    # ingress:']
    for name in ('science','model'):
        lines += ['    #   - source:',f'    #       uri: fuzzball://group/lymescope/ospc-v0.2.1/{RUN}/{name}.tar',
            '    #     destination:',f'    #       uri: file://ospc-v0.2.1/{RUN}/incoming/{name}.tar',
            '    #     policy:','    #       timeout:','    #         execute: 2m']
    lines+=['jobs:','  stage-and-verify:','    image:','      uri: docker://nvcr.io/nvidia/pytorch:25.11-py3',
        '    resource:','      cpu:','        cores: 1','      memory:','        size: 1GiB',
        '      annotations:','        fuzzball.io/provisioner_definition_id: team15',
        '    policy:','      timeout:','        execute: 2m','      restart: never',
        '    env:','      - HF_HUB_OFFLINE=1','      - TRANSFORMERS_OFFLINE=1','      - PYTHONDONTWRITEBYTECODE=1',
        '    mounts:','      /project: project','    files:',
        '      /opt/lymescope/storage-plan.json: file://storage-plan.json',
        '      /opt/lymescope/stage_shared.py: file://stage_shared.py',
        '    script: |','      #!/bin/bash','      set -euo pipefail',
        '      echo "HOLD: staging is not authorized; no project writes performed" >&2',
        '      exit 78',
        '      # Unreachable preparation; remove the guard only in an approved execution copy.',
        '      python3 -B /opt/lymescope/stage_shared.py --plan /opt/lymescope/storage-plan.json '+
        f'--root /project/ospc-v0.2.1/{RUN} --execute-approved-stage']
    (HERE/'storage-stage-team15.HOLD.fz').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:plan[k] for k in ('run_id','peak_payload_plus_output_budget_bytes','peak_quota_percent','incremental_reservation_bytes')}))


if __name__=='__main__':build()
