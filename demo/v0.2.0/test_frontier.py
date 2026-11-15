"""Offline scientific-presentation contracts; no rendering or inference claims."""
import hashlib
import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).resolve().parents[2]
DOCS=ROOT/'docs'


class FrontierTests(unittest.TestCase):
    def test_claim_index_sources_are_exact_and_levels_explicit(self):
        claims=json.loads((DOCS/'claim-index.json').read_text(encoding='utf-8'))['claims']
        self.assertEqual(len(claims),17)
        self.assertEqual(len({c['claim_id'] for c in claims}),17)
        for c in claims:
            for key in ('assertion','evidence_level','method','interpretation_limitations','verification_status'):
                self.assertTrue(c[key],(c['claim_id'],key))
            self.assertTrue(c['sources'] or c['primary_references'])
            for source in c['sources']:
                path=(ROOT/source['path']).resolve();self.assertTrue(path.is_relative_to(ROOT))
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),source['sha256'])
        byid={c['claim_id']:c for c in claims}
        self.assertEqual([byid['C02']['metrics'][k] for k in ('F','M','MF')],[202,162,159])
        self.assertEqual(byid['C14']['verification_status'],'NOT_RUN')
        self.assertIsNone(byid['C14']['metrics']['speedup'])

    def test_no_unvalidated_antibody_labels(self):
        data=json.loads((DOCS/'frontier_v0.3.0/experimental-evidence.json').read_text(encoding='utf-8'))
        self.assertEqual(data['mapping_status'],'PENDING_SPARK_VALIDATION')
        self.assertIsNone(data['mapped_antibody_contact_positions'])
        self.assertIsNone(data['antibody_contact_by_alignment_column'])
        self.assertEqual([s['pdb_id'] for s in data['sources']],['9BIF','7UIJ',None])
        self.assertTrue(all(s['lymescope_mapping']=='NOT_IMPORTED' for s in data['sources']))

    def test_packaged_assets_match_original_bytes(self):
        m=json.loads((DOCS/'workbench-manifest.json').read_text())
        self.assertFalse(m['model_weights_included']);self.assertFalse(m['hosting_settings_changed'])
        self.assertLess(m['total_copied_bytes'],10*1024*1024)
        listed={row['path'] for row in m['files'] if row['path'].startswith('workbench-assets/')}
        present={p.relative_to(DOCS).as_posix() for p in (DOCS/'workbench-assets').rglob('*') if p.is_file()}
        self.assertEqual(present,listed)
        for row in m['files']:
            path=DOCS/row['path'];source=ROOT/row['source']
            self.assertEqual(path.stat().st_size,row['bytes'])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),row['sha256'])
            self.assertEqual(path.read_bytes(),source.read_bytes())
            self.assertNotIn(path.suffix,('.safetensors','.bin','.tar','.pt'))
        self.assertEqual(hashlib.sha256((DOCS/'index.html').read_bytes()).hexdigest(),m['page_sha256'])

    def test_packaged_embedded_data_are_identical(self):
        source=(ROOT/'demo/v0.2.0/index.html').read_text(encoding='utf-8')
        page=(DOCS/'index.html').read_text(encoding='utf-8')
        def data(html):return json.loads(re.search(r'<script id="context" type="application/json">(.*?)</script>',html,re.S).group(1))
        self.assertEqual(data(page),data(source))
        self.assertEqual(data(page)['spark_science']['event_benchmark'],'NOT_RUN')
        self.assertTrue((DOCS/'.nojekyll').is_file())

    def test_package_local_links_and_media(self):
        page=(DOCS/'index.html').read_text(encoding='utf-8')
        for attr,value in re.findall(r'(href|src|srcset)="([^"<>]+)"',page):
            u=urlsplit(value)
            if not u.scheme and not u.netloc and u.path:
                self.assertTrue((DOCS/unquote(u.path)).is_file(),value)
        self.assertNotRegex(page,r'<(?:script|img|link)[^>]+(?:src|href)="https?://')
        for name in ('coverage-evidence','ospc-dimer','residue-mapping','ospc-rotation','alignment-map'):
            for ext in ('png','gif'):self.assertTrue((DOCS/f'workbench-assets/{name}.{ext}').is_file())

    def test_three_original_readme_animations_have_static_alternatives(self):
        text=(ROOT/'README.md').read_text(encoding='utf-8')
        for name in ('ospc-dimer','residue-mapping','coverage-evidence'):
            self.assertIn(name+'.gif',text);self.assertIn(name+'.png',text)
        self.assertIn('GitHub Pages hosting is prepared, not claimed live',text)
        self.assertIn('docs/claim-index.json',text)


if __name__=='__main__':unittest.main(verbosity=2)
