"""Focused saved-evidence checks; never invokes inference or edits imported science."""
import datetime
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / 'demo/v0.2.0'
EXPERIMENT = ROOT / 'sparkprep/experiments/stretch_v0.2.0_20261115T072916Z'
OUT = ROOT / 'submission/spark-integration-validation.json'


def run():
    receipt = {'checked_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'source_commit': 'aafe818a20ea025370cf4b65145a9684e80aaaef',
               'local_model_inference_runs': 0, 'cluster_calls': 0, 'model_downloads': 0,
               'browser_launch': 'NOT_CONFIRMED', 'browser_rendering': 'NOT_VERIFIED',
               'browser_error': 'The browser access host is unavailable',
               'published_spark_tests': {'passed': 16, 'locally_rerun_inference': False},
               'unavailable_tests': [
                   {'test': 'ScienceTests.test_calculated_sasa_analytical_spheres', 'status': 'NOT_RUN',
                    'prior_attempt': 'ModuleNotFoundError: No module named resource',
                    'reason': 'Published Linux source imports Unix resource; unavailable on Windows'},
                   {'test': 'TorchMaskTests.test_mask_single_original_only', 'status': 'NOT_RUN', 'reason': 'torch absent'},
                   {'test': 'TorchMaskTests.test_full_vocabulary_nll_known_uniform', 'status': 'NOT_RUN', 'reason': 'torch absent'}],
               'checks': []}
    OUT.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
    cpu_code = "import unittest,sys;from test_science import ScienceTests;names=[n for n in unittest.defaultTestLoader.getTestCaseNames(ScienceTests) if n!='test_calculated_sasa_analytical_spheres'];suite=unittest.TestSuite(ScienceTests(n) for n in names);r=unittest.TextTestRunner(verbosity=2).run(suite);sys.exit(not r.wasSuccessful())"
    checks = [
        ('adapter_and_overlay', DEMO, ['C:/Python314/python.exe', '-B', '-m', 'unittest', '-v', 'test_overlay', 'test_spark_adapter'], 15),
        ('published_available_cpu_science', EXPERIMENT/'tests', [sys.executable, '-B', '-c', cpu_code], 13),
        ('presentation_and_links', DEMO, [sys.executable, '-B', '-m', 'unittest', '-v', 'test_presentation'], 5),
        ('all_column_ui_fixtures', DEMO, ['node', 'test_ui_handlers.cjs'], None)]
    logs = []
    for name, cwd, command, count in checks:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        receipt['checks'].append({'name': name, 'exit_code': result.returncode, 'expected_tests': count, 'command': command})
        logs.append(f'=== {name} ===\n{result.stdout}{result.stderr}')
        print(name, 'PASS' if result.returncode == 0 else 'FAIL', flush=True)
        if result.returncode:
            print(result.stdout + result.stderr)
    plan = json.loads((ROOT/'workflows/ospc-spark-v0.2.1/trial.HOLD.json').read_text())
    manifest = json.loads((EXPERIMENT/'results/shard_manifest.json').read_text())
    assert plan['status'] == 'HOLD_NOT_AUTHORIZED_OR_SCHEDULER_VALIDATED'
    assert plan['batch_size'] == 8 and plan['event_speedup'] is None
    for task in plan['tasks']:
        sequences = [s for s in manifest['sequences'] if s['sequence_ordinal'] % task['shards'] == task['shard']]
        if task['trial'] == 'pilot':
            sequences = sequences[:1]
        assert sum(s['length'] for s in sequences) == task['scientific_masks']
        assert sum((s['length']+7)//8 for s in sequences) == task['scoring_forward_calls']
        assert task['external_timeout_seconds'] == 120 and task['warmup_examples'] == 24
    assert [t['physical_node'] for t in plan['tasks'] if t['trial'] == 'one'] == ['Spark30']
    assert [t['physical_node'] for t in plan['tasks'] if t['trial'] == 'two'] == ['Spark29', 'Spark30']
    assert hashlib.sha256((EXPERIMENT/'FILE_MANIFEST.json').read_bytes()).hexdigest() == plan['package_manifest_sha256']
    receipt['venue_task_specification'] = 'PASS_OFFLINE_ONLY'
    def git(*args):
        return subprocess.check_output(['git', '--no-optional-locks', *args], cwd=ROOT, text=True).strip()
    assert not git('diff', '--name-only', 'aafe818a20ea025370cf4b65145a9684e80aaaef', '--', str(EXPERIMENT.relative_to(ROOT)))
    assert not git('diff', '--name-only', '8058846c05d4dccd60117dd29ef784af43570418', '--', 'sparkprep/analysis/ospc_comparison_v0.1.0')
    assert git('rev-parse', 'main') == '8058846c05d4dccd60117dd29ef784af43570418'
    receipt['preservation'] = {'imported_science_unchanged': True, 'frozen_baseline_unchanged': True, 'main_unchanged': True}
    receipt['all_available_checks_passed'] = all(c['exit_code'] == 0 for c in receipt['checks'])
    OUT.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
    OUT.with_suffix('.log').write_text('\n'.join(logs).rstrip()+'\n', encoding='utf-8', newline='\n')
    return int(not receipt['all_available_checks_passed'])


if __name__ == '__main__':
    raise SystemExit(run())
