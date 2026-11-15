import os,sys,json,time,platform,importlib.metadata as md,subprocess
out={'host':platform.node(),'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'python':sys.version,'executable':sys.executable,'packages':{}}
for name in ['torch','transformers','safetensors','tokenizers','huggingface-hub','numpy','biopython','scipy']:
 try:out['packages'][name]=md.version(name)
 except md.PackageNotFoundError:out['packages'][name]=None
try:
 import torch
 out.update(torch_cuda=torch.version.cuda,cuda_available=torch.cuda.is_available(),compiled_arches=torch.cuda.get_arch_list())
 if out['cuda_available']:
  out.update(device=torch.cuda.get_device_name(0),capability=torch.cuda.get_device_capability(0),memory_before=torch.cuda.mem_get_info())
  torch.use_deterministic_algorithms(True);torch.backends.cuda.matmul.allow_tf32=False
  start=time.perf_counter();x=torch.arange(4096,device='cuda',dtype=torch.float32);y=x*2+1;torch.cuda.synchronize();elapsed=time.perf_counter()-start
  expected=torch.arange(4096,dtype=torch.float32)*2+1;actual=y.cpu()
  a=torch.arange(256,device='cuda',dtype=torch.float32).reshape(16,16)/256;b=torch.eye(16,device='cuda');c=a@b;torch.cuda.synchronize()
  out.update(test_pass=bool(torch.equal(actual,expected) and torch.equal(c.cpu(),a.cpu())),max_abs_error=float((actual-expected).abs().max()),checksum=float(actual.sum()),elapsed_s=elapsed,peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved())
except Exception as e:out['error']=repr(e)
print(json.dumps(out,indent=2))
