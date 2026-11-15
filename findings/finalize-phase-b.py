from pathlib import Path
import json,hashlib,uuid,datetime,textwrap,ast
run="phase-b-"+datetime.datetime.now().strftime("%Y%m%dT%H%M%S")+"-"+uuid.uuid4().hex[:8]
payload=("LymeScope persistent NFS verification\nrun_id="+run+"\n").encode()
digest=hashlib.sha256(payload).hexdigest()
base="/project/verification/"+run
info={"runId":run,"testDirectory":base,"testFile":base+"/sentinel.txt","expectedBytes":len(payload),"expectedSha256":digest,"expectedText":payload.decode(),"writerWorkflow":"workflows/pytorch-storage-write-team15.fz","readerWorkflow":"workflows/storage-two-node-read-team15.fz"}
Path("findings/phase-b-test-contract.json").write_text(json.dumps(info,indent=2)+"\n")
Path("findings/phase-b-sentinel.expected.txt").write_bytes(payload)
p=Path(info["writerWorkflow"]); f=p.read_text()
f=f.replace("# PROPOSED ONLY. No Phase B submission is authorized yet.","# Authorized Phase B: exactly one submission, after full preflight passes.")
f=f.replace("phase-b-20261114/pytorch-and-storage-write.txt",run+"/pytorch-and-storage-write.txt")
f=f.replace('import hashlib, json, os, platform, socket, time','import hashlib, json, os, platform, socket, time, subprocess')
f=f.replace('hostname=socket.gethostname(), architecture=platform.machine(),','hostname=socket.gethostname(), architecture=platform.machine(),\n                  python_version=platform.python_version(), run_id='+repr(run)+',\n                  driver_version=subprocess.check_output(["nvidia-smi","--query-gpu=driver_version","--format=csv,noheader"],text=True).strip(),')
f=f.replace('status="PASS", peak_cuda_allocated_bytes=', 'status="PASS", cuda_synchronized=True, result_device=str(b.device), peak_cuda_allocated_bytes=')
f=f.replace('p=Path("/project/verification/phase-b-20261114")\n      p.mkdir(parents=True,exist_ok=True)', 'p=Path('+repr(base)+')\n      p.parent.mkdir(parents=True,exist_ok=True)\n      p.mkdir(exist_ok=False)')
f=f.replace('payload=b"LymeScope persistent NFS probe 2026-11-14 phase-b-v1\\n"', 'payload='+repr(payload))
# Capture CUDA toolkit patch release from its installed metadata when present.
f=f.replace('      a=torch.ones', '      version_file=Path("/usr/local/cuda/version.json")\n      if version_file.is_file():\n          info["cuda_toolkit_metadata"]=json.loads(version_file.read_text()).get("cuda",{})\n      a=torch.ones')
p.write_text(f,encoding="utf-8",newline="\n")
reader_py=f"""import hashlib,json,socket,platform
from pathlib import Path
p=Path({base!r})
expected={payload!r}
with (p/"sentinel.txt").open("rb") as stream:
    actual=stream.read(2048)
assert actual==expected, "Persistent bytes mismatch"
actual_hash=hashlib.sha256(actual).hexdigest()
assert actual_hash=={digest!r}, "Persistent SHA256 mismatch"
receipt=dict(run_id={run!r},container_hostname=socket.gethostname(),
             architecture=platform.machine(),test_file=str(p/"sentinel.txt"),
             bytes=len(actual),sha256=actual_hash,bytes_match=True,sha256_match=True)
"""
ast.parse(reader_py)
# Each rank uses exclusive receipt creation in the unique run directory.
def block(rank):
    py=reader_py+f"""receipt["rank"]={rank}
receipt["status"]="PASS"
data=json.dumps(receipt,sort_keys=True)
with (p/"read-receipts"/"rank{rank}.txt").open("x") as f:
    f.write(data+"\\n"); f.flush()
print(data)
"""
    return "python3 - <<'PY'\n"+py+"PY\n"
script=f"""#!/bin/bash
set -euo pipefail
test -r /multinode/generic-helper
. /multinode/generic-helper
mkdir {base}/read-receipts
exec_rankN - <<'WORKER'
set -eu
{block(1)}WORKER
exec_rank0 - <<'HEAD'
set -eu
{block(0)}i=0
while [ ! -s {base}/read-receipts/rank1.txt ]; do
  i=$((i + 1))
  [ "$i" -le 30 ] || {{ echo 'FAIL: worker receipt missing'; exit 21; }}
  sleep 1
done
{{
  printf 'two-node shared-storage verification\\n'
  printf 'run_id={run}\\n'
  printf 'allocated_container_hostlist=%s\\n' "$MULTINODE_HOSTLIST_NOSLOTS"
  cat {base}/read-receipts/rank0.txt {base}/read-receipts/rank1.txt
  printf 'TWO_RANK_READ=PASS; verify physical scheduler node identities separately\\n'
}} | tee /reports/report.txt
HEAD
wait_rank0
"""
p=Path(info["readerWorkflow"]); f=p.read_text()
f=f.replace("# PROPOSED ONLY. No Phase B submission is authorized yet.","# Authorized Phase B: exactly one submission, only after writer success/export.")
f=f.replace("phase-b-20261114/storage-two-node-read.txt",run+"/storage-two-node-read.txt")
f=f.split("    script: |")[0]+"    script: |\n"+textwrap.indent(script,"      ")
p.write_text(f,encoding="utf-8",newline="\n")
print(json.dumps(info))

