"""Original accessible history SVG and local README preview, using existing libraries."""
import html
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
MILESTONES=[
 ('1958','Seeing a protein','X-ray analysis yields a myoglobin model.','https://www.nature.com/articles/181662a0'),
 ('1980s','Structures in solution','NMR constraints and distance geometry.','https://pubmed.ncbi.nlm.nih.gov/2582141/'),
 ('1992–97','Computational routes','Threading, homology and fragment assembly.','https://pubmed.ncbi.nlm.nih.gov/9149153/'),
 ('1994','CASP begins','Blind tests against experimental targets.','https://www.ebi.ac.uk/training/online/courses/alphafold/validation-and-impact/how-have-alphafolds-predictions-of-protein-structure-been-validated/'),
 ('2018','AlphaFold at CASP13','Deep learning in the structure benchmark.','https://deepmind.google/science/alphafold/'),
 ('2020 / 21','AlphaFold2','CASP14 in 2020; research paper in 2021.','https://www.nature.com/articles/s41586-021-03819-2'),
 ('2021 / 22','Predictions become a resource','AlphaFold DB launches, then expands.','https://www.ebi.ac.uk/about/news/technology-and-innovation/alphafold-200-million/'),
 ('2023','Language models meet structure','Meta FAIR publishes ESMFold research.','https://pubmed.ncbi.nlm.nih.gov/36927031/'),
 ('2024','Molecular interactions','AlphaFold3: joint structure prediction.','https://www.nature.com/articles/s41586-024-07487-w'),
 ('2026','LymeScope: inspect the evidence','Local workflow; CPU OspC baseline complete.','https://github.com/francolinx/LymeScope')]


def build():
    assets=HERE/'assets';assets.mkdir(exist_ok=True)
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="100%" viewBox="0 0 660 1640" role="img" aria-labelledby="title description">',
         '<title id="title">From experimental structures to inspectable local biology</title>',
         '<desc id="description">Ten milestones, 1958 to 2026. Experimental observations and predictions remain distinct. Full chronological text and references accompany this timeline in README.md.</desc>',
         '<rect width="660" height="1640" rx="20" fill="#071b26"/>',
         '<g font-family="Segoe UI,Arial,sans-serif" fill="#edf6f5">',
         '<text x="30" y="48" font-size="19" fill="#4ed9c1" letter-spacing="1">A HISTORY OF MAKING BIOLOGY VISIBLE</text>',
         '<text x="30" y="94" font-size="33" font-weight="700">Evidence. Models. New questions.</text>',
         '<path d="M49 140 V1550" stroke="#2a5562" stroke-width="3"/>']
    for i,(year,title,detail,url) in enumerate(MILESTONES):
        y=160+i*145;color='#ffc16b' if i==9 else '#4ed9c1'
        svg.extend([f'<a href="{html.escape(url,quote=True)}"><circle cx="49" cy="{y}" r="8" fill="{color}"/>',
                    f'<text x="80" y="{y+7}" font-size="24" font-weight="700" fill="{color}">{html.escape(year)}</text>',
                    f'<text x="80" y="{y+48}" font-size="27" font-weight="650">{html.escape(title)}</text>',
                    f'<text x="80" y="{y+84}" font-size="22" fill="#a8c2ca">{html.escape(detail)}</text></a>'])
    svg.extend(['<text x="30" y="1604" font-size="19" fill="#a8c2ca">Not a universal accuracy scale. Experiments remain essential.</text>','</g></svg>'])
    (assets/'biology-timeline.svg').write_text('\n'.join(svg)+'\n',encoding='utf-8')
    (assets/'timeline-sources.json').write_text(json.dumps(MILESTONES,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    import markdown
    source=(ROOT/'README.md').read_text(encoding='utf-8').replace('<details>','<details markdown="1">')
    body=markdown.markdown(source,extensions=['tables','fenced_code','md_in_html'])
    doc='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src 'self' data:; style-src 'unsafe-inline'; base-uri 'none'">
<title>LymeScope — local README preview</title><style>body{margin:0;background:#f3f7f7;color:#183440;font:17px/1.65 system-ui,sans-serif}main{max-width:940px;margin:32px auto;padding:32px;background:white}h1,h2{line-height:1.2}h1{letter-spacing:.12em;font-size:46px}h2{border-top:1px solid #cfe0e3;padding-top:25px;margin-top:38px}a{color:#086b78}img,svg{max-width:100%;height:auto}table{border-collapse:collapse;display:block;overflow:auto}td,th{padding:10px;border:1px solid #d3e1e4}code{overflow-wrap:anywhere}blockquote{border-left:4px solid #188a87;margin-left:0;padding:6px 20px;background:#edf7f6}summary{cursor:pointer}picture{display:block}@media(max-width:600px){main{padding:18px;margin:0}h1{font-size:34px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}</style><main><p><strong>Local preview.</strong> GitHub rendering has not been verified.</p>'''+body+'</main></html>'
    for attr in ('src','srcset','href'):
        for folder in ('demo','sparkprep','findings','portable_results','docs'):
            doc=doc.replace(f'{attr}="{folder}/',f'{attr}="../{folder}/')
    doc=doc.replace('href="submission/','href="').replace('href="RUN_LOCALLY.md','href="../RUN_LOCALLY.md')
    (ROOT/'submission').mkdir(exist_ok=True)
    (ROOT/'submission'/'README_PREVIEW.html').write_text(doc,encoding='utf-8')


if __name__=='__main__':build()
