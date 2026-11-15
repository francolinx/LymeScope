# Frozen early OspC handoff v0.1.0

Frozen 2026-11-14T23:34:55.660659+00:00 on PERSONAL Spark spark-6771. This version must never be silently overwritten. No transfer has occurred. All files remain on this Linux host.

Ready: 30 sequence-distinct, unmodified, natural-source UniProt OspC sequences (207–214 aa), accession/organism/strain metadata, source records, usage policies and experimental reference coordinates 1GGQ/1G5Z. FASTA accessions, lengths and sequence SHA256 values agree with metadata. No annotated fragments, exact duplicates or uncertain family assignments under the stated annotation rule are selected. Family support requires an OspC name/gene plus PF01441; no independent HMM/phylogeny was run. Natural-source status follows database organism/nucleotide-source annotation and was not independently audited against isolates.

Selection: first 500 UniProt search results, exact sequence deduplication, canonical amino acids, length window 190–230 aa, no annotated fragments, reviewed entries prioritized, then species round-robin with supplied strain and accession ordering. This is a provisional convenience panel, not an exhaustive or frequency-representative panel. Raw selected records preserve sequence versions and reference-comment strain evidence. Q0SL36 was excluded as an exact sequence duplicate of P0DW54 despite differing organism labels.

Strains: 5 of 30 have blank unresolved/missing primary strain fields. Multiple reference strains remain listed with reference numbers and are not collapsed into an invented strain. Sequence metadata flags remain authoritative.

Pre-existing references, not project-generated structures: both are 2.51 Å X-ray OspC structures. 1GGQ is B31, a 174-residue construct including an added initiating methionine and native residues 38–210; four asymmetric-unit protein instances, 48 unmodeled polymer residues in aggregate. 1G5Z is N40 by entry title, a 164-residue construct, one asymmetric-unit protein instance; its source-strain CIF field is unknown and its historical database mapping is O31117. Neither represents full-length native lipidated OspC. Align sequences and inspect biological-assembly operators before residue comparisons. Mutation field '?' is unspecified. Detailed mappings, refinement values and assembly definitions are in reference_summary.json.

Explicit omissions / incomplete items:
- Full B31 catalog and annotation table are omitted from this compact early bundle; they were already retrieved separately and validated at 1,291 matching accessions. They are not a prerequisite for using this panel.
- The full 500-record candidate response and full candidate exclusion table are omitted; selected raw records and upstream response URL/hash are retained.
- Complete literature collection and article full texts are omitted. Primary bibliographic records and reference-structure citations are included. No complete evidence review is claimed.
- Independent family validation, OspC typing, mature-protein trimming, alignments, new predictions and model outputs are not supplied.
- No GPU validation result, model weights, containers or environment setup is included. Personal Spark CUDA was unavailable in the earlier inventory; no event-cluster measurement is included.

Use: transfer this archive yourself through an authorized channel. In the archive's parent directory run `sha256sum -c lymescope_ospc_handoff_v0.1.0.tar.gz.sha256`. Extract into an empty directory, enter `lymescope_ospc_handoff_v0.1.0`, and run `sha256sum -c SHA256SUMS`. Join analyses by FASTA accession. Respect UniProt CC BY 4.0 attribution and its other-rights disclaimer; PDB archive coordinates are CC0, with attribution to the entries and primary studies. RCSB API integrated annotations may have external-source restrictions. Bibliographic records do not grant permission to redistribute linked article full texts.
