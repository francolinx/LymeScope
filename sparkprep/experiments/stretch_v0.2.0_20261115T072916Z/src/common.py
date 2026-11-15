import pathlib,json,csv,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()
def fasta(path):
 out={};key=None
 for line in pathlib.Path(path).read_text().splitlines():
  if line.startswith('>'):
   key=line[1:].split()[0];assert key not in out;out[key]=''
  elif line.strip():out[key]+=line.strip()
 return out
def write_json(path,data):pathlib.Path(path).write_text(json.dumps(data,indent=2,allow_nan=False)+'\n')
def write_tsv(path,rows):
 if not rows:return
 with pathlib.Path(path).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
def cif_rows(c,prefix):
 keys=[k for k in c if k.startswith(prefix+'.')]
 return [{k.split('.',1)[1]:c[k][i] for k in keys} for i in range(len(c[keys[0]]))] if keys else []
