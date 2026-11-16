#!/usr/bin/env python3
"""Build a source-bound public Better Ear essay in the active Fountain Press Reader.

The input is the exact, verified active public release and the private, admitted
Press route. EstatePublisher alone delivers the resulting immutable site.
"""
import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import shutil
import subprocess

TITLE = "A Better Ear for Fountain Coach"
SUBTITLE = "On listening, measurement, and musical judgment"
SLUG = "a-better-ear-for-fountain-coach"
PUBLIC_ROUTE = f"https://fountain.coach/estate/read/essay--{SLUG}/"
PUBLIC_REL = Path("estate/read") / f"essay--{SLUG}"
SOURCE_REL = Path("site/essays") / SLUG / f"{SLUG}.md"
ALT = "An axonometric listening chamber receives a terracotta sound pulse and returns a measured path across a layered floor."
AUDIO = {
    "csound-control.m4a": ("Csound output without Ear mapping", "d8a02db7222b25a0dd886c355b23d75b4ba9a38190cf6da622cc80961cee8b27"),
    "csound-by-ear.m4a": ("Csound output shaped by Ear RMS through MIDI 2.0 CC74", "48afe2ca50be06da1a5276413a9b368ca58ff23a826310400462907585bc28e0"),
}
OUTBOUND_STYLE = (
    '<style id="better-ear-outbound-link-style">'
    '#work-a-better-ear-for-fountain-coach ~ .book-chapter-text .frame-link-out-mark{font-family:Georgia,"Times New Roman",serif;'
    'font-variant-emoji:text;font-size:.48em;font-weight:400;font-style:normal;'
    'line-height:inherit;color:inherit;background:none;border:0;border-radius:0;vertical-align:baseline}'
    '</style>'
)

def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()

def sha(path):
    return sha_bytes(path.read_bytes())

def require_one(value, old, new, label):
    n = value.count(old)
    if n != 1:
        raise ValueError(f"{label}: expected exactly one match, found {n}")
    return value.replace(old, new, 1)

def parse_markdown(path):
    raw = path.read_text("utf-8")
    prefix = f"# {TITLE}\n\n*{SUBTITLE}*\n\n"
    if not raw.startswith(prefix):
        raise ValueError("Essay title or subtitle differs from publication source")
    paragraphs = [p.strip().replace("\n", " ") for p in raw[len(prefix):].split("\n\n") if p.strip()]
    if len(paragraphs) != 19:
        raise ValueError(f"Expected 19 source paragraphs; found {len(paragraphs)}")
    return raw, paragraphs

def render_paragraph(text, number):
    link_re = re.compile(r"\[([^\]]+)\]\((https?://[^)]+|/[^)\s]+|#[^)]*)\)")
    chunks, pos = [], 0
    for match in link_re.finditer(text):
        chunks.append(html.escape(text[pos:match.start()]))
        href = html.escape(match.group(2), quote=True)
        label = html.escape(match.group(1))
        if match.group(2).startswith(("https://", "http://")):
            spoken = html.escape(match.group(1) + " (external site)", quote=True)
            chunks.append(
                f'<a class="frame-link-out" href="{href}" aria-label="{spoken}">'
                f'{label}<span class="frame-link-out-mark" aria-hidden="true"> ↗︎</span></a>'
            )
        else:
            chunks.append(f'<a href="{href}">{label}</a>')
        pos = match.end()
    chunks.append(html.escape(text[pos:]))
    rendered = "".join(chunks)
    return (f'<p data-source-block="better-ear.p{number}" data-source-from="0" '
            f'data-source-to="{len(text)}">{rendered}</p>')

