"""Offline deterministic routing/merge rehearsal using existing scores. No model execution or event access."""
import tempfile,csv,contextlib,io,collections
from common import *
from summarize_scores import run as merge
from compare_runs import compare

def run():
 source=ROOT/'results/full_panel_v1/residue_nll.tsv';rows=list(csv.DictReader(source.read_text().splitlines(),delimiter='\t'));manifest=json.loads((ROOT/'results/shard_manifest.json').read_text());assign={x['accession']:x['two_node_shard'] for x in manifest['sequences']};shards=[[],[]]
 for r in rows:
  k=assign[r['accession']];shards[k].append({**r,'shard':k})
 assert [len(x) for x in shards]==manifest['two_node_masks'];tasksets=[{r['task_id'] for r in x} for x in shards];assert not tasksets[0]&tasksets[1] and tasksets[0]|tasksets[1]=={r['task_id'] for r in rows}
 with tempfile.TemporaryDirectory(prefix='lymescope-offline-rehearsal-') as tmp:
  tmp=pathlib.Path(tmp);paths=[]
  for k,rs in enumerate(shards):p=tmp/f'shard{k}.tsv';write_tsv(p,rs);paths.append(p)
  with contextlib.redirect_stdout(io.StringIO()):merge(paths,tmp/'merged')
  validation=compare(source,tmp/'merged/residue_nll_merged.tsv');mergedsha=sha(tmp/'merged/residue_nll_merged.tsv')
  failures={}
  for case,casepaths in [('missing_shard',[paths[0]]),('duplicated_shard',[paths[0],paths[1],paths[0]])]:
   try:merge(casepaths,tmp/case)
   except AssertionError as e:failures[case]={'correctly_rejected':True,'error':str(e)}
   else:raise AssertionError(case+' accepted')
  receipt={'status':'PASS','kind':'OFFLINE_ROUTING_MERGE_REHEARSAL_NOT_TWO_NODE_INFERENCE','source_scores_sha256':sha(source),'model_forward_passes':0,'event_access':False,'expected_shard_masks':manifest['two_node_masks'],'actual_routed_masks':[len(x) for x in shards],'task_sets_disjoint_and_complete':True,'numeric_merge_validation':validation,'merged_bytes_sha256':mergedsha,'negative_tests':failures,'ephemeral_files':'Routing TSVs were test intermediates in a temporary directory; original raw scores and deterministic source reproduce them.'}
 write_json(ROOT/'results/shard_merge_rehearsal.json',receipt);print(json.dumps(receipt,indent=2))
if __name__=='__main__':run()
