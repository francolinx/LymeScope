"""Reproduce in a new directory using archived sources only. No network, inference or package installs."""
import argparse, shutil, os, sys, time, subprocess, csv
from common import *

def compare_json(a, b, path=''):
    if isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), path
        for key in a:
            compare_json(a[key], b[key], path + '/' + key)
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), path
        for i, (x, y) in enumerate(zip(a, b)):
            compare_json(x, y, path + '/' + str(i))
    elif isinstance(a, float):
        import math
        assert isinstance(b, (float, int)) and math.isclose(a, b, rel_tol=1e-08, abs_tol=1e-08), (path, a, b)
    else:
        assert a == b, (path, a, b)

def run(destination):
    target = pathlib.Path(destination)
    assert not target.exists(), 'Destination must be new; original artifacts never overwritten'
    target.mkdir(parents=True)
    start = time.perf_counter()
    shutil.copytree(ROOT / 'inputs', target / 'inputs')
    shutil.copytree(ROOT / 'src', target / 'src', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copytree(ROOT / 'tests', target / 'tests', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copyfile(ROOT / 'EXPERIMENT_QUESTION.md', target / 'EXPERIMENT_QUESTION.md')
    (target / 'provenance').mkdir()
    (target / 'results').mkdir()
    for name in ['source_receipts.json', 'predeclaration.json', 'reference_inventory.json', 'reused_inputs.json', 'crystal_copy_audit_plan.json', 'ANALYSIS_BEFORE_SOLVER_RECOVERY.json', 'numerical_solver_note.json']:
        shutil.copyfile(ROOT / 'provenance' / name, target / 'provenance' / name)
    env = os.environ.copy()
    env.update(OMP_NUM_THREADS='4', OPENBLAS_NUM_THREADS='4', PYTHONDONTWRITEBYTECODE='1', HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1')
    stages = []
    for script in ['map_complex.py', 'build_site_table.py', 'exploratory_analysis.py', 'map_literature_region.py', 'audit_geometry.py', 'audit_statistics.py', 'audit_missingness.py', 'audit_crystal_copies.py', 'export_evidence.py', 'plot_frontier.py']:
        tick = time.perf_counter()
        with (target / 'provenance' / (script + '.log')).open('w') as log:
            subprocess.run([sys.executable, str(target / 'src' / script)], check=True, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=60)
        stages.append({'script': script, 'elapsed_s': time.perf_counter() - tick})
    with (target / 'provenance/tests.log').open('w') as log:
        subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(target / 'tests'), '-v'], check=True, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=60)
    exact_files = ['EXPERIMENTAL_MAPPING.tsv', 'results/9BIF_RESIDUE_MAPPING.tsv', 'results/7UIJ_RESIDUE_MAPPING.tsv', 'results/9BIF_FAB_CONTACT_PAIRS_5A.tsv', 'results/7UIJ_FAB_CONTACT_PAIRS_5A.tsv', 'results/ELIGIBILITY_GATES.json', 'results/8C1_LITERATURE_REGION.tsv', 'results/9BIF_CRYSTAL_COPY_CONTACTS.tsv']
    for rel in exact_files:
        assert (ROOT / rel).read_bytes() == (target / rel).read_bytes(), rel
    numeric_files = ['ANALYSIS_RESULTS.json', 'results/INDEPENDENT_GEOMETRY_AUDIT.json', 'results/INDEPENDENT_STATISTICS_AUDIT.json', 'results/MISSINGNESS_AUDIT.json', 'results/9BIF_CRYSTAL_COPY_AUDIT.json', 'results/FRONTIER_EVIDENCE.json']
    for rel in numeric_files:
        compare_json(json.loads((ROOT / rel).read_text()), json.loads((target / rel).read_text()), rel)
    original = list(csv.DictReader((ROOT / 'results/BLOCKED_OOF_PREDICTIONS.tsv').read_text().splitlines(), delimiter='\t'))
    repeated = list(csv.DictReader((target / 'results/BLOCKED_OOF_PREDICTIONS.tsv').read_text().splitlines(), delimiter='\t'))
    assert len(original) == len(repeated)
    max_error = 0
    for a, b in zip(original, repeated):
        for key in a:
            if key == 'oof_probability':
                max_error = max(max_error, abs(float(a[key]) - float(b[key])))
            else:
                assert a[key] == b[key], key
    assert max_error < 1e-08
    receipt = {'status': 'PASS', 'destination': str(target), 'network_retrieval': 'NOT_RUN', 'new_ESM_inference': 'NOT_RUN', 'input_source': 'Archived exact-byte local files only', 'stages': stages, 'exact_artifact_comparisons': exact_files, 'numeric_json_comparisons_tolerance_1e_8': numeric_files, 'OOF_predictions_checked': len(original), 'OOF_probability_max_abs_difference': max_error, 'tests_passed': int(__import__('re').search('Ran (\\d+) tests', (target / 'provenance/tests.log').read_text())[1]), 'elapsed_total_s': time.perf_counter() - start, 'figure_note': 'Regenerated from actual data. Renderer metadata/font outputs may differ; numerical results rather than image byte identity are the reproducibility endpoint.'}
    write_json(target / 'REPRODUCTION_RECEIPT.json', receipt)
    print(json.dumps(receipt, indent=2))
if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--destination', required=True)
    a = p.parse_args()
    run(a.destination)
