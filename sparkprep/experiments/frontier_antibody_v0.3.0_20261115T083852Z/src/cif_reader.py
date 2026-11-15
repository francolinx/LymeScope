import re
import pathlib

def cif_tokens(path):
 lines=iter(pathlib.Path(path).read_text().splitlines(keepends=True))
 for line in lines:
  if line.startswith(';'):
   block=[line[1:].rstrip('\n')]
   for l in lines:
    if l.startswith(';'):break
    block.append(l.rstrip('\n'))
   yield '\x00'+'\n'.join(block)
  else:
   if line.lstrip().startswith('#'):continue
   yield from re.findall(r"'(?:[^']|'(?!\s|$))*'|\"(?:[^\"]|\"(?!\s|$))*\"|\S+",line)

def clean(v):
 return v[1:] if v.startswith('\x00') else v[1:-1] if v.startswith(("'",'\"')) else v

def parse_cif(path):
 ts=list(cif_tokens(path));out={};i=0
 while i<len(ts):
  if ts[i]=='loop_':
   i+=1;tags=[]
   while i<len(ts) and ts[i].startswith('_'):tags.append(ts[i]);i+=1
   vals=[]
   while i<len(ts) and ts[i]!='loop_' and not ts[i].startswith('_') and not ts[i].startswith('data_'):vals.append(ts[i]);i+=1
   assert len(vals)%len(tags)==0,(path,tags)
   for j,t in enumerate(tags):out[t]=[clean(v) for v in vals[j::len(tags)]]
  elif ts[i].startswith('_'):
   out[ts[i]]=[clean(ts[i+1])];i+=2
  else:i+=1
 return out
