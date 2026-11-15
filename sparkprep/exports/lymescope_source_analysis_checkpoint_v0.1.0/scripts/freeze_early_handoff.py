import pathlib,json,csv,hashlib,datetime,shutil,tarfile
P=pathlib.Path
version='v0.1.0';name='lymescope_ospc_handoff_'+version
root=P('exports')/name;archive=P('exports')/(name+'.tar.gz')
assert not root.exists() and not archive.exists(),'Frozen version already exists; choose a new version.'
metadata=list(csv.DictReader(open('sequence_metadata.tsv'),delimiter='\t'))
seqs={};current=None
for line in P('input_sequences.fasta').read_text().splitlines():
 if line.startswith('>'):current=line[1:].split()[0];assert current not in seqs;seqs[current]=''
 elif line:seqs[current]+=line
assert len(seqs)==len(metadata)==30 and len(set(seqs.values()))==30
for r in metadata:
 assert hashlib.sha256(seqs[r['accession']].encode()).hexdigest()==r['sequence_sha256']
 assert int(r['length'])==len(seqs[r['accession']])
 assert not any(flag in r['quality_flags'] for flag in ['annotated_fragment','uncertain_family_membership','exact_duplicate_sequence'])
root.mkdir();(root/'evidence').mkdir();(root/'source_data').mkdir()
paths=['input_sequences.fasta','sequence_metadata.tsv','reference_structures/1GGQ.cif','reference_structures/1G5Z.cif','reference_structures/1GGQ.json','reference_structures/1G5Z.json','reference_structures/reference_summary.json','evidence/uniprot_license.json','evidence/rcsb_usage.html','evidence/primary_bibliographic_records.json','evidence/1GGQ_europepmc.json','evidence/1G5Z_europepmc.json']
for f in paths:
 dest=root/f;dest.parent.mkdir(exist_ok=True,parents=True);shutil.copyfile(f,dest)
