"""Offline venue acceptance extension; reuse the published exact-task comparator.

Adds frozen identity readback and relative deviations. No model, GPU or scheduler
calls. This numerical check does not certify runtime, physical nodes or timing.
"""
import argparse
import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACKAGE=ROOT/'sparkprep/experiments/stretch_v0.2.0_20261115T072916Z'
SOURCE=PACKAGE/'src/compare_runs.py'
sys.path.insert(0,str(SOURCE.parent))
spec=importlib.util.spec_from_file_location('published_venue_comparator',SOURCE)
published=importlib.util.module_from_spec(spec)
spec.loader.exec_module(published)
ATOL=1e-4
RTOL=1e-5
IDENTITY=('accession','sequence_position','alignment_column','original_residue','sequence_sha256')


def deviations(pairs):
    absolute=[];relative=[];zero_equal=0;zero_nonzero=0
    for x,y in pairs:
        if not(math.isfinite(x) and math.isfinite(y)) or min(x,y)<0:
            raise ValueError('NLL must be finite and nonnegative')
        error=abs(x-y)
        if error>ATOL+RTOL*abs(x):raise ValueError('Predeclared numerical tolerance failed')
        absolute.append(error)
        if x:
            ratio=error/abs(x)
            if math.isfinite(ratio):relative.append(ratio)
            else:zero_nonzero+=1
        elif error:zero_nonzero+=1
        else:zero_equal+=1;relative.append(0.0)
    return {'max_absolute_deviation_nats':max(absolute,default=0.0),
        'max_relative_deviation':None if zero_nonzero else max(relative,default=0.0),
        'max_finite_relative_deviation':max(relative,default=0.0),
        'undefined_or_overflow_relative_count':zero_nonzero,
        'equal_zero_reference_count':zero_equal,
        'relative_error_policy':'abs(candidate-reference)/abs(reference); equal zero is 0; nonzero/zero or overflow is explicit null, never silently 0'}


def compare(reference,candidate,pilot=False):
    if sys.flags.optimize:raise RuntimeError('Run without -O; published assertions are required')
    a=published.load(reference);b=published.load(candidate)
    known=published.load(PACKAGE/'results/full_panel_v1/residue_nll.tsv')
    expected={k for k,v in known.items() if not pilot or v['accession']=='Q07337'}
    if set(a)!=expected or set(b)!=expected:raise ValueError('Exact full-panel/pilot task coverage failed')
    for label,rows in [('reference',a),('candidate',b)]:
        for task,row in rows.items():
            if any(row[k]!=known[task][k] for k in IDENTITY):
                raise ValueError(f'{label} differs from frozen identity at {task}')
    result=published.compare(reference,candidate,reference_subset=pilot)
    result.update(deviations((float(a[k]['nll_nats']),float(b[k]['nll_nats'])) for k in sorted(a)))
    result.update(schema='lymescope.venue_numeric_acceptance.v1',
        status='PASS_NUMERICAL_AND_TASK_IDENTITY_ONLY',
        source_commit='aafe818a20ea025370cf4b65145a9684e80aaaef',
        published_comparator_sha256=published.sha(SOURCE),
        expected_identity_source_sha256=published.sha(PACKAGE/'results/full_panel_v1/residue_nll.tsv'),
        atol=ATOL,rtol=RTOL,pilot=pilot,
        runtime_and_model_identity='REQUIRES_SEPARATE_RECEIPTS',
        physical_node_and_timing_validation='REQUIRES_SEPARATE_RECEIPTS',
        event_speedup=None)
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',required=True,type=Path)
    parser.add_argument('--candidate',required=True,type=Path)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    output=args.output.resolve()
    for forbidden in (PACKAGE,ROOT/'sparkprep/analysis/ospc_comparison_v0.1.0'):
        if output.is_relative_to(forbidden):parser.error('Output must be outside immutable scientific evidence')
    result=compare(args.reference,args.candidate,args.pilot)
    # Exclusive creation prevents replacing any prior receipt.
    with output.open('x',encoding='utf-8',newline='\n') as handle:
        json.dump(result,handle,indent=2,allow_nan=False);handle.write('\n')
    print(json.dumps(result,indent=2,allow_nan=False))


if __name__=='__main__':main()
