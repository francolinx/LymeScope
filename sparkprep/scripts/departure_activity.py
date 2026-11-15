"""Scoped read-only activity check; no credentials, environments, or file contents read."""
import pathlib,os,json,datetime,argparse,subprocess
P=pathlib.Path;p=argparse.ArgumentParser();p.add_argument('--output',type=P,required=True);a=p.parse_args();root=P(__file__).resolve().parent.parent
raw=subprocess.run(['ps','-eo','pid=,ppid=,comm=,stat=,etime='],capture_output=True,text=True,check=True).stdout
rows=[dict(zip(['pid','ppid','name','state','elapsed'],s)) for l in raw.splitlines() if len(s:=l.split(None,4))==5]
build_names={'make','gmake','gcc','cc1','cc1plus','collect2','ld','mafft','tbfast','disttbfast','pairlocalalign','dvtditr','dndpre','splittbfast'}
scripts={x.name for x in (root/'scripts').glob('*.py')}|{x.name for x in (root/'analysis').rglob('*.py')};scripts.discard(P(__file__).name)
matched=[];writers=[];denied=0
for r in rows:
 proc=P('/proc')/r['pid']
 if r['name'] in ['python','python3','bash','sh','node']:
  try:
   cwd=(proc/'cwd').resolve()
   if cwd.is_relative_to(root):
    names=[P(x.decode(errors='replace')).name for x in (proc/'cmdline').read_bytes().split(b'\0') if x]
    found=sorted(set(names)&scripts)
    if found:matched.append({**r,'project_scripts':found})
  except (OSError,ValueError):pass
 try:
  targets=[]
  for fd in (proc/'fd').iterdir():
   try:
    target=P(os.readlink(fd))
    if not target.is_absolute() or not target.is_relative_to(root):continue
    flags=next(l.split()[1] for l in (proc/'fdinfo'/fd.name).read_text().splitlines() if l.startswith('flags:'))
    if int(flags,8)&os.O_ACCMODE in [os.O_WRONLY,os.O_RDWR]:
     rel=target.relative_to(root)
     if any(x in {'.aws','.ssh','.codex','.agents','.git'} for x in rel.parts):targets.append('[excluded configuration path; contents not read]')
     else:targets.append(str(rel))
   except (OSError,ValueError,StopIteration):pass
  if targets and int(r['pid'])!=os.getpid():writers.append({**r,'open_writable_workspace_paths':sorted(set(targets))})
 except (OSError,PermissionError):denied+=1
result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'hostname':os.uname().nodename,'uid':os.getuid(),'visible_process_count':len(rows),'active_build_or_aligner_processes':[r for r in rows if r['name'] in build_names],'recognized_project_script_processes':matched,'processes_with_open_writable_workspace_files':writers,'process_fd_directories_unreadable':denied,'limitations':'Point-in-time read-only host snapshot. Open writable descriptors indicate potential writing, not guaranteed activity. Other users/processes may be inaccessible; future work is not predicted. No environment or file contents read; no task stopped; no shutdown/reboot.'}
with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
