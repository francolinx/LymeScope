"""Validate/import a compact scientific bundle locally; no network or cluster calls.
Default is validation only. --import-to writes a new bundle directory, never overwrites.
See scientific_bundle_contract.json for the required structure. Missing data is never synthesized.
"""
import argparse, datetime, hashlib, json, re, stat, sys, zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

MAX_FILES=128
MAX_FILE=20*1024*1024
MAX_TOTAL=100*1024*1024
ROLES={"fasta","sequence_metadata","source_manifest","reference_structure"}
RESERVED={"CON","PRN","AUX","NUL"}|{f"{x}{i}" for x in ("COM","LPT") for i in range(1,10)}
AA=set("ACDEFGHIKLMNPQRSTVWYBXZJUO")

class InvalidBundle(ValueError): pass

def require(value,message):
    if not value: raise InvalidBundle(message)

def safe_path(value):
    require(isinstance(value,str) and value and "\\" not in value,"Use nonempty POSIX relative paths")
    p=PurePosixPath(value)
    require(not p.is_absolute() and p.as_posix()==value,"Noncanonical or absolute path")
    for part in p.parts:
        require(part not in (".","..") and ":" not in part and not part.startswith(".")
                and part.rstrip(" .")==part and part.split(".")[0].upper() not in RESERVED,
                "Unsafe path component")
        require(not re.search(r'[<>\"|?*\x00-\x1f]',part),"Invalid Windows filename")
    require(not any(s in value.lower() for s in (".env","credential","token","password","id_rsa","id_ed25519")),"Credential-like filename refused")
    return value

def read_bundle(source):
    source=Path(source)
    data={}; total=0
    if source.is_dir():
        require(not source.is_symlink(),"Bundle root cannot be a symlink")
        for p in source.rglob("*"):
            require(not p.is_symlink() and not (hasattr(p,"is_junction") and p.is_junction()),"Links/junctions are forbidden")
            if not p.is_file(): continue
            rel=safe_path(p.relative_to(source).as_posix())
            n=p.stat().st_size
            require(n<=MAX_FILE,"File exceeds 20 MiB limit")
            total+=n
            require(total<=MAX_TOTAL and len(data)<MAX_FILES,"Bundle exceeds limits")
            require(rel.casefold() not in {x.casefold() for x in data},"Duplicate/case-colliding path")
            data[rel]=p.read_bytes()
    elif source.is_file() and zipfile.is_zipfile(source):
        with zipfile.ZipFile(source) as z:
            infos=z.infolist()
            require(len(infos)<=MAX_FILES*2,"Too many archive entries")
            for item in infos:
                if item.is_dir():
                    safe_path(item.filename.rstrip("/")); continue
                rel=safe_path(item.filename)
                mode=item.external_attr>>16
                require(not stat.S_ISLNK(mode),"Archive symlinks are forbidden")
                require(not item.flag_bits & 1,"Encrypted files are forbidden")
                require(item.file_size<=MAX_FILE,"File exceeds 20 MiB limit")
                total+=item.file_size
                require(total<=MAX_TOTAL and len(data)<MAX_FILES,"Bundle exceeds limits")
                require(rel.casefold() not in {x.casefold() for x in data},"Duplicate/case-colliding path")
                with z.open(item) as stream: content=stream.read(MAX_FILE+1)
                require(len(content)==item.file_size,"Unexpected decompressed size")
                data[rel]=content
    else:
        raise InvalidBundle("Supply a local directory or ZIP; remote paths/URLs are not fetched")
    require("bundle_manifest.json" in data,"Missing bundle_manifest.json")
    return data

def parse_json(raw,label):
    try: return json.loads(raw.decode("utf-8-sig"))
    except (ValueError,UnicodeError) as e: raise InvalidBundle("Invalid JSON: "+label) from e

