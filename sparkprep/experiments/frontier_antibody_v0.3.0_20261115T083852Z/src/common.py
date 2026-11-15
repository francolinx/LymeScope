import pathlib, json, csv, hashlib
ROOT = pathlib.Path(__file__).resolve().parents[1]

def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()

def fasta(path):
    out = {}
    key = None
    for line in pathlib.Path(path).read_text().splitlines():
        if line.startswith('>'):
            key = line[1:].split()[0]
            assert key not in out
            out[key] = ''
        elif line.strip():
            out[key] += line.strip()
    return out

def rows(c, prefix):
    tags = [k for k in c if k.startswith(prefix + '.')]
    return [{k.split('.', 1)[1]: c[k][i] for k in tags} for i in range(len(c[tags[0]]))] if tags else []

def write_json(path, obj):
    pathlib.Path(path).write_text(json.dumps(obj, indent=2, allow_nan=False) + '\n')

def write_tsv(path, data):
    if not data:
        return
    with pathlib.Path(path).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(data[0]), delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows(data)

def blank(x):
    return '' if x in ['?', '.', ''] else x
