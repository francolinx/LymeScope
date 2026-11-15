"""Offline media/document checks; these do not exercise a browser."""
import hashlib
import json
import re
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
from PIL import Image, ImageChops

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def local_links(path):
    text=path.read_text(encoding='utf-8')
    links=re.findall(r'!?\[[^\]]*\]\(([^)]+)\)',text)
    links+=re.findall(r'(?:href|src|srcset)=["\']([^"\']+)["\']',text)
    for link in links:
        parsed=urlsplit(link)
        if not parsed.scheme and not parsed.netloc and parsed.path:
            yield (path.parent/unquote(parsed.path)).resolve()


class PresentationTests(unittest.TestCase):
    def test_six_actual_looping_gifs_and_static_alternatives(self):
        manifest=json.loads((HERE/'assets/manifest.json').read_text())
        self.assertEqual(len(manifest['assets']),6)
        self.assertLess(sum(a['bytes'] for a in manifest['assets']),8*1024*1024)
        for asset in manifest['assets']:
            path=HERE/'assets'/asset['path']
            self.assertEqual(path.stat().st_size,asset['bytes'])
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),asset['sha256'])
            with Image.open(path) as im:
                self.assertEqual(im.size,(960,640));self.assertEqual(im.info['loop'],0)
                self.assertEqual(im.n_frames,60)
                first=im.convert('RGB');changed=False;duration=0
                for n in range(im.n_frames):
                    im.seek(n);frame=im.convert('RGB');frame.load();duration+=im.info['duration']
                    changed=changed or bool(ImageChops.difference(first,frame).getbbox())
                self.assertTrue(changed);self.assertEqual(duration,asset['duration_ms'])
            with Image.open(HERE/'assets'/asset['static_preview']) as poster:self.assertEqual(poster.size,(960,640))

    def test_all_document_and_demo_relative_links_resolve(self):
        for path in [ROOT/'README.md',HERE/'index.html',ROOT/'submission/README_PREVIEW.html',*(ROOT/'submission').glob('*.md')]:
            for link in local_links(path):self.assertTrue(link.exists(),f'{path.name}: {link}')

    def test_timeline_is_accessible_and_sourced(self):
        tree=ET.parse(HERE/'assets/biology-timeline.svg');ns={'s':'http://www.w3.org/2000/svg'}
        self.assertEqual(tree.getroot().get('role'),'img')
        self.assertTrue(tree.find('s:title',ns).text);self.assertTrue(tree.find('s:desc',ns).text)
        milestones=json.loads((HERE/'assets/timeline-sources.json').read_text(encoding='utf-8'))
        self.assertEqual(len(milestones),10)
        self.assertTrue(all(row[3].startswith('https://') for row in milestones))

    def test_scientific_asset_claims_match_saved_context(self):
        context=json.loads((HERE/'context.json').read_text(encoding='utf-8'))
        manifest=json.loads((HERE/'assets/manifest.json').read_text())
        self.assertEqual(manifest['source_hashes'],context['provenance'])
        self.assertEqual(sorted(set(context['column_sets']['mapped_observed'])-set(context['column_sets']['fully_covered'])),[75,86,119])
        rows=context['references']['1GGQ']['mapping']
        self.assertEqual(sum(bool(r['CA_contact_proxy_within_8A']) for r in rows),49)
        mapped=next(r for r in rows if r['alignment_column']==68)
        self.assertEqual((mapped['panel_sequence_position'],mapped['auth_residue_number'],mapped['aa']),(67,'67','S'))
        assets={a['path']:a for a in manifest['assets']}
        self.assertEqual(assets['task-shards.gif']['evidence_kind'],'conceptual_unexecuted_workflow')
        self.assertEqual(assets['coverage-evidence.gif']['details']['sparse_gaps'],29)

    def test_static_first_demo_and_required_submission_files(self):
        page=(HERE/'index.html').read_text(encoding='utf-8')
        self.assertIn('id="scene-image" src="assets/coverage-evidence.png"',page)
        self.assertIn('Play animation',page);self.assertIn('Event two-node: NOT RUN',page)
        self.assertIn('full_panel_agreement_predictability.png', page)
        self.assertLess(page.index('id="spark-results"'), page.index('class="cinema"'))
        for name in ['ONE_PAGER.md','DEMO_SCRIPT.md','SOURCE_REFERENCES.md','CLAIM_VERIFICATION.md','SUBMISSION_CHECKLIST.md']:
            self.assertTrue((ROOT/'submission'/name).is_file())
        readme=(ROOT/'README.md').read_text(encoding='utf-8')
        self.assertIn('draft awaiting personal approval',readme)
        self.assertIn('prefers-reduced-motion: reduce',readme)
        self.assertNotIn('agreement?NLL',readme)


if __name__=='__main__':unittest.main(verbosity=2)