def fasta_records(raw,label):
    try: text=raw.decode("ascii")
    except UnicodeError as e: raise InvalidBundle("FASTA must be ASCII: "+label) from e
    out={}; key=None; seq=[]
    def commit():
        if key is None: return
        sequence="".join(seq)
        require(sequence and len(sequence)<=10000,"Sequence length must be 1..10000")
        if sequence.endswith("*"): sequence=sequence[:-1]
        require(sequence and set(sequence)<=AA,"Invalid residue/internal stop; no silent normalization")
        require(key not in out,"Duplicate FASTA sequence identifier")
        out[key]={"length":len(sequence),"sequence_sha256":hashlib.sha256(sequence.encode()).hexdigest(),
                  "ambiguous_residues":sum(sequence.count(x) for x in "BXZJ"),
                  "fasta_file":label}
    for line in text.splitlines():
        if not line.strip(): continue
        if line.startswith(">"):
            commit()
            require(line[1:].strip(),"Empty FASTA header")
            key=line[1:].split()[0]; seq=[]
        else:
            require(key is not None,"Sequence data before FASTA header")
            require(line==line.strip() and line==line.upper(),"FASTA must use uppercase residue lines without spaces")
            seq.append(line)
    commit()
    require(out,"No FASTA records")
    return out

def validate(source):
    data=read_bundle(source)
    m=parse_json(data["bundle_manifest.json"],"bundle_manifest.json")
    require(isinstance(m,dict) and m.get("schema_version")==1,"schema_version must be 1")
    require(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}",str(m.get("bundle_id",""))),"Invalid bundle_id")
    rows=m.get("files")
    require(isinstance(rows,list) and 1<=len(rows)<MAX_FILES,"Manifest files must be a bounded list")
    listed=set(); by_role={r:[] for r in ROLES}
    for row in rows:
        require(isinstance(row,dict),"Invalid manifest file entry")
        name=safe_path(row.get("path"))
        require(name!="bundle_manifest.json" and name not in listed,"Duplicate/self-referential manifest entry")
        listed.add(name)
        require(row.get("role") in ROLES,"Unknown file role; models/executables are not accepted")
        require(name in data,"Missing listed file: "+name)
        content=data[name]
        require(type(row.get("bytes")) is int and row["bytes"]==len(content),"Size mismatch: "+name)
        require(re.fullmatch(r"[0-9a-f]{64}",str(row.get("sha256",""))),"Invalid SHA256: "+name)
        require(hashlib.sha256(content).hexdigest()==row["sha256"],"Hash mismatch: "+name)
        by_role[row["role"]].append(row)
    require(set(data)==listed|{"bundle_manifest.json"},"Unlisted files present; review bundle contents")
    require(by_role["fasta"],"At least one FASTA file required")
    require(len(by_role["sequence_metadata"])==1 and len(by_role["source_manifest"])==1,
            "Exactly one sequence_metadata and source_manifest required")
    sources_doc=parse_json(data[by_role["source_manifest"][0]["path"]],"source manifest")
    sources=sources_doc.get("sources",[]) if isinstance(sources_doc,dict) else []
    require(sources,"No source records")
    source_ids=set()
    for s in sources:
        require(isinstance(s,dict) and isinstance(s.get("id"),str) and s["id"] and s["id"] not in source_ids,"Invalid/duplicate source ID")
        source_ids.add(s["id"])
        url=urlsplit(s.get("url",""))
        require(url.scheme=="https" and url.netloc and not url.username and not url.password,"Use credential-free HTTPS source URLs")
        require(not re.search(r"(?i)(token|password|secret|signature|api_key)=",url.query),"Secret-like source URL query refused")
        require(all(isinstance(s.get(k),str) and s[k].strip() for k in ("license","citation","retrieved_at")),"Source citation/license/retrieval time required")
    sequences={}
    for row in by_role["fasta"]:
        current=fasta_records(data[row["path"]],row["path"])
        require(not set(current)&set(sequences),"FASTA IDs must be unique across files")
        sequences.update(current)
    require(len(sequences)<=512,"More than 512 sequences; use a smaller bundle")
    meta=parse_json(data[by_role["sequence_metadata"][0]["path"]],"sequence metadata")
    require(isinstance(meta,list),"Sequence metadata must be a JSON list")
    ids=set()
    for row in meta:
        require(isinstance(row,dict) and row.get("sequence_id") in sequences,"Unknown/missing sequence_id")
        sid=row["sequence_id"]
        require(sid not in ids,"Duplicate sequence metadata")
        ids.add(sid)
        require(isinstance(row.get("accession"),str) and row["accession"].strip(),"Accession required")
        require(row.get("source_id") in source_ids,"Unknown source_id")
        sequences[sid].update(accession=row["accession"],source_id=row["source_id"])
    require(ids==set(sequences),"Every sequence needs metadata")
    refs=[]
    for row in by_role["reference_structure"]:
        require(row.get("origin")=="pre-existing","References must be labeled pre-existing")
        require(row.get("source_id") in source_ids and row.get("reference_id"),"Reference ID/source required")
        name=row["path"]; ext=Path(name).suffix.lower()
        require(ext in (".pdb",".cif",".mmcif"),"Reference must be uncompressed PDB/mmCIF")
        content=data[name].decode("utf-8")
        require(("ATOM  " in content or "HETATM" in content) if ext==".pdb" else "_atom_site." in content,
                "No recognizable coordinate records; structure semantics require separate review")
        refs.append({"path":name,"reference_id":row["reference_id"],"origin":"pre-existing","source_id":row["source_id"]})
    warnings=[]
    if not refs: warnings.append("Reference structures missing; no structures fabricated")
    if any(v["ambiguous_residues"] for v in sequences.values()): warnings.append("Ambiguous residues present; scientific method must define handling")
    digest=hashlib.sha256(data["bundle_manifest.json"]).hexdigest()
    report={"status":"VALIDATED_LOCAL_ONLY","bundle_id":m["bundle_id"],"manifest_sha256":digest,
            "file_count":len(data),"total_bytes":sum(map(len,data.values())),
            "sequences":sequences,"reference_structures":refs,"warnings":warnings,
            "scientific_results":False,"remote_actions":0,"method_approval":"REQUIRED before any scientific run",
            "validated_at":datetime.datetime.now().astimezone().isoformat()}
    return data,report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle",type=Path)
    parser.add_argument("--import-to",type=Path,help="Optional local destination root; creates a NEW bundle-specific folder")
    parser.add_argument("--report",type=Path,help="Optional new local validation report")
    args=parser.parse_args()
    try:
        data,report=validate(args.bundle)
        if args.import_to:
            dest=args.import_to/(report["bundle_id"]+"-"+report["manifest_sha256"][:12])
            require(not dest.exists(),"Import destination already exists; refusing overwrite")
            dest.mkdir(parents=True)
            for rel,raw in data.items():
                p=dest/rel; p.parent.mkdir(parents=True,exist_ok=True)
                with p.open("xb") as f: f.write(raw)
            for rel,raw in data.items():
                require((dest/rel).read_bytes()==raw,"Post-copy verification failed")
            report["import_directory"]=str(dest.resolve())
            report["copy_hash_verification"]="PASS"
            with (dest/"local-import-validation.json").open("x",encoding="utf-8") as f:
                json.dump(report,f,indent=2); f.write("\n")
        if args.report:
            with args.report.open("x",encoding="utf-8") as f:
                json.dump(report,f,indent=2); f.write("\n")
        print(json.dumps(report,indent=2))
        return 0
    except (InvalidBundle,OSError,ValueError,zipfile.BadZipFile) as exc:
        print(json.dumps({"status":"REJECTED","reason":str(exc),"remote_actions":0}),file=sys.stderr)
        return 1
if __name__=="__main__": raise SystemExit(main())

