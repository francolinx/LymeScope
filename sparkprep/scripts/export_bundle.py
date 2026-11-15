import pathlib,json,hashlib,datetime,tarfile,csv,io
P=pathlib.Path;now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.load(open('source_manifest.json'))
# Independently validate deliverables before creating the archive.
def fasta(path):
 records={};acc=None
 for line in P(path).read_text().splitlines():
  if line.startswith('>'):
   acc=line[1:].split()[0]
   if '|' in acc:acc=acc.split('|')[1]
   assert acc not in records;records[acc]=''
  elif line:records[acc]+=line.strip()
 return records
panel=fasta('input_sequences.fasta');meta=list(csv.DictReader(open('sequence_metadata.tsv'),delimiter='\t'))
assert 20<=len(panel)<=40 and len(panel)==len(meta)==len(set(panel.values()))
assert set(panel)=={r['accession'] for r in meta}
for r in meta:
 assert r['sequence_sha256']==hashlib.sha256(panel[r['accession']].encode()).hexdigest()
 assert int(r['length'])==len(panel[r['accession']])
 assert 'annotated_fragment' not in r['quality_flags'] and 'uncertain_family_membership' not in r['quality_flags']
prot=fasta('source_data/proteome.fasta');anns=list(csv.DictReader(open('source_data/proteome_annotations.tsv'),delimiter='\t'))
assert len(prot)==len(anns)==json.load(open('source_data/proteome.json'))['proteinCount']
assert set(prot)=={r['Entry'] for r in anns}
for code in ['1GGQ','1G5Z']:
 assert P('reference_structures/'+code+'.cif').read_text().startswith('data_'+code)
 assert 'ATOM ' in P('reference_structures/'+code+'.cif').read_text()
 assert json.load(open('reference_structures/'+code+'.json'))['rcsb_id']==code
extra=[
('evidence/uniprot_license.json','https://rest.uniprot.org/help/license','UniProt license, CC BY 4.0 with patent/other-rights disclaimer'),
('evidence/1GGQ_europepmc.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:11230121%20AND%20SRC:MED&format=json','Primary bibliographic metadata; full text not downloaded; OA flag N'),
('evidence/1G5Z_europepmc.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:11139584%20AND%20SRC:MED&format=json&resultType=core','Primary bibliographic metadata; full text not downloaded'),
('evidence/ospc_epitope_bibliography.json','https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:10.1128/mbio.02981-22&format=json&resultType=core','Primary study bibliographic record; OA status and CC BY license'),
('evidence/PMC10128040.html','https://pmc.ncbi.nlm.nih.gov/articles/PMC10128040/?pdf=0','Permitted open-access primary article, CC BY 4.0. Authors/title/DOI in accompanying bibliographic record; retained HTML unmodified.')]
m['sources']=[s for s in m['sources'] if s['path'] not in {x[0] for x in extra}]
for path,url,desc in extra:
 p=P(path);m['sources'].append({'path':path,'url':url,'description':desc,'retrieved_utc':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),'status':'ok','bytes':p.stat().st_size,'sha256':digest(p)})
for s in m['sources']:
 if s['path'].startswith('source_data/') or 'uniprot' in s['path']:s['usage_restrictions']='UniProt copyrightable data CC BY 4.0; attribution required; patent/other rights may apply. See evidence/uniprot_license.json.'
 elif s['path'].startswith('reference_structures/'):s['usage_restrictions']='PDB archive CC0; RCSB API same except externally integrated annotations may carry source restrictions. Cite entry and primary study.'
 elif s['path'].endswith('PMC10128040.html'):s['usage_restrictions']='CC BY 4.0; attribute primary article authors, DOI 10.1128/mbio.02981-22, and license; no changes to archived HTML.'
 else:s.setdefault('usage_restrictions','Bibliographic/policy evidence retained with attribution and source URL; no blanket license for linked third-party material.')
 s['source_identifier']= {'source_data/proteome.json':'UP000001807','source_data/proteome.fasta':'UP000001807','source_data/proteome_annotations.tsv':'UP000001807'}.get(s['path'], '1GGQ' if '1GGQ' in s['path'] else '1G5Z' if '1G5Z' in s['path'] else 'PMC10128040 / DOI:10.1128/mbio.02981-22' if 'epitope' in s['path'] or 'PMC10128040' in s['path'] else s['url'])
m['retrieval_blockers']=[{'issue':'Sandbox DNS failures','detail':'curl exit 6: Could not resolve host (UniProt/RCSB); resolved by approved network execution. No credentials inspected.'},{'url':'https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10128040/fullTextXML','status':'failed','http_status':500,'retrieved_utc':datetime.datetime.fromtimestamp(P('evidence/PMC10128040.html').stat().st_mtime,datetime.timezone.utc).isoformat(),'fallback':'PMC HTML retrieved successfully; failed XML not included'}]
m['successful_public_download_bytes']=sum(s['bytes'] for s in m['sources'] if s['status']=='ok')
assert m['successful_public_download_bytes']<500000000
m['prepared_utc']=now;m['hash_policy']='SHA256 over raw file bytes. Derived artifacts listed separately. Manifest excludes its own hash; internal/export SHA256SUMS cover it and the archive respectively.'
files=[P(x) for x in ['runtime_inventory.json','input_sequences.fasta','sequence_metadata.tsv','data_quality_report.md','READY_FOR_CLUSTER.md']]
for folder in ['source_data','reference_structures','evidence','scripts']:
 files.extend(p for p in P(folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
files=sorted(files)
m['artifacts']=[{'path':str(p),'bytes':p.stat().st_size,'sha256':digest(p),'provenance':'retrieved' if any(s['path']==str(p) for s in m['sources']) else 'derived locally; see scripts and source records'} for p in files]
P('source_manifest.json').write_text(json.dumps(m,indent=2)+'\n');files.append(P('source_manifest.json'));files=sorted(files)
checks=''.join(f'{digest(p)}  {p}\n' for p in files)
P('exports/bundle_contents.sha256').write_text(checks)
archive=P('exports/lymescope_data_bundle.tar.gz')
with tarfile.open(archive,'w:gz') as tar:
 for p in files:tar.add(p,arcname='lymescope_data_bundle/'+str(p),recursive=False)
 data=checks.encode();ti=tarfile.TarInfo('lymescope_data_bundle/SHA256SUMS');ti.size=len(data);tar.addfile(ti,io.BytesIO(data))
P('exports/SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in [archive,P('exports/bundle_contents.sha256')]))
# Verify every archived payload against its recorded source hash, without extraction.
with tarfile.open(archive) as tar:
 for p in files:
  data=tar.extractfile('lymescope_data_bundle/'+str(p)).read();assert hashlib.sha256(data).hexdigest()==digest(p)
 assert tar.extractfile('lymescope_data_bundle/SHA256SUMS').read().decode()==checks
validation={'verified_utc':now,'proteome_fasta_count':len(prot),'proteome_table_rows':len(anns),'proteome_accession_sets_match':True,'panel_count':len(panel),'panel_sequences_distinct':True,'archived_files_checked':len(files),'archive_bytes':archive.stat().st_size,'archive_sha256':digest(archive),'public_download_bytes':m['successful_public_download_bytes']}
P('exports/validation.json').write_text(json.dumps(validation,indent=2)+'\n');P('exports/SHA256SUMS').write_text(''.join(f'{digest(p)}  {p.name}\n' for p in [archive,P('exports/bundle_contents.sha256'),P('exports/validation.json')]))
print(json.dumps(validation,indent=2))
