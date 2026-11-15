"""Narrow official RCSB coordinate/metadata retrieval; no model or dataset downloads."""
import pathlib, json, hashlib, urllib.request, datetime, concurrent.futures
R = pathlib.Path(__file__).resolve().parents[1]
SOURCES = [('9BIF.cif', 'https://files.rcsb.org/download/9BIF.cif', 10000000), ('9BIF_entry.json', 'https://data.rcsb.org/rest/v1/core/entry/9BIF', 300000), ('9BIF_entity_1.json', 'https://data.rcsb.org/rest/v1/core/polymer_entity/9BIF/1', 300000), ('9BIF_entity_2.json', 'https://data.rcsb.org/rest/v1/core/polymer_entity/9BIF/2', 300000), ('9BIF_entity_3.json', 'https://data.rcsb.org/rest/v1/core/polymer_entity/9BIF/3', 300000), ('7UIJ.cif', 'https://files.rcsb.org/download/7UIJ.cif', 5000000), ('7UIJ_entry.json', 'https://data.rcsb.org/rest/v1/core/entry/7UIJ', 300000), ('7UIJ_entity_3.json', 'https://data.rcsb.org/rest/v1/core/polymer_entity/7UIJ/3', 300000)]

def fetch(item):
    name, url, cap = item
    p = R / 'inputs' / name
    assert not p.exists(), name
    with urllib.request.urlopen(url, timeout=45) as response:
        raw = response.read(cap + 1)
        headers = {k: response.headers.get(k) for k in ['Last-Modified', 'ETag', 'Content-Type']}
    assert len(raw) <= cap, (name, len(raw))
    p.write_bytes(raw)
    return {'file': 'inputs/' + name, 'url': url, 'retrieved_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(), 'headers': headers, 'status': 'RETRIEVED'}

def main():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        rows = list(executor.map(fetch, SOURCES))
    assert sum((x['bytes'] for x in rows)) < 17000000
    (R / 'provenance/source_receipts.json').write_text(json.dumps(rows, indent=2) + '\n')
    print(json.dumps(rows, indent=2))
if __name__ == '__main__':
    main()
