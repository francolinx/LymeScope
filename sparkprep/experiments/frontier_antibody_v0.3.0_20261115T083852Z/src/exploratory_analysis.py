"""Predeclared, fixed-penalty descriptive/blocked logistic diagnostics. No inference or tuning."""
import csv, collections, math
import numpy as np
from scipy.special import expit
from scipy.optimize import minimize
from scipy.stats import rankdata
from common import *
AA = 'ACDEFGHIKLMNPQRSTVWY'

def auc(y, score):
    y = np.asarray(y, dtype=int)
    score = np.asarray(score, dtype=float)
    n1 = int(y.sum())
    n0 = len(y) - n1
    if not n1 or not n0:
        return None
    ranks = rankdata(score, method='average')
    return float((ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0))

def metrics(y, p):
    y = np.asarray(y, dtype=float)
    p = np.asarray(p, dtype=float)
    assert np.isfinite(p).all()
    clipped = np.clip(p, 1e-12, 1 - 1e-12)
    return {'n': len(y), 'contacts': int(y.sum()), 'prevalence': float(y.mean()), 'brier': float(np.mean((p - y) ** 2)), 'log_loss': float(-np.mean(y * np.log(clipped) + (1 - y) * np.log1p(-clipped))), 'auroc': auc(y, p)}

def design(rows, name):
    names = []
    values = []
    continuous = []
    for r in rows:
        vals = []
        if name != 'B0':
            vals.append(float(r['modal_fraction']))
        if name in ['B2', 'B3', 'B4', 'B5']:
            vals.extend([float(r['reference_aa'] == aa) for aa in AA[1:]])
            vals.extend([math.log1p(float(r['reference_dimer_sasa_A2'])), math.log1p(float(r['reference_dimerization_sasa_loss_A2'])), float(r['reference_dimer_contact'] == 'True')])
        if name == 'B3':
            vals.append(float(r['signed_discordance']))
        if name == 'B4':
            vals.append(float(r['mean_nll_nats']))
        if name == 'B5':
            vals.append(float(r['Q07337_nll_nats']))
        values.append(vals)
    if name != 'B0':
        names = ['modal_fraction']
        continuous = [0]
    if name in ['B2', 'B3', 'B4', 'B5']:
        names.extend(['AA_' + aa for aa in AA[1:]] + ['log1p_dimer_SASA', 'log1p_dimerization_loss', 'dimer_contact'])
        continuous.extend([20, 21])
    if name in ['B3', 'B4', 'B5']:
        names.append({'B3': 'signed_discordance', 'B4': 'panel_mean_NLL', 'B5': 'Q07337_NLL'}[name])
        continuous.append(len(names) - 1)
    return (np.asarray(values, dtype=float).reshape(len(rows), len(names)), names, continuous)

def newton_recover(X, y, penalty, init):
    from scipy.optimize import OptimizeResult
    beta = init.copy()

    def value(b):
        z = X @ b
        return float(np.sum(np.logaddexp(0, z) - y * z) + 0.5 * np.sum(penalty * b * b))
    for iteration in range(100):
        p = expit(X @ beta)
        g = X.T @ (p - y) + penalty * beta
        if np.max(np.abs(g)) < 1e-08:
            return OptimizeResult(success=True, x=beta, nit=iteration, fun=value(beta), jac=g, message='Newton gradient convergence')
        H = X.T * (p * (1 - p)) @ X + np.diag(penalty)
        step = np.linalg.solve(H, g)
        old = value(beta)
        alpha = 1.0
        while value(beta - alpha * step) > old + 1e-12:
            alpha *= 0.5
            if alpha < 1e-10:
                raise ValueError('Newton fallback line search stalled')
        beta -= alpha * step
    raise ValueError('Newton fallback failed gradient convergence')

