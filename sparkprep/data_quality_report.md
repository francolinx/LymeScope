# LymeScope data quality report

Prepared 2026-11-14T23:30:21.331028+00:00. All runtime observations belong to PERSONAL Spark spark-6771 only.

## Proteome verification

UniProt UP000001807 identifies Borreliella burgdorferi B31 (taxon 224326), assembly GCA_000008685.2. API reports 1291 proteins; downloaded canonical FASTA contains 1291 unique accessions and annotation table contains 1291 rows. Accession sets match exactly. One isoform is reported separately by UniProt; this canonical export does not include extra isoforms.

## Provisional natural OspC panel

Selected 30 distinct amino-acid sequences from the first 500 UniProt search results (not an exhaustive population sample). 59 entries passed the selection filters. 3 reviewed distinct entries are prioritized (one of the four reviewed source records is an exact sequence duplicate); remaining entries are chosen by species round-robin, with supplied strains then accession ordering within species. Reference-comment strain lists and their reference numbers are preserved even for merged records. Selection preserves native database sequences without trimming, mutations or synthetic designs. No OspC type is inferred. PF01441 supports a shared family and is insufficient alone; an explicit OspC name/gene is also required. This is annotation-supported family assignment, not an independent HMM or phylogenetic validation. Natural provenance is based on biological organism and nucleotide-source annotations, not an independent audit of the original isolate. Reviewed Q0SL36 is an exact sequence duplicate of P0DW54 despite their differing organism labels; both raw records are preserved, and only the first is retained in this sequence-distinct panel.

Full pool QC flags: {'multiple_reference_strains': 91, 'strain_unresolved_or_missing': 121, 'strain_not_supplied_in_organism_field': 495, 'exact_duplicate_sequence': 18, 'annotated_fragment': 434, 'outside_190_230_length_window': 321, 'noncanonical_residues': 8, 'uncertain_family_membership': 7}.

Selected panel unresolved/missing strain: 5. Selected annotated fragments: 0. Selected exact duplicates: 0. Selected uncertain family: 0 under the stated annotation rule. Length window 190–230 aa is a conservative heuristic, not proof of completeness. Strains are copied from the organism field or a single distinct STRAIN reference comment. Multiple reference strains remain explicitly listed with reference numbers and are not collapsed to an invented strain; unresolved fields stay blank. No strains inferred from species, sequence, or structure. Raw records retain additional source-reference context. Candidate exact duplicates refer to the first occurrence in the retrieved pool; excluded records and reasons are in source_data/candidate_quality.tsv.

## Pre-existing structural references

1GGQ: B31 OspC, X-ray, 2.51 Å, 174 residues per deposited polymer, four polymer instances; 648 modeled and 48 unmodeled polymer residues in aggregate. 1G5Z: N40 OspC by entry title, X-ray, 2.51 Å, 164-residue polymer, one asymmetric-unit polymer, 164 modeled and zero unmodeled residues within its deposited construct. Neither is a full-length native lipidated protein. N40 is supplied in the 1G5Z title, while its CIF source-strain field is unknown. Historical CIF database mapping O31117 should not be silently replaced by current web mappings; preserve and align before assigning residue numbers. The complete CIF construct, sequence differences, source, refinement, and assembly fields are extracted into reference_summary.json. Mutation field '?' means unspecified, not proven absence of mutations. Suitable as fold and assembly references after sequence alignment; not independent validation of new predictions.

## Evidence and reuse

Primary bibliographic records come directly from UniProt and RCSB, with DOI/PubMed identifiers as supplied; duplicate citations are intentionally retained with source context. UniProt data: CC BY 4.0, subject to its patent/other-rights disclaimer. PDB archive coordinates: CC0; RCSB API data follow archive terms except integrated external resources. Policies saved in evidence/. Primary study DOI 10.1128/mbio.02981-22 is verified open access CC BY 4.0; PMC HTML includes its license. Other primary papers are retained as bibliographic records only, without assuming their full texts are redistributable.

## Runtime limitations and blockers

Hostname/user verified locally. nvidia-smi could not communicate with NVIDIA driver; no /dev/nvidia* nodes visible. Existing torch imports succeed in cnh-venv (2.15.0+cu132), ftvenv and forge/.venv (2.14.1+cu130); all CUDA availability checks false and tiny GPU tensor attempts fail with 'No CUDA GPUs are available'. No successful GPU computation or performance timing. Docker image listing fails with socket permission denied. Targeted standard Hugging Face/Torch cache checks show no named ESM/Prot/Fold model cache; other model directory names do not establish complete usable weights. No package, model, container downloads or runtime changes performed.

Sandbox DNS initially blocked downloads; approved network access succeeded. Europe PMC fullTextXML request returned HTTP 500; PMC HTML fallback succeeded. Download provenance, sizes, hashes and restrictions are in source_manifest.json. No event cluster access or speedup claims.
