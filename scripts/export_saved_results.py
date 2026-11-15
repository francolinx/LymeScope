"""Offline allowlist exporter. No network clients, cluster commands, or recursive copy."""
from pathlib import Path
import datetime, hashlib, html, json, shutil

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"portable_results"
DEST.mkdir(exist_ok=True)
index=json.loads((ROOT/"findings/result-export-index.json").read_text(encoding="utf-8"))
records=[]
for item in index["evidence_files"]:
    rel=Path(item["path"])
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("Only relative workspace paths are allowed")
    src=ROOT/rel
    if not src.is_file():
        raise FileNotFoundError(f"Missing approved evidence: {rel}")
    data=src.read_bytes()
    if len(data)>2*1024*1024:
        raise ValueError(f"Review large artifact before export: {rel}")
    # Explicit source allowlist excludes credential files, models and unrelated data.
    target=DEST/rel
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,target)
    records.append(dict(path=rel.as_posix(),sha256=hashlib.sha256(data).hexdigest(),
                        bytes=len(data),classification=item["classification"],
                        provenance=item["provenance"]))
def e(x): return html.escape(str(x),quote=True)
cards=[]
for run in index["runs"]+index.get("scientific_runs",[]):
    files="".join(f'<li><a href="{e(p)}">{e(p)}</a></li>' for p in run["files"])
    fields=[("Classification",run["kind"]),("Status",run["status"]),
            ("Workflow",run["id"]),("Physical nodes",", ".join(run["physical_nodes"])),
            ("Result",run["result"]),("Timing",run["timing"]),("Inputs",run["inputs"]),
            ("Model/settings",run["model"]),("Success / failure",f'{run["success_count"]} / {run["failure_count"]}')]
    rows="".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k,v in fields)
    cards.append(f'<article><h2>{e(run["title"])}</h2><dl>{rows}</dl><details><summary>Local evidence files</summary><ul>{files}</ul></details></article>')
missing="".join(f"<li>{e(s)}</li>" for s in index["missing"])
stamp=datetime.datetime.now().astimezone().isoformat(timespec="seconds")
page="""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; connect-src 'none'; img-src 'none'; media-src 'none'; font-src 'none'; frame-src 'none'; script-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<title>LymeScope — saved results</title>
<style>
:root{font-family:system-ui,Segoe UI,sans-serif;color:#182b36;background:#eef3f6;color-scheme:light}
body{max-width:1000px;margin:0 auto;padding:32px 24px 64px}h1{font-size:30px;margin-bottom:8px}
header p{max-width:760px;line-height:1.55}.badge{display:inline-block;padding:6px 12px;background:#dcebdd;border-radius:6px;font-weight:650}
article,section{background:white;border:1px solid #cbd8df;border-radius:10px;padding:22px;margin-top:20px}
h2{margin:0 0 18px;font-size:21px}dl{display:grid;grid-template-columns:160px 1fr;gap:12px}
dt{font-weight:650}dd{margin:0;overflow-wrap:anywhere;line-height:1.4}a{color:#15578a}li{margin:8px 0}
.note{border-left:5px solid #c89430}summary{cursor:pointer;font-weight:650}footer{margin-top:24px;color:#52616b;font-size:13px}
@media(max-width:640px){dl{grid-template-columns:1fr;gap:7px}dd{margin-bottom:10px}body{padding:20px 14px}h1{font-size:25px}}
</style></head><body><header><p class="badge">Local files • Cluster requests disabled</p>
<h1>Saved results from completed cluster runs.</h1>
<p>LymeScope evidence viewer. Everything essential is saved alongside this page. No Fuzzball connection, model endpoint, notebook, web font, JavaScript library or local server is required.</p>
</header>"""
page+="".join(cards)
science_count=len(index.get("scientific_runs",[]))
page=page.replace("Local files", "Infrastructure results only" if science_count==0 else "Saved scientific and infrastructure results")
science_title="Scientific results: none yet" if science_count==0 else f"Scientific runs: {science_count}"
page+=f'<section class="note"><h2>{science_title}</h2><p>Setup tests are not scientific results. {e(index["benchmark"]["status"])}: identical-workload one-node/two-node pilot.</p><ul>{missing}</ul></section>'
page+='<section><h2>Portable evidence</h2><p><a href="manifest.json">SHA256 manifest and provenance</a> · <a href="results-index.json">Result index</a></p><p>Reference structures, when added, must be labeled pre-existing. A proposed workflow is never evidence that it executed.</p></section>'
page+=f'<footer>Export generated {e(stamp)}. Node access after the event is unknown and is not required to view these files.</footer></body></html>'
(DEST/"index.html").write_text(page,encoding="utf-8")
(DEST/"results-index.json").write_text(json.dumps(index,indent=2)+"\n",encoding="utf-8")
for name,classification in [("index.html","offline_viewer"),("results-index.json","result_index")]:
    b=(DEST/name).read_bytes()
    records.append(dict(path=name,sha256=hashlib.sha256(b).hexdigest(),bytes=len(b),
                        classification=classification,provenance="Generated locally from findings/result-export-index.json"))
manifest=dict(schema_version=1,generated_at=stamp,label=index["label"],
              files=records,missing=index["missing"],
              exclusions=["model weights","whole dataset volumes","authentication files","tokens","unrelated team data"],
              self_hash_note="manifest.json does not hash itself")
(DEST/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
for item in records:
    assert hashlib.sha256((DEST/item["path"]).read_bytes()).hexdigest()==item["sha256"]
print(json.dumps(dict(exported_files=len(records),manifest="portable_results/manifest.json",sha256_verification="PASS",network_requests=0)))
