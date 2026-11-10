#!/usr/bin/env python3
"""Full existing Fountain Press reader/index source-parity acceptance.

Usage:
python3 scripts/test_client_centered_press_shell.py --site /path/to/site/ [--predecessor /path/to/current/]
This checks static bytes and preservation; live-browser E2E is separate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import re
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_client_centered_press_production import (
    SOURCE_SHA, SOURCE_REV, ENGINE_SHA, PUBLIC_REL, SOCIAL, ORIGINAL_ENGINE
)

ROOT = None
PREVIOUS = None
TEMPLATES = re.compile(
    r'<template data-reader-volume="([^"]+)"[^>]*>.*?</template>', re.S
)
GALLERY = re.compile(
    r'<script type="application/json" id="reader-gallery-data">(.*?)</script>', re.S
)
ORIGINAL_READER_APP = 'reading-first-app.47b1250c4feb1cd6b920b451d2b0a6dd14207020857600f39192361c3e4fe725.js'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


class ClientCenteredShellParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if ROOT is None:
            raise unittest.SkipTest("Explicit --site release path required for full-shell parity")
        cls.source = (ROOT / 'estate/index.html').read_text()
        cls.templates = {m.group(1):m.group() for m in TEMPLATES.finditer(cls.source)}
        cls.gallery = json.loads(GALLERY.search(cls.source).group(1))
        cls.pages = [p for p in ROOT.rglob('index.html')
                     if 'id="reader-gallery-data"' in p.read_text(errors='replace')]

    def test_every_reader_entry_has_identical_full_source(self):
        self.assertEqual(len(self.pages),55)
        self.assertEqual(len(self.templates),51)
        self.assertEqual(len(self.gallery['collections']['essays']),7)
        self.assertEqual(len(self.gallery['collections']['first-readings']),30)
        self.assertEqual(self.gallery['collections']['essays'][0]['id'],
                         'essay--client-centered')
        for page in self.pages:
            with self.subTest(route=page.relative_to(ROOT)):
                s=page.read_text()
                present={m.group(1):m.group() for m in TEMPLATES.finditer(s)}
                self.assertEqual(present,self.templates,'Incomplete source prose/figure parity')
                self.assertEqual(json.loads(GALLERY.search(s).group(1)),self.gallery)
                self.assertEqual(s.count(ORIGINAL_READER_APP),1)
                self.assertEqual(s.count('data-reader-volume="essay--client-centered"'),1)
                self.assertEqual(s.count('data-reader-volume="essay--a-sound-must-earn-its-place"'),1)
                self.assertNotIn('reading-first-app.client-centered-review.js',s)
                self.assertIn(ENGINE_SHA,s)

    def test_all_admitted_reader_entrances_have_correct_volume(self):
        for route,volume in {
            'index.html':'library',
            'estate/index.html':'library',
            'estate/bookshelf/index.html':'library',
            'estate/read/library/index.html':'library',
            'estate/read/essays/index.html':'essays',
            'estate/read/first-readings/index.html':'first-readings',
            'estate/collections/first-readings/index.html':'first-readings',
            'estate/read/essay--client-centered/index.html':'essay--client-centered',
            'estate/read/essay--the-ear-that-learns/index.html':'essay--the-ear-that-learns',
            'estate/read/continuity/index.html':'continuity',
            'estate/read/essay--a-sound-must-earn-its-place/index.html':
                'essay--a-sound-must-earn-its-place'
        }.items():
            with self.subTest(route=route):
                page=(ROOT/route).read_text()
                self.assertIn('data-initial-volume="'+volume+'"',page)
                self.assertIn('data-reader-volume="essay--client-centered"',page)

    def test_legacy_indexes_reconcile_without_rewriting_history(self):
        for path in ('essays/index.html','estate/essays/index.html'):
            s=(ROOT/path).read_text()
            self.assertIn('href="/estate/read/essay--client-centered/"',s)
            self.assertEqual(s.count('data-essay-route="/estate/read/essay--client-centered/"'),1)
            self.assertIn('Client-Centered',s)
        edition_index=(ROOT/'estate/editions/index.html').read_text()
        self.assertIn('href="/estate/read/essays/"',edition_index)
        self.assertIn('data-book-id="fountain-coach" data-release-status="published"',
                      edition_index)
        self.assertIn('href="/estate/read/essays/"',
                      (ROOT/'estate/editions/catalogue/index.html').read_text())
        self.assertNotIn('href="/assets/estate-shell.css"',
                         (ROOT/'estate/editions/catalogue/index.html').read_text())
        self.assertNotIn('href="/assets/estate-shell.css"',
                         (ROOT/'estate/essays/index.html').read_text())
        self.assertIn('rel="icon"',
                      (ROOT/'essays/index.html').read_text().split('</head>')[0])
        if PREVIOUS:
            for hist in ('estate/editions/essays/index.html',
                         'estate/editions/essays-continuing/index.html'):
                self.assertEqual(sha(ROOT/hist),sha(PREVIOUS/hist))

    def test_source_images_manifests_production_unchanged(self):
        work=json.loads((ROOT/PUBLIC_REL/'edition-manifest.json').read_text())
        self.assertEqual(work['sourceSHA256'],SOURCE_SHA)
        self.assertEqual(work['sourceRevision'],SOURCE_REV)
        self.assertTrue(work['productionAuthorized'])
        self.assertEqual(work['publicationState'],'published')
        self.assertEqual(len(work['blocks']),26)
        self.assertEqual(work['figures'][1]['after'],'client-centered.s2.p6')
        self.assertEqual(sha(ROOT/'estate/assets/linotype'/ORIGINAL_ENGINE),ENGINE_SHA)
        if PREVIOUS:
            for f in [
                PUBLIC_REL/'edition-manifest.json',
                SOCIAL,
                PUBLIC_REL/'assets/images/client-centered-positions.svg',
                PUBLIC_REL/'assets/images/client-centered-open-method.svg'
            ]:
                self.assertEqual(sha(ROOT/f),sha(PREVIOUS/f))
            prior={f.relative_to(PREVIOUS).as_posix():f for f in PREVIOUS.rglob('*') if f.is_file()}
            new={f.relative_to(ROOT).as_posix():f for f in ROOT.rglob('*') if f.is_file()}
            self.assertEqual(prior.keys(),new.keys())
            rc=json.loads((ROOT/'release-manifest.json').read_text())['clientCenteredShellReconciliation']
            self.assertEqual(rc['readerEntryRouteCount'],55)
            diff=[key for key in new if sha(new[key])!=sha(prior[key])]
            self.assertEqual(set(diff),set(rc['modifiedRouteHTML'])|{'release-manifest.json'})
            self.assertEqual(len(diff),60)

    def test_per_work_canonical_and_social_metadata_retained(self):
        for route in ('essay--client-centered','essay--the-ear-that-learns',
                      'essay--a-sound-must-earn-its-place'):
            page=(ROOT/f'estate/read/{route}/index.html').read_text()
            self.assertIn('https://fountain.coach/estate/read/'+route+'/',page)
            self.assertNotIn('owner-WLAN-editorial-review',page)
        client=(ROOT/PUBLIC_REL/'index.html').read_text()
        self.assertIn('name="fountain:publication-state" content="published"',client)
        self.assertIn('name="fountain:manuscript-sha256" content="'+SOURCE_SHA+'"',client)
        self.assertIn('og:image" content="https://fountain.coach/estate/assets/social/client-centered-',client)


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--site',required=True,type=Path)
    parser.add_argument('--predecessor',type=Path)
    a=parser.parse_args()
    ROOT=a.site
    PREVIOUS=a.predecessor
    unittest.main(argv=['test_client_centered_press_shell.py'],verbosity=2)
