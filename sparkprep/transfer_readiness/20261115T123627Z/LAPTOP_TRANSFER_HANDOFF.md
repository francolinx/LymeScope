# Model transfer readiness — 2026-11-15 12:37 UTC

Status: model archive VERIFIED; both scientific archives VERIFIED; secure transfer route BLOCKED from Spark; laptop copy NOT VERIFIED.

All checks were read-only hash/archive checks. No inference, downloads, event-node access, authentication changes or host changes occurred. Scientific evidence is unchanged at Spark commit `82fb8b53018ba4012ccebf02a29efa87b892f6ed`, including the negative frontier diagnostic. See `INTEGRITY.json` for every model-file SHA256 and both scientific archive hashes.

## Model identity

Model: `facebook/esm2_t6_8M_UR50D`; immutable revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`.

Archive on Spark:

```text
/home/darkstar90/lymescope-sparkprep/.model-cache/transfer/esm2_t6_8M_UR50D_c731040fcd8d73dceaa04b0a8e6329b345b0f5df_six_files.tar
```

Expected bytes: **31395840**. SHA256:

```text
4e24f435628bb2c3b1a1a27664807c5d8c41ce7a94d3c2031b0f96363cb5d9ab
```

Exactly six safe flat regular-file members: README.md, config.json, model.safetensors, special_tokens_map.json, tokenizer_config.json, vocab.txt. Their total payload is 31387085 bytes; the tar adds framing/padding. All six contents match the original pinned download receipt. The tar has no embedded revision marker; identity is established by that receipt and exact content hashes.

## Transfer status and conditional laptop pull

Local device inventory reports both known Windows peers offline. Spark has no configured trusted laptop SSH destination and no active SSH connection. An available SSH agent does not establish laptop access. No network login was attempted. This does not rule out an already trusted laptop-to-Spark LAN route invisible from Spark.

Laptop Codex: use the following ONLY if `darkstar90@spark-6771` is your existing authorized, trusted SSH endpoint. Do not add host keys, prompt for credentials, change networking or substitute unfamiliar access methods. If the command fails, stop and retain the Spark originals. This procedure has NOT been executed here.

PowerShell, outside the Git repository:

```powershell
$ErrorActionPreference = 'Stop'
$name = 'esm2_t6_8M_UR50D_c731040fcd8d73dceaa04b0a8e6329b345b0f5df_six_files.tar'
$cache = Join-Path $env:USERPROFILE 'LymeScope-model-cache'
New-Item -ItemType Directory -Path $cache -Force | Out-Null
$dest = Join-Path $cache $name
$partial = "$dest.partial"
$expected = '4e24f435628bb2c3b1a1a27664807c5d8c41ce7a94d3c2031b0f96363cb5d9ab'
function Assert-Archive($path) {
    if ((Get-Item -LiteralPath $path).Length -ne 31395840) { throw 'Archive size mismatch; preserve file and stop.' }
    if ((Get-FileHash -LiteralPath $path -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expected) { throw 'Archive SHA256 mismatch; preserve file and stop.' }
}
if (Test-Path -LiteralPath $dest) {
    Assert-Archive $dest
} else {
    if (Test-Path -LiteralPath $partial) { throw 'Existing partial file; preserve it and stop.' }
    scp -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=10 "darkstar90@spark-6771:/home/darkstar90/lymescope-sparkprep/.model-cache/transfer/$name" $partial
    if ($LASTEXITCODE -ne 0) { throw 'SCP failed; no authentication/network changes authorized.' }
    Assert-Archive $partial
    Move-Item -LiteralPath $partial -Destination $dest
    Assert-Archive $dest
}
Get-Item -LiteralPath $dest | Select-Object FullName,Length
Get-FileHash -LiteralPath $dest -Algorithm SHA256
```

After success, record the destination, measured size and SHA256 as the laptop receipt. Do not call the copy verified until those checks pass. Never place weights in Git or publish the archive publicly.

After verifying the outer archive, extract into a NEW empty local model directory outside Git. Use the existing offline hash-only verifier from the scientific package:

```powershell
python C:\Users\franc\Projects\LymeScope\sparkprep\experiments\stretch_v0.2.0_20261115T072916Z\src\verify_package.py --model-dir <extracted-model-directory>
```

Do not execute the angle-bracket placeholder literally. This verifier performs hashes only, not inference or networking. It requires the complete scientific experiment directory from the pinned Spark commit.

## Spark recheck commands

```bash
archive='/home/darkstar90/lymescope-sparkprep/.model-cache/transfer/esm2_t6_8M_UR50D_c731040fcd8d73dceaa04b0a8e6329b345b0f5df_six_files.tar'
stat -c '%s' "$archive"
sha256sum "$archive"
tar -tf "$archive"
```

Scientific packages remain under `/home/darkstar90/lymescope-sparkprep/experiments/exports/`:

- `lymescope_stretch_v0.2.1_full_panel_20261115T075845Z.tar.gz`: 2340578 bytes; SHA256 `e24097ab102ff7a7b571477983a5d47fff80ee0b9ab19203e0e0f1e810e95968`. All 104 internally manifested files verified.
- `lymescope_frontier_v0.3.0_20261115T091901Z.tar.gz`: 3495094 bytes; SHA256 `843af025c1c2c3ee1ed9bdd2b6c5b89605d4cdb9bd2814a523f2a4dbd8968304`. All 83 internally manifested files verified. The negative diagnostic result is preserved, not replaced by a positive claim.

## Event-runtime portability concerns — preparation only

The event image has NOT been inspected or validated. Personal-Spark recorded runtime used Python 3.12.3, Linux aarch64, PyTorch 2.14.1+cu130, CUDA 13.0, Transformers 5.20.0, safetensors 0.8.0 and tokenizers 0.23.3. The event image must already support ARM64/GB10 CUDA execution, ESM masked-LM/tokenizer loading and safetensors. Carrying the tar on Windows needs no GPU runtime.

Use the saved VENUE_CONTRACT.md and runtime specification: offline local model loading, FP32 eager attention, no TF32/autocast, eval/inference mode, batch size 8. Record actual event versions; after venue access is separately authorized, validate the saved Q07337 pilot before a full run, with the contract's numerical tolerance `abs(error) <= 1e-4 + 1e-5 * abs(reference)`. Separate cold/startup/loading and warm timing. No installation or event execution is authorized by this readiness check.
