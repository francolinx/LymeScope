import subprocess,json,pathlib,datetime,platform,shutil,os
root=pathlib.Path.cwd()
def run(a):
 try:
  p=subprocess.run(a,capture_output=True,text=True,timeout=45);return {'command':a,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
 except Exception as e:return {'command':a,'error':str(e)}
probe="""import json,sys,importlib.util
r={'python':sys.version,'executable':sys.executable}
if importlib.util.find_spec('torch'):
 try:
  import torch
  r.update(torch_version=torch.__version__,cuda_build=torch.version.cuda,cuda_available=torch.cuda.is_available())
  try:
   x=torch.tensor([1.,2.],device='cuda');r['tiny_gpu_result']=(x*x).sum().item()
  except Exception as e:r['tiny_gpu_error']=str(e)
 except Exception as e:r['torch_import_error']=str(e)
else:r['torch_available']=False
print(json.dumps(r))"""
paths=['/usr/bin/python3']+[str(p/'bin/python') for p in [pathlib.Path.home()/x for x in ['cnh-venv','ftvenv','gymvenv','gymvenv313','forge/.venv','gmaps-spark-workpackage/.venv']] if (p/'bin/python').exists()]
r={'scope':'PERSONAL Spark only; no event-cluster measurements','retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostname':platform.node(),'username':os.environ.get('USER'),'architecture':platform.machine(),'checks':[run(a) for a in [['uname','-a'],['nvidia-smi'],['free','-b'],['df','-B1','.'],['docker','image','ls','--format','{{json .}}'],['lspci']]],'python_environments':[run([p,'-c',probe]) for p in paths]}
for name,path in [('huggingface',pathlib.Path.home()/'.cache/huggingface/hub'),('torch',pathlib.Path.home()/'.cache/torch')]:
 r[name+'_cache']={'path':str(path),'entries':sorted(p.name for p in path.iterdir()) if path.exists() else [],'note':'Targeted names only; cache presence does not verify weight completeness. No weights downloaded.'}
p=pathlib.Path('/proc/driver/nvidia/version');r['kernel_driver_version']=p.read_text() if p.exists() else None
r['device_nodes']=[str(x) for x in pathlib.Path('/dev').glob('nvidia*')]
(root/'runtime_inventory.json').write_text(json.dumps(r,indent=2))
print(json.dumps(r['python_environments'],indent=2))
