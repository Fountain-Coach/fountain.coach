#!/usr/bin/env python3
"""Project the approved Client-Centered v178 Press source into current public Reader.

Inputs are independently read-only captured current Caddy release and exact
owner-WLAN v178 essay artifact. Output is a complete local immutable candidate;
EstatePublisher alone publishes it. No new reader, no source-prose editing.
"""
import argparse
import hashlib
import html as htmllib
import json
from pathlib import Path
import re
import shutil
import struct
import subprocess
import tempfile

SOURCE_REV = "4a89ae5c2d822a0f594c382748277e2b818d82e4"
SOURCE_SHA = "03e4497f6deabe173958bd632b721ac7f23ae95e3bbe0043a1204ad5039de78a"
ENGINE_SHA = "e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a"
STAGE_LOCK = "fba0862de16c2507cb27244bd53315fbf072b54273efdfcff0ba3cc6af30fa48"
PREV = "fcis-5f94d0f-ear-sing-20261107"
RELEASE = "fcis-client-centered-20261110-4a89ae5"
URL = "https://fountain.coach/estate/read/essay--client-centered/"
PUBLIC_REL = Path("estate/read/essay--client-centered")
HERO = "client-centered-positions.svg"
SECOND = "client-centered-open-method.svg"
SOCIAL = Path("estate/assets/social/client-centered-4a89ae5.png")
PUBLIC_APP = "reading-first-app.704f14f99f15952f19cf7026225b93212b49ae276c3dfd3667e24b00701fc449.js"
ORIGINAL_ENGINE = "reading-first-press-engine." + ENGINE_SHA + ".js"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_one(text, before, after, label):
    if text.count(before) != 1:
        raise ValueError(f"{label}: expected one occurrence; got {text.count(before)}")
    return text.replace(before, after, 1)


def extract_template(text):
    start = text.index('<template data-reader-volume="essay--client-centered">')
    stop = text.index("</template>", start) + len("</template>")
    return text[start:stop]


