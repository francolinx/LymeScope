import pathlib,tarfile,json,hashlib,csv,datetime
P=pathlib.Path;archive=P('exports/lymescope_ospc_handoff_v0.1.0.tar.gz');out=P('analysis/ospc_comparison_v0.1.0');out.mkdir(exist_ok=False);inp=out/'frozen_inputs';inp.mkdir()
h=hashlib.sha256(archive.read_bytes()).hexdigest();assert h=='1ce0fff5a1b8d7d24ed6d70844f798484ac81231bcf2350ddcd8f6551ec1fa0f'
with tarfile.open(archive) as t:
 names=t.getnames();mp=[x for x in names if x.endswith('/source_manifest.json')];assert len(mp)==1
 prefix=mp[0].rsplit('/',1)[0]+'/';manifest=json.load(t.extractfile(mp[0]))
 for a in manifest['artifacts']:
  path=P(a['path']);assert not path.is_absolute() and '..' not in path.parts
  b=t.extractfile(prefix+a['path']).read();assert len(b)==a['bytes'] and hashlib.sha256(b).hexdigest()==a['sha256']
  dest=inp/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b)
 (inp/'source_manifest.json').write_bytes(t.extractfile(mp[0]).read())
 def actual(basename):
  matches=[a['path'] for a in manifest['artifacts'] if P(a['path']).name==basename];assert len(matches)==1;return matches[0]
 paths={k:actual(k) for k in ['input_sequences.fasta','sequence_metadata.tsv','1GGQ.cif','1G5Z.cif','1GGQ.json','1G5Z.json','reference_summary.json']}
rows=list(csv.DictReader(open(inp/paths['sequence_metadata.tsv']),delimiter='\t'))
from collections import Counter
scope={'sequences':len(rows),'unique_accessions':len({r['accession'] for r in rows}),'organism_labels':dict(Counter(r['organism'] for r in rows)),'taxon_ids':dict(Counter(r['taxon_id'] for r in rows)),'distinct_nonblank_strain_labels':len({r['strain'] for r in rows if r['strain']}),'blank_strain_fields':sum(not r['strain'] for r in rows),'multiple_reference_strain_records':sum('multiple_reference_strains' in r['quality_flags'] for r in rows),'interpretation':'Sequence-distinct convenience panel; strain labels are not a count of distinct biological strains; missing/merged reference strains retained; not universally representative.'}
(out/'panel_scope.json').write_text(json.dumps(scope,indent=2)+'\n')
(out/'analysis_state.json').write_text(json.dumps({'status':'awaiting_alignment_dependency_approval','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_archive':str(archive.resolve()),'frozen_archive_sha256':h,'manifest_paths':paths,'aligner_search':'No mafft, muscle, clustalo, kalign or t_coffee found on PATH; no MAFFT in checked standard/local bin and known venv locations.','missing_dependency':'Established multiple-sequence aligner; proposed isolated MAFFT 7.525 source install pending user approval.','alignment_generated':False},indent=2)+'\n')
print(json.dumps(scope,indent=2))
