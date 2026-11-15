import json,csv,re,hashlib,pathlib,datetime,collections,shlex
P=pathlib.Path; now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
def write_tsv(path,rows):
 with open(path,'w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
es=json.load(open('source_data/ospc_candidates.json'))['results']; rows=[]; seen={};eligible=[]
for e in es:
 a=e['primaryAccession'];s=e.get('sequence',{}).get('value','');o=e.get('organism',{}).get('scientificName','');d=e.get('proteinDescription',{});name=d.get('recommendedName',{}).get('fullName',{}).get('value') or next(iter(d.get('submissionNames',[{}])),{}).get('fullName',{}).get('value','')
 genes=[g.get('geneName',{}).get('value','') for g in e.get('genes',[])];pf=[x['id'] for x in e.get('uniProtKBCrossReferences',[]) if x['database']=='Pfam'];strain=re.search(r'\(strain ([^)]+)\)',o)
 refstrains=[{'reference_number':ref.get('referenceNumber'),'strain':c['value']} for ref in e.get('references',[]) for c in ref.get('referenceComments',[]) if c.get('type')=='STRAIN']
 refvalues=sorted({x['strain'] for x in refstrains})
 strain_value=strain.group(1) if strain else refvalues[0] if len(refvalues)==1 else ''
 strain_provenance='UniProt organism scientificName' if strain else 'UniProt referenceComments STRAIN (single distinct value)' if len(refvalues)==1 else 'multiple reference strains; see strain_reference_comments' if refvalues else 'not supplied'
 flags=[]
 if len(refvalues)>1:flags.append('multiple_reference_strains')
 if not strain_value:flags.append('strain_unresolved_or_missing')
 if 'fragment'  in str(d).lower():flags.append('annotated_fragment')
 if not 190<=len(s)<=230:flags.append('outside_190_230_length_window')
 if set(s)-set('ACDEFGHIKLMNPQRSTVWY'):flags.append('noncanonical_residues')
 if not strain:flags.append('strain_not_supplied_in_organism_field')
 if not o:flags.append('missing_organism')
 family=('outer surface protein c' in name.lower() or 'ospc' in [x.lower() for x in genes]) and 'PF01441' in pf
 if not family:flags.append('uncertain_family_membership')
 if re.search('synthetic|mutant|engineered',name+' '+o,re.I):flags.append('possible_engineered_source')
 dup=seen.get(s,'');seen.setdefault(s,a)
 if dup:flags.append('exact_duplicate_sequence')
 r={'accession':a,'organism':o,'taxon_id':e.get('organism',{}).get('taxonId',''),'strain':strain_value, 'strain_provenance':strain_provenance,'strain_reference_comments':json.dumps(refstrains,separators=(',',':')),'protein_name':name,'genes':';'.join(genes),'length':len(s),'reviewed':'Swiss-Prot' in e['entryType'],'source_url':'https://www.uniprot.org/uniprotkb/'+a,'retrieved_utc':now,'sequence_sha256':sha(s.encode()),'duplicate_of':dup,'family_support':'name/gene OspC + Pfam PF01441' if family else 'uncertain','quality_flags':';'.join(flags),'selected':False,'selection_criteria':'natural UniProt record; named OspC + PF01441; no annotated fragment; 190-230 aa; canonical residues; exact sequence deduplicated; reviewed then supplied strain then accession; species round-robin'}
 rows.append(r)
 if s and family and not any(f in flags for f in ['annotated_fragment','outside_190_230_length_window','noncanonical_residues','missing_organism','uncertain_family_membership','possible_engineered_source','exact_duplicate_sequence']):eligible.append((e,r))
eligible.sort(key=lambda x:(not x[1]['reviewed'],not bool(x[1]['strain']),x[1]['accession']))
# Preserve reviewed sequences, then round-robin across species within remaining pool.
selected=[x for x in eligible if x[1]['reviewed']];groups=collections.defaultdict(list)
for x in eligible:
 if not x[1]['reviewed']:groups[x[1]['organism'].split(' (')[0]].append(x)
while len(selected)<30 and any(groups.values()):
 for k in sorted(groups):
  if groups[k] and len(selected)<30:selected.append(groups[k].pop(0))
assert 20<=len(selected)<=40
for e,r in selected:r['selected']=True
write_tsv('source_data/candidate_quality.tsv',rows);write_tsv('sequence_metadata.tsv',[r for e,r in selected])
with open('input_sequences.fasta','w') as f:
 for e,r in selected:
  s=e['sequence']['value'];f.write('>'+r['accession']+' '+r['organism']+' | natural OspC provisional panel\n');f.write('\n'.join(s[i:i+80] for i in range(0,len(s),80))+'\n')
assert len({e['sequence']['value'] for e,r in selected})==len(selected)
proteome=json.load(open('source_data/proteome.json'));fa=open('source_data/proteome.fasta').read();ids=[line.split('|')[1] for line in fa.splitlines() if line.startswith('>')];table=list(csv.DictReader(open('source_data/proteome_annotations.tsv'),delimiter='\t'))
assert len(ids)==len(set(ids))==len(table)==proteome['proteinCount'];assert set(ids)=={r['Entry'] for r in table}
# Minimal mmCIF tokenizer: semicolon multiline values and shell-style quoted tokens.
def cif_tokens(path):
 lines=iter(open(path))
 for line in lines:
  if line.startswith(';'):
   block=[line[1:].rstrip('\n')]
   for l in lines:
    if l.startswith(';'):break
    block.append(l.rstrip('\n'))
   yield '\x00'+'\n'.join(block)
  else:
   if line.lstrip().startswith('#'):continue
   yield from re.findall(r"'(?:[^']|'(?!\s|$))*'|\"(?:[^\"]|\"(?!\s|$))*\"|\S+",line)

def clean(v):
 return v[1:] if v.startswith('\x00') else v[1:-1] if v.startswith(("'",'\"')) else v
def parse_cif(path):
 ts=list(cif_tokens(path));out={};i=0
 while i<len(ts):
  if ts[i]=='loop_':
   i+=1;tags=[]
   while i<len(ts) and ts[i].startswith('_'):tags.append(ts[i]);i+=1
   vals=[]
   while i<len(ts) and ts[i]!='loop_' and not ts[i].startswith('_') and not ts[i].startswith('data_'):vals.append(ts[i]);i+=1
   assert len(vals)%len(tags)==0,(path,tags)
   for j,t in enumerate(tags):out[t]=[clean(v) for v in vals[j::len(tags)]]
  elif ts[i].startswith('_'):
   out[ts[i]]=[clean(ts[i+1])];i+=2
  else:i+=1
 return out
summaries=[];bibs=[]
for code in ['1GGQ','1G5Z']:
 d=json.load(open('reference_structures/'+code+'.json'));c=parse_cif('reference_structures/'+code+'.cif');info=d['rcsb_entry_info']
 cats=['_entity.','_entity_poly.','_struct_ref.','_struct_ref_seq.','_struct_ref_seq_dif.','_pdbx_struct_assembly.','_entity_src_gen.','_refine.ls_R_factor']
 summary={'pdb_id':code,'provenance':'PRE-EXISTING EXPERIMENTAL REFERENCE; not generated by LymeScope','title':d['struct']['title'],'method':d.get('exptl'),'resolution_A':info['resolution_combined'],'modeled_polymer_residues':info['deposited_modeled_polymer_monomer_count'],'unmodeled_polymer_residues':info['deposited_unmodeled_polymer_monomer_count'],'polymer_instances':info['deposited_polymer_entity_instance_count'],'construct_length':info['polymer_monomer_count_maximum'],'source_cif_fields':{k:v for k,v in c.items() if any(k.startswith(cat) for cat in cats)},'suitability':'Useful OspC fold/dimer reference; recombinant truncated construct, not full-length lipidated protein. Map each natural sequence to the construct before residue comparisons. Biological assemblies differ from asymmetric unit; inspect assembly operators. No claim of universal epitope coverage or project-generated structure.'}
 summaries.append(summary);bibs.append({'source':'RCSB '+code,'citation':d['rcsb_primary_citation']})
P('reference_structures/reference_summary.json').write_text(json.dumps(summaries,indent=2))
bibs.extend({'source':'UniProt UP000001807','citation':c} for c in proteome['citations'])
for e,r in selected:
 for ref in e.get('references',[]):
  cit=ref.get('citation',{})
  if cit.get('citationType')=='journal article':bibs.append({'source':'UniProt '+e['primaryAccession'],'citation':cit})
P('evidence/primary_bibliographic_records.json').write_text(json.dumps(bibs,indent=2))
counts=collections.Counter(f for r in rows for f in r['quality_flags'].split(';') if f)
report=f'''# LymeScope data quality report

Prepared {now}. All runtime observations belong to PERSONAL Spark spark-6771 only.

## Proteome verification

UniProt UP000001807 identifies Borreliella burgdorferi B31 (taxon 224326), assembly {proteome['genomeAssembly']['assemblyId']}. API reports {proteome['proteinCount']} proteins; downloaded canonical FASTA contains {len(ids)} unique accessions and annotation table contains {len(table)} rows. Accession sets match exactly. One isoform is reported separately by UniProt; this canonical export does not include extra isoforms.

## Provisional natural OspC panel

Selected {len(selected)} distinct amino-acid sequences from the first 500 UniProt search results (not an exhaustive population sample). {len(eligible)} entries passed the selection filters. {sum(r['reviewed'] for e,r in selected)} reviewed distinct entries are prioritized (one of the four reviewed source records is an exact sequence duplicate); remaining entries are chosen by species round-robin, with supplied strains then accession ordering within species. Reference-comment strain lists and their reference numbers are preserved even for merged records. Selection preserves native database sequences without trimming, mutations or synthetic designs. No OspC type is inferred. PF01441 supports a shared family and is insufficient alone; an explicit OspC name/gene is also required. This is annotation-supported family assignment, not an independent HMM or phylogenetic validation. Natural provenance is based on biological organism and nucleotide-source annotations, not an independent audit of the original isolate. Reviewed Q0SL36 is an exact sequence duplicate of P0DW54 despite their differing organism labels; both raw records are preserved, and only the first is retained in this sequence-distinct panel.

Full pool QC flags: {dict(counts)}.

Selected panel unresolved/missing strain: {sum(not r['strain'] for e,r in selected)}. Selected annotated fragments: 0. Selected exact duplicates: 0. Selected uncertain family: 0 under the stated annotation rule. Length window 190–230 aa is a conservative heuristic, not proof of completeness. Strains are copied from the organism field or a single distinct STRAIN reference comment. Multiple reference strains remain explicitly listed with reference numbers and are not collapsed to an invented strain; unresolved fields stay blank. No strains inferred from species, sequence, or structure. Raw records retain additional source-reference context. Candidate exact duplicates refer to the first occurrence in the retrieved pool; excluded records and reasons are in source_data/candidate_quality.tsv.

## Pre-existing structural references

1GGQ: B31 OspC, X-ray, 2.51 Å, 174 residues per deposited polymer, four polymer instances; 648 modeled and 48 unmodeled polymer residues in aggregate. 1G5Z: N40 OspC by entry title, X-ray, 2.51 Å, 164-residue polymer, one asymmetric-unit polymer, 164 modeled and zero unmodeled residues within its deposited construct. Neither is a full-length native lipidated protein. N40 is supplied in the 1G5Z title, while its CIF source-strain field is unknown. Historical CIF database mapping O31117 should not be silently replaced by current web mappings; preserve and align before assigning residue numbers. The complete CIF construct, sequence differences, source, refinement, and assembly fields are extracted into reference_summary.json. Mutation field '?' means unspecified, not proven absence of mutations. Suitable as fold and assembly references after sequence alignment; not independent validation of new predictions.

## Evidence and reuse

Primary bibliographic records come directly from UniProt and RCSB, with DOI/PubMed identifiers as supplied; duplicate citations are intentionally retained with source context. UniProt data: CC BY 4.0, subject to its patent/other-rights disclaimer. PDB archive coordinates: CC0; RCSB API data follow archive terms except integrated external resources. Policies saved in evidence/. Primary study DOI 10.1128/mbio.02981-22 is verified open access CC BY 4.0; PMC HTML includes its license. Other primary papers are retained as bibliographic records only, without assuming their full texts are redistributable.

## Runtime limitations and blockers

Hostname/user verified locally. nvidia-smi could not communicate with NVIDIA driver; no /dev/nvidia* nodes visible. Existing torch imports succeed in cnh-venv (2.15.0+cu132), ftvenv and forge/.venv (2.14.1+cu130); all CUDA availability checks false and tiny GPU tensor attempts fail with 'No CUDA GPUs are available'. No successful GPU computation or performance timing. Docker image listing fails with socket permission denied. Targeted standard Hugging Face/Torch cache checks show no named ESM/Prot/Fold model cache; other model directory names do not establish complete usable weights. No package, model, container downloads or runtime changes performed.

Sandbox DNS initially blocked downloads; approved network access succeeded. Europe PMC fullTextXML request returned HTTP 500; PMC HTML fallback succeeded. Download provenance, sizes, hashes and restrictions are in source_manifest.json. No event cluster access or speedup claims.
'''
P('data_quality_report.md').write_text(report)
print('proteome',len(ids),'selected',len(selected),'eligible',len(eligible),'flags',dict(counts));print([(x['pdb_id'],x['source_cif_fields'].get('_struct_ref_seq_dif.details')) for x in summaries])
