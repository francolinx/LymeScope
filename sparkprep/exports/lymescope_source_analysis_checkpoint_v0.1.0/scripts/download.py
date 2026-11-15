import subprocess,json,pathlib,datetime,hashlib,urllib.parse
jobs=[('source_data/proteome.json','https://rest.uniprot.org/proteomes/UP000001807','UniProt proteome metadata'),('source_data/proteome.fasta','https://rest.uniprot.org/uniprotkb/stream?'+urllib.parse.urlencode({'query':'proteome:UP000001807','format':'fasta'}),'UniProt proteome canonical FASTA'),('source_data/proteome_annotations.tsv','https://rest.uniprot.org/uniprotkb/stream?'+urllib.parse.urlencode({'query':'proteome:UP000001807','format':'tsv','fields':'accession,id,protein_name,gene_names,organism_name,organism_id,length,protein_existence,sequence_version'}),'UniProt identifier/annotation table'),('source_data/ospc_candidates.json','https://rest.uniprot.org/uniprotkb/search?'+urllib.parse.urlencode({'query':'(gene:ospC OR protein_name:"outer surface protein C") AND taxonomy_id:64895','format':'json','size':500}),'Provisional OspC candidate pool; first API page, not exhaustive')]
for x in ['1GGQ','1G5Z']:
 jobs.extend([(f'reference_structures/{x}.cif',f'https://files.rcsb.org/download/{x}.cif','Pre-existing experimental reference coordinates'),(f'reference_structures/{x}.json',f'https://data.rcsb.org/rest/v1/core/entry/{x}','RCSB entry metadata and primary citation')])
jobs.extend([('evidence/uniprot_license.html','https://www.uniprot.org/help/license','UniProt usage terms'),('evidence/rcsb_usage.html','https://www.rcsb.org/pages/policies','RCSB usage policies')])
records=[]
for dest,url,desc in jobs:
 p=pathlib.Path(dest);stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
 if dest=='source_data/proteome.json' and p.exists():code=0;err='Retrieved in initial curl request'
 else:
  v=subprocess.run(['curl','-fL','--retry','1','--max-time','90','--max-filesize','20000000',url,'-o',dest],capture_output=True,text=True);code=v.returncode;err=v.stderr[-1200:]
 rec={'path':dest,'url':url,'description':desc,'retrieved_utc':stamp,'curl_returncode':code,'status':'ok' if code==0 else 'failed','diagnostic':err if code else None}
 if p.exists():rec.update(bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest())
 records.append(rec);print(dest,code,rec.get('bytes'),flush=True)
 pathlib.Path('source_manifest.json').write_text(json.dumps({'scope':'public data only; PERSONAL Spark','download_limit_bytes':500000000,'max_concurrent_downloads':1,'sources':records},indent=2))