def fit_predict(trainx, trainy, testx, continuous):
    trainx = trainx.copy()
    testx = testx.copy()
    mean = np.zeros(trainx.shape[1])
    scale = np.ones(trainx.shape[1])
    for j in continuous:
        mean[j] = trainx[:, j].mean()
        std = trainx[:, j].std()
        scale[j] = std if std > 0 else 1
    trainx = (trainx - mean) / scale
    testx = (testx - mean) / scale
    X = np.column_stack([np.ones(len(trainx)), trainx])
    T = np.column_stack([np.ones(len(testx)), testx])
    penalty = np.ones(X.shape[1])
    penalty[0] = 0
    if len(set(trainy.tolist())) < 2:
        raise ValueError('Training fold lacks both endpoint classes')

    def objective(beta):
        z = X @ beta
        loss = np.sum(np.logaddexp(0, z) - trainy * z) + 0.5 * np.sum(penalty * beta * beta)
        grad = X.T @ (expit(z) - trainy) + penalty * beta
        return (loss, grad)
    init = np.zeros(X.shape[1])
    p = trainy.mean()
    init[0] = math.log(p / (1 - p))
    fit = minimize(objective, init, jac=True, method='L-BFGS-B', options={'maxiter': 2000, 'ftol': 1e-12, 'gtol': 1e-08})
    solver = 'L-BFGS-B'
    failure = None
    if not fit.success:
        failure = str(fit.message)
        fit = newton_recover(X, trainy, penalty, init)
        solver = 'Newton_fallback_same_objective'
    return (expit(T @ fit.x), {'solver_used': solver, 'initial_solver_failure': failure, 'coefficients': fit.x.tolist(), 'continuous_means': mean.tolist(), 'continuous_scales': scale.tolist(), 'iterations': fit.nit, 'objective': float(fit.fun), 'gradient_inf_norm': float(np.max(np.abs(fit.jac)))})

def analyze(code, cutoff='4_5'):
    allrows = list(csv.DictReader((ROOT / 'EXPERIMENTAL_MAPPING.tsv').read_text().splitlines(), delimiter='\t'))
    data = [r for r in allrows if r['pdb_id'] == code and r['strict_eligible'] == 'True']
    y = np.array([r[f'strict_contact_union_{cutoff}_A'] == 'True' for r in data], dtype=float)
    assert all((r[f'strict_contact_union_{cutoff}_A'] in ['True', 'False'] for r in data))
    descriptives = {}
    for key in ['modal_fraction', 'mean_nll_nats', 'signed_discordance', 'reference_dimer_sasa_A2', 'reference_dimerization_sasa_loss_A2', 'reference_dimer_contact', 'Q07337_nll_nats', 'absolute_discordance']:
        values = np.array([abs(float(r['signed_discordance'])) if key == 'absolute_discordance' else float(r[key] == 'True') if key == 'reference_dimer_contact' else float(r[key]) for r in data])
        pos = values[y == 1]
        neg = values[y == 0]
        den = math.sqrt(((len(pos) - 1) * np.var(pos, ddof=1) + (len(neg) - 1) * np.var(neg, ddof=1)) / (len(values) - 2)) if len(pos) > 1 and len(neg) > 1 else math.nan
        descriptives[key] = {'contact_mean': float(pos.mean()) if len(pos) else None, 'noncontact_mean': float(neg.mean()) if len(neg) else None, 'mean_contact_minus_noncontact': float(pos.mean() - neg.mean()) if len(pos) and len(neg) else None, 'contact_median': float(np.median(pos)) if len(pos) else None, 'noncontact_median': float(np.median(neg)) if len(neg) else None, 'pooled_standardized_mean_difference': float((pos.mean() - neg.mean()) / den) if den > 0 else None, 'auroc_raw_higher_score': auc(y, values)}
    result = {'pdb_id': code, 'cutoff_A': float(cutoff.replace('_', '.')), 'eligible_n': len(data), 'contact_n': int(y.sum()), 'noncontact_n': int(len(y) - y.sum()), 'descriptives': descriptives, 'models': {}, 'status': 'COMPLETED'}
    predrows = []
    if len(data) < 60 or min(y.sum(), len(y) - y.sum()) < 10:
        result['model_status'] = 'NOT_RUN_MINIMUM_COUNTS'
        return (result, predrows)
    for name in ['B0', 'B1', 'B2', 'B3', 'B4', 'B5']:
        x, names, continuous = design(data, name)
        oof = np.full(len(data), np.nan)
        folds = []
        positions = np.array([int(r['alignment_column']) for r in data])
        blocks = np.array([int(r['fixed_reference_block']) for r in data])
        status = 'COMPLETED'
        for b in range(8):
            test = np.flatnonzero(blocks == b)
            if not len(test):
                folds.append({'block': b, 'status': 'NO_ELIGIBLE_TEST_POSITIONS'})
                continue
            lo = positions[test].min() - 5
            hi = positions[test].max() + 5
            train = np.flatnonzero((positions < lo) | (positions > hi))
            fold = {'block': b, 'train_n': len(train), 'test_n': len(test), 'train_contacts': int(y[train].sum()), 'test_contacts': int(y[test].sum()), 'held_alignment_min': int(positions[test].min()), 'held_alignment_max': int(positions[test].max()), 'train_guard_low': int(lo), 'train_guard_high': int(hi)}
            try:
                pred, fit = fit_predict(x[train], y[train], x[test], continuous)
            except ValueError as e:
                fold.update(status='NOT_RUN', reason=str(e))
                status = 'NOT_RUN'
                folds.append(fold)
                continue
            oof[test] = pred
            fold.update(status='COMPLETED', fit=fit, metrics=metrics(y[test], pred))
            folds.append(fold)
        model = {'status': status, 'feature_names': names, 'folds': folds}
        if np.isfinite(oof).all():
            model['oof_metrics'] = metrics(y, oof)
            for i, row in enumerate(data):
                predrows.append({'pdb_id': code, 'cutoff_A': result['cutoff_A'], 'model': name, 'alignment_column': int(row['alignment_column']), 'Q07337_position': row['Q07337_position'], 'reference_aa': row['reference_aa'], 'block': int(blocks[i]), 'observed_antibody_contact': bool(y[i]), 'oof_probability': float(oof[i])})
        apparent, fit = fit_predict(x, y, x, continuous)
        model['apparent_training_metrics'] = metrics(y, apparent)
        model['full_data_fit'] = {'feature_names': ['intercept'] + names, **fit}
        result['models'][name] = model
    result['model_status'] = 'COMPLETED' if all((m['status'] == 'COMPLETED' for m in result['models'].values())) else 'PARTIAL'
    if 'oof_metrics' in result['models']['B2'] and 'oof_metrics' in result['models']['B3']:
        result['primary_delta_oof_brier_B3_minus_B2'] = result['models']['B3']['oof_metrics']['brier'] - result['models']['B2']['oof_metrics']['brier']
        result['delta_oof_logloss_B3_minus_B2'] = result['models']['B3']['oof_metrics']['log_loss'] - result['models']['B2']['oof_metrics']['log_loss']
        result['delta_oof_auroc_B3_minus_B2'] = result['models']['B3']['oof_metrics']['auroc'] - result['models']['B2']['oof_metrics']['auroc']
    return (result, predrows)

