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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--public-baseline", type=Path, required=True)
    ap.add_argument("--staged-essay", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = render(args.staged_essay, args.public_baseline, args.output)
    print(json.dumps(result, indent=2, ensure_ascii=False))
