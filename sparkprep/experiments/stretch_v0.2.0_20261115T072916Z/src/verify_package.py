"""Offline exact-byte package and optional local model-cache verification. No network, downloads or inference."""
import argparse,sys
from common import *
def verify(model_dir=None):
 manifest=json.loads((ROOT/'FILE_MANIFEST.json').read_text());files=manifest['files'];seen=set()
 for item in files:
  rel=pathlib.PurePosixPath(item['path']);assert not rel.is_absolute() and '..' not in rel.parts;assert str(rel) not in seen;seen.add(str(rel));p=ROOT/rel;assert p.is_file() and not p.is_symlink(),str(rel);assert p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],str(rel)
 sums={line.split(maxsplit=1)[1]:line.split(maxsplit=1)[0] for line in (ROOT/'SHA256SUMS').read_text().splitlines() if line.strip()};assert sums=={f['path']:f['sha256'] for f in files}
 model=[]
 if model_dir:
  receipt=json.loads((ROOT/'provenance/model_download_receipt.json').read_text())
  for item in receipt['files']:
   p=pathlib.Path(model_dir)/item['name'];assert p.is_file() and p.stat().st_size==item['bytes'] and sha(p)==item['sha256'],item['name'];model.append({'name':item['name'],'sha256':sha(p),'bytes':p.stat().st_size})
  assert len(model)==6 and sum(x['bytes'] for x in model)==31387085
 return {'status':'PASS','package_file_hashes_checked':len(files),'manifest_sha256':sha(ROOT/'FILE_MANIFEST.json'),'model_files_checked':model,'network_access':False,'model_inference':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--model-dir');p.add_argument('--output');a=p.parse_args();j=verify(a.model_dir)
 if a.output:write_json(a.output,j)
 print(json.dumps(j,indent=2))
