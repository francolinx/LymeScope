"""Prepared storage transport/verification only; never model inference.

The committed Fuzzfile remains HOLD. This script requires explicit execution
selection and operates only in a fresh run directory. Failed partial writes are
retained for inspection, never deleted or overwritten.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import time


def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):digest.update(block)
    return digest.hexdigest()


def check_archive(path,expected):
    path=Path(path)
    if path.is_symlink() or not path.is_file():raise ValueError('Archive must be a regular non-symlink file')
    if path.stat().st_size!=expected['archive_bytes'] or sha(path)!=expected['archive_sha256']:
        raise ValueError('Archive size/SHA256 differs from reviewed plan')


def members_checked(archive,kind,package_path,expected_bytes,model_names):
    members=archive.getmembers();seen=set();file_names=set();size=0
    for item in members:
        name=PurePosixPath(item.name)
        if name.is_absolute() or '..' in name.parts or '\\' in item.name or ':' in item.name or not name.parts:
            raise ValueError('Unsafe archive path')
        normalized=name.as_posix()
        if normalized in seen:raise ValueError('Duplicate archive path')
        seen.add(normalized)
        if not(item.isfile() or item.isdir()):raise ValueError('Archive links/devices are forbidden')
        if kind=='science':
            allowed=(normalized==package_path or normalized.startswith(package_path+'/')
                     or item.isdir() and package_path.startswith(normalized+'/'))
            if not allowed:raise ValueError('File outside pinned scientific package')
        elif normalized not in model_names or not item.isfile():
            raise ValueError('Model archive must contain exactly the six reviewed files')
        if item.isfile():size+=item.size;file_names.add(normalized)
    if size!=expected_bytes:raise ValueError('Expanded payload size mismatch')
    if kind=='model' and file_names!=set(model_names):raise ValueError('Missing model files')
    return members


def extract_new(path,destination,kind,plan):
    destination=Path(destination)
    if destination.exists() or destination.is_symlink():raise FileExistsError('Preserve existing extraction destination')
    expected=plan[kind]
    with tarfile.open(path,'r:') as archive:
        members=members_checked(archive,kind,plan['package_path'],expected['expanded_bytes'],plan['model']['file_names'])
        destination.mkdir()
        for member in members:
            target=destination.joinpath(*PurePosixPath(member.name).parts)
            if member.isdir():target.mkdir(parents=True,exist_ok=True);continue
            target.parent.mkdir(parents=True,exist_ok=True)
            with archive.extractfile(member) as source,target.open('xb') as output:
                shutil.copyfileobj(source,output,1024*1024);output.flush();os.fsync(output.fileno())


def stage(root,plan):
    start=time.perf_counter();root=Path(root)
    if root.is_symlink() or not root.is_dir():raise ValueError('Run root must exist from authorized ingress')
    root=root.resolve()
    if {p.name for p in root.iterdir()}!={'incoming'}:raise ValueError('Fresh run root must contain only incoming archives')
    incoming=root/'incoming'
    if incoming.is_symlink():raise ValueError('Incoming directory must not be a symlink')
    if {p.name for p in incoming.iterdir()}!={'science.tar','model.tar'}:raise ValueError('Unexpected incoming files')
    # Filesystem free space is only an additional guard, not proof of per-volume quota.
    if shutil.disk_usage(root).free<plan['incremental_reservation_bytes']:
        raise ValueError('Insufficient filesystem free space; volume quota also requires prior confirmation')
    t=time.perf_counter()
    for kind in ('science','model'):check_archive(incoming/(kind+'.tar'),plan[kind])
    archive_read_s=time.perf_counter()-t
    t=time.perf_counter()
    extract_new(incoming/'science.tar',root/'science-tree','science',plan)
    extract_new(incoming/'model.tar',root/'model','model',plan)
    extract_write_s=time.perf_counter()-t
    receipts=root/'receipts';receipts.mkdir()
    package=root/'science-tree'/plan['package_path']
    t=time.perf_counter()
    result=subprocess.run([sys.executable,'-B',str(package/'src/verify_package.py'),
        '--model-dir',str(root/'model'),'--output',str(receipts/'package-model-verification.json')],
        cwd=package,capture_output=True,text=True,timeout=90)
    verify_s=time.perf_counter()-t
    (receipts/'verification.log').write_text(result.stdout+result.stderr,encoding='utf-8')
    if result.returncode:raise RuntimeError('Published package/model verification failed; partial artifacts retained')
    receipt={'schema':'lymescope.shared_storage_staging.v1','status':'STAGED_AND_HASH_VERIFIED',
        'scientific_commit':plan['scientific_commit'],'model_revision':plan['model']['revision'],
        'root':str(root),'archive_bytes':sum(plan[k]['archive_bytes'] for k in ('science','model')),
        'expanded_bytes':sum(plan[k]['expanded_bytes'] for k in ('science','model')),
        'archive_hash_read_elapsed_s':archive_read_s,'extract_write_and_fsync_elapsed_s':extract_write_s,
        'published_verification_elapsed_s':verify_s,'staging_process_elapsed_s':time.perf_counter()-start,
        'model_inference':False,'vast_backend_status':'UNVERIFIED_UNLESS_SEPARATE_PROVIDER_EVIDENCE',
        'quota_free_space_verified_by_script':False,
        'timing_limit':'CPU hashing, extraction and fsync included; not raw disk throughput or total workflow makespan',
        'ingress_stage_timing':'REQUIRES_FUZZBALL_STAGE_RECEIPT',
        'physical_node':'REQUIRES_SCHEDULER_ATTRIBUTION'}
    with (receipts/'staging.json').open('x',encoding='utf-8') as stream:
        json.dump(receipt,stream,indent=2,allow_nan=False);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan',required=True,type=Path)
    parser.add_argument('--root',required=True,type=Path)
    parser.add_argument('--execute-approved-stage',action='store_true')
    args=parser.parse_args()
    if not args.execute_approved_stage:parser.error('HOLD: no staging writes without explicit execution selection')
    if sys.flags.optimize:parser.error('Published verification assertions require normal Python, not -O')
    stage(args.root,json.loads(args.plan.read_text(encoding='utf-8')))
