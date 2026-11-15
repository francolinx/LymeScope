"""Read-only scoped host status; no environments or unrelated arguments recorded."""
import pathlib,subprocess,json,datetime,argparse
p=argparse.ArgumentParser();p.add_argument('--output',required=True,type=pathlib.Path);args=p.parse_args()
r=subprocess.run(['ps','-eo','pid=,ppid=,comm=,stat=,etime='],capture_output=True,text=True,check=True)
rows=[dict(zip(['pid','ppid','name','state','elapsed'],parts)) for line in r.stdout.splitlines() if len(parts:=line.split(None,4))==5]
names={'make','gmake','gcc','cc1','cc1plus','collect2','ld','mafft','tbfast','disttbfast','pairlocalalign','dvtditr','dndpre','splittbfast'}
active=[r for r in rows if r['name'] in names];workspace=pathlib.Path(__file__).resolve().parent.parent;tasks=[]
recognized_names={'run_alignment_analysis.py','finalize_export.py','save_partial.py','prepare.py','download.py','inventory.py','freeze_early_handoff.py','start_ospc_analysis.py','build_view.py','reproduce_checkpoint_analysis.py'}
for r in rows:
 if r['name'] not in ['python','python3','bash','sh','node']:continue
 try:
  proc=pathlib.Path('/proc')/r['pid'];cwd=(proc/'cwd').resolve()
  if not cwd.is_relative_to(workspace):continue
  # Only whitelisted project script basenames leave this check.
  args_raw=(proc/'cmdline').read_bytes().split(b'\0');names_found=[pathlib.Path(x.decode(errors='replace')).name for x in args_raw if x and pathlib.Path(x.decode(errors='replace')).name in recognized_names]
  if names_found:tasks.append({**r,'recognized_project_scripts':names_found})
 except (OSError,ValueError):pass
result={'checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'visible_process_count':len(rows),'active_build_or_aligner_processes':active,'recognized_project_script_processes':tasks,'method':'Host process names plus whitelisted project script basenames for processes with workspace cwd. No environment or unrelated command arguments retained.','limitations':'Point-in-time snapshot; no processes killed; no shutdown/reboot.'}
with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
