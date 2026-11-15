# Primary evidence inventory and provenance

All coordinates are existing experimental structures, not AI predictions or newly generated proteins. The new work calculates observed contacts and reuses the frozen model/sequence data. Official coordinate/core-metadata responses are archived, with retrieval UTC, URL, bytes, SHA256 and available HTTP metadata in `provenance/source_receipts.json`. Public PDB archive coordinates are reusable under wwPDB policies: https://www.wwpdb.org/about/usage-policies . The project does not redistribute publisher article PDFs, third-party figures or model weights.

## Experimental coordinate sources — COMPLETED

| Source | Role | Version read from mmCIF | Coordinate bytes | Coordinate SHA256 |
|---|---|---|---:|---|
| [PDB 9BIF](https://www.rcsb.org/structure/9BIF), [official mmCIF](https://files.rcsb.org/download/9BIF.cif) | Primary human B11 Fab–OspC complex, assembly 1; 3.09 Å X-ray structure | 1.0, 2024-11-20 | 6,788,086 | `5b46c89e31b034591fcaff67d8286220e28240ec04d0142c0ba8bf02896eb325` |
| [PDB 7UIJ](https://www.rcsb.org/structure/7UIJ), [official mmCIF](https://files.rcsb.org/download/7UIJ.cif) | Secondary mouse B5 Fab–OspC complex, assembly 1; 2.701 Å X-ray structure | 1.3, 2024-11-20 | 1,714,403 | `7d2e247e4121a7ec4359815a31f2b72d9ef94dcb4ccbc473028ecac4e5f18986` |

RCSB entry metadata and polymer-entity records identify the OspC and Fab entities. Source descriptions and both label/author chain namespaces are preserved. The primary and secondary OspC entity sequence is exactly the same 164-residue Q07337 construct, positions 38–201. Version and resolution come from archive categories, not file timestamps. Last-modified headers alone do not establish structural revision or scientific provenance.

Official metadata endpoints used: `https://data.rcsb.org/rest/v1/core/entry/{PDB}` and `https://data.rcsb.org/rest/v1/core/polymer_entity/{PDB}/{entity}` for the specifically archived entry/entity IDs. No broad structure dataset or arbitrary archive was downloaded.

## Primary papers — source verified, not our experimental claims

1. Rudolph MJ et al. (2024). *Structure of a Human Monoclonal Antibody in Complex with Outer Surface Protein C of the Lyme Disease Spirochete, Borreliella burgdorferi.* J Immunol 213:1234–1243. [DOI](https://doi.org/10.4049/jimmunol.2400247), [PubMed PMID 39240158](https://pubmed.ncbi.nlm.nih.gov/39240158/). This is the primary citation attached to 9BIF. The published record and abstract identify human B11 and the Fab–OspC study. No claim of exact replication of every paper epitope table is made: our heavy-atom distance cutoff is an explicitly defined coordinate-derived endpoint. The [PMC11092446 record](https://pmc.ncbi.nlm.nih.gov/articles/PMC11092446/) is explicitly a **preprint**, not a substitute mislabeled as the final peer-reviewed article.
2. Rudolph MJ et al. (2023). *Structural Elucidation of a Protective B Cell Epitope on Outer Surface Protein C (OspC) of the Lyme Disease Spirochete, Borreliella burgdorferi.* mBio 14:e02981-22. [DOI](https://doi.org/10.1128/mbio.02981-22), [PMC10128040](https://pmc.ncbi.nlm.nih.gov/articles/PMC10128040/). This is the citation attached to 7UIJ. Its experimental functional context belongs to the authors; our recomputed contact labels do not newly demonstrate protection or functional necessity.
3. Vance DJ et al. (2025). *A type-specific B-cell epitope at the apex of outer surface protein C (OspC) of the Lyme disease spirochete, Borreliella burgdorferi.* Microbiol Spectr 13:e02883-24. [Primary article](https://journals.asm.org/doi/10.1128/spectrum.02883-24), [DOI](https://doi.org/10.1128/spectrum.02883-24), [PMC11960070](https://pmc.ncbi.nlm.nih.gov/articles/PMC11960070/). The source reports an HDX-supported region at OspC type-A positions 130–150. Published residue-identity anchors match frozen Q07337, allowing an individually mapped **regional** annotation. Regional membership does not establish an atom contact for every residue. It is not pooled with B11/B5 labels.

Bibliographic metadata were verified by exact DOI through Europe PMC and retained in `inputs/literature_bibliography.json`. Only selected bibliographic fields are archived, not a purported complete copy of publisher text. Coordinate-derived results in this experiment are independently computed from the archived official files.

## A source correction worth preserving — NOT RUN

An official later deposition, [PDB 9BX7](https://www.rcsb.org/structure/9BX7), is titled *Fab 8C1 in complex with OspCA peptide P20 (residues 131–150)* and was released 2025-08-27. Its citation is marked “To be published.” This is a separately identified **real peptide-complex deposition**, not an invented full-OspC complex, and not automatically the structure underlying the February 2025 HDX paper. Coordinates were **not retrieved or analyzed here**; no residue-level labels from it are claimed. A future check would need construct, antibody-form and numbering validation. The current 8C1 product remains literature-only.

## Reused project evidence — COMPLETED, unchanged

- Scientific commit `aafe818a20ea025370cf4b65145a9684e80aaaef`; local input aliases/hashes are in `provenance/reused_inputs.json`.
- Exact 6,305 ESM-2 scores, SHA256 `b27d926285a8dc338abceba953229089be4f35fcba7c166c1a922be146a6317f`, checkpoint `facebook/esm2_t6_8M_UR50D` revision `c731040fcd8d73dceaa04b0a8e6329b345b0f5df`. No ESM execution or weight retrieval in this sprint.
- Frozen Q07337 UniProt-derived record, original sequence SHA256 `8939ee76df09336cca51badd169a15d142bcd48b90b928cfcebc1ef733ac1d7e`. UniProt Consortium database data are CC BY 4.0: https://www.uniprot.org/help/license . Attribution, source URLs, retrieval and original record extraction provenance are preserved. The sequence was not edited.
- Existing [1GGQ](https://www.rcsb.org/structure/1GGQ) reference coordinates/mapping and earlier independently calculated homodimer contact/SASA. Their area calculation is not an antibody contact definition or physiological-accessibility measurement.
- The small CIF parser is copied unchanged from the project's prior scientific source. No new parsing library, statistical package, model, driver or environment was installed. New arithmetic uses existing NumPy/SciPy/Matplotlib; external packages are not vendored.
