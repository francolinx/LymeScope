# Frontier result in one minute

**COMPLETED: exact experimental mapping. NOT ESTABLISHED: a new epitope predictor.**

- Official 9BIF/B11 and 7UIJ/B5 OspC constructs exactly match all 164 residues of frozen Q07337 positions 38–201. Atom/chain/numbering identities, assembly operations and missing residues are checked; all observed distance labels are independently reproduced.
- B11: 32 observed construct union-contact positions at 4.5 Å; 31 contacts among 152 strict eligible unique alignment sites. B5: 27 observed construct positions, 25 among its own 152 strict eligible sites.
- The predeclared agreement/AA/geometry baseline has blocked Brier 0.168634. Adding frozen signed discordance worsens it to 0.174022 (**+0.00538833**); AUROC changes 0.620634 → 0.616369. Absolute discordance alone has AUROC 0.49840. The negative incremental direction persists at both distance sensitivities and in related B5 diagnostics.
- This is one correlated, selected antigen/reference context and a coordinate-derived observed-contact endpoint, not external functional validation. Missing Fab loops, residue chemistry, sampling, construct/copy differences and the small ridge diagnostic limit conclusions.
- The 8C1 product is a source-verified regional HDX annotation, not fabricated atom contacts. The later real 9BX7 peptide-complex deposition is noted but NOT RUN here.
- Zero new model inference or weights; existing 6,305 scores reused exactly. 26 frontier tests and the 16 existing v0.2.1 experiment tests pass. A clean offline rebuild reproduces all 5,472 declared OOF predictions exactly in this runtime.

Start with `LAPTOP_NEXT_HANDOFF.md`; use `results/FRONTIER_EVIDENCE.json` or `EXPERIMENTAL_MAPPING.tsv`, and the original `results/FRONTIER_EXPERIMENT.png`/`.svg`. Full controls, coefficients, predictions, source hashes and limitations are included. The stable v0.2.1 fallback, frozen outputs and laptop submission remain separately owned and unchanged by this work.
