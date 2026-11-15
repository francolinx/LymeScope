"""Render saved benchmark measurements only; no inference or live telemetry.

Run with Pillow installed. Pass --font-dir if Segoe UI is not in the system
font directory. Interpolated allocation widths are explicitly illustrative;
only recorded endpoint counts are printed. All time bars remain fixed.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import argparse, hashlib, json, math, os

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'demo/benchmark-comparison-v1'
W, H, SCALE = 1600, 900, 2
BG, INK, MUTED = '#edf3f2', '#173b46', '#49636e'
TEAL, AMBER, SINGLE = '#086d7c', '#e9b657', '#6c8795'
WHITE, LINE = '#ffffff', '#cededc'

parser = argparse.ArgumentParser()
parser.add_argument('--font-dir', type=Path, default=Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts')
args = parser.parse_args()
fonts = {}
def font(size, bold=False):
    key=(size,bold)
    if key not in fonts:
        path=args.font_dir/('seguisb.ttf' if bold else 'segoeui.ttf')
        if not path.exists(): raise FileNotFoundError('Supply --font-dir containing segoeui.ttf and seguisb.ttf')
        fonts[key]=ImageFont.truetype(str(path),size*SCALE)
    return fonts[key]

original=json.loads((ROOT/'submission/venue_secondnode_v1/RESULT.json').read_text(encoding='utf-8'))
exploratory=json.loads((HERE/'EXPLORATORY_RESULT.json').read_text(encoding='utf-8'))
assert original['exact_tasks']==exploratory['exact_tasks']==6305
assert original['shard_task_counts']==[3156,3149]
assert [exploratory['shards'][n]['masks'] for n in ['Spark29','Spark30']]==[1691,4614]
assert exploratory['post_hoc_exploratory'] and exploratory['checks']['merged_vs_frozen']['max_absolute_error_nats']==0
assert exploratory['checks']['merged_vs_frozen']['max_relative_error']==0
assert original['merged_vs_single']['max_absolute_error_nats']==original['max_relative_error']==0
one=original['single_coordinator_s']; equal=original['two_coordinator_s']; optimized=exploratory['coordinator_s']
reduction=100*(1-optimized/equal)
assert f'{one:.3f}'=='52.111' and f'{equal:.3f}'=='67.982' and f'{optimized:.3f}'=='51.952'
assert f'{reduction:.1f}'=='23.6'

def render(progress, final=False):
    im=Image.new('RGB',(W*SCALE,H*SCALE),BG);d=ImageDraw.Draw(im)
    def box(xy,fill,r=0,outline=None,width=1):
        b=tuple(round(v*SCALE) for v in xy)
        if r:d.rounded_rectangle(b,radius=r*SCALE,fill=fill,outline=outline,width=width*SCALE)
        else:d.rectangle(b,fill=fill,outline=outline,width=width*SCALE)
    def text(x,y,s,size=24,bold=False,color=INK,anchor='la'):
        f=font(size,bold);d.text((round(x*SCALE),round(y*SCALE)),s,font=f,fill=color,anchor=anchor)
    def line(x1,y1,x2,y2,color=LINE,width=2):d.line(tuple(round(v*SCALE) for v in [x1,y1,x2,y2]),fill=color,width=width*SCALE)
    def centered(x,y,s,size=28,bold=True,color=INK):
        text(x,y,s,size,bold,color,anchor='mm')
    def allocation(y,n29,labels):
        x=100; total_width=700; split=x+total_width*n29/6305
        box((x,y,split,y+58),TEAL)
        box((split,y,x+total_width,y+58),AMBER)
        if labels:
            centered((x+split)/2,y+29,f'{round(n29):,}',28,color=WHITE)
            centered((split+x+total_width)/2,y+29,f'{6305-round(n29):,}',28)
        else:
            # No fictitious intermediate task counts are displayed.
            centered((x+split)/2,y+29,'Spark29',23,color=WHITE)
            centered((split+x+total_width)/2,y+29,'Spark30',23)
    box((0,0,W,8),TEAL)
    text(66,31,'LYMESCOPE  /  VERIFIED EVENT BENCHMARK',21,True,TEAL)
    text(66,69,'Same 6,305 tasks. A different split.',49,True)
    text(67,131,'Recorded assignments and measured coordinator times — no live telemetry',26,color=MUTED)

    box((66,188,837,586),WHITE,14,LINE)
    text(100,208,'Work allocation',32,True)
    text(100,250,'6,305 original residue masks in each run',23,color=MUTED)
    box((101,292,118,309),TEAL,3);text(131,282,'Spark29',24,True)
    box((285,292,302,309),AMBER,3);text(315,282,'Spark30',24,True)
    text(100,327,'Original equal split',25,True)
    text(800,330,'RECORDED',18,True,MUTED,anchor='ra')
    allocation(366,3156,True)
    label='Exploratory optimized split' if final else 'Reassignment illustration'
    text(100,442,label,25,True)
    allocation(480,3156+(1691-3156)*progress,final)
    text(100,548,'1,465 masks reassigned from Spark29 to Spark30',22,color=MUTED)

    box((863,188,1534,586),WHITE,14,LINE)
    text(899,208,'Coordinator time',32,True)
    text(900,250,'Measured phases · lower is better · bars stay fixed',22,color=MUTED)
    max_width=596
    for y,label,value,color in [(300,'Original two-node',equal,AMBER),(390,'Exploratory two-node',optimized,TEAL),(480,'Single-node reference',one,SINGLE)]:
        text(900,y,label,25,True)
        text(1498,y,f'{value:.3f} s',27,True,anchor='ra')
        box((901,y+45,1498,y+74),'#edf2f2',4)
        box((901,y+45,901+max_width*value/equal,y+74),color,4)

    text(69,610,f'{reduction:.1f}% shorter',47,True,TEAL)
    text(71,669,'than the original distributed coordinator phase',25)
    text(866,613,'Near single-node parity',39,True)
    text(868,671,'51.952 s vs 52.111 s — NOT faster',27,True)
    line(68,729,1532,729)
    text(70,746,'Exploratory split selected after the original run; one trial, no timing uncertainty estimate.',24,color=MUTED)
    text(70,785,'Prepared-input phases exclude common setup and final export. No whole-workflow speedup measured.',24,color=MUTED)
    text(70,841,'All 6,305 scientific results matched exactly. Zero saved-score deviation.',27,True,TEAL)
    return im.resize((W,H),Image.Resampling.LANCZOS)

OUT.mkdir(parents=True,exist_ok=True)
still=render(1,True)
still.save(OUT/'benchmark-comparison.png',optimize=True)
# Global palette keeps typography and colors stable between GIF frames.
palette=still.quantize(colors=160,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
frames=[render(0)]
for n in range(1,29):
    t=n/29; ease=t*t*(3-2*t)
    frames.append(render(ease))
frames.append(still)
durations=[2400]+[80]*28+[6200]
encoded=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
encoded[0].save(OUT/'benchmark-comparison.gif',save_all=True,append_images=encoded[1:],duration=durations,loop=0,disposal=1,optimize=False)
metadata={
    'schema':'lymescope.benchmark_animation.v1',
    'base_commit':'6ad4bb776a1f0a89132f465fd6f63ecff93c73a2',
    'dimensions':[W,H], 'aspect_ratio':'16:9', 'loop_duration_ms':sum(durations),
    'original':{'Spark29_masks':3156,'Spark30_masks':3149,'coordinator_s':equal},
    'exploratory':{'Spark29_masks':1691,'Spark30_masks':4614,'coordinator_s':optimized},
    'single_node_coordinator_s':one,'coordinator_time_reduction_percent':reduction,
    'total_tasks':6305,'max_absolute_error_nats':0,'max_relative_error':0,
    'source_workflows':{'original':'79319e56-f368-4eba-8cae-7c646737b9fc','exploratory':exploratory['workflow_id']},
    'sources':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [ROOT/'submission/venue_secondnode_v1/RESULT.json',HERE/'EXPLORATORY_RESULT.json']],
    'animation_semantics':'Only the allocation boundary moves. Intermediate widths illustrate reassignment, not observed intermediate partitions or telemetry. Recorded endpoint masks are printed only at actual recorded allocations. Coordinator bars remain fixed across every frame.',
    'limitations':['One post-hoc exploratory trial chosen after the original run; no repeated timing uncertainty estimate.','Near parity with single node, not established acceleration.','Prepared-input phases exclude common setup and final export; no whole-workflow speedup.','Exploratory trial added a diagnostic sampler; no causal attribution to scheduling alone.'],
    'assets':[{'path':str(p.relative_to(ROOT)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [OUT/'benchmark-comparison.gif',OUT/'benchmark-comparison.png']]
}
(HERE/'PROVENANCE.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'files':metadata['assets'],'duration_ms':sum(durations),'frames_requested':len(frames)}))
