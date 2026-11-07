#!/usr/bin/env python3
"""Bounded Fountain Press migration repair for the original public Ear/Sing study.

Retains the current immutable production release as baseline. Replaces the
accidentally flattened source blocks p6..p20 in each Press book entry HTML,
preserving all other authored blocks and the existing Linotype page compositor.
"""
from __future__ import annotations
import argparse
import hashlib
from html import escape
from pathlib import Path
import json
import re
import shutil

HEAD_CSS = '<link rel="stylesheet" href="/estate/assets/linotype/ear-sing-press-listening.css"/>'
HEAD_JS = '<script type="module" src="/estate/assets/linotype/ear-sing-press-listening.mjs"></script>'
MANIFEST_ID = 'ear-sing-press-manifest'
STUDY_RE = re.compile(
    r'<p data-source-block="the-ear-that-learns\.p6"[^>]*>.*?</p>\s*'
    r'(?:<p data-source-block="the-ear-that-learns\.p(?:[7-9]|1[0-9])"[^>]*>.*?</p>\s*)*'
    r'<p data-source-block="the-ear-that-learns\.p20"[^>]*>.*?</p>',
    re.DOTALL
)
def sha(path: Path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(262144),b''): h.update(chunk)
    return h.hexdigest()

def figure(manifest: dict) -> str:
    articulated = next(t for t in manifest['takes'] if t['id']=='articulated')
    return (
        '<figure class="frame-press-av ear-sing-exhibit" '
        'data-press-media="ear-sing.original-synthetic-study.v1" '
        'data-source-block="the-ear-that-learns.listening.v1" data-ear-listening="" '
        'aria-label="Ear and Sing source-bound audio listening study">'
        '<figcaption>Listening study 01 · One score, three original Sing takes (5.20 seconds)</figcaption>'
        '<div class="ear-sing-takes" role="group" aria-label="Select source-bound recording">'
        '<button type="button" data-ear-take="plain" aria-pressed="false">01 / Plain</button>'
        '<button type="button" data-ear-take="articulated" aria-pressed="true">02 / Articulated</button>'
        '<button type="button" data-ear-take="expressive" aria-pressed="false">03 / Expressive</button>'
        '</div>'
        '<audio controls playsinline preload="metadata" '
        'src="/essays/the-ear-that-learns/media/sing-articulated-compare.m4a" '
        'aria-label="The selected original Sing rehearsal take">Your browser cannot play this original recording.</audio>'
        f'<details class="ear-sing-about"><summary>About this take</summary><p class="ear-sing-description" data-ear-description="">{escape(articulated["description"])}</p></details>'
        '<p class="ear-sing-cues-heading">Comments on the sound · select a timestamp</p>'
        '<div class="ear-sing-cue-strip" data-ear-cues="" role="group" aria-label="Source-time annotations">'
        '<button type="button">0.00 s</button><button type="button">1.15 s</button>'
        '<button type="button">2.15 s</button><button type="button">3.35 s</button></div>'
        f'<p class="ear-sing-current" data-ear-current="" role="status">{escape(articulated["comments"][0]["text"])}</p>'
        '<details class="ear-sing-comment"><summary>Write and copy a time-addressed comment</summary>'
        '<label for="ear-sing-comment-entry">Your listening observation (stored nowhere)</label>'
        '<textarea id="ear-sing-comment-entry" data-ear-note="" rows="2" maxlength="2000" '
        'placeholder="What do you hear at this instant?"></textarea>'
        '<button type="button" data-ear-copy="">Copy comment and source address</button>'
        '<textarea data-ear-fallback="" rows="3" readonly hidden '
        'aria-label="Manually copy your source-addressed comment"></textarea></details>'
        '<p class="ear-sing-status" data-ear-status="" role="status">Public, author-approved synthetic audition. '
        'Three recordings retained from the original PCM study; no human singer or qualified lyric recognition.</p>'
        '</figure>'
    )

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--release-root',required=True,type=Path)
    parser.add_argument('--source-owner',required=True,type=Path)
    parser.add_argument('--original',required=True,type=Path)
    args=parser.parse_args()
    original=args.original.read_text()
    found=re.search(r'<script id="ear-sing-audio-manifest" type="application/json">(.+?)</script>',original,re.DOTALL)
    if not found: raise RuntimeError('Original author-approved audio manifest missing')
    manifest=json.loads(found.group(1))
    if manifest.get('publicationGrant')!='Fountain-Coach-Ear-Sing-2026-10-25' or manifest.get('release')!='public-original-synthetic-v1':
        raise RuntimeError('This is not the accepted public original Sing audio study')
    if len(manifest.get('takes',[]))!=3 or {t['id'] for t in manifest['takes']}!={'plain','articulated','expressive'}:
        raise RuntimeError('Unrecognized take count or identities')
    media=args.release_root/'essays/the-ear-that-learns/media'
    for take in manifest['takes']:
        asset=media/take['media'].split('/')[-1]
        assert asset.is_file(), f'Released audio missing: {asset}'
        actual=sha(asset)
        assert actual==take['deliverySHA256'], f'Published audio source digest mismatch: {asset} ({actual})'
    manifest_json=json.dumps(manifest,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    manifest_tag=f'<script type="application/json" id="{MANIFEST_ID}">{manifest_json}</script>'
    def transform(text):
        if HEAD_CSS in text or MANIFEST_ID in text:
            raise RuntimeError('Refusing to duplicate an existing Ear Press repair')
        if text.count('<template data-reader-volume="essay--the-ear-that-learns">')!=1:
            raise RuntimeError('Not the admitted Fountain Press book')
        text,n=STUDY_RE.subn(lambda _:figure(manifest),text)
        if n!=1: raise RuntimeError(f'Expected one flattened 6..20 block, found {n}')
        if text.count('</head>')!=1 or text.count('</body>')!=1:
            raise RuntimeError('Malformed Press source')
        text=text.replace('</head>',HEAD_CSS+'\n'+HEAD_JS+'\n</head>',1)
        text=text.replace('</body>',manifest_tag+'\n</body>',1)
        return text
    # The same admitted book is embedded in every deep-link copy; patch them all
    # so entry via the Bookshelf, direct URL, and Back produce the same edition.
    updated=[]
    for p in sorted(args.release_root.rglob('*.html')):
        if '<template data-reader-volume="essay--the-ear-that-learns">' in p.read_text(errors='replace'):
            p.write_text(transform(p.read_text()))
            updated.append(p)
    if len(updated)!=54:raise RuntimeError(f'Expected 54 active Press routes, found {len(updated)}')
    owner_html=args.source_owner/'index.html'
    owner_html.write_text(transform(owner_html.read_text()))
    owner_study=args.source_owner/'ear-sing-press-manifest.json'
    owner_study.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    assets=args.release_root/'estate/assets/linotype'
    for name in ('ear-sing-press-listening.mjs','ear-sing-press-listening.css'):
        shutil.copyfile(args.source_owner/name,assets/name)
    print('REPAIRED',len(updated),'production-equivalent reader routes')
    print('SOURCE',owner_html)
    print('FILES',updated[0],updated[-1])
    print('AUDIO_DIGESTS_VERIFIED',len(manifest['takes']))
    print('NEW_ASSETS',[(name,sha(assets/name)) for name in ('ear-sing-press-listening.mjs','ear-sing-press-listening.css')])

if __name__=='__main__':
    main()
