from pathlib import Path
import json,hashlib,datetime,tarfile
root=Path(__file__).resolve().parent.parent;workspace=root.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
run=json.loads((root/'alignment_run.json').read_text());summary=json.loads((root/'summary.json').read_text());tool=json.loads((root/'tool_provenance.json').read_text());viewer=json.loads((root/'viewer_data.json').read_text())
full=[c for c in viewer['columns'] if c['contributing_sequences']==30]
method=f'''# OspC alignment comparison v0.1.0

Completed on PERSONAL Spark spark-6771. This continues the existing prealignment task; earlier partial files and its prealignment export are preserved. Scientific results are in results_v0.1.0, separate from the frozen inputs. No Fuzzball or event-cluster access, archive transfer, model downloads or GPU-model work occurred.

## Actual findings

30 accessions, 218 aligned columns. 202 columns have standard residues from all 30 sequences; 16 columns contain gaps. No ambiguous/missing residues or undefined columns occur in this actual alignment. 76 columns are identical at full coverage. There are 82 columns with modal fraction 1 among their observed residues, including six with incomplete coverage. The mean modal fraction is {summary['mean_modal_fraction']:.6f} across all columns and {sum(c['modal_fraction'] for c in full)/len(full):.6f} across fully covered columns. These are unweighted descriptive means, not accuracy or protection measures. At alignment columns 154 and 173, only one sequence contributes, so a modal fraction of 1 is not evidence of broad conservation.

The panel has 30 distinct sequences/accessions, 25 distinct nonblank supplied strain labels, and five unresolved/missing primary strain fields. Six records contain multiple reference-strain comments. Strain-label count is not a count of distinct biological strains. All 10 supplied organism labels/taxon IDs, including strain-specific labels, are preserved in panel_scope.json and inputs/sequence_metadata.tsv; the convenience panel is not universally representative. Use the phrase "conserved within this analyzed panel."

## Aligner provenance and execution

MAFFT {tool['version']}; official without-extensions source URL: {tool['official_source_url']}. Source archive {tool['source_archive_bytes']} bytes (under the approved 10 MB cap), SHA256 {tool['source_archive_sha256']}. Download date and installed-file hashes are in tool_provenance.json.

Before compilation, the core Makefile PREFIX was set to `{tool['installation_prefix']}`. LIBDIR, BINDIR and MANDIR resolve under that prefix. The install dry run was inspected. Source, objects/build files, wrappers, native helper binaries, manual pages and build temporary files remain under that workspace prefix. Built with existing gcc and `make -j2`; installed with `make install`; no sudo, system packages, global PATH or shell-profile changes. Original/configured Makefiles, build/install logs and source license are included under tool_provenance/.

Version verified by invoking the absolute executable path. A three-sequence, 20-aa identical-input sanity alignment passed with exact identifiers/sequences preserved. The panel command was:

```text
{' '.join(run['command'])}
```

L-INS-i (`--localpair --maxiterate 1000`), forced amino acids, one CPU thread, input order preserved. Other scoring parameters use MAFFT 7.525 defaults; stderr records the actual strategy and defaults. MAFFT_BINARIES was unset only for the subprocess, and TMPDIR/MAFFT_TMPDIR pointed under tools/mafft-7.525/tmp. Elapsed wall time {run['elapsed_seconds']:.6f} seconds is this small PERSONAL Spark CPU alignment only, not a GPU or event-cluster benchmark.

Exact frozen archive SHA256: {run['frozen_archive_sha256']}.
Exact input FASTA SHA256: {run['input_fasta_sha256']}.
Exact aligned FASTA SHA256: {run['output_aligned_fasta_sha256']}.
All actual included accessions and the full command are in alignment_run.json. sequence_validation.tsv records per-accession hashes: removing '-' from every aligned sequence exactly reproduces its original input and identifiers/order are preserved.

## Transparent baseline

For every 1-based alignment column, conservation_coverage.tsv reports the most frequent observed standard amino acid, all tied modes, modal fraction, number of contributing sequences, gap count, ambiguous/missing count, total panel count, and coverage. Only ACDEFGHIKLMNPQRSTVWY contribute. '-' is a gap; any other symbol is ambiguous/missing. Modal fraction = modal count / contributing standard residues. Coverage = contributing standard residues / all 30 sequences. Ties display the alphabetically first residue with all tied residues retained separately. If there are no standard observations, the modal residue and fraction are null (blank in TSV), not zero or fully conserved; coverage remains 0 for a nonempty panel. The actual panel has no undefined columns, but tests exercise that case.

No weighting, phylogenetic correction, statistical significance, antigen ranking or protection inference is supplied. Conservation depends on this alignment and sampling; alignability/structural accessibility and signal-peptide processing are not modeled. Full-length source sequences are not trimmed. Low coverage can create apparently high modal fractions; the local view shows coverage separately.

## First reference and explicit residue mapping

Coordinates are a PRE-EXISTING experimental X-ray structure, PDB 1GGQ, chain A (label and author), model 1, 2.51 Å; not project-generated folding. Deposited native positions 38–210 match all 173 residues of panel accession Q07337 exactly. The construct's extra initiating methionine (label_seq_id 1; author position 37) is not assigned to the panel. Native residue 38 and residues 201–210 lack coordinates. Of 174 total construct residues, 162 have positive-occupancy Cα atoms, spanning author/native positions 39–200. No insertion codes occur in this chain.

The CIF polymer scheme, sequence mapping, atom records and unobserved-residue category were cross-checked for residue identity, author chain/number and insertion code. No residue number was guessed from a simple array index. native position -> Q07337 alignment column -> construct residue -> observed CA supplies the mapping. alignment_to_structure.tsv has one row for each of 218 columns: 162 observed/scored, 11 unobserved/unscored, 37 outside the construct/unscored, and eight reference-gap/unscored. A separate structure_residues.tsv/JSON includes every construct residue, including the initiating methionine. Scores are null/blank for unobserved or unmapped residues. Coverage accompanies every scored residue. Experimental B-factors are not read as prediction-confidence scores. The display uses only an illustrative rotatable Cα trace of chain A, not a complete molecular surface or oligomer model.

## Investigation of the earlier 1G5Z empty list

The `[]` output referred to the optional `_pdbx_unobs_or_zero_occ_residues` category, absent in this CIF. It did not mean empty coordinates. Independently checked 164 polymer-scheme residues and 164 positive-occupancy Cα positions in chain A/model 1, labels 1–164. Its full construct exactly matches Q44717 native positions 40–203. Historical CIF accession O31117 is retained as supplied. No second-reference score map was invented; 1GGQ is the first scored reference. Details are saved in secondary_reference_check.json.

## Files, validation and local use

Open index.html directly in a local browser: all measured data and viewer code are embedded, with no server/CDN/network dependency. It shows separate conservation/coverage plots, the full alignment, selectable column details, reference mapping, unscored positions, supplied metadata, and a rotatable experimental Cα trace. The headless Chrome check populated all alignment columns and metadata successfully; JavaScript syntax and embedded data were independently checked. Initial browser validation was blocked by the sandbox's local socket restriction, then succeeded through approved execution with a fresh workspace-only profile.

Machine-readable display data: viewer_data.json. Primary scientific tables: aligned.fasta, conservation_coverage.tsv, alignment_to_structure.tsv, structure_residues.tsv and sequence_validation.tsv. summary.json, alignment_run.json, panel_scope.json and source_manifest under inputs retain provenance/scope. All file-byte hashes, including copied frozen inputs and source, are in analysis_manifest.json; SHA256SUMS additionally covers that manifest. The manifest does not hash itself. The original frozen archive is excluded from the analysis archive and remains unchanged.

Eleven tests passed: identical/variable/tied columns, gaps, ambiguous/missing residues, undefined columns, insertion-code and unobserved mapping fixtures, mismatch rejection, actual frozen reference consistency, actual round-trip/identifier preservation, full saved statistics, saved TSV/JSON agreement and the secondary-reference category check. Run `python3 -m unittest -v test_baseline test_results` from source/. No extra packages are required. Scientific calculations can be independently reproduced from saved aligned.fasta and the frozen CIFs using baseline.py/cif_reader.py. run_alignment_analysis.py records the original workspace orchestration and assumes that original directory layout; it refuses to overwrite a completed run. The viewer can be rebuilt with `python3 source/build_view.py` without realigning.

Input usage terms and primary citations are retained under inputs/evidence and inputs/source_manifest.json. UniProt data require CC BY 4.0 attribution with the supplied other-rights disclaimer; PDB archive coordinates are CC0. Cite the experimental entry and its primary paper. Bibliographic records do not grant blanket redistribution rights to linked full text.

## Bounded next GPU experiment — approval required; not launched

After restoring personal GPU visibility through a separately authorized process, use Meta ESM-2 8M embeddings on these 30 sequences, batch size one, no training/gradients, maximum five minutes. Compare per-column embedding dispersion at full-coverage sites with this alignment's modal fractions; this could distinguish variable sites that retain similar learned representations. It is exploratory and does not establish protective efficacy, antigen safety or structure accuracy. Requires explicit approval for the model/tokenizer/config download (100 MB cap) and GPU execution; no package installation or fallback workloads. Official model record: https://huggingface.co/facebook/esm2_t6_8M_UR50D. No such download or GPU run was authorized or performed.
'''
(root/'METHOD_AND_LIMITATIONS.md').write_text(method)
(root/'OPEN_RESULTS.md').write_text('''# Open the OspC comparison locally

Open `index.html` directly in a local browser. All data and scripts are embedded; no server is needed. The local view shows measured alignment/conservation/coverage and the mapped pre-existing experimental reference.

To check this directory's contents, run `sha256sum -c SHA256SUMS` here. From the archive's parent directory, verify the adjacent `.tar.gz.sha256` file before extracting into a new directory. The archive unpacks under `lymescope_ospc_analysis_v0.1.0/`.

See METHOD_AND_LIMITATIONS.md for actual results, exact input/output hashes, MAFFT command/version, reference mapping and caveats. Inputs and usage policies are included. No archive transfer has occurred. This analysis contains no event-cluster measurements.
''')
archive=workspace/'exports/lymescope_ospc_analysis_v0.1.0.tar.gz';assert not archive.exists()
files=[p for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name not in ['analysis_manifest.json','SHA256SUMS']]
# Exclusion applies only to our top-level manifests; preserve the frozen source manifest.
files=[p for p in sorted(root.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p not in [root/'analysis_manifest.json',root/'SHA256SUMS']]
manifest={'version':'v0.1.0','status':'completed alignment/conservation baseline and first-reference mapping','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'PERSONAL Spark only','frozen_input_archive_sha256':run['frozen_archive_sha256'],'input_fasta_sha256':run['input_fasta_sha256'],'aligned_fasta_sha256':run['output_aligned_fasta_sha256'],'tool_version':run['tool_version'],'summary':summary,'files':[{'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in files],'hash_policy':'All payload bytes excluding this manifest/SHA256SUMS; SHA256SUMS covers payload and manifest. Archive has an external checksum.'}
(root/'analysis_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');files.append(root/'analysis_manifest.json')
(root/'SHA256SUMS').write_text(''.join(sha(p)+'  '+str(p.relative_to(root))+'\n' for p in sorted(files)));files.append(root/'SHA256SUMS')
with archive.open('xb') as out:
 with tarfile.open(fileobj=out,mode='w:gz') as t:
  for p in sorted(files):t.add(p,arcname='lymescope_ospc_analysis_v0.1.0/'+str(p.relative_to(root)),recursive=False)
with tarfile.open(archive) as t:
 for line in t.extractfile('lymescope_ospc_analysis_v0.1.0/SHA256SUMS').read().decode().splitlines():
  h,p=line.split('  ',1);assert hashlib.sha256(t.extractfile('lymescope_ospc_analysis_v0.1.0/'+p).read()).hexdigest()==h
frozen=workspace/'exports/lymescope_ospc_handoff_v0.1.0.tar.gz';assert sha(frozen)==run['frozen_archive_sha256']
h=sha(archive)
with Path(str(archive)+'.sha256').open('x') as f:f.write(h+'  '+archive.name+'\n')
receipt={'version':'v0.1.0','status':'completed scientific alignment baseline; not transferred','path':str(archive),'bytes':archive.stat().st_size,'sha256':h,'frozen_input_unchanged':True,'archive_payload_hash_checks':'all passed','analysis_directory':str(root),'tests_passed':11}
with Path(str(archive)+'.receipt.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
with (root.parent/'CONTINUATION_RESULTS.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt,indent=2))
