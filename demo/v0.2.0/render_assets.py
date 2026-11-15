"""Original CPU-only presentation renders from frozen coordinates/alignment.

Requires existing Pillow and NumPy. No model, downloads, or scientific output writes.
Camera motion is illustrative; it is not a molecular dynamics trajectory.
"""
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from build_overlay import HERE, FROZEN, _cif, assembly_one, observed_ca, load_panel, build_context

OUT = HERE / 'assets'
W, H, N = 960, 640, 60
BG = '#071b26'
INK = '#edf6f5'
MUTED = '#a8c2ca'
TEAL = '#4ed9c1'
BLUE = '#6cafff'
ORANGE = '#ffc16b'
PANEL = '#102c3a'
FONT = Path('C:/Windows/Fonts')


class SmoothDraw:
    """Draw at 2x resolution, then downsample for readable original assets."""
    def __init__(self, image): self.draw = ImageDraw.Draw(image)
    def _xy(self, value):
        return tuple(self._xy(v) if isinstance(v, (tuple, list, np.ndarray)) else float(2*v) for v in value)
    def text(self, xy, value, font, fill):
        self.draw.text(self._xy(xy), value, font=font.font_variant(size=font.size*2), fill=fill)
    def line(self, xy, fill, width=1): self.draw.line(self._xy(xy), fill=fill, width=width*2)
    def rectangle(self, xy, fill): self.draw.rectangle(self._xy(xy), fill=fill)
    def rounded_rectangle(self, xy, radius, fill, outline=None, width=1):
        self.draw.rounded_rectangle(self._xy(xy), radius=radius*2, fill=fill, outline=outline, width=width*2)
    def ellipse(self, xy, fill=None, outline=None, width=1):
        self.draw.ellipse(self._xy(xy), fill=fill, outline=outline, width=width*2)


def font(size, bold=False):
    return ImageFont.truetype(str(FONT / ('segoeuib.ttf' if bold else 'segoeui.ttf')), size)


def text(d, xy, value, size=26, fill=INK, bold=False):
    d.text(xy, value, font=font(size, bold), fill=fill)


def frame(number, title, subtitle):
    im = Image.new('RGB', (W*2, H*2), BG)
    d = SmoothDraw(im)
    text(d, (38, 24), 'LYMESCOPE   /   '+number, 19, TEAL, True)
    text(d, (38, 62), title, 42, bold=True)
    text(d, (38, 120), subtitle, 25, MUTED)
    d.line((38, 575, 922, 575), fill='#29434f', width=1)
    return im, d


def footer(d, line):
    text(d, (38, 592), line, 22, MUTED)


def shade(color, depth):
    rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    return tuple(round(v * (.6 + .4 * depth)) for v in rgb)


def project(points, t, center=(480, 365), size=340):
    # Fixed camera scale, rigid rotation only. No deformation of deposited data.
    a = t * 2 * math.pi
    rx = np.array([[1, 0, 0], [0, .94, -.342], [0, .342, .94]])
    ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
    pts = (points - points.mean(axis=0)) @ (ry @ rx).T
    radius = np.linalg.norm(points - points.mean(axis=0), axis=1).max()
    scale = size / (2 * radius)
    return np.column_stack((center[0]+pts[:, 0]*scale, center[1]-pts[:, 1]*scale, pts[:, 2]))


def trace(d, points, groups, colors, labels, highlights=None):
    zmin, zmax = points[:, 2].min(), points[:, 2].max()
    edges = []
    for group, color in zip(groups, colors):
        for a, b in zip(group, group[1:]):
            if labels[b] - labels[a] == 1:
                edges.append((float((points[a, 2]+points[b, 2])/2), a, b, color))
    for z, a, b, color in sorted(edges):
        xy = [tuple(points[a, :2]), tuple(points[b, :2])]
        d.line(xy, fill=shade(color, (z-zmin)/(zmax-zmin or 1)), width=7)
    for k in sorted(highlights or [], key=lambda k: points[k, 2]):
        x, y = points[k, :2]
        d.ellipse((x-4, y-4, x+4, y+4), fill=ORANGE)


