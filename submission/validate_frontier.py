"""Validate Frontier presentation offline; retain historical validation receipts."""
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEMO=ROOT/'demo/v0.2.0'
EXPERIMENT=ROOT/'sparkprep/experiments/stretch_v0.2.0_20261115T072916Z'
OUT=ROOT/'submission/frontier-validation.json'


def git(*args):
    return subprocess.check_output(['git','--no-optional-locks',*args],cwd=ROOT,text=True).strip()


def run():
    baseline=json.loads((ROOT/'submission/frontier-baseline-tests.json').read_text(encoding='utf-8'))
    assert baseline['passed']==26 and all(x['exit_code']==0 for x in baseline['tests'])
    receipt={'schema':'lymescope.frontier_validation.v1',
        'checked_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'starting_commit':'9e46ec46b85ed2990f89e16cbf6e7aba707e0c95',
        'scientific_source_commit':'aafe818a20ea025370cf4b65145a9684e80aaaef',
        'branch':git('branch','--show-current'),
        'model_inference_runs':0,'cluster_calls':0,'model_downloads':0,
        'baseline_tests_passed_this_sprint':26,
        'baseline_receipt':'submission/frontier-baseline-tests.json',
        'browser_launch':'NOT_CONFIRMED','browser_rendering':'NOT_VERIFIED',
        'browser_screenshot':'NOT_CAPTURED','browser_error':'The browser access host is unavailable',
        'browser_route':'normal scoped Chrome request for local docs/index.html; no alternate route',
        'published_spark_tests':{'passed':16,'locally_rerun_inference':False},
        'not_run_locally':[
            {'test':'ScienceTests.test_calculated_sasa_analytical_spheres','reason':'Published source imports Unix resource, unavailable on Windows'},
            {'test':'TorchMaskTests.test_mask_single_original_only','reason':'torch absent'},
            {'test':'TorchMaskTests.test_full_vocabulary_nll_known_uniform','reason':'torch absent'}],
        'resolved_check_failures':[{'check':'presentation relative links','cause':'Old regex mistook JavaScript .src string fragments for HTML attributes','resolution':'Parse actual HTML attributes with HTMLParser; dynamic image behavior covered separately by UI fixtures'}],
        'checks':[]}
    # Write before link checks; final readback replaces this current sprint receipt.
    OUT.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    cpu_code="import unittest,sys;from test_science import ScienceTests;names=[n for n in unittest.defaultTestLoader.getTestCaseNames(ScienceTests) if n!='test_calculated_sasa_analytical_spheres'];suite=unittest.TestSuite(ScienceTests(n) for n in names);r=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(not r.wasSuccessful())"
    checks=[
        ('adapter_and_overlay',DEMO,[sys.executable,'-B','-m','unittest','-v','test_overlay','test_spark_adapter'],15),
        ('available_published_cpu_science',EXPERIMENT/'tests',[sys.executable,'-B','-c',cpu_code],13),
        ('presentation_links_and_assets',DEMO,[sys.executable,'-B','-m','unittest','-v','test_presentation'],5),
        ('frontier_claims_and_packaging',DEMO,[sys.executable,'-B','-m','unittest','-v','test_frontier'],6),
        ('venue_acceptance_offline',ROOT/'docs',[sys.executable,'-B','-m','unittest','-v','test_venue_scores'],5),
        ('source_demo_ui_fixtures',ROOT,['node','demo/v0.2.0/test_ui_handlers.cjs'],None),
        ('packaged_demo_ui_fixtures',ROOT,['node','demo/v0.2.0/test_ui_handlers.cjs','docs/index.html'],None)]
    logs=[]
    for name,cwd,command,count in checks:
        result=subprocess.run(command,cwd=cwd,capture_output=True,text=True,encoding='utf-8',errors='replace')
        receipt['checks'].append({'name':name,'exit_code':result.returncode,'expected_tests':count,'command':command})
        logs.append(f'=== {name} ===\n{result.stdout}{result.stderr}')
        print(name,'PASS' if result.returncode==0 else 'FAIL',flush=True)
        if result.returncode:print(result.stdout+result.stderr)
    plan=json.loads((ROOT/'workflows/ospc-spark-v0.2.1/trial.HOLD.json').read_text())
    manifest=json.loads((EXPERIMENT/'results/shard_manifest.json').read_text())
    assert plan['status']=='HOLD_NOT_AUTHORIZED_OR_SCHEDULER_VALIDATED'
    assert plan['batch_size']==8 and plan['event_speedup'] is None
    for task in plan['tasks']:
        seqs=[s for s in manifest['sequences'] if s['sequence_ordinal']%task['shards']==task['shard']]
        if task['trial']=='pilot':seqs=seqs[:1]
        assert sum(s['length'] for s in seqs)==task['scientific_masks']
        assert sum((s['length']+7)//8 for s in seqs)==task['scoring_forward_calls']
        assert task['external_timeout_seconds']==120 and task['warmup_examples']==24
    assert [t['physical_node'] for t in plan['tasks'] if t['trial']=='one']==['Spark30']
    assert [t['physical_node'] for t in plan['tasks'] if t['trial']=='two']==['Spark29','Spark30']
    assert hashlib.sha256((EXPERIMENT/'FILE_MANIFEST.json').read_bytes()).hexdigest()==plan['package_manifest_sha256']
    assert not git('diff','--name-only',receipt['scientific_source_commit'],'--',str(EXPERIMENT.relative_to(ROOT)))
    assert not git('diff','--name-only','8058846c05d4dccd60117dd29ef784af43570418','--','sparkprep/analysis/ospc_comparison_v0.1.0')
    assert git('rev-parse','main')=='8058846c05d4dccd60117dd29ef784af43570418'
    assert git('rev-parse','fallback/frontier-20261115T084009Z')==receipt['starting_commit']
    receipt['venue_task_specification']='PASS_OFFLINE_ONLY'
    receipt['preservation']={'imported_science_unchanged':True,'frozen_baseline_unchanged':True,'main_unchanged':True,'starting_fallback_preserved':True}
    receipt['python_tests_passed']=26+sum(x['expected_tests'] or 0 for x in receipt['checks'] if x['exit_code']==0)
    receipt['all_available_checks_passed']=all(x['exit_code']==0 for x in receipt['checks'])
    OUT.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    OUT.with_suffix('.log').write_text('\n'.join(logs).rstrip()+'\n',encoding='utf-8',newline='\n')
    return int(not receipt['all_available_checks_passed'])


if __name__=='__main__':raise SystemExit(run())