def main():
    pre = json.loads((ROOT / 'provenance/predeclaration.json').read_text())
    assert sha(ROOT / 'EXPERIMENT_QUESTION.md') == pre['question_sha256']
    out = []
    predictions = []
    for code in ['9BIF', '7UIJ']:
        for cut in ['4_5', '4_0', '5_0']:
            result, rows_ = analyze(code, cut)
            out.append(result)
            predictions.extend(rows_)
    primary = out[0]
    report = {'status': 'COMPLETED', 'predeclaration_sha256': pre['question_sha256'], 'raw_scores_reused_sha256': sha(ROOT / 'inputs/frozen_residue_nll.tsv'), 'additional_ESM_inference_forward_passes': 0, 'primary': primary, 'sensitivity_and_secondary': out[1:], 'interpretation_status': 'DESCRIPTIVE_EXPLORATORY_NOT_EXTERNAL_VALIDATION', 'primary_conclusion': {'hypothesis_support': 'NOT_SUPPORTED_BY_PREDECLARED_DIAGNOSTIC', 'primary_added_discordance_Brier_change': primary['primary_delta_oof_brier_B3_minus_B2'], 'direction': 'WORSE_WITH_DISCORDANCE', 'scope': 'Observed B11 coordinate footprint only; not proof of no biological relationship elsewhere.'}, 'endpoint': 'Any observed Fab heavy-atom contact across two complete OspC copies, unique eligible alignment sites; biological assembly1', 'limitations': ['Single antigen/reference and related, overlapping residues; no population significance or statistical independence.', 'Antibody contact at a fixed cutoff is not proof a residue is functionally necessary, antigenic across strains, or protective.', 'B11 and B5 footprints are biologically related and are not independent external validation sets.', 'D is a deterministic transform of agreement and NLL, not information beyond those components.', 'Features use panel means while antibodies bind a single experimental serotype; amino-acid/geometry controls and Q07337-specific NLL comparator address but do not remove confounding.', 'Blocked held-region performance is exploratory and penalty/splits are fixed, not optimized.', 'All negative/inconclusive outcomes retained.']}
    write_json(ROOT / 'ANALYSIS_RESULTS.json', report)
    write_tsv(ROOT / 'results/BLOCKED_OOF_PREDICTIONS.tsv', predictions)
    print(json.dumps({'primary_n': primary['eligible_n'], 'contacts': primary['contact_n'], 'descriptives': primary['descriptives'], 'OOF': {k: v.get('oof_metrics') for k, v in primary['models'].items()}, 'primary_delta_Brier': primary.get('primary_delta_oof_brier_B3_minus_B2')}, indent=2))
if __name__ == '__main__':
    main()
