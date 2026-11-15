"""Allowlisted, revision-pinned downloader. Run only after the user's explicit bounded approval."""
import argparse,pathlib,json,urllib.request,hashlib
from common import *
def main():
 p=argparse.ArgumentParser();p.add_argument('--approval-record',required=True);p.add_argument('--destination',required=True);a=p.parse_args();approval=json.loads(pathlib.Path(a.approval_record).read_text());plan=json.loads((ROOT/'provenance/model_download_plan.json').read_text());assert approval['approved'] is True and approval['revision']==plan['revision'] and approval['cap_bytes']==32_000_000
 assert plan['total_download_bytes']<=approval['cap_bytes'];dest=pathlib.Path(a.destination);dest.mkdir(parents=True,exist_ok=False);total=0;receipt=[]
 for entry in plan['files']:
  assert entry['name'] in ['model.safetensors','config.json','vocab.txt','tokenizer_config.json','special_tokens_map.json','README.md'];url=f"https://huggingface.co/{plan['model_id']}/resolve/{plan['revision']}/{entry['name']}"
  with urllib.request.urlopen(url,timeout=60) as response:
   raw=response.read(entry['bytes']+1)
  total+=len(raw);assert len(raw)==entry['bytes'] and total<=approval['cap_bytes']
  digest=hashlib.sha256(raw).hexdigest()
  if entry.get('sha256'):assert digest==entry['sha256']
  else:assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==entry['git_blob_oid']
  (dest/entry['name']).write_bytes(raw);receipt.append({**entry,'sha256':digest})
 write_json(ROOT/'provenance/model_download_receipt.json',{'model_id':plan['model_id'],'revision':plan['revision'],'downloaded_bytes':total,'files':receipt,'approval_record_sha256':sha(a.approval_record)})
 print(json.dumps({'destination':str(dest),'verified_bytes':total},indent=2))
if __name__=='__main__':main()
