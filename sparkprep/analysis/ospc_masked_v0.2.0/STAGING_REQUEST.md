# One bounded request: stage the pinned model only

Approval requested, **not granted by the implementation task**: retrieve exactly the five allowlisted files below from `facebook/esm2_t6_8M_UR50D`, revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`, into the existing repository's ignored project-local location:

`models/esm2_t6_8M_UR50D/c731040fcd8d73dceaa04b0a8e6329b345b0f5df/`

| File | Expected bytes |
|---|---:|
| model.safetensors | 31,384,292 |
| config.json | 775 |
| special_tokens_map.json | 125 |
| tokenizer_config.json | 95 |
| vocab.txt | 93 |
| Total | 31,385,380 |

**Hard cap: 100 MiB (104,857,600 bytes) total.** Stop on changed revision, unexpected/missing files, cap exceedance or a failed identity check. No `.bin`, `.pt`, TensorFlow checkpoint, alternative format/model, recursive repository download or fallback download. No inference, GPU/cluster work, driver changes, global configuration, package installation or GitHub weight upload is included in this request.

Weight SHA256: `24c5fa474c48f3b754b86efe752d5f189d2bcd88190fa2270fc92b2ef3034189`. Small-file pinned Git blob identities are in `model_lock.json`; verify them and record raw-file SHA256 for all five files plus revision, retrieval time and total bytes. `runtime.verify_assets()` implements local verification without inference or network access. Existing `models/` ignore protection remains in effect.

## Missing dependencies — separate from this request

Local inspection found no **torch, transformers, safetensors or tokenizers** in Python 3.14.4, standalone Python 3.13.7 or Anaconda Python 3.13.5. NumPy 2.1.3 is present only in Anaconda; huggingface_hub 2.1.1 is present only in Python 3.14.4. No additional Conda environments or project virtual environments were found in the inspected locations. Imports/inference compatibility have not been tested because the required runtime is absent.

The exact model was absent from the project model/cache directories, the user's default Hugging Face model cache, and the configured `HF_HOME` cache path. This is a scoped laptop observation, not proof about every disk or remote host. Current event-node and personal-Spark runtimes were **NOT INSPECTED** because cluster/remote calls are outside this instruction. Historical runtime records are not treated as current availability.

Dependency installation requires a separate explicit environment-specific request after selecting a compatible existing runtime. Do not assume model staging alone permits a pilot. The real-model pilot and one/two-node workflows remain prepared but unexecuted; the CPU baseline remains available.
