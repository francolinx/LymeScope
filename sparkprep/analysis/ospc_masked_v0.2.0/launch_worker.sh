#!/bin/bash
# Prepared only. No downloads, installs or scheduler submission occur here.
set -euo pipefail
MODE=${1:?pilot, one or two required}
RANK=${2:?rank required}
case "$MODE" in pilot|one|two) ;; *) exit 2 ;; esac
case "$RANK" in 0|1) ;; *) exit 2 ;; esac
BASE=/project/lymescope-v0.2.0
CODE="$BASE/sparkprep/analysis/ospc_masked_v0.2.0"
APPROVAL="$BASE/approvals/$MODE.json"
test -r "$APPROVAL"
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 PYTHONDONTWRITEBYTECODE=1
export OMP_NUM_THREADS=2 CUBLAS_WORKSPACE_CONFIG=:4096:8
RUN_ID=$(python3 -c 'import json,re,sys; d=json.load(open(sys.argv[1])); r=d["run_id"]; assert d.get("approved") is True and re.fullmatch(r"[A-Za-z0-9_-]{1,64}",r); print(r)' "$APPROVAL")
ARGS=(--mode "$MODE" --rank "$RANK" --plan "$CODE/plans/workload.json"
      --approval "$APPROVAL" --output-dir "$BASE/runs/$RUN_ID"
      --model-dir "$BASE/models/esm2_t6_8M_UR50D/c731040fcd8d73dceaa04b0a8e6329b345b0f5df")
if [ "$MODE" != pilot ]; then
    # An explicit existing real-model pilot file, not a fixture or a regenerated result.
    ARGS+=(--pilot-receipt "$BASE/approved-pilot/pilot.json")
fi
python3 -B "$CODE/run_worker.py" "${ARGS[@]}"