def replace_source_paragraphs(template, paragraphs):
    pattern = re.compile(r'<p\b[^>]*data-source-block="better-ear\.p([0-9]+)"[^>]*>.*?</p>', re.S)
    seen = []
    def substitute(match):
        number = int(match.group(1))
        if not 1 <= number <= len(paragraphs):
            raise ValueError("Unexpected essay source block")
        seen.append(number)
        return render_paragraph(paragraphs[number - 1], number)
    result, count = pattern.subn(substitute, template)
    if count != 19 or sorted(seen) != list(range(1, 20)):
        raise ValueError(f"Stage template source blocks are incomplete: {seen}")
    result = require_one(
        result,
        '<p class="frame-lead" data-source-block="better-ear.subtitle"',
        '<p class="frame-lead" data-editorial-role="proem" data-source-block="better-ear.subtitle"',
        "Reader editorial proem"
    )
    if result.count('class="frame-link-out"') != 7:
        raise ValueError("Rendered essay outbound links do not match source")
    return result

def build(args):
    repo = Path(args.repo).resolve()
    source = repo / SOURCE_REL
    hero = repo / "site/essays" / SLUG / "assets/a-better-ear-hero.jpg"
    raw, paragraphs = parse_markdown(source)
    source_sha = sha_bytes(raw.encode("utf-8"))
    source_revision = args.source_revision
    if not re.fullmatch(r"[0-9a-f]{40}", source_revision):
        raise ValueError("Source revision must be an exact merged Git SHA")

    current = Path(args.current_root).resolve()
    stage = Path(args.stage_route).resolve()
    stage_manifest_path = stage / "edition-manifest.json"
    stage_manifest = json.loads(stage_manifest_path.read_text("utf-8"))
    if stage_manifest.get("sourceSHA256") != source_sha:
        raise ValueError("Stage manuscript hash does not match canonical source")
    if stage_manifest.get("publicationState") != "private-owner-WLAN-review" or stage_manifest.get("productionAuthorized") is not False:
        raise ValueError("Stage must remain a private review artifact")
    stage_index = (stage / "index.html").read_text("utf-8")
    if 'name="robots" content="noindex,nofollow"' not in stage_index:
        raise ValueError("Stage route must remain noindex")
    if stage_manifest.get("paragraphCount") != 19:
        raise ValueError("Stage paragraph count mismatch")

    stage_receipt = json.loads(Path(args.stage_receipt).read_text("utf-8"))
    if (stage_receipt.get("state") != "active" or
        stage_receipt.get("releaseID") != args.stage_release or
        stage_receipt.get("sourceSHA256") != source_sha or
        stage_receipt.get("exactHTTPResources") != 16 or
        stage_receipt.get("exactCsoundMedia") != 2 or
        stage_receipt.get("productionAffected") is not False or
        stage_receipt.get("noindex") is not True):
        raise ValueError("Private-stage terminal receipt does not prove this source/media set")
    inventory_path = Path(args.stage_inventory)
    inventory = json.loads(inventory_path.read_text("utf-8"))
    if inventory.get("sourceSHA256") != source_sha or len(inventory.get("files", {})) != 16:
        raise ValueError("Stage file inventory does not match the essay/media source")
    for rel, digest in inventory["files"].items():
        f = stage / rel
        if not f.is_file() or f.is_symlink() or sha(f) != digest:
            raise ValueError("Stage file inventory mismatch: " + rel)
    for name, (_, expected) in AUDIO.items():
        if sha(repo / "site/essays" / SLUG / "assets/audio" / name) != expected:
            raise ValueError("Source audio digest mismatch: " + name)
        if sha(stage / "assets/audio" / name) != expected:
            raise ValueError("Stage audio digest mismatch: " + name)

    marker = f'<template data-reader-volume="essay--{SLUG}">'
    template_match = re.search(re.escape(marker) + r".*?</template>", stage_index, re.S)
    if not template_match:
        raise ValueError("Stage reader volume template is missing")
    template = replace_source_paragraphs(template_match.group(0), paragraphs)
    if '/teatro/experiments/composing-by-ear/' in template or '/estate/essays/the-ear-that-learns/' in template:
        raise ValueError("Private or source-candidate route survived source projection")
    if template.count('/assets/audio/csound-control.m4a') < 2 or template.count('/assets/audio/csound-by-ear.m4a') < 2:
        raise ValueError("Reader audio controls do not resolve to the source-owned recordings")

    if args.previous_release != "fountain-press-if-only-20261113-4258957":
        raise ValueError("Active production predecessor changed; inspect it before rebuilding")
    if current.is_symlink() or not current.is_dir():
        raise ValueError("Current public snapshot must be a real directory")
    old_index = current / "estate/index.html"
    old_root_index = current / "index.html"
    if old_index.read_bytes() != old_root_index.read_bytes():
        raise ValueError("Current root and Estate Reader are not the same Bookshelf")
    if json.loads((current / "release-manifest.json").read_text("utf-8")).get("publicationState") != "public-release-authorized":
        raise ValueError("Current public release manifest is not authorized")
    if Path(args.output).exists():
        raise ValueError("Refusing to overwrite an existing immutable build")

    output = Path(args.output).resolve()
    shutil.copytree(current, output, symlinks=False)
    route = output / PUBLIC_REL
    route.mkdir(parents=True)
    (route / "assets/images").mkdir(parents=True)
    (route / "assets/audio").mkdir(parents=True)
    shutil.copy2(hero, route / "assets/images/a-better-ear-hero.jpg")
    for name in AUDIO:
        shutil.copy2(repo / "site/essays" / SLUG / "assets/audio" / name, route / "assets/audio" / name)
    hero_sha = sha(hero)
    hero_url = f"https://fountain.coach/{PUBLIC_REL.as_posix()}/assets/images/a-better-ear-hero.jpg"
    social_rel = Path("estate/assets/social") / f"a-better-ear-{source_revision[:8]}.png"
    social_file = output / social_rel
    social_file.parent.mkdir(parents=True, exist_ok=True)
    magick = shutil.which("magick")
    if not magick:
        raise ValueError("ImageMagick magick executable is required for the established social derivative")
    subprocess.run([magick, str(hero), "-resize", "1200x630", "-background", "#f7f6f0",
                    "-gravity", "center", "-extent", "1200x630", "-strip", str(social_file)], check=True)
    social_sha = sha(social_file)
    social_url = "https://fountain.coach/" + social_rel.as_posix()

    base_html = old_index.read_text("utf-8")
    app_match = re.search(r'(/estate/assets/linotype/reading-first-app\.([a-f0-9]{64})\.js)', base_html)
    engine_match = re.search(r'(/estate/assets/linotype/reading-first-press-engine\.([a-f0-9]{64})\.js)', base_html)
    if not app_match or not engine_match:
        raise ValueError("Active public Press runtime references are missing")
    app_rel, app_old_sha = app_match.group(1).lstrip("/"), app_match.group(2)
    engine_rel, engine_sha = engine_match.group(1).lstrip("/"), engine_match.group(2)
    app_file = current / app_rel
    engine_file = current / engine_rel
    if sha(app_file) != app_old_sha or sha(engine_file) != engine_sha:
        raise ValueError("Active Press runtime content address is not valid")
    app = app_file.read_text("utf-8")
    app = require_one(app, "essaySequence.length!==8", "essaySequence.length!==9", "Essay sequence cardinality")
    app = require_one(app, "galleries.essays.length!==9", "galleries.essays.length!==10", "Essay Bookshelf cardinality")
    app_bytes = app.encode("utf-8")
    app_sha = sha_bytes(app_bytes)
    app_name = f"reading-first-app.{app_sha}.js"
    new_app = output / "estate/assets/linotype" / app_name
    new_app.write_bytes(app_bytes)

    base_html = require_one(base_html, app_match.group(1), "/" + str(Path("estate/assets/linotype") / app_name), "Content-addressed Reader app")
    base_html = require_one(base_html, ' <script type="application/json" id="reader-gallery-data">', template + '\n <script type="application/json" id="reader-gallery-data">', "Reader source template injection")
    gallery_match = re.search(r'(<script type="application/json" id="reader-gallery-data">)(.*?)(</script>)', base_html, re.S)
    if not gallery_match:
        raise ValueError("Public Bookshelf gallery JSON is missing")
    gallery = json.loads(gallery_match.group(2))
    essays = gallery["collections"]["essays"]
    if len(essays) != 9 or any(item.get("id") == f"essay--{SLUG}" for item in essays):
        raise ValueError("Public Bookshelf membership predecessor changed")
    entry = {
        "id": f"essay--{SLUG}",
        "src": f"/{PUBLIC_REL.as_posix()}/assets/images/a-better-ear-hero.jpg",
        "alt": ALT,
        "sourceKind": "source-owned-essay-hero",
        "sourceSHA256": hero_sha,
    }
    essays.insert(0, entry)
    gallery_bytes = json.dumps(gallery, ensure_ascii=False, separators=(",", ":"))
    base_html = base_html[:gallery_match.start(2)] + gallery_bytes + base_html[gallery_match.end(2):]
    if base_html.count(marker) != 1:
        raise ValueError("Reader template was not admitted exactly once")
    if base_html.count("reader-gallery-data") != 1:
        raise ValueError("Reader gallery must remain singular")
    base_html = require_one(base_html, "</head>", OUTBOUND_STYLE + "</head>", "Baseline-aligned Linotype outbound cue")
    (output / "estate/index.html").write_text(base_html, "utf-8")
    (output / "index.html").write_text(base_html, "utf-8")

    page = require_one(base_html, 'data-initial-volume="continuity"',
                       f'data-initial-volume="essay--{SLUG}"', "Direct essay volume")
    page = re.sub(r"<title>[^<]*</title>", f"<title>{TITLE} · Fountain Coach</title>", page, count=1)
    page = re.sub(r'<meta name="description"[^>]*>\s*', "", page)
    page = re.sub(r'<link rel="canonical"[^>]*>\s*', "", page)
    page = re.sub(r'<meta name="robots"[^>]*>\s*', "", page)
    page = re.sub(r'<meta property="og:[^"]+"[^>]*/>\s*', "", page)
    page = re.sub(r'<meta name="twitter:[^"]+"[^>]*/>\s*', "", page)
    page = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', "", page, flags=re.S)
    tags = [
        f'<link rel="canonical" href="{PUBLIC_ROUTE}"/>',
        '<meta name="robots" content="index,follow"/>',
        f'<meta name="description" content="{html.escape(SUBTITLE, quote=True)}"/>',
        '<meta name="fountain:source-owner" content="Fountain-Coach/fountain.coach"/>',
        f'<meta name="fountain:source-revision" content="{source_revision}"/>',
        f'<meta name="fountain:manuscript-sha256" content="{source_sha}"/>',
        '<meta name="fountain:publication-state" content="published"/>',
        '<meta property="og:type" content="article"/>',
        '<meta property="og:site_name" content="Fountain Coach"/>',
        f'<meta property="og:title" content="{TITLE}"/>',
        f'<meta property="og:description" content="{html.escape(SUBTITLE, quote=True)}"/>',
        f'<meta property="og:url" content="{PUBLIC_ROUTE}"/>',
        f'<meta property="og:image" content="{social_url}"/>',
        f'<meta property="og:image:secure_url" content="{social_url}"/>',
        '<meta property="og:image:type" content="image/png"/>',
        '<meta property="og:image:width" content="1200"/>',
        '<meta property="og:image:height" content="630"/>',
        f'<meta property="og:image:alt" content="{html.escape(ALT, quote=True)}"/>',
        '<meta name="twitter:card" content="summary_large_image"/>',
        f'<meta name="twitter:title" content="{TITLE}"/>',
        f'<meta name="twitter:description" content="{html.escape(SUBTITLE, quote=True)}"/>',
        f'<meta name="twitter:image" content="{social_url}"/>',
    ]
    jsonld = {
        "@context": "https://schema.org", "@type": "Article", "headline": TITLE,
        "description": SUBTITLE, "url": PUBLIC_ROUTE, "mainEntityOfPage": PUBLIC_ROUTE,
        "author": {"@type": "Person", "name": "Benedikt Eickhoff"},
        "publisher": {"@type": "Organization", "name": "Fountain Coach"},
        "datePublished": args.publication_date, "inLanguage": "en", "image": social_url,
        "identifier": "sha256:" + source_sha,
        "isPartOf": {"@type": "CollectionPage", "name": "Essays", "url": "https://fountain.coach/estate/"},
    }
    tags.append('<script type="application/ld+json">' +
                json.dumps(jsonld, ensure_ascii=False, separators=(",", ":")) + '</script>')
    page = require_one(page, "</head>", "\n" + "\n".join(tags) + "\n</head>", "Public metadata")
    if "noindex,nofollow" in page or "WLAN editorial review" in page:
        raise ValueError("Private staging metadata survived")
    (route / "index.html").write_text(page, "utf-8")

    edition = {
        "schema": "fountain.press.source-owned-essay-publication.v1",
        "title": TITLE, "subtitle": SUBTITLE, "sourceOwner": "Fountain-Coach/fountain.coach",
        "sourcePath": SOURCE_REL.as_posix(), "sourceRevision": source_revision, "sourceSHA256": source_sha,
        "publicationState": "published", "productionAuthorized": True,
        "approvedDate": args.publication_date, "publicRoute": PUBLIC_ROUTE,
        "stageRelease": args.stage_release,
        "stageSourceRevision": stage_receipt["sourceRevision"],
        "stageInventorySHA256": sha(inventory_path),
        "productionRenderer": f"active public Fountain Press Reader engine SHA-256 {engine_sha}",
        "sameReaderAndEngine": True, "bookshelfMembershipAdded": True,
        "robots": "index,follow",
        "hero": {"file": "assets/images/a-better-ear-hero.jpg", "sha256": hero_sha,
                 "width": 1536, "height": 1024, "alt": ALT},
        "recordedAudio": {
            name: {"file": "assets/audio/" + name, "sha256": expected, "role": role}
            for name, (role, expected) in AUDIO.items()
        },
        "paragraphCount": len(paragraphs),
        "sourceBlocks": [f"better-ear.p{i}" for i in range(1, 20)],
        "publicSocialImage": {"url": social_url, "width": 1200, "height": 630,
                              "mime": "image/png", "sha256": social_sha,
                              "sourceFigureSHA256": hero_sha},
    }
    (route / "edition-manifest.json").write_text(json.dumps(edition, ensure_ascii=False, indent=2) + "\n")

    pub_file = output / "publication-manifest.json"
    pub = json.loads(pub_file.read_text("utf-8"))
    if any(item.get("name") == TITLE for item in pub.get("publications", [])):
        raise ValueError("Publication already exists in estate manifest")
    pub["publications"].append({
        "name": TITLE, "url": PUBLIC_ROUTE, "role": "authored-audio-essay",
        "sourceOwner": "Fountain-Coach/fountain.coach", "sourceRevision": source_revision,
        "sourceSHA256": source_sha, "image": social_url,
        "audio": [PUBLIC_ROUTE + "assets/audio/" + name for name in AUDIO],
    })
    pub_file.write_text(json.dumps(pub, ensure_ascii=False, indent=2) + "\n")

    release_id = f"fountain-press-better-ear-{args.publication_date.replace('-', '')}-{source_revision[:7]}"
    release_manifest_path = output / "release-manifest.json"
    rm = json.loads(release_manifest_path.read_text("utf-8"))
    rm.update({
        "schema": "fountain.press.source-bound-static-release.v1",
        "host": "fountain.coach", "releaseID": release_id,
        "releaseMode": "EstatePublisher-SSH-static-immutable",
        "previousReleaseID": args.previous_release,
        "publicationState": "public-release-authorized",
        "sourceRepo": "Fountain-Coach/fountain.coach", "sourceRevision": source_revision,
        "sourceSHA256": source_sha, "stageRelease": args.stage_release,
        "stageSourceLockSHA256": sha(inventory_path),
        "approvedWork": f"essay--{SLUG}", "workRoute": PUBLIC_ROUTE,
        "collectionRoute": "https://fountain.coach/estate/",
        "heroOriginalSHA256": hero_sha, "socialDerivativeSHA256": social_sha,
        "publicationDecision": "Author instructed public publication to Essays of the Fountain Coach estate, 2026-11-16",
        "publicationExclusions": ["live Csound service", "private Sing source WAV", "unreleased staging pages"],
        "machineRoutes": ["/estate/books/catalog.json", f"/{PUBLIC_REL.as_posix()}/edition-manifest.json"],
    })
    rm["addedPaths"] = list(rm.get("addedPaths", [])) if isinstance(rm.get("addedPaths", []), list) else []
    rm["modifiedPaths"] = list(rm.get("modifiedPaths", [])) if isinstance(rm.get("modifiedPaths", []), list) else []
    rm["addedPaths"].extend([
        PUBLIC_REL.as_posix() + "/index.html",
        PUBLIC_REL.as_posix() + "/edition-manifest.json",
        PUBLIC_REL.as_posix() + "/assets/images/a-better-ear-hero.jpg",
        PUBLIC_REL.as_posix() + "/assets/audio/csound-control.m4a",
        PUBLIC_REL.as_posix() + "/assets/audio/csound-by-ear.m4a",
        social_rel.as_posix(), "estate/assets/linotype/" + app_name,
    ])
    rm["modifiedPaths"].extend(["index.html", "estate/index.html", "publication-manifest.json", "release-manifest.json"])
    rm["newWork"] = {
        "title": TITLE, "route": PUBLIC_ROUTE, "sourceRevision": source_revision,
        "sourceSHA256": source_sha, "stageRelease": args.stage_release,
        "stageSourceLockSHA256": sha(inventory_path), "audioSHA256": {name: expected for name, (_, expected) in AUDIO.items()},
        "bookshelfEssayCount": 10, "previousEssayCount": 9,
    }
    (output / "release-manifest.json").write_text(json.dumps(rm, ensure_ascii=False, indent=2) + "\n")
    if base_html != (output / "estate/index.html").read_text("utf-8"):
        raise ValueError("Bookshelf base projection changed after admission")
    for name, (_, expected) in AUDIO.items():
        if sha(route / "assets/audio" / name) != expected:
            raise ValueError("Published audio source bytes changed")
    result = {
        "schema": "fountain.press.better-ear.public-composition.v1",
        "releaseID": release_id, "previousReleaseID": args.previous_release,
        "sourceRevision": source_revision, "sourceSHA256": source_sha,
        "stageRelease": args.stage_release, "stageInventorySHA256": sha(inventory_path),
        "rendererSHA256": engine_sha, "appSHA256": app_sha,
        "publicRoute": PUBLIC_ROUTE, "routeFiles": 5,
        "essayGalleryCount": 10, "paragraphs": 19,
        "audioSHA256": {name: expected for name, (_, expected) in AUDIO.items()},
        "socialSHA256": social_sha,
    }
    Path(args.summary).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--repo", required=True)
    p.add_argument("--stage-route", required=True)
    p.add_argument("--stage-inventory", required=True)
    p.add_argument("--stage-receipt", required=True)
    p.add_argument("--stage-release", required=True)
    p.add_argument("--current-root", required=True)
    p.add_argument("--previous-release", required=True)
    p.add_argument("--source-revision", required=True)
    p.add_argument("--publication-date", default="2026-11-16")
    p.add_argument("--output", required=True)
    p.add_argument("--summary", required=True)
    build(p.parse_args())

if __name__ == "__main__":
    main()
