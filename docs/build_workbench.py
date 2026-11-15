"""Package the existing demo for offline use or a future /docs Pages source.

No hosting calls, installs, model downloads or scientific-output writes.
"""
import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote, urlsplit

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
DEMO=ROOT/'demo/v0.2.0'
EXPERIMENT=ROOT/'sparkprep/experiments/stretch_v0.2.0_20261115T072916Z'
SOURCE_COMMIT='aafe818a20ea025370cf4b65145a9684e80aaaef'
FRONTIER=ROOT/'sparkprep/experiments/frontier_antibody_v0.3.0_20261115T083852Z'
FRONTIER_COMMIT='82fb8b53018ba4012ccebf02a29efa87b892f6ed'
BRANCH='main'  # Reviewed homepage release target; no publication performed here.
SCENES=('coverage-evidence','ospc-rotation','alignment-map','residue-mapping','ospc-dimer')
FIGURES=('full_panel_agreement_predictability','experimental_dimer_comparison','calculated_sasa_dimer_context')


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def build():
    copies={}
    for scene in SCENES:
        for ext in ('png','gif'):copies[DEMO/'assets'/f'{scene}.{ext}']=DOCS/'workbench-assets'/f'{scene}.{ext}'
    for figure in FIGURES:
        for ext in ('png','svg'):copies[EXPERIMENT/'results'/f'{figure}.{ext}']=DOCS/'workbench-assets/science'/f'{figure}.{ext}'
    for ext in ('png','svg'):
        copies[FRONTIER/'results'/f'FRONTIER_EXPERIMENT.{ext}']=DOCS/'workbench-assets/science'/f'FRONTIER_EXPERIMENT.{ext}'
    # The six-scene historical asset manifest includes an intentionally omitted
    # batch-16 animation. Link to the original rather than ship a partial bundle
    # with a manifest that appears to promise that obsolete scene locally.
    copies[DEMO/'context.json']=DOCS/'workbench-data.json'
    records=[]
    for source,target in copies.items():
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
        assert digest(source)==digest(target)
        records.append({'source':source.relative_to(ROOT).as_posix(),'path':target.relative_to(DOCS).as_posix(),
                        'bytes':target.stat().st_size,'sha256':digest(target)})
    def rebase(match):
        attr,value=match.group(1),match.group(2)
        parsed=urlsplit(value)
        if parsed.scheme or parsed.netloc or not parsed.path:return match.group(0)
        source=(DEMO/parsed.path).resolve()
        if source in copies:
            dest=copies[source].relative_to(DOCS).as_posix()
        elif source.is_relative_to(DOCS):
            dest=source.relative_to(DOCS).as_posix()
        else:
            assert source.is_relative_to(ROOT),value
            ref=SOURCE_COMMIT if source.is_relative_to(EXPERIMENT) else FRONTIER_COMMIT if source.is_relative_to(FRONTIER) else BRANCH
            dest=f'https://github.com/francolinx/LymeScope/blob/{ref}/'+quote(source.relative_to(ROOT).as_posix(),safe='/')
        if parsed.fragment:dest+='#'+parsed.fragment
        return attr+'="'+dest+'"'
    page=(DEMO/'index.html').read_text(encoding='utf-8')
    page=re.sub(r'(href|src|srcset)="([^"<>]+)"',rebase,page)
    # JS image paths are deliberately local too; JSON evidence has no such paths.
    page=page.replace("'assets/'","'workbench-assets/'").replace("'assets/ospc-dimer.","'workbench-assets/ospc-dimer.")
    # Reuse original static-first behavior; this package adds no scientific logic.
    page=page.replace('<body><main>','<body><main><p class="note">Offline workbench / prepared GitHub Pages source. Hosting is not verified. <a href="PAGES_PREPARATION.md">Deployment status</a> · <a href="workbench-manifest.json">File manifest</a></p>',1)
    (DOCS/'index.html').write_text(page,encoding='utf-8',newline='\n')
    (DOCS/'.nojekyll').write_text('',encoding='utf-8')
    manifest={'schema':'lymescope.offline_workbench.v1','status':'PREPARED_NOT_HOSTED_OR_BROWSER_VERIFIED',
              'source_demo':'demo/v0.2.0/index.html','source_demo_sha256':digest(DEMO/'index.html'),
              'page_sha256':digest(DOCS/'index.html'),'scientific_source_commit':SOURCE_COMMIT,
              'frontier_source_commit':FRONTIER_COMMIT,
              'repository_link_ref':BRANCH,'files':records,'total_copied_bytes':sum(x['bytes'] for x in records),
              'model_weights_included':False,'hosting_settings_changed':False}
    (DOCS/'workbench-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'page':str(DOCS/'index.html'),'copied_files':len(records),'bytes':manifest['total_copied_bytes']}))


if __name__=='__main__':build()
