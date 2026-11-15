"""Exact task identity and numeric-tolerance acceptance for repeated/sharded model runs."""
import argparse,csv,math
from common import *
def load(path):
 rows=list(csv.DictReader(pathlib.Path(path).read_text().splitlines(),delimiter='\t'));out={r['task_id']:r for r in rows};assert len(out)==len(rows),'Duplicate tasks';return out
def compare(reference,candidate,reference_subset=False):
 a=load(reference);b=load(candidate)
 expected={r['task_id'] for r in csv.DictReader((ROOT/'results/residue_alignment_mapping.tsv').read_text().splitlines(),delimiter='\t')}
 if reference_subset:assert set(a)<=set(b)<=expected,'Task-set mismatch'
 else:assert set(a)==set(b)==expected,'Task-set mismatch or incomplete panel'
 errors=[]
 for task,r in a.items():
  q=b[task]
  for key in ['accession','sequence_position','alignment_column','original_residue','sequence_sha256']:assert r[key]==q[key],(task,key)
  x=float(r['nll_nats']);y=float(q['nll_nats']);assert math.isfinite(x) and math.isfinite(y) and min(x,y)>=0
  error=abs(x-y);assert error<=1e-4+1e-5*abs(x),(task,error);errors.append(error)
 return {'status':'PASS','task_count':len(a),'max_absolute_error_nats':max(errors,default=0),'tolerance':'abs(candidate-reference) <= 1e-4 + 1e-5*abs(reference)','reference_sha256':sha(reference),'candidate_sha256':sha(candidate)}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--reference',required=True);p.add_argument('--candidate',required=True);p.add_argument('--output',required=True);p.add_argument('--reference-subset',action='store_true');args=p.parse_args();j=compare(args.reference,args.candidate,args.reference_subset);write_json(args.output,j);print(json.dumps(j,indent=2))
