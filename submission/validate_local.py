"""Run local offline checks with existing interpreters; never installs or executes models."""
import ast
import datetime
import json
import subprocess
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PYTHON='C:/Python314/python.exe'
ANACONDA='C:/Users/franc/anaconda3/python.exe'
CODE=ROOT/'sparkprep/analysis/ospc_masked_v0.2.0'
DEMO=ROOT/'demo/v0.2.0'
CHECKS=[
 ('existing_importer',ROOT,[PYTHON,'-B','-m','unittest','discover','-s','tests','-v'],8),
 ('existing_baseline',ROOT/'sparkprep/analysis/ospc_comparison_v0.1.0',[PYTHON,'-B','-m','unittest','-v','test_baseline'],7),
 ('existing_frozen_results',ROOT/'sparkprep/analysis/ospc_comparison_v0.1.0/results_v0.1.0/source',[PYTHON,'-B','-m','unittest','discover','-v'],11),
 ('masked_offline',CODE,[PYTHON,'-B','-m','unittest','-v','test_offline'],23),
 ('overlay_data',DEMO,[PYTHON,'-B','-m','unittest','-v','test_overlay'],7),
 ('presentation_media',DEMO,[ANACONDA,'-B','-m','unittest','-v','test_presentation'],5),
 ('overlay_ui_fixtures',DEMO,['node','test_ui_handlers.cjs'],None)]


def run():
    receipt={'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':[],
             'real_model_pilot':'NOT_RUN','scientific_benchmark':'NOT_RUN','browser_rendering':'NOT_VERIFIED',
             'browser_error':'The browser access host is unavailable','gpu_runs':0,'cluster_calls':0,'model_downloads':0}
    # Create before relative-link tests; replaced with actual final results below.
    target=ROOT/'submission/validation.json';target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    logs=[]
    for name,cwd,command,count in CHECKS:
        result=subprocess.run(command,cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace')
        logs.append(f'=== {name} ===\n{result.stdout}{result.stderr}')
        receipt['checks'].append({'name':name,'command':command,'cwd':str(cwd.relative_to(ROOT)),
                                  'exit_code':result.returncode,'expected_tests':count,'kind':'offline_only'})
        print(name,'PASS' if result.returncode==0 else 'FAIL',flush=True)
        if result.returncode:print(result.stdout+result.stderr)
    for path in [*CODE.glob('*.py'),*DEMO.glob('*.py'),Path(__file__)]:ast.parse(path.read_text(encoding='utf-8'))
    receipt['python_syntax']='PASS'
    plan=json.loads((CODE/'plans/workload.json').read_text())
    receipt.update(plan_sha256=plan['plan_sha256'],source_sha256=plan['source_sha256'])
    target.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    (ROOT/'submission/validation.log').write_text('\n'.join(logs),encoding='utf-8')
    sys.exit(int(any(x['exit_code'] for x in receipt['checks'])))


if __name__=='__main__':run()
