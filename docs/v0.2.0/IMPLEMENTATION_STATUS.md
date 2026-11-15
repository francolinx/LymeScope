# Incremental implementation status

> Current milestone: personal-Spark commit `aafe818a20ea025370cf4b65145a9684e80aaaef` is integrated into the existing feature branch. Its v2 adapter and original figures feed the demo. See [integration status](../../submission/SPARK_INTEGRATION.md). The pre-milestone status below is historical; personal-model NOT RUN statements are superseded.

Baseline preserved: `8058846c05d4dccd60117dd29ef784af43570418`. Work is isolated on `feature/ospc-masked-scoring-v0.2.0`; main and all tracked v0.1.0 inputs, outputs, manifests and viewer files remain unchanged. No model downloads, GPU runs, cluster calls, driver changes, package installs, repository recovery or backup work occurred.

## Implemented locally

- Masked-original-residue NLL scorer with lazy local-only model loading, token-offset/single-mask assertions, stable log probabilities, explicit float32/evaluation settings, per-position provenance, actual/successful forward counters and separate phase timings.
- Fixed-alignment leave-out aggregation using remaining-row coverage and cached per-sequence scores. Explicit raw metadata groups, common rank populations and average exact-tie handling; no significance/permutation test.
- Strict receipt ingestion and reference-map overlay, including exact task coverage, source/model/runtime identity, physical-node evidence and predeclared float tolerances. Fixture results cannot unlock real benchmarking.
- A locked workload manifest: 6,305 scored examples, 415 scoring forwards at batch size 16; two complete-sequence shards require 208/207 forwards. The full-coverage/observed/intersection column sets contain 202/162/159 columns.
- Separate offline demo overlay with annotated processing versus construct/coordinate coverage; checked 1GGQ assembly-1 A/B contact proxy; checked secondary 1G5Z correspondence. Proxy distances are not solvent/antibody accessibility. Frozen evidence was not edited.
- Initial submission/demo drafts retained, with the current package in `submission/`: one-pager, 4:30 narration plus 30-second buffer, sources, claim verification and checklist. Root README and six original GIF/PNG assets are added to the separate versioned presentation. Unrun-model placeholders remain explicit.

## Actual local checks

**23 masked-scoring/ingestion fixture tests + seven overlay data-contract tests + five presentation/media tests passed.** The 26 existing tests and JavaScript control fixtures also passed. Python syntax and all three HOLD workflow YAML files/shell scripts passed local checks using already-present dependencies. These do not validate actual ESM inference, scheduler compatibility, node availability or runtime throughput. Current checks: `submission/validation.json` and `submission/validation.log`.

Evidence: `sparkprep/analysis/ospc_masked_v0.2.0/results/offline-validation.json`, `offline-tests.log`, `workflow-static-validation.json`, and `runtime-availability.json`.

The normal scoped browser request returned **“The browser access host is unavailable.”** No alternate automation route was used. Actual overlay rendering and screenshots remain NOT VERIFIED. Open `demo/v0.2.0/index.html` locally for the presenter check; the original viewer and saved tables remain the fallback.

## Prepared, not executed

The real-model pilot, one-node benchmark and two-node benchmark are prepared in versioned code and `.HOLD.fz` files. The pilot compares eight actual input positions in singleton/batched/repeated-batched passes and independent normalization: 14 pilot forwards, 24 examples and one separate warm-up. The final contract adds sequence hashes, maximum length, memory, failed/successful positions, relative deviations and exact Spark30 versus Spark29/Spark30 checks. Placement remains HOLD pending authorized scheduler validation. No timing or speedup result exists.

## Remaining blockers and one next request

The exact pinned ESM-2 model is absent from the inspected project, default and configured caches. Python 3.14.4, standalone 3.13.7 and Anaconda 3.13.5 lack torch, transformers, safetensors and tokenizers. NumPy 2.1.3 exists in Anaconda and huggingface_hub 2.1.1 in Python 3.14.4. No GPU probe or current remote-runtime inspection was performed. Historical event PyTorch evidence does not establish current model-library readiness.

Next bounded request: stage only the five pinned model/config/tokenizer files, expected 31,385,380 bytes, hard cap 100 MiB, in the ignored project-local cache. See `sparkprep/analysis/ospc_masked_v0.2.0/STAGING_REQUEST.md`. No package install, alternative checkpoint, GPU run, cluster submission or weight upload is included. Runtime dependency preparation is a separate unresolved issue; staging does not authorize inference.

The final Claude reference was supplied and reconciled incrementally in `CONTRACT.md`. Gemini feedback was incorporated as targeted amendments. Organizer-confirmed eligibility/exception details and personal-statement approval remain open; no organizer was contacted. Repository metadata was rechecked as public without changing visibility. No main push or submission was performed.
