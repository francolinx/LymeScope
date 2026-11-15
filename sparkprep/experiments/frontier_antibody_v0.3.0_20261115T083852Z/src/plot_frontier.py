"""Original scientific figure from actual deposited coordinates and predeclared comparison results."""
import csv, collections
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from common import *

def plot():
    evidence = json.loads((ROOT / 'results/FRONTIER_EVIDENCE.json').read_text())
    result = json.loads((ROOT / 'ANALYSIS_RESULTS.json').read_text())
    points = evidence['experimental_CA_coordinates']['9BIF']
    sites = evidence['sites']
    coords = collections.defaultdict(list)
    for p in points:
        coords[p['instance']].append(p)
    mapping = list(csv.DictReader((ROOT / 'results/9BIF_RESIDUE_MAPPING.tsv').read_text().splitlines(), delimiter='\t'))
    contact = {(r['OspC_instance'], int(r['label_seq_id'])) for r in mapping if r['observed_contact_4_5_A'] == 'True'}
    fig = plt.figure(figsize=(15, 8.5), layout='constrained')
    gs = fig.add_gridspec(2, 2, width_ratios=[1.2, 1])
    ax = fig.add_subplot(gs[:, 0], projection='3d')
    palette = {'C@1': '#0f766e', 'D@1': '#0891b2'}
    for instance, ps in coords.items():
        ps.sort(key=lambda p: p['label_seq_id'])
        segments = [[a['xyz_A'], b['xyz_A']] for a, b in zip(ps, ps[1:]) if b['label_seq_id'] == a['label_seq_id'] + 1]
        is_antigen = ps[0]['role'] == 'OspC'
        color = palette.get(instance, '#a8a29e')
        collection = Line3DCollection(segments, colors=color, linewidths=2.6 if is_antigen else 1.0, alpha=1 if is_antigen else 0.6)
        ax.add_collection3d(collection)
        selected = [p['xyz_A'] for p in ps if (instance, p['label_seq_id']) in contact]
        if selected:
            a = np.array(selected)
            ax.scatter(a[:, 0], a[:, 1], a[:, 2], s=13, c='#c026d3', depthshade=False)
        if is_antigen:
            mid = ps[len(ps) // 2]
            ax.text(*mid['xyz_A'], 'OspC ' + mid['auth_chain'], fontsize=9)
    allxyz = np.array([p['xyz_A'] for p in points])
    lo = allxyz.min(0)
    hi = allxyz.max(0)
    for j, name in enumerate(['set_xlim', 'set_ylim', 'set_zlim']):
        getattr(ax, name)(lo[j] - 3, hi[j] + 3)
    ax.set_box_aspect(hi - lo)
    ax.view_init(elev=18, azim=-65)
    ax.set_axis_off()
    ax.set_title('9BIF: existing B11 Fab–OspC complex\nTeal: antigen · Gray: Fab · Magenta: atom-contact sites', fontsize=11)
    bx = fig.add_subplot(gs[0, 1])
    labels = []
    for index, (code, label) in enumerate([('9BIF', 'B11 atom contacts'), ('7UIJ', 'B5 atom contacts')]):
        rs = [r for r in sites if r['pdb_id'] == code]
        complete = [r['alignment_column'] for r in rs if r['strict_contact_union_4_5_A'] is not None]
        positive = [r['alignment_column'] for r in rs if r['observed_contact_union_4_5_A'] is True]
        bx.scatter(complete, [index] * len(complete), marker='s', s=15, c='#d1d5db')
        bx.scatter(positive, [index] * len(positive), marker='s', s=20, c='#c026d3')
        labels.append(label)
    literature = [int(r['alignment_column']) for r in evidence['literature_region_8C1']]
    bx.scatter(literature, [2] * len(literature), marker='|', s=150, c='#2563eb')
    labels.append('8C1 HDX region only')
    bx.set_yticks(range(3), labels)
    bx.set_ylim(2.7, -0.7)
    bx.set_xlim(0.5, 218.5)
    bx.set_xlabel('Frozen alignment column (not PDB author numbering)')
    bx.set_title('Experimental evidence types remain separate', fontsize=11)
    bx.grid(axis='x', alpha=0.15)
    cx = fig.add_subplot(gs[1, 1])
    primary = result['primary']
    names = ['B2: agreement + AA + geometry', 'B3: B2 + signed discordance', 'B4: B2 + mean NLL']
    values = [primary['models'][m]['oof_metrics']['brier'] for m in ['B2', 'B3', 'B4']]
    colors = ['#475569', '#b91c1c', '#0f766e']
    for i, (v, color) in enumerate(zip(values, colors)):
        cx.scatter([v], [i], s=70, c=color, zorder=3)
        cx.text(v + 0.00025, i, f'{v:.5f}', va='center', fontsize=9)
    cx.axvline(values[0], ls='--', c='#94a3b8')
    cx.set_yticks(range(3), names, fontsize=8)
    cx.invert_yaxis()
    cx.set_xlabel('Blocked out-of-fold Brier error (lower is better)')
    cx.set_xlim(min(values) - 0.0015, max(values) + 0.003)
    cx.grid(axis='x', alpha=0.15)
    cx.set_title('Predeclared result: discordance does not improve B11 diagnostic', fontsize=11)
    fig.suptitle('A real antibody footprint mapped exactly — and an incremental-signal hypothesis not supported', fontsize=14, weight='bold')
    fig.supxlabel('Primary: 152 eligible alignment sites, 31 B11 contacts, 4.5 Å cutoff. Correlated residues; one antigen/complex; exploratory, not a validated functional predictor.\nCα traces display existing experimental coordinates; contact labels derive from heavy atoms. No new inference, structure prediction or clinical claim.', fontsize=9)
    fig.savefig(ROOT / 'results/FRONTIER_EXPERIMENT.png', dpi=180)
    fig.savefig(ROOT / 'results/FRONTIER_EXPERIMENT.svg')
    plt.close(fig)
if __name__ == '__main__':
    plot()
