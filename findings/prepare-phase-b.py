from pathlib import Path
import textwrap, json, hashlib, datetime
root=Path.cwd()
def put(path, text):
    p=root/path; p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists(): raise SystemExit("Refusing to overwrite "+str(p))
    p.write_text(text,encoding="utf-8",newline="\n")
def resource(gpu=False):
    return "    resource:\n      cpu:\n        cores: "+("2" if gpu else "1")+"\n      memory:\n        size: "+("16GiB" if gpu else "1GiB")+"\n"+("      devices:\n        nvidia.com/gpu: 1\n" if gpu else "")+"      annotations:\n        fuzzball.io/provisioner_definition_id: team15\n"
def output_volume(key):
    return f"""  reports:
    use: team15
    size: 16MiB
    egress:
      - source:
          uri: file://report.txt
        destination:
          uri: fuzzball://group/lymescope/phase-b-20261114/{key}.txt
        policy:
          timeout:
            execute: 1m
"""
header="""# PROPOSED ONLY. No Phase B submission is authorized yet.
# Event v4 syntax: https://ui.fb-hack.civilfritz.net/docs/appendices/workflow-syntax/
# Image family appears in the event guide; this newer tag is grounded in
# NVIDIA's DGX Spark PyTorch playbook. Cache/pull and cluster runtime untested.
# No installs, model weights, model calls, shared-dataset changes, or services.
# Execution limits exclude queueing and image staging.
version: v4
volumes:
  project:
    use: team15
    name: lymescope-project
"""
gpu_script="""#!/bin/bash
set -euo pipefail
{
  hostname
  uname -m
  nvidia-smi
  python3 - <<'PY'
import hashlib, json, os, platform, socket, time
from pathlib import Path
import torch
assert platform.machine() in ("aarch64", "arm64"), "Expected ARM64"
assert torch.cuda.is_available(), "CUDA unavailable"
assert torch.cuda.device_count() == 1, "Expected one GPU"
torch.set_num_threads(2)
torch.backends.cuda.matmul.allow_tf32 = False
info = dict(kind="runtime_setup_test", scientific_result=False,
            hostname=socket.gethostname(), architecture=platform.machine(),
            torch_version=torch.__version__, cuda_runtime=torch.version.cuda,
            gpu_name=torch.cuda.get_device_name(0),
            capability=list(torch.cuda.get_device_capability(0)),
            compiled_architectures=torch.cuda.get_arch_list())
a=torch.ones((32,32),device="cuda",dtype=torch.float32)
b=a @ a
torch.cuda.synchronize()
assert b.is_cuda and torch.all(b == 32).item(), "GPU matrix product mismatch"
value=b.sum().item()
assert value == 32768.0
info.update(gpu_operation="ones(32,32) @ ones(32,32)", gpu_result=value,
            status="PASS", peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated())
p=Path("/project/verification/phase-b-20261114")
p.mkdir(parents=True,exist_ok=True)
payload=b"LymeScope persistent NFS probe 2026-11-14 phase-b-v1\\n"
with (p/"sentinel.txt").open("xb") as f:
    f.write(payload); f.flush(); os.fsync(f.fileno())
assert (p/"sentinel.txt").read_bytes() == payload
info.update(persistence_write="PASS", sentinel_sha256=hashlib.sha256(payload).hexdigest(),
            sentinel_bytes=len(payload), sentinel_path=str(p/"sentinel.txt"))
with (p/"runtime.json").open("x") as f:
    json.dump(info,f,indent=2); f.flush(); os.fsync(f.fileno())
print(json.dumps(info,sort_keys=True))
print("GPU_CALCULATION=PASS; PERSISTENT_WRITE_AND_LOCAL_READ=PASS")
PY
} 2>&1 | tee /reports/report.txt
"""
gpu=header+output_volume("pytorch-and-storage-write")+"""jobs:
  pytorch-and-storage-write:
    image:
      uri: docker://nvcr.io/nvidia/pytorch:25.11-py3
    policy:
      timeout:
        execute: 2m
      restart: never
"""+resource(True)+"""    env:
      - OMP_NUM_THREADS=2
      - HF_HUB_OFFLINE=1
      - TRANSFORMERS_OFFLINE=1
      - PYTHONDONTWRITEBYTECODE=1
    mounts:
      /project: project
      /reports: reports
    script: |
"""+textwrap.indent(gpu_script,"      ")
put(Path("workflows/pytorch-storage-write-team15.fz"),gpu)
# The helper dispatches workers asynchronously: rank 0 polls for both receipts
# before exiting, and only then assembles one report for object-cache egress.
payload=b"LymeScope persistent NFS probe 2026-11-14 phase-b-v1\n"
digest=hashlib.sha256(payload).hexdigest()
reader=f"""#!/bin/bash
set -euo pipefail
test -r /multinode/generic-helper
. /multinode/generic-helper
mkdir /project/verification/phase-b-20261114/read-receipts
exec_rankN - <<'WORKER'
set -eu
dir=/project/verification/phase-b-20261114
echo '{digest}  /project/verification/phase-b-20261114/sentinel.txt' | sha256sum -c -
{{
  printf 'rank=1\\ncontainer_hostname='
  hostname
  printf 'cpu_architecture='
  uname -m
  printf 'sentinel_sha256='
  sha256sum "$dir/sentinel.txt"
  printf 'PERSISTENT_READ=PASS\\n'
}} > "$dir/read-receipts/rank1.tmp"
mv "$dir/read-receipts/rank1.tmp" "$dir/read-receipts/rank1.txt"
WORKER
exec_rank0 - "$MULTINODE_HOSTLIST_NOSLOTS" <<'HEAD'
set -eu
dir=/project/verification/phase-b-20261114
echo '{digest}  /project/verification/phase-b-20261114/sentinel.txt' | sha256sum -c -
{{
  printf 'rank=0\\ncontainer_hostname='
  hostname
  printf 'cpu_architecture='
  uname -m
  printf 'sentinel_sha256='
  sha256sum "$dir/sentinel.txt"
  printf 'PERSISTENT_READ=PASS\\n'
}} > "$dir/read-receipts/rank0.txt"
i=0
while [ ! -f "$dir/read-receipts/rank1.txt" ]; do
  i=$((i + 1))
  [ "$i" -le 30 ] || {{ echo 'FAIL: worker receipt missing'; exit 21; }}
  sleep 1
done
{{
  printf 'kind=storage_setup_test; scientific_result=false\\n'
  printf 'allocated_container_hostlist=%s\\n' "$1"
  cat "$dir/read-receipts/rank0.txt" "$dir/read-receipts/rank1.txt"
  printf 'TWO_RANK_READ=PASS; physical_node_mapping_requires_stage_events\\n'
}} | tee /reports/report.txt
HEAD
wait_rank0
"""
rd=header.replace("# Image family appears in the event guide; this newer tag is grounded in\n# NVIDIA's DGX Spark PyTorch playbook. Cache/pull and cluster runtime untested.","# Generic multinode: https://ui.fb-hack.civilfritz.net/docs/parallel-and-distributed/generic/\n# Uses the Rocky image already executed in Phase A; per-node cache may vary.")+output_volume("storage-two-node-read")+"""jobs:
  storage-two-node-read:
    image:
      uri: docker://rockylinux:9
    policy:
      timeout:
        execute: 2m
      restart: never
"""+resource(False)+"""    multinode:
      nodes: 2
      implementation: generic
    env:
      - MULTINODE_WRAPPER_FORWARD_STREAMS=1
    mounts:
      /project: project
      /reports: reports
    script: |
"""+textwrap.indent(reader,"      ")
put(Path("workflows/storage-two-node-read-team15.fz"),rd)
# Inspection remains outside the immediate approval bundle because per-job
# read-only mount enforcement is not documented and read-only:true was discarded.
scan="""#!/bin/bash
set -euo pipefail
{
  python3 - <<'PY'
import json, os, stat, time
from collections import deque
root="/datasets"
with open("/proc/self/mountinfo") as f:
    mounts=[line.split() for line in f if line.split()[4] == root]
if not mounts or "ro" not in mounts[-1][5].split(","):
    raise SystemExit("BLOCKED: /datasets is not an enforced read-only mount; inspected no contents")
print(json.dumps(dict(kind="dataset_metadata_inventory",scientific_result=False,read_only_verified=True)))
queue=deque([(root,0)])
count=0; deadline=time.monotonic()+15
while queue and count < 100 and time.monotonic() < deadline:
    directory,depth=queue.popleft()
    with os.scandir(directory) as entries:
        for entry in entries:
            if count >= 100 or time.monotonic() >= deadline: break
            st=entry.stat(follow_symlinks=False)
            print(json.dumps(dict(path=os.path.relpath(entry.path,root),
                                 type="directory" if stat.S_ISDIR(st.st_mode) else "symlink" if stat.S_ISLNK(st.st_mode) else "file" if stat.S_ISREG(st.st_mode) else "other",
                                 bytes=st.st_size,mtime_ns=st.st_mtime_ns)))
            count+=1
            if depth < 1 and stat.S_ISDIR(st.st_mode): queue.append((entry.path,depth+1))
print(json.dumps(dict(entries_inspected=count,entry_limit=100,depth_limit=2,time_limit_seconds=15,
                     file_contents_read=False,weights_present="UNCONFIRMED",bounded_partial_listing=True)))
PY
} 2>&1 | tee /reports/report.txt
"""
ds="""# HOLD: excluded from next approval; no documented enforced read-only job mount.
# read-only:true was silently discarded by installed CLI normalization.
# This job fails closed before directory access unless /datasets is mounted ro.
# Never attempt a write to test the mount. No symlink traversal or file reads.
version: v4
volumes:
  datasets:
    use: shared
    name: datasets
"""+output_volume("datasets-metadata")+"""jobs:
  datasets-metadata:
    image:
      uri: docker://rockylinux:9
    policy:
      timeout:
        execute: 1m
      restart: never
"""+resource(False)+"""    mounts:
      /datasets: datasets
      /reports: reports
    script: |
"""+textwrap.indent(scan,"      ")
put(Path("workflows/datasets-metadata-team15.HOLD.fz"),ds)
print(json.dumps({"created":["workflows/pytorch-storage-write-team15.fz","workflows/storage-two-node-read-team15.fz","workflows/datasets-metadata-team15.HOLD.fz"],"sentinel_sha256":digest}))

