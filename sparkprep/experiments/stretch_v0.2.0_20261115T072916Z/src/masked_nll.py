"""Portable singleton-mask original-residue NLL implementation.
Execution requires a confirmed external method contract, pinned local weights, and a GPU.
No model/cache download paths are implemented.
"""
import os
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG',':4096:8')
import argparse,csv,json,math,time,resource,sys,hashlib,pathlib
from common import *

def masked_batch(ids,positions,mask_token_id):
 import torch
 # Each row is one independent original sequence with exactly one residue replaced.
 rows=ids.repeat(len(positions),1).clone()
 for i,pos in enumerate(positions):rows[i,pos]=mask_token_id
 return rows

def original_nll(logits,positions,targets):
 import torch
 selected=logits[torch.arange(len(positions),device=logits.device),positions,:].float()
 return -torch.log_softmax(selected,dim=-1)[torch.arange(len(positions),device=logits.device),targets]

def validate_tokenization(tokenizer,seq):
 ids=tokenizer(seq,return_tensors='pt',add_special_tokens=True)['input_ids']
 assert ids.shape==(1,len(seq)+2),('Token count',ids.shape,len(seq))
 assert ids[0,0].item()==tokenizer.cls_token_id and ids[0,-1].item()==tokenizer.eos_token_id
 expected=[tokenizer.convert_tokens_to_ids(aa) for aa in seq]
 assert ids[0,1:-1].tolist()==expected
 assert not set(expected)&set(tokenizer.all_special_ids)
 assert tokenizer.mask_token_id not in ids[0].tolist()
 assert tokenizer.unk_token_id not in expected
 return ids