ids=set(seqs);pool=json.load(open('source_data/ospc_candidates.json'))['results'];selected=[r for r in pool if r['primaryAccession'] in ids]
assert len(selected)==30
(root/'source_data/selected_uniprot_records.json').write_text(json.dumps({'results':selected,'provenance':'Unmodified selected record objects extracted from the original 500-result UniProt response; original response hash and URL retained in source_manifest.json.'},indent=2)+'\n')
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
report=f'''# Frozen early OspC handoff {version}

Frozen {stamp} on PERSONAL Spark spark-6771. This version must never be silently overwritten. No transfer has occurred. All files remain on this Linux host.

Ready: 30 sequence-distinct, unmodified, natural-source UniProt OspC sequences (207–214 aa), accession/organism/strain metadata, source records, usage policies and experimental reference coordinates 1GGQ/1G5Z. FASTA accessions, lengths and sequence SHA256 values agree with metadata. No annotated fragments, exact duplicates or uncertain family assignments under the stated annotation rule are selected. Family support requires an OspC name/gene plus PF01441; no independent HMM/phylogeny was run. Natural-source status follows database organism/nucleotide-source annotation and was not independently audited against isolates.

Selection: first 500 UniProt search results, exact sequence deduplication, canonical amino acids, length window 190–230 aa, no annotated fragments, reviewed entries prioritized, then species round-robin with supplied strain and accession ordering. This is a provisional convenience panel, not an exhaustive or frequency-representative panel. Raw selected records preserve sequence versions and reference-comment strain evidence. Q0SL36 was excluded as an exact sequence duplicate of P0DW54 despite differing organism labels.

Strains: {sum(not r['strain'] for r in metadata)} of 30 have blank unresolved/missing primary strain fields. Multiple reference strains remain listed with reference numbers and are not collapsed into an invented strain. Sequence metadata flags remain authoritative.

Pre-existing references, not project-generated structures: both are 2.51 Å X-ray OspC structures. 1GGQ is B31, a 174-residue construct including an added initiating methionine and native residues 38–210; four asymmetric-unit protein instances, 48 unmodeled polymer residues in aggregate. 1G5Z is N40 by entry title, a 164-residue construct, one asymmetric-unit protein instance; its source-strain CIF field is unknown and its historical database mapping is O31117. Neither represents full-length native lipidated OspC. Align sequences and inspect biological-assembly operators before residue comparisons. Mutation field '?' is unspecified. Detailed mappings, refinement values and assembly definitions are in reference_summary.json.

Explicit omissions / incomplete items:
- Full B31 catalog and annotation table are omitted from this compact early bundle; they were already retrieved separately and validated at 1,291 matching accessions. They are not a prerequisite for using this panel.
- The full 500-record candidate response and full candidate exclusion table are omitted; selected raw records and upstream response URL/hash are retained.
- Complete literature collection and article full texts are omitted. Primary bibliographic records and reference-structure citations are included. No complete evidence review is claimed.
- Independent family validation, OspC typing, mature-protein trimming, alignments, new predictions and model outputs are not supplied.
- No GPU validation result, model weights, containers or environment setup is included. Personal Spark CUDA was unavailable in the earlier inventory; no event-cluster measurement is included.

Use: transfer this archive yourself through an authorized channel. In the archive's parent directory run `sha256sum -c {name}.tar.gz.sha256`. Extract into an empty directory, enter `{name}`, and run `sha256sum -c SHA256SUMS`. Join analyses by FASTA accession. Respect UniProt CC BY 4.0 attribution and its other-rights disclaimer; PDB archive coordinates are CC0, with attribution to the entries and primary studies. RCSB API integrated annotations may have external-source restrictions. Bibliographic records do not grant permission to redistribute linked article full texts.
'''
(root/'READY_FOR_CLUSTER.md').write_text(report)
upstream=json.load(open('source_manifest.json'))
kept=[]
for s in upstream['sources']:
 if (root/s['path']).is_file():kept.append(dict(s,bundled=True))
 elif s['path']=='source_data/ospc_candidates.json':kept.append(dict(s,bundled=False,role='upstream response; selected record objects bundled as source_data/selected_uniprot_records.json'))
manifest={'version':version,'frozen_utc':stamp,'scope':'EARLY DATA HANDOFF; PERSONAL Spark only; no transfer performed','panel_count':len(metadata),'sources':kept,'derived_records':{'path':'source_data/selected_uniprot_records.json','upstream_path':'source_data/ospc_candidates.json','selection_accessions':sorted(ids)},'omissions':'See READY_FOR_CLUSTER.md explicit omissions section','artifacts':[],'hash_policy':'SHA256 over file bytes; SHA256SUMS covers manifest and all payloads. Outer checksum covers frozen archive.'}
for p in sorted(root.rglob('*')):
 if p.is_file():manifest['artifacts'].append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(root/'source_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(root/'SHA256SUMS').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(root))+'\n' for p in sorted(root.rglob('*')) if p.is_file()))
with archive.open('xb') as out:
 with tarfile.open(fileobj=out,mode='w:gz') as tar:tar.add(root,arcname=name)
with tarfile.open(archive) as tar:
 checks=tar.extractfile(name+'/SHA256SUMS').read().decode()
 for line in checks.splitlines():
  h,f=line.split('  ',1);assert hashlib.sha256(tar.extractfile(name+'/'+f).read()).hexdigest()==h
h=hashlib.sha256(archive.read_bytes()).hexdigest();checksum=P(str(archive)+'.sha256')
with checksum.open('x') as f:f.write(h+'  '+archive.name+'\n')
receipt={'version':version,'frozen_utc':stamp,'path':str(archive.resolve()),'bytes':archive.stat().st_size,'sha256':h,'archive_payload_checks':'all passed','transfer_status':'NOT TRANSFERRED; local export only','policy':'Never overwrite this version; subsequent changes require a new version.'}
with (P('exports')/(name+'.receipt.json')).open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
print(json.dumps(receipt,indent=2))
