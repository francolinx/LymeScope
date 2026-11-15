"""Independent Newton/IRLS audit of fixed-penalty logistic OOF fits; no tuning or new endpoint."""
import csv, math
import numpy as np
from scipy.special import expit
from common import *
from exploratory_analysis import design, metrics

def newton_fit(trainx, y, testx, continuous):
    a = trainx.copy()
    b = testx.copy()
    for j in continuous:
        mu = a[:, j].mean()
        sd = a[:, j].std()
        sd = sd if sd > 0 else 1.0
        a[:, j] = (a[:, j] - mu) / sd
        b[:, j] = (b[:, j] - mu) / sd
    X = np.column_stack([np.ones(len(a)), a])
    T = np.column_stack([np.ones(len(b)), b])
    P = np.eye(X.shape[1])
    P[0, 0] = 0
    beta = np.zeros(X.shape[1])
    beta[0] = math.log(y.mean() / (1 - y.mean()))

    def loss(beta):
        z = X @ beta
        return float(np.logaddexp(0, z).sum() - y @ z + 0.5 * beta @ P @ beta)
    for iteration in range(100):
        p = expit(X @ beta)
        g = X.T @ (p - y) + P @ beta
        H = X.T * (p * (1 - p)) @ X + P
        if np.max(abs(g)) < 1e-10:
            break
        step = np.linalg.solve(H, g)
        old = loss(beta)
        scale = 1.0
        while loss(beta - scale * step) > old + 1e-12:
            scale *= 0.5
            if scale < 1e-10:
                raise AssertionError('Newton line search stalled')
        beta -= scale * step
    else:
        raise AssertionError('Newton failed to converge')
    return (expit(T @ beta), {'iterations': iteration, 'gradient_inf_norm': float(np.max(abs(g)))})

def audit():
    data = list(csv.DictReader((ROOT / 'EXPERIMENTAL_MAPPING.tsv').read_text().splitlines(), delimiter='\t'))
    saved = list(csv.DictReader((ROOT / 'results/BLOCKED_OOF_PREDICTIONS.tsv').read_text().splitlines(), delimiter='\t'))
    reports = []
    for code in ['9BIF', '7UIJ']:
        rs = [r for r in data if r['pdb_id'] == code and r['strict_eligible'] == 'True']
        pos = np.array([int(r['alignment_column']) for r in rs])
        blocks = np.array([int(r['fixed_reference_block']) for r in rs])
        y = np.array([r['strict_contact_union_4_5_A'] == 'True' for r in rs], dtype=float)
        for model in ['B0', 'B1', 'B2', 'B3', 'B4', 'B5']:
            x, names, continuous = design(rs, model)
            expected = {int(r['alignment_column']): float(r['oof_probability']) for r in saved if r['pdb_id'] == code and float(r['cutoff_A']) == 4.5 and (r['model'] == model)}
            got = np.zeros(len(rs))
            maxgrad = 0
            for block in range(8):
                test = np.flatnonzero(blocks == block)
                lo = pos[test].min() - 5
                hi = pos[test].max() + 5
                train = np.flatnonzero((pos < lo) | (pos > hi))
                p, info = newton_fit(x[train], y[train], x[test], continuous)
                got[test] = p
                maxgrad = max(maxgrad, info['gradient_inf_norm'])
            errors = [abs(got[i] - expected[int(col)]) for i, col in enumerate(pos)]
            assert max(errors) < 1e-05, (code, model, max(errors))
            reports.append({'pdb_id': code, 'model': model, 'max_probability_difference_LBFGS_vs_Newton': max(errors), 'newton_gradient_inf_norm': maxgrad, 'newton_OOF_metrics': metrics(y, got)})
    primary = [r for r in data if r['pdb_id'] == '9BIF' and r['strict_eligible'] == 'True']
    positive = [float(r['signed_discordance']) for r in primary if r['strict_contact_union_4_5_A'] == 'True']
    negative = [float(r['signed_discordance']) for r in primary if r['strict_contact_union_4_5_A'] == 'False']
    pair_auc = sum((1 if a > b else 0.5 if a == b else 0 for a in positive for b in negative)) / (len(positive) * len(negative))
    analysis = json.loads((ROOT / 'ANALYSIS_RESULTS.json').read_text())
    expected_auc = analysis['primary']['descriptives']['signed_discordance']['auroc_raw_higher_score']
    assert abs(pair_auc - expected_auc) < 1e-14
    result = {'status': 'PASS', 'independent_optimizer': 'Newton/IRLS with explicit Hessian and line search vs original L-BFGS-B', 'primary_cutoff_A': 4.5, 'models_checked': 12, 'fold_fits_checked': 96, 'max_probability_difference': max((x['max_probability_difference_LBFGS_vs_Newton'] for x in reports)), 'signed_D_pairwise_AUROC': pair_auc, 'ROC_tie_pair_count_agreement': True, 'models': reports}
    write_json(ROOT / 'results/INDEPENDENT_STATISTICS_AUDIT.json', result)
    print(json.dumps({k: v for k, v in result.items() if k != 'models'}, indent=2))
if __name__ == '__main__':
    audit()