def render(stage_root, current_root, output):
    source_stage = json.loads((stage_root / "edition-manifest.json").read_text())
    assert source_stage["sourceRevision"] == SOURCE_REV
    assert source_stage["sourceSHA256"] == SOURCE_SHA
    assert source_stage["paragraphCount"] == 22
    assert len(source_stage["figures"]) == 2
    assert source_stage["figures"][1]["after"] == "client-centered.s2.p6"
    assert not source_stage["productionAuthorized"]
    predecessor = json.loads((current_root / "release-manifest.json").read_text())
    if predecessor["releaseID"] != PREV:
        raise ValueError("Active public predecessor drift")
    old_app_path = current_root / "estate/assets/linotype" / PUBLIC_APP
    old_engine_path = current_root / "estate/assets/linotype" / ORIGINAL_ENGINE
    if sha(old_app_path) != PUBLIC_APP.removeprefix("reading-first-app.").removesuffix(".js"):
        raise ValueError("Current public Reader app SHA drift")
    if sha(old_engine_path) != ENGINE_SHA:
        raise ValueError("Original Linotype engine SHA drift")
    if output.exists():
        raise ValueError("Refuse overwrite of generated publication candidate")
    shutil.copytree(current_root, output, symlinks=False)
    dest = output / PUBLIC_REL
    dest.mkdir(parents=True)
    (dest / "assets/images").mkdir(parents=True)
    for name in (HERO, SECOND):
        shutil.copy2(stage_root / "assets/images" / name, dest / "assets/images" / name)
    for item in source_stage["figures"]:
        if sha(dest / "assets/images" / item["file"]) != item["sha256"]:
            raise ValueError("Illustration/source digest mismatch: " + item["file"])
    tool = shutil.which("rsvg-convert")
    if not tool:
        raise ValueError("Standard SVG rasterizer unavailable")
    out_image = output / SOCIAL
    out_image.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as scratch:
        source_raster = Path(scratch) / "original-plate.png"
        subprocess.run([tool, "-w", "1500", "-h", "980",
                        "-o", str(source_raster),
                        str(dest / "assets/images" / HERO)], check=True)
        subprocess.run([shutil.which("magick"), str(source_raster), "-resize", "1200x630",
                        "-background", "#f7f6f0", "-gravity", "center",
                        "-extent", "1200x630", "-strip", str(out_image)], check=True)
    raw = out_image.read_bytes()
    if not raw.startswith(b"\x89PNG\r\n\x1a\n") or struct.unpack(">II", raw[16:24]) != (1200, 630):
        raise ValueError("Source artwork social derivative invalid")
    social_sha = sha(out_image)
    social_url = "https://fountain.coach/" + SOCIAL.as_posix()

    template = extract_template((stage_root / "index.html").read_text())
    assert template.count('data-inline-after-paragraph="13"') == 1
    assert template.count('data-source-illustration-id="client-centered.method"') == 1
    assert template.count('<section class="book-chapter-text">') == 1
    template = replace_one(
        template,
        '<p class="frame-lead" data-source-block="client-centered.subtitle"',
        '<p class="frame-lead" data-editorial-role="proem" data-source-block="client-centered.subtitle"',
        "source-authored editorial proem semantics"
    )
    # Do not add a second paragraph, change any manuscript text or image geometry.
    base_html = (current_root / "estate/index.html").read_text()
    assert base_html.count("reader-gallery-data") == 1
    assert base_html.count("data-reader-volume=") == 50
    base_html = replace_one(
        base_html,
        ' <script type="application/json" id="reader-gallery-data">',
        template + '\n <script type="application/json" id="reader-gallery-data">',
        "source template injection"
    )
    app = old_app_path.read_text()
    app = replace_one(app, "essaySequence.length!==5||solsticeSequence.length!==32",
                      "essaySequence.length!==6||solsticeSequence.length!==32", "six existing plus new essay")
    app = replace_one(app, "galleries.essays.length!==6||galleries['first-readings'].length!==30",
                      "galleries.essays.length!==7||galleries['first-readings'].length!==30", "seven essay gallery")
    app = replace_one(app,
        'querySelectorAll(\'.frame-editorial-proem[data-editorial-role="proem"]\')',
        'querySelectorAll(\'.frame-editorial-proem[data-editorial-role="proem"],.frame-lead[data-editorial-role="proem"]\')',
        "proem recognition without stylesheet mutation"
    )
    app = app.replace("chapters of the five-essay literary collection.",
                      "chapters of the current literary collection.")
    app_bytes = app.encode()
    app_sha = hashlib.sha256(app_bytes).hexdigest()
    new_app = f"reading-first-app.{app_sha}.js"
    (output / "estate/assets/linotype" / new_app).write_bytes(app_bytes)
    base_html = replace_one(base_html, PUBLIC_APP, new_app, "content-addressed Press app")
    gallery_match = re.search(
        r'(<script type="application/json" id="reader-gallery-data">)(.*?)(</script>)',
        base_html, re.S
    )
    if not gallery_match:
        raise ValueError("Authored Bookshelf gallery not found")
    gallery = json.loads(gallery_match.group(2))
    assert len(gallery["collections"]["essays"]) == 6
    new_entry = {
        "id": "essay--client-centered",
        "src": "/estate/read/essay--client-centered/assets/images/" + HERO,
        "alt": next(x["alt"] for x in source_stage["figures"] if x["file"] == HERO),
        "sourceKind": "source-owned-Teatro-Score-illustration",
        "sourceSHA256": next(x["sha256"] for x in source_stage["figures"] if x["file"] == HERO),
    }
    gallery["collections"]["essays"].insert(0, new_entry)
    new_gallery = json.dumps(gallery, ensure_ascii=False, separators=(",", ":"))
    base_html = (base_html[:gallery_match.start(2)] + new_gallery +
                 base_html[gallery_match.end(2):])
    assert base_html.count('data-reader-volume="essay--client-centered"') == 1
    assert base_html.count(new_app) == 1
    (output / "estate/index.html").write_text(base_html)

    # Production direct route uses that SAME current Fountain Press book with its
    # active seven-essay catalogue, but distinct source-authored page metadata.
    page = replace_one(base_html, 'data-initial-volume="continuity"',
                       'data-initial-volume="essay--client-centered"', "direct essay volume")
    page = re.sub(r'<title>[^<]*</title>',
                  '<title>Client-Centered — Benedikt Eickhoff | Fountain Press</title>', page, count=1)
    page = re.sub(r'<meta name="description"[^>]*>\s*', '', page)
    page = re.sub(r'<link rel="canonical"[^>]*>\s*', '', page)
    page = re.sub(r'<meta name="robots"[^>]*>\s*', '', page)
    page = re.sub(r'<meta property="og:[^"]+"[^>]*>\s*', '', page)
    page = re.sub(r'<meta name="twitter:[^"]+"[^>]*>\s*', '', page)
    page = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', page, flags=re.S)
    abstract = source_stage["subtitle"]
    title = source_stage["title"]
    photo_alt = new_entry["alt"]
    tags = [
        '<link rel="canonical" href="' + URL + '"/>',
        '<meta name="robots" content="index,follow"/>',
        '<meta name="description" content="' + htmllib.escape(abstract, quote=True) + '"/>',
        '<meta name="fountain:source-owner" content="Fountain-Coach/fountain.coach"/>',
        '<meta name="fountain:source-revision" content="' + SOURCE_REV + '"/>',
        '<meta name="fountain:manuscript-sha256" content="' + SOURCE_SHA + '"/>',
        '<meta name="fountain:publication-state" content="published"/>',
        '<meta property="og:type" content="article"/>',
        '<meta property="og:site_name" content="Fountain Coach"/>',
        '<meta property="og:title" content="' + title + '"/>',
        '<meta property="og:description" content="' + htmllib.escape(abstract, quote=True) + '"/>',
        '<meta property="og:url" content="' + URL + '"/>',
        '<meta property="og:image" content="' + social_url + '"/>',
        '<meta property="og:image:secure_url" content="' + social_url + '"/>',
        '<meta property="og:image:type" content="image/png"/>',
        '<meta property="og:image:width" content="1200"/>',
        '<meta property="og:image:height" content="630"/>',
        '<meta property="og:image:alt" content="' + htmllib.escape(photo_alt, quote=True) + '"/>',
        '<meta name="twitter:card" content="summary_large_image"/>',
        '<meta name="twitter:title" content="' + title + '"/>',
        '<meta name="twitter:description" content="' + htmllib.escape(abstract, quote=True) + '"/>',
        '<meta name="twitter:image" content="' + social_url + '"/>',
    ]
    jsonld = {
        "@context": "https://schema.org", "@type": "Article", "headline": title,
        "description": abstract, "url": URL, "mainEntityOfPage": URL,
        "author": {"@type": "Person", "name": "Benedikt Eickhoff"},
        "publisher": {"@type": "Organization", "name": "Fountain Coach"},
        "datePublished": "2026-11-10", "inLanguage": "en", "image": social_url,
        "identifier": "sha256:" + SOURCE_SHA,
        "isPartOf": {"@type": "CollectionPage", "name": "Essays", "url": "https://fountain.coach/estate/"},
    }
    tags.append('<script type="application/ld+json">' +
                json.dumps(jsonld, ensure_ascii=False, separators=(",", ":")) + '</script>')
    page = replace_one(page, "</head>", "\n" + "\n".join(tags) + "\n</head>", "metadata head")
    assert 'noindex,nofollow' not in page
    assert 'WLAN editorial review' not in page
    assert 'client-centered-review.js' not in page
    (dest / "index.html").write_text(page)

    manifest = dict(source_stage)
    manifest.update({
        "schema": "fountain.press.source-owned-essay-publication.v1",
        "publicationState": "published", "productionAuthorized": True,
        "approvedDate": "2026-11-10", "publicRoute": URL,
        "stageRelease": "shared-shell-20261110-v178-client-centered-flow-4a89ae5",
        "stageSourceLockSHA256": STAGE_LOCK,
        "productionRenderer": "original published Linotype engine, SHA-256 " + ENGINE_SHA,
        "currentPublishedEssaysUnchanged": False,
        "publicEssaysCount": 7,
        "publicSocialImage": {"url": social_url, "width": 1200, "height": 630,
                              "mime": "image/png", "sha256": social_sha,
                              "sourceFigureSHA256": new_entry["sourceSHA256"]},
    })
    manifest.pop("stagingAdapter", None)
    (dest / "edition-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    )
    estate_manifest = output / "publication-manifest.json"
    pub = json.loads(estate_manifest.read_text())
    assert pub["publicationState"] == "published"
    if any(x.get("name") == "Client-Centered" for x in pub["publications"]):
        raise ValueError("Publication already registered")
    pub["publications"].append({
        "name": "Client-Centered", "url": URL, "role": "authored-essay",
        "sourceOwner": "Fountain-Coach/fountain.coach", "sourceRevision": SOURCE_REV,
        "sourceSHA256": SOURCE_SHA,
        "image": social_url,
    })
    estate_manifest.write_text(json.dumps(pub, indent=2, ensure_ascii=False) + "\n")

    old_release = output / "release-manifest.json"
    rm = json.loads(old_release.read_text())
    assert rm["releaseID"] == PREV
    rm.update({
        "releaseID": RELEASE, "previousReleaseID": PREV,
        "generatorSHA256": sha(Path(__file__).resolve()),
        "sourceBuilder": "scripts/build_client_centered_press_production.py",
        "sourceRevision": SOURCE_REV,
        "publicationState": "published-client-centered-source-owned",
        "authorDecision": "2026-11-10: publish staged Client-Centered v178 via the existing Fountain Press Reader",
        "contentScope": "Add source-pinned Client-Centered to seven-essay public Bookshelf; preserve all former assets and current Kino publication",
        "stageRelease": "shared-shell-20261110-v178-client-centered-flow-4a89ae5",
        "clientCenteredAdmission": {
            "sourceOwner": "Fountain-Coach/fountain.coach", "sourceRevision": SOURCE_REV,
            "manuscriptSHA256": SOURCE_SHA, "originalPressEngineSHA256": ENGINE_SHA,
            "sourceLockSHA256": STAGE_LOCK, "publicRoute": URL,
            "coverFigureSHA256": new_entry["sourceSHA256"], "socialRasterSHA256": social_sha,
            "publishedCurrentEssayCount": 7, "separatePublicApproval": True,
        },
    })
    rm["addedPaths"] = list(rm.get("addedPaths", []) if isinstance(rm.get("addedPaths"), list) else [])
    rm["addedPaths"].extend([
        (PUBLIC_REL / "index.html").as_posix(),
        (PUBLIC_REL / "edition-manifest.json").as_posix(),
        (PUBLIC_REL / "assets/images" / HERO).as_posix(),
        (PUBLIC_REL / "assets/images" / SECOND).as_posix(),
        SOCIAL.as_posix(),
        "estate/assets/linotype/" + new_app,
    ])
    rm["modifiedPaths"] = list(rm.get("modifiedPaths", [])) + [
        "estate/index.html", "publication-manifest.json", "release-manifest.json"
    ]
    old_release.write_text(json.dumps(rm, indent=2, ensure_ascii=False) + "\n")

    public_template = extract_template(page)
    assert public_template.replace(' data-editorial-role="proem"', "") == extract_template(
        (stage_root / "index.html").read_text()
    ), "Source composition differs from approved staged content"
    assert sha(output / "estate/assets/linotype" / ORIGINAL_ENGINE) == ENGINE_SHA
    output_summary = {
        "schema": "fountain.press.client-centered.production-composition.v1",
        "sourceRevision": SOURCE_REV, "sourceSHA256": SOURCE_SHA,
        "stageRelease": manifest["stageRelease"], "predecessor": PREV,
        "intendedRelease": RELEASE, "newAppSHA256": app_sha,
        "originalPressEngineSHA256": ENGINE_SHA,
        "sourceBlocks": len(manifest["blocks"]), "paragraphs": 22,
        "originalFigureSHA256": [item["sha256"] for item in source_stage["figures"]],
        "socialImageSHA256": social_sha,
        "publicEditionSHA256": sha(dest / "edition-manifest.json"),
        "publicEssayHTMLSHA256": sha(dest / "index.html"),
        "publicBookshelfSHA256": sha(output / "estate/index.html"),
        "sourceMarkupVerifiedEqualToStage": True,
        "publicEssaysCount": 7,
    }
    return output_summary



# Subsequent publication maintenance uses the SAME source/compositor/public
# release pattern.  The first public promotion admitted the work only in
# /estate/index and the work's own route.  Each copied Reader entrance was
# therefore a different, historically frozen catalogue.  This reconciles
# all actual Reader entrances, without altering the semantic manuscript.
META_TAG = re.compile(
    r'<(?:meta|link)\s+[^>]*?/?>(?:\s*)'
    r'|<title>.*?</title>\s*'
    r'|<script type="application/ld\+json">.*?</script>\s*',
    re.S
)


def page_metadata(tag):
    if tag.startswith('<title>'):
        return True
    if tag.startswith('<script type="application/ld+json">'):
        return True
    if tag.startswith('<link '):
        return bool(re.search(r'\brel="canonical"', tag))
    if tag.startswith('<meta '):
        name = re.search(r'\bname="([^"]+)"', tag)
        prop = re.search(r'\bproperty="([^"]+)"', tag)
        if prop and prop.group(1).startswith('og:'):
            return True
        if name:
            key = name.group(1)
            return key in {'description', 'robots', 'fountain:publication-state',
                           'fountain:source-owner', 'fountain:source-revision',
                           'fountain:manuscript-sha256'} or key.startswith('twitter:')
    return False


def extract_head(page):
    if page.count('</head>') != 1:
        raise ValueError('Ambiguous Reader head')
    return page[:page.index('</head>')], page[page.index('</head>'):]


def project_reader_entry(canonical, old, target):
    canonical_head, canonical_tail = extract_head(canonical)
    original_head, _ = extract_head(old)
    # Site metadata is per-path; the complete source-bound Reader shell,
    # assets and edition membership are shared between every entrance.
    preserved = [m.group() for m in META_TAG.finditer(original_head)
                 if page_metadata(m.group())]
    if target in {'index.html','estate/index.html',
                  'estate/bookshelf/index.html','estate/collections/first-readings/index.html'}:
        # These are public entrances, not their historical WLAN previews.
        preserved = [x for x in preserved
                     if not (x.startswith('<meta ') and 'name="robots"' in x)]
        preserved.append('<meta name="robots" content="index,follow"/>\n')
    shell_head = META_TAG.sub(
        lambda m: '' if page_metadata(m.group()) else m.group(),
        canonical_head
    )
    if not any('<title>' in x for x in preserved):
        raise ValueError('Missing route-specific document title: ' + target)
    head = shell_head + '\n' + ''.join(preserved).rstrip() + '\n'
    if target in {'index.html', 'estate/index.html',
                  'estate/bookshelf/index.html', 'estate/read/library/index.html'}:
        volume = 'library'
    elif target == 'estate/collections/first-readings/index.html':
        volume = 'first-readings'
    elif target.startswith('estate/read/'):
        volume = Path(target).parts[2]
    else:
        old_volume = re.search(r'data-initial-volume="([^"]+)"', old)
        if not old_volume:
            raise ValueError('Reader initial volume missing: ' + target)
        volume = old_volume.group(1)
    tail = canonical_tail
    if volume != 'continuity':
        tail = replace_one(tail, 'data-initial-volume="continuity"',
                           'data-initial-volume="' + volume + '"',
                           'Reader initial volume')
    page = head + tail
    # The original per-route HTML assets may be obsolete, but the canonical
    # module and 49 semantic templates must be identical across all entrances.
    if page.count('data-reader-volume="essay--client-centered"') != 1:
        raise ValueError('Work template not admitted: ' + target)
    if page.count('reading-first-app.47b1250c4feb1cd6b920b451d2b0a6dd14207020857600f39192361c3e4fe725.js') != 1:
        raise ValueError('Current Press Reader app not admitted: ' + target)
    if page.count('id="reader-gallery-data"') != 1:
        raise ValueError('Current catalogue not admitted: ' + target)
    if 'noindex,nofollow' in page and target in {
            'index.html', 'estate/index.html', 'estate/bookshelf/index.html'}:
        raise ValueError('Review-only metadata leaked into root: '+target)
    return page


def add_client_centered_to_legacy_essay_gallery(page, figure_alt, target):
    if 'data-essay-gallery=' not in page:
        raise ValueError('Unexpected historic index shell: ' + target)
    if 'data-essay-route="/estate/read/essay--client-centered/"' in page:
        raise ValueError('Already listed, cannot insert twice: ' + target)
    # Retain historical/archived content as source references, but add a real
    # link to the current author-approved source-bound public edition.
    import html as html_helper
    new = (
        '<article class="essay-gallery-card" '
        'data-essay-route="/estate/read/essay--client-centered/">'
        '<a class="essay-gallery-image" '
        'href="/estate/read/essay--client-centered/" aria-label="Read Client-Centered">'
        '<img src="/estate/read/essay--client-centered/assets/images/'
        'client-centered-positions.svg" width="1500" height="980" alt="' +
        html_helper.escape(figure_alt, quote=True) + '"></a>'
        '<div class="essay-gallery-copy"><div class="eyebrow">'
        'ESSAY · NOVEMBER 2026</div><h3><a '
        'href="/estate/read/essay--client-centered/">Client-Centered</a></h3>'
        '<p>On expertise, participation, and the freedom of another person.</p>'
        '</div></article>'
    )
    first = '<article class="essay-gallery-card"'
    if page.count(first) < 5:
        raise ValueError('Historical essay gallery count abnormal: ' + target)
    return page.replace(first, new + first, 1)


def reconcile_public_shell(public_root, output, publisher_revision):
    if not re.fullmatch('[a-f0-9]{40}', publisher_revision):
        raise ValueError('Publisher source revision must be exact 40-character SHA')
    if output.exists():
        raise ValueError('Immutable output already exists')
    before = json.loads((public_root / 'release-manifest.json').read_text())
    if before['releaseID'] != RELEASE:
        raise ValueError('Live public predecessor changed')
    source_manifest = json.loads((public_root / PUBLIC_REL / 'edition-manifest.json').read_text())
    if source_manifest['sourceSHA256'] != SOURCE_SHA or not source_manifest['productionAuthorized']:
        raise ValueError('Source publication not admitted')
    original_client = (public_root / PUBLIC_REL / 'index.html').read_text()
    original_edition_sha = sha(public_root / PUBLIC_REL / 'edition-manifest.json')
    original_social_sha = sha(public_root / SOCIAL)
    if original_social_sha != '7a19bb703dec14ac26cc769884a18e8fb19225556ded172e0307eeaec91ba3ac':
        raise ValueError('Source-owned public social artwork drift')
    press_engine = public_root / 'estate/assets/linotype' / ORIGINAL_ENGINE
    if sha(press_engine) != ENGINE_SHA:
        raise ValueError('Original Press engine changed')
    canonical = (public_root / 'estate/index.html').read_text()
    if canonical.count('data-reader-volume="essay--client-centered"') != 1:
        raise ValueError('Current published work missing from canonical shell')
    gallery_match = re.search(
        r'<script type="application/json" id="reader-gallery-data">(.*?)</script>',
        canonical, re.S
    )
    if not gallery_match:
        raise ValueError('Current Press catalogue unavailable')
    library = json.loads(gallery_match.group(1))
    ids = [e['id'] for e in library['collections']['essays']]
    if len(ids) != 7 or ids[0] != 'essay--client-centered' or len(set(ids)) != 7:
        raise ValueError('Current seven-essay catalogue is not source admitted')
    if len(library['collections']['first-readings']) != 30:
        raise ValueError('First Readings collection drift')
    if output.exists():
        raise ValueError('Output exists')
    shutil.copytree(public_root, output, symlinks=False)
    changed=[]
    entries=[]
    for file in sorted((public_root / 'estate/read').glob('*/index.html')):
        old=file.read_text()
        if 'id="reader-gallery-data"' not in old or 'data-reader-volume=' not in old:
            raise ValueError('Non-Reader entry unexpectedly found: ' + str(file))
        entries.append(file)
    entries.extend([
        public_root/'index.html',
        public_root/'estate/index.html',
        public_root/'estate/bookshelf/index.html',
        public_root/'estate/collections/first-readings/index.html'
    ])
    for file in entries:
        rel=file.relative_to(public_root).as_posix()
        old=file.read_text()
        page=project_reader_entry(canonical, old, rel)
        if page != old:
            (output/rel).write_text(page)
            changed.append(rel)
    # Gallery-only historical pages are still index surfaces.  Do not rewrite
    # their authored historical essays as current books; give their readers
    # the exact source-owned current edition target alongside legacy works.
    figure_alt=next(x['alt'] for x in source_manifest['figures']
                    if x['file'] == HERO)
    for name in ('essays/index.html', 'estate/essays/index.html'):
        old=(public_root/name).read_text()
        page=add_client_centered_to_legacy_essay_gallery(old,figure_alt,name)
        if name == 'essays/index.html' and 'rel="icon"' not in page[:page.index('</head>')]:
            page=replace_one(page,'</head>',
                '<link rel="icon" href="/estate/assets/fountain-coach-logo-transparent.png"/>\n</head>',
                'legacy current-work index favicon')
        if name == 'estate/essays/index.html':
            # The historical alias returns 404. Reuse its already-published
            # content-addressed CSS rather than introducing a new CSS file.
            page=replace_one(page,'href="/assets/estate-shell.css"',
                'href="/assets/estate-shell-d9a170d82a21d19b.css"',
                'existing production stylesheet')
        (output/name).write_text(page)
        changed.append(name)
    # Two older "edition" indexes remain useful historical records.  Keep
    # their original claims and contents, but surface the current published
    # Essays entry point instead of presenting the old draft as today's book.
    edition='estate/editions/index.html'
    page=(public_root/edition).read_text()
    page=replace_one(page,
      'href="/estate/editions/essays-continuing/"',
      'href="/estate/read/essays/"',
      'existing Essays index entry')
    page=replace_one(page,
      'aria-label="Open Essays — A Book Continually Written; seven source-authored chapters, WLAN candidate"',
      'aria-label="Open current Essays in Fountain Press; seven published source-authored essays"',
      'existing Essays index accessible name')
    page=replace_one(page,
      'data-canonical-href="https://fountain.coach/editions/essays-continuing/"',
      'data-canonical-href="https://fountain.coach/estate/read/essays/"',
      'current essays canonical index target')
    # The index's old cover claimed only a WLAN candidate and attributed an
    # obsolete 2026-10 publication artifact to the newly linked public Reader.
    # Its currently displayed link must identify the actual admitted artefact,
    # but preserve the separate First Readings entry without rewriting it.
    item=re.search(r'<li class="shelf-item" data-book-id="fountain-coach".*?</li>',
                   page,re.S)
    if not item:raise ValueError('Current Essays edition card absent')
    before_item=item.group()
    current_item=replace_one(before_item,
        'data-release-status="wlan-proof"',
        'data-release-status="published"', 'public Essays collection status')
    current_item=re.sub(r'data-source-revision="[a-f0-9]{40}"',
        'data-source-revision="'+publisher_revision+'"',current_item,count=1)
    current_item=re.sub(r'data-reader-artifact-sha256="[a-f0-9]{64}"',
        'data-reader-artifact-sha256="'+sha(output/'estate/index.html')+'"',
        current_item,count=1)
    current_item=current_item.replace(' data-preview-host="fountain"','')
    if current_item==before_item:
        raise ValueError('Current Essays provenance did not reconcile')
    page=replace_one(page,before_item,current_item,'single existing Essays edition entry')
    (output/edition).write_text(page)
    changed.append(edition)

    catalogue='estate/editions/catalogue/index.html'
    page=(public_root/catalogue).read_text()
    anchor='Read the edition <span aria-hidden="true">→</span></a></p>'
    page=replace_one(page,anchor,anchor+
      '<p><a class="edition-open" href="/estate/read/essays/">'
      'Read the current seven-essay Fountain Press collection '
      '<span aria-hidden="true">→</span></a></p>',
      'historical three-essay index access to current edition')
    page=replace_one(page,'href="/assets/estate-shell.css"',
        'href="/assets/estate-shell-d9a170d82a21d19b.css"',
        'current authenticated estate stylesheet')
    (output/catalogue).write_text(page)
    changed.append(catalogue)

    # The historical continuing book is NOT an index and remains source-owned,
    # without being silently rebuilt or containing an invented new chapter.
    if original_edition_sha != sha(output/PUBLIC_REL/'edition-manifest.json'):
        raise ValueError('Original essay semantic manifest changed')
    if original_social_sha != sha(output/SOCIAL):
        raise ValueError('Original social image changed')
    if original_client != (output/PUBLIC_REL/'index.html').read_text() and (
        extract_template(original_client) != extract_template(
          (output/PUBLIC_REL/'index.html').read_text())):
        raise ValueError('Original source manuscript projection changed')

    previous_release=output/'release-manifest.json'
    data=json.loads(previous_release.read_text())
    data['previousReleaseID']=RELEASE
    data['releaseID']='fcis-client-centered-shell-20261110-'+publisher_revision[:7]
    data['sourceRevision']=publisher_revision
    data['publicationState']='published-client-centered-all-reader-indexes-reconciled'
    data['authorDecision']='2026-11-10: correct misintegrated index-like publication shell across existing public Reader entrances'
    data['contentScope']='Seven-essay Bookshelf and all existing Reader entry routes; original manuscript and old editions intact'
    data['clientCenteredShellReconciliation']={
        'sourceOwner':'Fountain-Coach/fountain.coach',
        'publisherSourceRevision':publisher_revision,
        'workSourceRevision':SOURCE_REV,
        'workSourceSHA256':SOURCE_SHA,
        'originalPressEngineSHA256':ENGINE_SHA,
        'sourceEditionManifestSHA256':original_edition_sha,
        'sourceSocialSHA256':original_social_sha,
        'readerEntryRouteCount':len(entries),
        'readerCurrentEssayCount':7,
        'firstReadingsCount':30,
        'modifiedRouteHTML':sorted(changed),
        'preservedOriginalHistoricalEdition':True,
        'productionActivationAuthorized':True,
    }
    data['modifiedPaths']=sorted(set(data.get('modifiedPaths',[]))|set(changed)|{'release-manifest.json'})
    previous_release.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n')
    actual_changed=[]
    old_files={q.relative_to(public_root).as_posix():q for q in public_root.rglob('*') if q.is_file()}
    new_files={q.relative_to(output).as_posix():q for q in output.rglob('*') if q.is_file()}
    if set(old_files)!=set(new_files):
        raise ValueError('Unrelated existing site files added/deleted')
    for key,file in old_files.items():
        if sha(file)!=sha(new_files[key]):
            actual_changed.append(key)
    if set(actual_changed)!=set(changed)|{'release-manifest.json'}:
        raise ValueError('Undeclared public mutation: '+str(sorted(set(actual_changed)^set(changed)|{'release-manifest.json'})))
    print(json.dumps({
        'schema':'fountain.press.reader-index-reconciliation.v1',
        'publisherSourceRevision':publisher_revision,
        'manuscriptSourceRevision':SOURCE_REV,
        'previousReleaseID':RELEASE,
        'releaseID':data['releaseID'],
        'filesPreserved':len(old_files)-len(actual_changed),
        'readerRoutes':len(entries),
        'modifiedPaths':sorted(actual_changed),
        'currentEssays':ids,
        'firstReadings':30,
        'workManifestSHA256':original_edition_sha,
        'workSocialSHA256':original_social_sha,
        'originalEngineSHA256':ENGINE_SHA,
    },indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--public-baseline", type=Path, required=True)
    ap.add_argument("--staged-essay", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--reconcile-shell", action="store_true")
    ap.add_argument("--publisher-revision")
    args=ap.parse_args()
    if args.reconcile_shell:
        if not args.publisher_revision:
            ap.error("--publisher-revision required when reconciling shell")
        reconcile_public_shell(args.public_baseline,args.output,args.publisher_revision)
    else:
        if not args.staged_essay:
            ap.error("--staged-essay is required for initial production projection")
        print(json.dumps(render(args.staged_essay,args.public_baseline,args.output),
                         indent=2, ensure_ascii=False))
