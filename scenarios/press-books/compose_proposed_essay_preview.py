#!/usr/bin/env python3
"""Compose a source-pinned, NOINDEX Fountain Press editorial preview.

This is a compiler, not an activator. The original Linotype Reader and all
published works are retained. EstatePublisher owns every remote activation.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

from publication_closure import verify as verify_closure
from published_frontend import GALLERY_PATTERN, source_templates
from published_frontend_stage import preserve_book_meta

HERE = Path(__file__).resolve().parent
WORK = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
VOL = re.compile(r'<template data-reader-volume="(essay--[^"]+)"[^>]*>')
SCRIPT = r'(<script type="application/json" id="{id}">)(.*?)(</script>)'


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(obj: object) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"{label}: expected one match, got {text.count(old)}")
    return text.replace(old, new, 1)


def json_script(page: str, identity: str) -> tuple[dict, str]:
    pattern = re.compile(SCRIPT.format(id=re.escape(identity)), re.S)
    found = pattern.findall(page)
    if len(found) != 1:
        raise ValueError("Missing/duplicate source script " + identity)
    return json.loads(found[0][1]), "".join(found[0])


def with_json(page: str, identity: str, payload: dict) -> str:
    _, old = json_script(page, identity)
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    return replace_once(
        page, old,
        '<script type="application/json" id="' + identity + '">' + body + "</script>",
        "source script " + identity,
    )


def metadata(source: str) -> dict[str, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", source, re.S)
    if not match:
        raise ValueError("Missing source-owned frontmatter")
    fields = dict(re.findall(r'^([a-z_]+):\s*(.+)$', match.group(1), re.M))
    fields = {key: value.strip().strip('"') for key, value in fields.items()}
    for key in ("title", "subtitle", "date", "status"):
        if not fields.get(key):
            raise ValueError("Missing source metadata " + key)
    if fields["status"] != "proposed":
        raise ValueError("Only unadmitted, proposed manuscripts may use this preview lane")
    return fields


def render_template(source_file: Path, work_id: str, stage: Path):
    manuscript = source_file.read_bytes()
    fields = metadata(manuscript.decode())
    slug = work_id.removeprefix("essay--")
    preview_path = Path("estate/read") / work_id / "assets"
    rendered = subprocess.run(
        ["pandoc", "--from=markdown-smart+yaml_metadata_block",
         "--to=html5", "--wrap=none", str(source_file)],
        check=True, text=True, capture_output=True,
    ).stdout.splitlines()
    if len(rendered) < 5 or not rendered[0].startswith("<h1 "):
        raise ValueError("Unexpected source Markdown structure")
    if html.unescape(re.sub("<[^>]*>", "", rendered[0])) != fields["title"]:
        raise ValueError("Markdown title differs from frontmatter")
    if html.unescape(re.sub("<[^>]*>", "", rendered[1])) != fields["subtitle"]:
        raise ValueError("Markdown subtitle differs from frontmatter")
    blocks = []
    figure_records = []
    paragraph = 0
    for line in rendered[2:]:
        if line == '<h2 id="abstract">Abstract</h2>':
            blocks.append(
                '<p class="frame-subheading" data-source-block="' +
                slug + '.abstract-heading">Abstract</p>'
            )
        elif line.strip() == "<hr />":
            blocks.append('<hr class="frame-section-rule" data-source-block="' +
                          slug + '.abstract-end"/>')
        elif line.startswith('<p><img src="figures/'):
            image = re.fullmatch(
                r'<p><img src="figures/([^"]+)" alt="([^"]+)" /> <em>(.*?)</em></p>',
                line, re.S,
            )
            if not image:
                raise ValueError("Unrecognized manuscript figure/caption")
            name, alt, caption = image.groups()
            if not re.fullmatch(r"[0-9]{2}-[a-z0-9-]+\.svg", name):
                raise ValueError("Unsafe source figure filename")
            original = source_file.parent / "figures" / name
            if not original.is_file() or original.is_symlink():
                raise ValueError("Missing source-owned figure " + name)
            raw = original.read_bytes()
            dims = re.search(rb'viewBox="[\d.]+\s+[\d.]+\s+([\d.]+)\s+([\d.]+)"', raw)
            width, height = (int(float(x)) for x in dims.groups()) if dims else (1100, 640)
            target = stage / preview_path / "figures" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            image_url = "/" + (preview_path / "figures" / name).as_posix()
            figure_records.append({
                "sourcePath": str(original.relative_to(source_file.parent.parent.parent.parent)),
                "publishedPath": image_url, "sha256": sha(raw),
                "alt": html.unescape(alt), "caption": html.unescape(re.sub("<[^>]*>", "", caption)),
            })
            blocks.append(
                '<figure class="frame-reading-figure" data-source-block="' + slug +
                f'.figure-{len(figure_records):02d}" data-source-plate-sha256="{sha(raw)}" ' +
                f'data-inline-after-paragraph="{paragraph}">' +
                f'<img loading="eager" decoding="sync" src="{image_url}" alt="{alt}" ' +
                f'width="{width}" height="{height}"/><figcaption>{caption}</figcaption></figure>'
            )
        elif line.startswith("<p>") and line.endswith("</p>"):
            paragraph += 1
            plain = html.unescape(re.sub("<[^>]*>", "", line[3:-4]))
            blocks.append(line.replace(
                "<p>", f'<p data-source-block="{slug}.p{paragraph:02d}" ' +
                f'data-source-from="0" data-source-to="{len(plain)}">', 1
            ))
        else:
            raise ValueError("Unrecognized manuscript paragraph: " + line[:90])
    if len(figure_records) != 3:
        raise ValueError("Expected three declared source-anchored plates")
    header = (
        f'<template data-reader-volume="{work_id}" data-editorial-state="proposed" '
        f'data-source-sha256="{sha(manuscript)}"><div class="book-flow" '
        f'data-min-leaves="1" data-source-work-sha256="{sha(manuscript)}">'
        f'<section class="book-chapter" id="work-{slug}">'
        '<div class="book-chapter-heading">'
        f'<h2 data-source-block="{slug}.title">{html.escape(fields["title"])}</h2>'
        f'<div class="frame-source" data-source-block="{slug}.subtitle">'
        f'{html.escape(fields["subtitle"])}</div></div></section>'
        '<section class="book-chapter-text"><article class="book-prose">'
        f'<p class="frame-edition-imprint" data-source-block="{slug}.editorial-status">'
        f'Editorial preview · Proposed · {html.escape(fields["date"])}</p>'
    )
    return header + "\n".join(blocks) + "</article></section></div></template>", fields, figure_records


def compose(args: argparse.Namespace):
    origin = args.source.resolve(strict=True)
    repo = args.repository.resolve(strict=True)
    manuscript = (repo / args.manuscript).resolve(strict=True)
    if not manuscript.is_relative_to(repo / "site" / "essays"):
        raise ValueError("Manuscript must reside in the owned essays source tree")
    revision = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "--verify",
         args.revision + "^{commit}"], check=True, text=True, capture_output=True,
    ).stdout.strip()
    if revision != args.revision:
        raise ValueError("Source revision drift")
    paths = [manuscript, *sorted((manuscript.parent / "figures").glob("*.svg"))]
    relpaths = [str(p.relative_to(repo)) for p in paths]
    pinned = subprocess.run(
        ["git", "-C", str(repo), "diff", "--quiet", revision, "--", *relpaths],
        check=False, capture_output=True,
    )
    if pinned.returncode != 0:
        raise ValueError("Source revision drift: manuscript/figure bytes changed")
    dirty = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain", "--", *relpaths],
        check=True, text=True, capture_output=True,
    ).stdout.strip()
    if dirty:
        raise ValueError("Uncommitted manuscript or figures")
    slug = manuscript.parent.name
    if not WORK.fullmatch(slug):
        raise ValueError("Unsafe source work ID")
    work_id = "essay--" + slug
    if args.output.exists() or args.receipt.exists():
        raise ValueError("Immutable output or receipt already exists")
    prior = verify_closure(origin, lane="public")
    if prior["status"] != "PUBLICATION_CLOSURE_PASSED_BYTES_ONLY":
        raise ValueError("Public predecessor closure did not pass")

    shutil.copytree(origin, args.output, symlinks=False)
    out = args.output
    base_page = (origin / "estate/index.html").read_text()
    gallery, _ = json_script(base_page, "reader-gallery-data")
    snapshot, _ = json_script(base_page, "reader-publication-data")
    catalog = json.loads((origin / "estate/books/catalog.json").read_text())
    if any(item["id"] == work_id for item in gallery["collections"]["essays"]):
        raise ValueError("Work already exists in predecessor")
    original_names, _ = source_templates(base_page)
    template, fields, figures = render_template(manuscript, work_id, out)
    volumes = list(VOL.finditer(base_page))
    if not volumes or volumes[-1][1] != original_names[-1]:
        raise ValueError("Unexpected Reader template order")
    insertion = base_page.index("</template>", volumes[-1].end()) + len("</template>")
    page = base_page[:insertion] + "\n" + template + "\n" + base_page[insertion:]
    if source_templates(page)[0] != original_names + [work_id]:
        raise ValueError("Original Reader source changed or new work misplaced")
    first = figures[0]
    gallery["collections"]["essays"].append({
        "id": work_id, "src": first["publishedPath"], "alt": first["alt"],
        "sourceKind": "source-owned-proposed-essay-plate",
        "sourceSHA256": first["sha256"],
        "stageOnly": True, "publicReleaseAuthorized": False,
    })
    gallery["stagingSourceGitRevision"] = revision
    page = with_json(page, "reader-gallery-data", gallery)

    snapshot["publicationLane"] = "private-owner-WLAN-editorial-review"
    snapshot["sourcePredecessorReleaseID"] = catalog.get("currentReleaseID")
    snapshot["stagingReleaseID"] = args.release_id
    snapshot["stagingSourceGitRevision"] = revision
    snapshot["latestProposedWork"] = work_id
    for book in snapshot["books"]:
        book["stageOnly"] = True
        book["publicReleaseAuthorized"] = False
        book["stagePreviewAuthorized"] = True
        book["publicationState"] = "private-owner-WLAN-editorial-review"
        if book["id"] == "essays":
            book["orderedWorkIDs"].append(work_id)
            book["illustratedWorkIDs"].append(work_id)
    page = with_json(page, "reader-publication-data", snapshot)
    page = replace_once(
        page, '<meta name="robots" content="index,follow"/>',
        '<meta name="robots" content="noindex,nofollow"/>',
        "stage robots",
    )
    for rel in ("estate/index.html", "estate/read/library/index.html", "index.html"):
        (out / rel).write_text(page)

    for book in catalog["books"]:
        book["stageOnly"] = True
        book["publicReleaseAuthorized"] = False
        book["stagePreviewAuthorized"] = True
        book["publicationState"] = "private-owner-WLAN-editorial-review"
        current = next(item for item in snapshot["books"] if item["id"] == book["id"])
        book["orderedWorkIDs"] = current["orderedWorkIDs"]
        book["illustratedWorkIDs"] = current["illustratedWorkIDs"]
        book["sourceRevision"] = revision
        original = (origin / "estate/books" / book["id"] / "index.html").read_text()
        current["expectedMissing"] = [work_id]
        direct = preserve_book_meta(page, original, current, gallery["collections"][book["id"]])
        del current["expectedMissing"]
        direct = direct.replace(
            "https://fountain.coach/estate/read/" + work_id + "/",
            "https://staging.fountain.coach/estate/read/" + work_id + "/",
        )
        (out / "estate/books" / book["id"] / "index.html").write_text(direct)
    (out / "estate/essays/index.html").write_bytes(
        (out / "estate/books/essays/index.html").read_bytes()
    )
    catalog["publicPredecessorReleaseID"] = catalog.get("currentReleaseID")
    catalog["stagingReleaseID"] = args.release_id
    catalog["sourceGitRevision"] = revision
    catalog["stageOnly"] = True
    catalog["publicReleaseAuthorized"] = False
    catalog["status"] = "private-owner-WLAN-editorial-review"
    catalog["stagedCollectionOrder"] = [b["id"] for b in snapshot["books"]]
    catalog["publicationSnapshotSchema"] = snapshot["schema"]
    catalog["publicationSnapshotSourceReleaseID"] = args.release_id
    catalog["latestProposedEssay"] = work_id
    (out / "estate/books/catalog.json").write_bytes(json_bytes(catalog))

    preview_dir = out / "estate/read" / work_id
    social_path = preview_dir / "assets" / (slug + "-social.jpg")
    original_plate = manuscript.parent / "figures" / Path(first["publishedPath"]).name
    png = subprocess.run(["rsvg-convert", "-w", "1200", str(original_plate)],
                         check=True, capture_output=True).stdout
    subprocess.run(
        ["magick", "-", "-resize", "1200x630", "-background", "#F9F7F0",
         "-gravity", "center", "-extent", "1200x630", "-quality", "90", str(social_path)],
        input=png, check=True, capture_output=True,
    )
    social_url = "https://staging.fountain.coach/estate/read/" + work_id + "/assets/" + social_path.name
    ref = (origin / "estate/read/essay--the-proof-of-the-page/index.html").read_text()
    head = ref.split("</head>", 1)[0]
    head = re.sub(r"<title>.*?</title>", "<title>" + html.escape(fields["title"]) +
                  " — Fountain Press editorial preview</title>", head, count=1)
    head = re.sub(r'(<link rel="canonical" href=")[^"]+', r'\g<1>' +
                  "https://staging.fountain.coach/estate/read/" + work_id + "/", head, count=1)
    for label, value in (
        ("og:title", fields["title"]), ("og:description", fields["subtitle"]),
        ("og:url", "https://staging.fountain.coach/estate/read/" + work_id + "/"),
        ("og:image", social_url), ("og:image:alt", first["alt"]),
        ("twitter:title", fields["title"]), ("twitter:image", social_url),
    ):
        attr = "property" if label.startswith("og:") else "name"
        pattern = r'(<meta ' + attr + r'="' + re.escape(label) + r'" content=")[^"]*'
        head, count = re.subn(pattern, lambda m: m[1] + html.escape(value, quote=True),
                              head, count=1)
        if count != 1:
            raise ValueError("Missing per-work social head field " + label)
    head = head.replace('<meta name="robots" content="index,follow"/>',
                        '<meta name="robots" content="noindex,nofollow"/>')
    ld = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', head, re.S)
    if not ld:
        raise ValueError("Missing per-work provenance JSON-LD")
    ld_obj = json.loads(ld[2])
    ld_obj.update({
        "identifier": work_id, "headline": fields["title"],
        "description": fields["subtitle"], "dateCreated": fields["date"],
        "image": social_url, "creativeWorkStatus": "Proposed",
        "url": "https://staging.fountain.coach/estate/read/" + work_id + "/",
    })
    head = replace_once(head, ld[0], ld[1] + json.dumps(ld_obj, ensure_ascii=False) + ld[3],
                        "article JSON-LD")
    preview_html = head + "</head>" + page.split("</head>", 1)[1]
    preview_html = replace_once(preview_html, 'data-initial-volume="library"',
                                'data-initial-volume="essays"', "reader volume")
    (preview_dir / "index.html").write_text(preview_html)
    (preview_dir / "edition-manifest.json").write_bytes(json_bytes({
        "schema": "fountain.press.proposed-editorial-preview.v1",
        "sourceOwner": "Fountain-Coach/fountain.coach", "sourceGitRevision": revision,
        "sourceManuscript": args.manuscript.as_posix(),
        "sourceSHA256": sha(manuscript.read_bytes()), "status": "proposed",
        "publicationLane": "private-owner-WLAN-editorial-review", "publicReleaseAuthorized": False,
        "stageOnly": True, "workID": work_id, "figures": figures,
        "socialDerivative": {"path": "/estate/read/" + work_id + "/assets/" + social_path.name,
                             "sha256": sha(social_path.read_bytes())},
    }))

    release = {
        "schema": "fountain.press.editorial-preview-release.v1",
        "releaseID": args.release_id, "host": "staging.fountain.coach",
        "sourceOwner": "Fountain-Coach/fountain.coach",
        "sourceGitRevision": revision, "sourceSHA256": sha(manuscript.read_bytes()),
        "publicPredecessor": catalog["publicPredecessorReleaseID"],
        "stageOnly": True, "publicReleaseAuthorized": False,
        "latestProposedWork": work_id,
        "files": {
            str(p.relative_to(out)): sha(p.read_bytes())
            for p in sorted(out.rglob("*")) if p.is_file() and
            p.relative_to(out).as_posix() not in ("release.json", "estate/release.json")
        },
    }
    for path in (out / "release.json", out / "estate/release.json"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(json_bytes(release))
    closure = verify_closure(out, predecessor=origin, lane="staging",
                             expected_work=work_id)
    result = {
        "status": "PREPARED_NOT_ACTIVATED",
        "sourceRevision": revision, "releaseID": args.release_id,
        "publicPredecessor": release["publicPredecessor"],
        "candidateRoot": str(out), "stagingHost": "staging.fountain.coach",
        "latestProposedWork": work_id, "sourceSHA256": release["sourceSHA256"],
        "socialSHA256": sha(social_path.read_bytes()),
        "preActivationClosure": closure,
        "publisherPreflightBinding": "NOT_ESTABLISHED",
        "DNS": "UNVERIFIED",
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    args.receipt.write_bytes(json_bytes(result))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--manuscript", required=True, type=Path)
    parser.add_argument("--revision", required=True)
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--receipt", required=True, type=Path)
    args = parser.parse_args()
    if not re.fullmatch("[0-9a-f]{40}", args.revision):
        parser.error("Revision must be a pinned Git SHA40")
    if not re.fullmatch("[a-z0-9][a-z0-9-]{8,100}", args.release_id):
        parser.error("Invalid immutable release ID")
    try:
        result = compose(args)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(2, "PREVIEW_COMPOSITION_REFUSED: " + str(error) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
