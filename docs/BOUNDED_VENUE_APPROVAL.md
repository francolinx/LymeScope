# One bounded request for the morning venue trial

**Prepared request, not granted authorization. No event action was performed.** The completed offline submission remains usable if this request is declined or a gate fails.

Approve Team 15 access and the existing project volume for **one staged correctness-and-timing trial on assigned physical Spark29 and Spark30**, ending before **10:30 AM Central, November 15, 2026**, under these bounds:

| Item | Exact bound |
|---|---|
| Scientific source | `aafe818a20ea025370cf4b65145a9684e80aaaef`, unchanged 30-sequence package; about 6,443,982 tracked bytes |
| Model | Existing six-file `facebook/esm2_t6_8M_UR50D` safetensors cache; revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df` |
| Transfer | Reuse the personal-Spark tar, 31,395,840 bytes; SHA256 `4e24f435628bb2c3b1a1a27664807c5d8c41ce7a94d3c2031b0f96363cb5d9ab`. At most **100 MiB of project/model payload total** across both destination copies; record actual bytes and hashes |
| Destination | Approved project-local cache and new output directories only; no global environment changes or GitHub weight upload |
| Runtime | Existing verified event image/runtime, starting from the historical PyTorch candidate. Read versions and verify dependencies; **stop and list missing dependencies instead of installing** |
| Pilot | One Q07337 pilot on each node: 210 scientific masks and 27 scoring calls each; three warm-up and three validation calls per pilot |
| One-node trial | Spark30: all 6,305 masks / 805 scoring calls |
| Two-node trial | Concurrent Spark29 shard 0: 3,156 / 403; Spark30 shard 1: 3,149 / 402 |
| Total inference allowance | **Five processes**, 13,030 scientific masked examples and 1,664 scoring forwards; 15 warm-up forwards / 120 examples and six validation calls / examples separate. No retries, repeats or additional checkpoint without review |
| Process limits | External timeout 120 s each; allocated GPU <2 GiB, reserved <4 GiB, RSS <16 GiB; ≥8 GiB free GPU-visible memory after loading |
| Method | Same batch 8, float32, eager attention, TF32 disabled, no autocast, full-vocabulary original-residue NLL |
| Acceptance | Exact frozen identities and task coverage; `abs(candidate-reference) <= 1e-4 + 1e-5*abs(reference)`; report absolute/relative deviations; matching model/runtime receipts |
| Timing/attribution | Scheduler evidence of actual Spark29/Spark30 assignment, overlapping shard execution, separate load/compute/transfer/startup/queue/merge and coordinator makespan |

The two runtime probes and existing test suite precede model execution and are recorded separately from model-call counts. Existing services and security checks stay intact. A failed access, staging, dependency, placement or pilot gate stops dependent work. No new model download, package installation, driver repair, larger workload, sequence design, force-push, hosting change or main integration is included.

This authorization would permit only the bounded venue workflow described in the [morning runbook](MORNING_RUNBOOK.md). Main/Pages publication and the actual organizer submission remain separate decisions. A numerical pass or two worker hostnames alone is insufficient for a scientific speedup claim.