def save(name, frames, evidence, caption, details, duration=180):
    OUT.mkdir(parents=True, exist_ok=True)
    frames = [f.resize((W, H), Image.Resampling.LANCZOS) for f in frames]
    frames[0].save(OUT / (name+'.png'), optimize=True)
    # One shared palette prevents frame-to-frame color flicker.
    palette = frames[0].quantize(colors=128)
    indexed = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    target = OUT / (name+'.gif')
    indexed[0].save(target, save_all=True, append_images=indexed[1:], duration=duration,
                    loop=0, optimize=True, disposal=1)
    with Image.open(target) as decoded:
        count = decoded.n_frames
        for i in range(count): decoded.seek(i); decoded.convert('RGB').load()
        assert decoded.size == (W, H) and decoded.info.get('loop') == 0
    return {'path':target.name, 'static_preview':name+'.png', 'width':W, 'height':H,
            'bytes':target.stat().st_size, 'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
            'decoded_frames':count, 'duration_ms':duration*N, 'loop':0,
            'evidence_kind':evidence, 'caption':caption, 'details':details,
            'verification':'All GIF frames decoded; static previews inspected separately; browser playback not yet verified'}


def render():
    data = build_context()
    seq, alignment = load_panel()
    cif = _cif.parse_cif(FROZEN / 'inputs/reference_structures/1GGQ.cif')
    assembly = assembly_one(cif)  # Validate before depicting the biological A/B dimer.
    atoms = {c: observed_ca(cif, c) for c in ('A', 'B')}
    ids = {c:sorted(atoms[c]) for c in atoms}
    xyz = {c:np.array([[float(atoms[c][i][k]) for k in ('Cartn_x','Cartn_y','Cartn_z')] for i in ids[c]]) for c in atoms}
    primary = [r for r in data['references']['1GGQ']['mapping'] if r['xyz'] is not None]
    assert len(primary) == len(xyz['A']) == 162
    assert np.allclose(xyz['A'], [r['xyz'] for r in primary], atol=0, rtol=0)
    ca_dist = np.linalg.norm(xyz['A'][:, None, :] - xyz['B'][None, :, :], axis=2)
    contact_a = np.where(ca_dist.min(axis=1) <= 8)[0].tolist()
    contact_b = np.where(ca_dist.min(axis=0) <= 8)[0].tolist()
    assert contact_a == [i for i, r in enumerate(primary) if r['CA_contact_proxy_within_8A']]
    full = next(c for c in data['columns'] if c['coverage'] == c['modal_fraction'] == 1)
    mapping_row = next(r for r in primary if r['alignment_column'] == 68)
    assert mapping_row['panel_sequence_position'] == 67 and mapping_row['auth_residue_number'] == '67'
    output = []
    frames = []
    for i in range(N):
        im, d = frame('01 / EXPERIMENT', 'OspC, seen through experiment', '1GGQ chain A • X-ray coordinates • 162 observed Cα positions')
        p = project(xyz['A'], i/N, size=380)
        trace(d, p, [list(range(len(p)))], [TEAL], ids['A'])
        text(d, (45, 200), 'Observed', 27, TEAL, True)
        text(d, (45, 239), '39–200', 35, bold=True)
        text(d, (690, 420), 'Unobserved', 25, ORANGE)
        text(d, (690, 456), '≠ invented', 27, ORANGE)
        footer(d, 'Rigid camera rotation, not folding or dynamics. Cα trace, not a molecular surface.')
        frames.append(im)
    output.append(save('ospc-rotation', frames, 'experimental_coordinates', 'A. Observed OspC chain A rotates without changing its deposited coordinates.', {'pdb':'1GGQ','chain':'A','observed_CA':162}))
    frames = []
    for i in range(N):
        im, d = frame('02 / ALIGNMENT', 'Thirty sequences. Shared positions.', 'Actual fixed alignment → observed agreement and coverage')
        blend = (1-math.cos(2*math.pi*i/N))/2
        text(d, (40, 171), '30 selected natural sequences', 25, TEAL)
        x0, y0, cw, rh = 45, 223, 4, 7
        for row, aligned in enumerate(alignment.values()):
            for col, aa in enumerate(aligned):
                c = data['columns'][col]
                color = '#16303c' if aa == '-' else (TEAL if aa in c['tied_modes'] else ORANGE)
                # Collapse only presentation tiles; scientific positions never move or renumber.
                y = y0+row*rh*(1-blend)+blend*45
                d.rectangle((x0+col*cw,y,x0+col*cw+2,y+max(2,rh*(1-blend)-1)),fill=color)
        text(d, (45, 454), '218 fixed alignment columns', 26, INK, True)
        for c in data['columns']:
            x = x0+(c['alignment_column']-1)*cw
            d.line((x, 520, x, 520-34*c['modal_fraction']),fill=ORANGE,width=3)
            d.line((x, 563, x, 563-30*c['coverage']),fill=TEAL,width=3)
        text(d,(620,454),'Agreement / coverage',25,MUTED)
        footer(d,'Teal tiles: observed mode. Amber: other residues. Dark: gaps. No realignment.')
        frames.append(im)
    output.append(save('alignment-map',frames,'saved_alignment_statistics','B. The frozen 30 × 218 alignment collapses visually into its saved column summaries.',{'sequence_count':30,'alignment_columns':218,'full_coverage_columns':202}))
    frames=[]
    for i in range(N):
        im,d=frame('03 / COVERAGE','Two perfect percentages. Different evidence.','Modal fraction = agreement among residues actually observed')
        for x,col,color in [(40,full,TEAL),(500,data['columns'][153],ORANGE)]:
            d.rounded_rectangle((x,180,x+420,555),radius=18,fill=PANEL)
            text(d,(x+24,199),'Column '+str(col['alignment_column']),26,color,True)
            text(d,(x+24,235),'100%',76,bold=True)
            text(d,(x+24,337),str(col['contributing_sequences'])+'/30 observations',32,color,True)
            pulse=(1-math.cos(2*math.pi*i/N))/2
            for k in range(30):
                xx=x+30+(k%10)*38; yy=409+(k//10)*38
                fill=color if k<col['contributing_sequences'] else '#29434f'
                d.ellipse((xx,yy,xx+22,yy+22),fill=fill)
            d.rounded_rectangle((x+24,528,x+24+round(370*col['coverage']),538),radius=3,fill=color)
            d.line((x+24,518,x+24+370*pulse,518),fill=MUTED,width=2)
        footer(d,'Col 154: N in 1 sequence, 29 gaps; no 1GGQ coordinate. Coverage is visible.')
        frames.append(im)
    output.append(save('coverage-evidence',frames,'saved_alignment_statistics','C. Column 1 and column 154 both have 100% observed agreement; support is 30/30 versus 1/30.',{'full_column':1,'sparse_column':154,'sparse_mode':'N','sparse_gaps':29}))
    frames=[]
    both=np.concatenate((xyz['A'],xyz['B'])); na=len(xyz['A'])
    for i in range(N):
        im,d=frame('04 / ASSEMBLY','One deposited biological dimer','1GGQ assembly 1 • chains A/B • identity operator validated')
        p=project(both,i/N,size=375)
        trace(d,p,[list(range(na)),list(range(na,len(both)))],[TEAL,BLUE],ids['A']+ids['B'],contact_a+[na+k for k in contact_b])
        text(d,(40,190),'Chain A',26,TEAL,True);text(d,(40,230),'Chain B',26,BLUE,True)
        text(d,(650,190),'Amber regions',26,ORANGE,True)
        text(d,(650,230),'nearest Cα ≤8 Å',25,ORANGE)
        text(d,(650,475),f'A: {len(contact_a)} / {na}',25,TEAL)
        text(d,(650,511),f'B: {len(contact_b)} / {len(xyz["B"])}',25,BLUE)
        footer(d,'Interchain proximity proxy only. Not measured solvent or antibody accessibility.')
        frames.append(im)
    output.append(save('ospc-dimer',frames,'experimental_assembly_plus_geometric_proxy','D. Validated deposited A/B assembly; amber marks a declared interchain Cα-distance proxy.',{'assembly':assembly['selected_assembly'],'chain_A_proxy_count':len(contact_a),'chain_B_proxy_count':len(contact_b),'threshold_A':8}))
    frames=[]
    selected=next(i for i,r in enumerate(primary) if r['alignment_column']==68)
    for i in range(N):
        im,d=frame('05 / CORRESPONDENCE','One column. One explicit correspondence.','Alignment column 68 → Q07337 native 67 → 1GGQ A author Ser67')
        p=project(xyz['A'],.08+.04*math.sin(2*math.pi*i/N),center=(660,366),size=350)
        trace(d,p,[list(range(len(p)))],[TEAL],ids['A'])
        x,y=p[selected,:2];radius=12+3*math.sin(2*math.pi*i/N)
        d.ellipse((x-radius,y-radius,x+radius,y+radius),outline=ORANGE,width=3)
        d.line((325,335,x-14,y),fill=ORANGE,width=2)
        d.rounded_rectangle((40,205,325,503),radius=14,fill=PANEL)
        text(d,(60,227),'COLUMN 68',27,ORANGE,True)
        text(d,(60,279),'30/30',58,bold=True)
        text(d,(60,350),'observed residues',24,MUTED)
        text(d,(60,410),f'{100*mapping_row["modal_fraction"]:.1f}% agree',31,TEAL,True)
        text(d,(60,459),'Ser67 has coordinates',22,MUTED)
        footer(d,'Mapping uses the fixed alignment and saved residue table. No coordinate is inferred.')
        frames.append(im)
    output.append(save('residue-mapping',frames,'saved_explicit_mapping','E. An explicit saved mapping connects alignment column 68 to observed 1GGQ A Ser67.',{'alignment_column':68,'native_position':67,'author_residue':'67','chain':'A','residue':'S'}))
    frames=[]
    for i in range(N):
        im,d=frame('06 / PREPARED WORKFLOW','Same biology. Independent GPU tasks.','Conceptual task distribution • no benchmark or speedup measured')
        text(d,(45,176),'6,305 masks • 30 sequences • batch 16',30,INK,True)
        for y,label,counts in [(254,'One node',[415]),(400,'Two nodes',[208,207])]:
            text(d,(45,y+20),label,29,TEAL,True)
            for j,count in enumerate(counts):
                left=280+j*310
                d.rounded_rectangle((left,y,left+270,y+100),radius=14,fill=PANEL,outline=BLUE,width=2)
                text(d,(left+19,y+12),f'{count} forwards',28,bold=True)
                text(d,(left+19,y+54),'sequence shards',23,MUTED)
                for k in range(7):
                    xx=left+20+((i/N*230+k*32)%230)
                    d.ellipse((xx,y+85,xx+5,y+90),fill=TEAL)
        footer(d,'Warm-up / pilot counted separately. Physical nodes and float equivalence required.')
        frames.append(im)
    output.append(save('task-shards',frames,'conceptual_unexecuted_workflow','F. Same 6,305 masked examples; per-sequence batching gives 415 forwards, split 208/207.',{'model':'facebook/esm2_t6_8M_UR50D','execution':'NOT RUN','masked_examples':6305,'scoring_calls':415,'shard_calls':[208,207]}))
    manifest={'version':'0.2.0','origin':'Original project-generated presentation assets; no copied video',
              'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'source_hashes':data['provenance'],'camera_motion':'Rigid illustration, not dynamics',
              'browser_playback':'NOT VERIFIED','assets':output}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
    for asset in output: print(asset['path'],asset['width'],asset['height'],asset['bytes'],asset['decoded_frames'])


if __name__=='__main__':render()
