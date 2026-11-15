"""Verify archived frontier inputs/results/source exactly, without network or computation."""
import json,pathlib,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def verify():
 manifest=json.loads((ROOT/'FILE_MANIFEST.json').read_text());seen=set()
 for entry in manifest['files']:
  rel=pathlib.PurePosixPath(entry['path']);assert not rel.is_absolute() and '..' not in rel.parts and str(rel) not in seen;seen.add(str(rel));p=ROOT/rel;assert p.is_file() and not p.is_symlink();raw=p.read_bytes();assert len(raw)==entry['bytes'] and hashlib.sha256(raw).hexdigest()==entry['sha256'],str(rel)
 sums={line.split(maxsplit=1)[1]:line.split(maxsplit=1)[0] for line in (ROOT/'SHA256SUMS').read_text().splitlines() if line.strip()};assert sums=={r['path']:r['sha256'] for r in manifest['files']}
 return {'status':'COMPLETED','file_hash_verification':'PASS','files_checked':len(seen),'network_access':'NOT RUN','model_inference':'NOT RUN'}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
