"""Read package metadata and exact model-cache locations. No GPU/model imports."""
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path
from core import HERE, write_new

PROBE = """
import importlib.metadata as m, importlib.util as u, json, sys
names=['torch','transformers','safetensors','tokenizers','numpy','huggingface_hub']
result={}
for name in names:
    present=u.find_spec(name) is not None
    try: version=m.version(name) if present else None
    except m.PackageNotFoundError: version='module found without distribution metadata'
    result[name]={'installed':present,'version':version}
print(json.dumps({'python':sys.executable,'version':sys.version,'packages':result}))
"""


def inspect():
    repo = HERE.parents[2]
    home = Path.home()
    interpreters = [Path(sys.executable), home / "AppData/Local/Programs/Python/Python313/python.exe", home / "anaconda3/python.exe"]
    for env in (repo / ".venv", repo / "venv"):
        interpreters.append(env / "Scripts/python.exe")
    conda_envs = home / "anaconda3/envs"
    if conda_envs.is_dir():
        interpreters.extend(p / "python.exe" for p in conda_envs.iterdir() if p.is_dir())
    runtimes = []
    seen = set()
    for p in interpreters:
        if not p.is_file() or str(p.resolve()) in seen:
            continue
        seen.add(str(p.resolve()))
        probe = subprocess.run([str(p), "-B", "-c", PROBE], text=True, capture_output=True, timeout=30)
        runtimes.append(json.loads(probe.stdout) if probe.returncode == 0 else {"python": str(p), "probe_error": probe.stderr})
    lock = json.loads((HERE / "model_lock.json").read_text())
    name = "models--facebook--esm2_t6_8M_UR50D"
    candidates = [repo / lock["project_local_cache"], repo / ".cache/huggingface/hub" / name,
                  home / ".cache/huggingface/hub" / name]
    for key in ("HF_HOME", "HF_HUB_CACHE", "TRANSFORMERS_CACHE"):
        if os.environ.get(key):
            base = Path(os.environ[key])
            candidates.append(base / "hub" / name if key == "HF_HOME" else base / name)
    return {"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "scope": "Known local interpreters, project environments and exact requested-model cache directories only",
            "runtimes": runtimes, "model_cache_locations": [{"path": str(p), "exists": p.exists()} for p in candidates],
            "model_id": lock["model_id"], "required_revision": lock["revision"],
            "inference_import_tests": "NOT_RUN", "gpu_availability": "NOT_PROBED", "remote_runtime": "NOT_INSPECTED",
            "model_downloads": 0, "package_installs": 0, "gpu_runs": 0, "cluster_calls": 0,
            "historical_runtime_records": "Not used as proof of current availability"}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    result = inspect()
    write_new(args.output, result)
    print(json.dumps(result, indent=2))
