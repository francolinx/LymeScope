# LymeScope — Frontier result, November 15, 2026

**Scientific acceptance: PASS.** One completed post-hoc exploratory whole-sequence partition reproduced all **6,305 original-residue NLL scores**, with **zero maximum absolute and relative deviation** from the frozen reference and original event single-node output. No duplicate or missing tasks. Original evidence and its 25 readback artifacts remain unchanged.

## Three measured configurations

| Configuration | Spark29 masks / forwards / warm seconds | Spark30 masks / forwards / warm seconds | Slowest warm scoring | Prepared-input coordinator |
|---|---:|---:|---:|---:|
| Original single node | idle | 6,305 / 805 / 30.224 | 30.224 s | 52.111 s |
| Original equal-count two nodes | 3,156 / 403 / 42.397 | 3,149 / 402 / 16.233 | 42.397 s | 67.982 s |
| Exploratory throughput-informed two nodes | 1,691 / 216 / 22.707 | 4,614 / 589 / 22.871 | 22.871 s | 51.952 s |

The exploratory prepared-input phase was **23.6% shorter than the original two-node phase** (1.309× ratio). The maximum worker warm-scoring duration fell by **46.1%**. Against the original single-node phase, the difference was only **0.158 seconds / 0.3%**: describe this as **near parity**, not demonstrated acceleration. One exploratory observation does not estimate timing variance or general scaling.

Common model/runtime preparation and final object export are excluded from all coordinator-phase comparisons. The exploratory workflow itself took **128.643 seconds**, including its common setup and final export. The original 224.698-second workflow also included a correctness pilot and BOTH benchmark phases; those whole-workflow totals are unequal work and **must not be used as a speedup comparison**. Neither compute-only nor prepared-input timings establish cold-launch end-to-end acceleration.

## What changed, and what did not

The fixed original panel, alignment, frozen scorer file, six checkpoint files, tokenization, batch 8, float32/eager, disabled TF32/no autocast, and fixed tolerance were preserved. The adapter selected deterministic whole-sequence subsets in memory without rewriting input files or scientific code. Spark29 received eight sequences and 216 calls; Spark30 received the other 22 sequences and 589 calls. The assignment was declared before launch; all task identities were independently verified after readback.

This partition was selected after observing the original result. It is an **exploratory optimization**, not a new scheduler algorithm or a pre-registered performance result. Both workers also had a new read-only diagnostic sampler at about 1 Hz; any sampling overhead is a comparison caveat. Each subset TSV uses shard=0 within its selected sequence set; [ASSIGNMENT.json](ASSIGNMENT.json) defines the actual physical partition. Local CRLF and executed LF assignment files have different hashes but identical normalized text and parsed content; both hashes are recorded in [RESULT.json](RESULT.json).

## Asymmetry: observation versus cause

The original nearly equal workloads ran at about 9.51 versus 24.76 scoring forwards/second. Original synchronized forward/log-softmax block sums were 38.654 versus 14.759 seconds. The block includes CPU launch and GPU synchronization; it is not isolated kernel time. Similar model loading (2.278 versus 2.187 seconds), matching runtime versions and similar allocated memory do not explain the disparity. Original logs contain no contemporaneous power/thermal/clock trace.

During the exploratory scoring intervals, Spark29's 21 samples reported **507 MHz SM clock**, 41°C and median 6.53 W. Spark30's 22 samples reported **2,509–2,535 MHz**, 44–47°C and median 24.925 W. Both reported P0, four PyTorch threads, the same CPU affinity indices and 2,808,000 kHz for allowed CPU cores. This is measured current-run clock/power asymmetry. Its cause—and whether the same state caused the earlier slowdown—remains **UNRESOLVED**. Power limits, memory clocks and GPU memory-used fields were unavailable; no claim about throttling, administrator settings, contention or thermal cause is justified. No settings were altered.

## Execution, concurrency and persistence

- Original workflow: `79319e56-f368-4eba-8cae-7c646737b9fc`.
- Exploratory workflow: `3f511bf2-b3b7-4346-b5d8-9a56cef5fc53`, finished 11:09:02 AM Central, all stages finished; three job exits were zero.
- Two GPU jobs: `704470a3-00dc-51bc-adda-8b00dec5daa8` and `e60b1700-0c69-5d9c-9d7e-73b8b9c3fcfd`; exact scheduler-to-machine mapping is in [WORKFLOW_RECEIPT.json](WORKFLOW_RECEIPT.json).
- Fuzzball physical-node metadata and known assigned GPU UUIDs identify distinct Spark29 and Spark30.
- Recorded scoring overlap: **22.707 seconds**. Host UTC epochs show overlap; independent clock calibration was not performed. Durations use process monotonic timers.
- Existing staff-confirmed VAST-backed project storage supplied immutable science and persisted fresh result shards. Eighteen exported artifacts totaling **1,551,439 bytes** passed object digest, byte count and independent laptop SHA256 readback. Each worker fsynced and reread its results; merged output SHA256: `ea043d2df33841260d322caebe2a8939750f0df9818920653008b872ffbfee84`.
- Model weights stayed in the separate private ephemeral runtime, outside the project volume and release. No VAST throughput or NCCL/RDMA claim is made.
- Source inventory reconciliation remains **106 regular files = 104 scientific payload files + two manifest files**, with no missing payload.

Two preceding exploratory workflow preparations failed **before any masks or scoring forwards**: one rejected a changed transitive dependency; a second encountered Windows-style separators in an input path. Their receipts remain preserved. Exact baseline dependency/wheel locks and wrapper path normalization corrected those preparation issues; the model/runtime versions and scientific method did not change. Only the final workflow completed exploratory science. See [PREPARATION_ATTEMPTS.json](PREPARATION_ATTEMPTS.json).

## What this demonstrates

In this small OspC workload, equal task counts did not produce equal worker times. A throughput-informed whole-sequence assignment brought the two workers to about 22.7 and 22.9 seconds and reduced the observed two-node coordinator phase. Startup, loading, synchronization and validation still consumed enough time that the result was near the original single-node duration. Numerical reproducibility succeeded independently of performance scaling. This is one engineering observation, not a general scaling law or a new biological finding.

The biological evidence remains 30 natural sequences, 6,305 original-residue NLL measurements, explicit experimental mapping and a negative B11 controlled diagnostic. Neither this computing result nor masked predictability establishes antigenicity, protection, antibody accessibility or clinical utility.

## Review and submission

The [offline comparison](../../demo/venue-frontier-v1/index.html) is generated from the saved accepted data. Its numbers, local links and source assets are checked; browser rendering is **UNVERIFIED** because the supported Computer Use route could not enforce its URL policy. No bypass was attempted. The existing six-animation README and original scientific viewer were preserved.

Publication and organizer submission require separate project-lead approval. Historical reports retain their original dates/statuses. The original verified submission PDF/ZIP remain fallback artifacts.

## Public metadata scope

Raw technical receipts remain privately preserved. Public workflow metadata retains completed workflow/jobs; operational staging paths, host fields and GPU UUIDs are omitted. Scientific task TSVs, score values, timing values and numerical acceptance are unchanged. Original readback hashes identify original bytes; [PUBLICATION_PROVENANCE.json](PUBLICATION_PROVENANCE.json) records sanitized public hashes separately.
