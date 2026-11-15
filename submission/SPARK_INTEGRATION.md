# Personal-Spark milestone integration

The existing clean feature branch at `36ee4d9a0cd07b5980b4ab1e4007ce291edec1ac` was merged with the verified remote `feat/ospc-esm2-spark-pilot` commit `aafe818a20ea025370cf4b65145a9684e80aaaef`. Both histories are preserved. Work remains on `feature/ospc-masked-scoring-v0.2.0`; no main push, event call, model download or inference rerun occurred.

The four requested handoff files were read at the exact commit. The complete committed experiment is imported unchanged, including its v0.2.1 release receipt, current v2 aggregate and original scientific figures. The full scientific archive and six-file model transfer tar remain on the personal Spark; their presence on the laptop or event nodes is not assumed.

## Integrated result

- The existing [demo](../demo/v0.2.0/index.html) consumes the published typed JSON through a validating adapter. It retains the original coverage/mapping/reference controls and frozen viewer link.
- Original scientific PNG/SVG figures appear before the earlier illustrations. No new illustration or scientific result was generated.
- All 218 columns retain observed-residue counts, masked-original-residue NLL and eligibility. Thirty sequence summaries explicitly score all original positions 1..L. Contact geometry and calculated SASA stay separate from agreement/NLL; unknown values remain null. Switching reference mappings never relabels primary 1GGQ values as 1G5Z.
- Measured: 6,305 masks / 805 scoring forwards at batch 8; three separate warm-up calls / 24 examples; 9.909294 s warm scoring. Full-panel agreement/predictability rho 0.134696 uses F=202. The 239 overlapping perturbations are descriptive sensitivity, not significance or confidence intervals.
- The previous batch-16 scorer, plans and assets remain preserved. The task animation is removed from the current selector because it is not the new venue protocol.

## Validation and limitations

**33 available Python tests passed**: 15 adapter/overlay, 13 published CPU science and five presentation/media/link tests. Offline JavaScript checks also passed for every displayed column NLL, sequence rows, navigation and null/false/zero states. The exact venue task specification passed offline count/assignment checks. See [current validation](spark-integration-validation.json) and [log](spark-integration-validation.log). These checks are not model inference. The published **16-test personal-Spark receipt** is preserved separately.

On this Windows laptop, **13 published CPU science tests passed**. The analytic-sphere test initially failed to import Unix `resource`; this is recorded as unavailable locally, without editing scientific source. Two PyTorch tests are NOT RUN because torch is absent. Available numpy/scipy do not remove the Unix-module blocker. No packages were installed and no compatibility stub was used.

The browser request returned **“The browser access host is unavailable.”** File generation, data readback, figure inspection and offline JS checks do not establish browser launch or rendering. No browser screenshot exists for this integration. Presenter checklist: [DEMO_SCRIPT.md](DEMO_SCRIPT.md). The frozen viewer and scientific PNG/SVG files remain the fallback.

## Venue and submission

[Venue staging/trial handoff](../workflows/ospc-spark-v0.2.1/VENUE_HANDOFF.md) and [exact task specification](../workflows/ospc-spark-v0.2.1/trial.HOLD.json) reuse the published scorer and batch-8 inputs. They do not claim scheduler validation. Blockers: bounded access/transfer/run authorization, existing model tar transport, current matching runtime, physical Spark30 versus Spark29/Spark30 placement, and passing venue pilots. No matched event scientific timing or speedup exists.

The [one-page draft](ONE_PAGER.md), [five-minute script](DEMO_SCRIPT.md), README and [claims](CLAIM_VERIFICATION.md) now use measured personal-Spark evidence with exact provenance. Content is prepared; final browser rehearsal, organizer eligibility/submission-route confirmation, personal-statement approval and publication/submission remain open. No project license is invented. Original historical validation and publication receipts are preserved.