def run(args):
 import torch,transformers
 from transformers import AutoModelForMaskedLM,EsmTokenizer
 contract=json.loads(pathlib.Path(args.method_contract).read_text())
 assert contract['status']=='CONFIRMED_FINAL','Await confirmed Claude final method; do not silently choose a definition.'
 assert contract['algorithm']=='singleton_mask_original_residue_nll_natural_log_full_vocab'
 modeldir=pathlib.Path(args.model_dir)
 plan=json.loads((ROOT/'provenance/model_download_plan.json').read_text())
 for item in plan['files']:
  p=modeldir/item['name'];assert p.is_file() and p.stat().st_size==item['bytes'],item['name']
  if item.get('sha256'):assert sha(p)==item['sha256'],item['name']
  else:
   raw=p.read_bytes();assert hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['git_blob_oid'],item['name']
 assert torch.cuda.is_available();torch.set_num_threads(4);torch.manual_seed(0);torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
 assert 1<=args.batch_size<=8;assert args.shards in [1,2] and 0<=args.shard<args.shards
 out=pathlib.Path(args.output);out.mkdir(parents=True,exist_ok=False)
 panel=fasta(ROOT/'inputs/panel.fasta');aligned=fasta(ROOT/'inputs/aligned.fasta');items=[(i,k,panel[k]) for i,k in enumerate(aligned) if i%args.shards==args.shard]
 if args.pilot:items=items[:1]
 total_start=time.perf_counter();load_start=total_start
 tokenizer=EsmTokenizer.from_pretrained(modeldir,local_files_only=True)
 model=AutoModelForMaskedLM.from_pretrained(modeldir,local_files_only=True,use_safetensors=True,dtype=torch.float32,attn_implementation='eager').eval().to('cuda')
 torch.cuda.synchronize();load_s=time.perf_counter()-load_start
 assert not model.training and model.config.mask_token_id==tokenizer.mask_token_id
 count=sum(p.numel() for p in model.parameters());assert 7_000_000<=count<=9_000_000
 assert torch.cuda.mem_get_info()[0]>=8*1024**3,'Insufficient free memory with existing services'
 rows=[];per_sequence=[];cold_forward_s=None;scoring_forward_passes=0;warmup_forward_passes=0;validation_forward_passes=0;warmup_masked_examples=0
 torch.cuda.reset_peak_memory_stats();inference_start=time.perf_counter()
 with torch.inference_mode():
  # Warmup is explicit and separate. First forward is cold-forward-after-model-load, not OS-cold filesystem.
  _,firstkey,firstseq=items[0];ids=validate_tokenization(tokenizer,firstseq).to('cuda');positions=torch.arange(1,min(args.batch_size,len(firstseq))+1,device='cuda');warm_ids=masked_batch(ids,positions,tokenizer.mask_token_id);att=torch.ones_like(warm_ids)
  warmups=[]
  for rep in range(3):
   torch.cuda.synchronize();t=time.perf_counter();logits=model(input_ids=warm_ids,attention_mask=att).logits;torch.cuda.synchronize();warmups.append(time.perf_counter()-t);warmup_forward_passes+=1;warmup_masked_examples+=len(positions)
   assert torch.isfinite(logits).all()
  cold_forward_s=warmups[0]
  del logits
  timed_start=time.perf_counter()
  for ordinal,key,seq in items:
   ids=validate_tokenization(tokenizer,seq).to('cuda');columns=[c for c,aa in enumerate(aligned[key],1) if aa!='-'];assert len(columns)==len(seq);tseq=time.perf_counter();gpu_seconds=0
   for start in range(1,len(seq)+1,args.batch_size):
    positions=torch.arange(start,min(start+args.batch_size,len(seq)+1),device='cuda');batch=masked_batch(ids,positions,tokenizer.mask_token_id);targets=ids[0,positions].clone()
    assert (batch==tokenizer.mask_token_id).sum(dim=1).eq(1).all()
    assert torch.equal(batch[:,0],ids[0,0].expand(len(positions))) and torch.equal(batch[:,-1],ids[0,-1].expand(len(positions)))
    torch.cuda.synchronize();t=time.perf_counter();logits=model(input_ids=batch,attention_mask=torch.ones_like(batch)).logits;values=original_nll(logits,positions,targets);torch.cuda.synchronize();gpu_seconds+=time.perf_counter()-t;scoring_forward_passes+=1
    assert torch.isfinite(values).all() and (values>=0).all()
    for pos,nll in zip(positions.cpu().tolist(),values.cpu().tolist()):rows.append({'task_id':f'{key}:{pos}','accession':key,'sequence_position':pos,'alignment_column':columns[pos-1],'original_residue':seq[pos-1],'sequence_sha256':hashlib.sha256(seq.encode()).hexdigest(),'nll_nats':nll,'shard':args.shard})
    del logits,values
    assert torch.cuda.max_memory_allocated()<2*1024**3 and torch.cuda.max_memory_reserved()<4*1024**3,'GPU memory cap exceeded'
    assert resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024<16*1024**3,'Process RSS cap exceeded'
    assert time.perf_counter()-total_start<120,'Measured runtime cap exceeded; stop and propose separately'
   seq_values=[r['nll_nats'] for r in rows if r['accession']==key];mean_nll=sum(seq_values)/len(seq_values)
   per_sequence.append({'accession':key,'sequence_sha256':hashlib.sha256(seq.encode()).hexdigest(),'scored_positions':'all full-length ungapped standard residues 1..L','mean_nll_nats':mean_nll,'ppl':math.exp(mean_nll),'masks':len(seq),'gpu_inference_plus_logsoftmax_s':gpu_seconds,'sequence_wall_s':time.perf_counter()-tseq})
  torch.cuda.synchronize();warm_scoring_s=time.perf_counter()-timed_start
 assert len(rows)==sum(len(seq) for _,_,seq in items);assert len(set(r['task_id'] for r in rows))==len(rows)
 pilot_check=[]
 if args.pilot:
  # Independent batch-one score calculation and repeat check at first/middle/last natural residues.
  key=items[0][1];seq=items[0][2];ids=validate_tokenization(tokenizer,seq).to('cuda')
  with torch.inference_mode():
   for pos in [1,len(seq)//2,len(seq)]:
    single=ids.clone();single[0,pos]=tokenizer.mask_token_id;torch.cuda.synchronize()
    direct_logits=model(input_ids=single,attention_mask=torch.ones_like(single)).logits[0,pos].float();validation_forward_passes+=1;target=ids[0,pos]
    direct=(torch.logsumexp(direct_logits,dim=0)-direct_logits[target]).item();reference=next(r['nll_nats'] for r in rows if r['sequence_position']==pos)
    error=abs(direct-reference);assert error<=1e-4+1e-5*abs(direct),('Batch-one comparison failed',pos,error)
    pilot_check.append({'sequence_position':pos,'batch_one_nll':direct,'batched_nll':reference,'absolute_error':error})
 write_json(out/'pilot_correctness.json',{'checks':pilot_check,'status':'PASS' if args.pilot else 'NOT_APPLICABLE','tokenizer_exact_original_residues':True,'single_mask_each_row':True,'special_tokens_preserved':True,'finite_nonnegative_scores':True})
 write_tsv(out/'residue_nll.tsv',rows)
 timing={'host':os.uname().nodename,'device':torch.cuda.get_device_name(0),'torch':torch.__version__,'transformers':transformers.__version__,'cuda_runtime':torch.version.cuda,'model_id':plan['model_id'],'model_revision':plan['revision'],'parameter_count':count,'precision':'float32; TF32 disabled; eager attention; no autocast','masking':'one independent mask per original residue; all model vocabulary classes in log-softmax','batch_size':args.batch_size,'shards':args.shards,'shard':args.shard,'pilot':args.pilot,'task_count':len(rows),'scoring_masked_examples':len(rows),'warmup_masked_examples':warmup_masked_examples,'validation_masked_examples':validation_forward_passes,'scoring_forward_passes':scoring_forward_passes,'warmup_forward_passes':warmup_forward_passes,'validation_forward_passes':validation_forward_passes,'total_forward_passes':scoring_forward_passes+warmup_forward_passes+validation_forward_passes,'model_load_and_cuda_transfer_s':load_s,'first_forward_after_load_s':cold_forward_s,'warmup_forward_s':warmups,'warm_scoring_wall_s':warm_scoring_s,'end_to_end_wall_s':time.perf_counter()-total_start,'peak_gpu_allocated_bytes':torch.cuda.max_memory_allocated(),'peak_gpu_reserved_bytes':torch.cuda.max_memory_reserved(),'process_max_rss_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024,'sequence_timings':per_sequence,'method_contract_sha256':sha(args.method_contract),'model_files':[{**x,'sha256':sha(modeldir/x['name'])} for x in plan['files']],'score_sha256':sha(out/'residue_nll.tsv'),'timing_scope':'Personal Spark with existing services; not a matched event-cluster benchmark. Cold load means new process with uncontrolled OS page cache, not guaranteed cold disk.'}
 write_json(out/'timings.json',timing);print(json.dumps(timing,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--model-dir',required=True);p.add_argument('--method-contract',required=True);p.add_argument('--output',required=True);p.add_argument('--batch-size',type=int,default=8);p.add_argument('--shards',type=int,default=1);p.add_argument('--shard',type=int,default=0);p.add_argument('--pilot',action='store_true');run(p.parse_args())
