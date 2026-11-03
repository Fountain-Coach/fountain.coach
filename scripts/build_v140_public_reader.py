#!/usr/bin/env python3
"""Produce a media-free v140 public READER CANDIDATE without deployment.
The only admitted inputs are the pinned v140 source and selected published art.
Never copy the WLAN stage or private listening manifests.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.request import Request, urlopen
import ssl

ROOT = Path(__file__).resolve().parents[1]
SCEN = ROOT / "scenarios/reading-first-20261101"
OUT = ROOT / "build/public-v140-text-only"
COMMIT = "611c3e34c9dfffc932d86d957edf49bda46927ec"
SOURCE_ORIGIN = "https://192.168.8.50:8243"
EXPECTED_IMAGES_MIN = 15

head = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
if head != COMMIT:
    raise SystemExit("Refusing unpinned source: " + head)
if OUT.exists():
    raise SystemExit("Refusing to overwrite candidate: " + str(OUT))
if not (SCEN / "BOOK_ADDENDUM_V140_ACCEPTANCE.md").is_file():
    raise SystemExit("Missing v140 acceptance")
html = (SCEN / "index.html").read_text()
app = (SCEN / "reading-first-app.js").read_text()
engine = (SCEN / "reading-first-press-engine.js").read_text()
if 'data-reader-volume="publication-notes"' not in html or 'folioReturn' not in engine:
    raise SystemExit("Missing same-position addendum")

# Remove the private sound-study playback figure, not its surrounding authored text.
html, removed = re.subn(r'<figure class="frame-press-av"[^>]*>.*?</figure>',
   '<aside class="public-media-note" role="note">The recorded performances belong to a private rehearsal and are not part of this edition.</aside>', html, count=1, flags=re.S)
if removed != 1:
    raise SystemExit("Expected exactly one private Door recording figure")
# Preserve citations as text, but do not link from public source to withheld samples or DSP files.
html = re.sub(r'<a\b[^>]*href="/estate/[^"]+\.(?:ogg|wav|mp3|mjs|json)"[^>]*>(.*?)</a>',
              r'<span class="withheld-media-reference">\1</span>', html, flags=re.S)
html = re.sub(r'^<link[^>]*href="/estate/assets/linotype/(?:teatro-vergil-hearing|vergil-prologue-hearing)\.css"[^>]*>\s*', '', html, flags=re.M)
html = re.sub(r'^<script[^>]*src="/estate/assets/linotype/(?:teatro-vergil-hearing|vergil-prologue-hearing)\.mjs"[^>]*></script>\s*', '', html, flags=re.M)
# Private narrator adapters are never loaded on the public reader.
app, removed = re.subn(r'^import \{ registerSatzfunkMedia \}.*?\nregisterSatzfunkMedia\(\);\n',
                       '', app, count=1, flags=re.S)
if removed != 1: raise SystemExit("Private Satzfunk import shape changed")
app, removed = re.subn(r'^const securePlayerOrigin=.*?(?=^if\(!viewport\|\|!source\|\|!window\.SolsticeLinotype\))',
                       '', app, count=1, flags=re.M | re.S)
if removed != 1: raise SystemExit("Private sound manifest shape changed")
app, removed = re.subn(r'^function syncSatzfunkPlayer\(\)\{.*?(?=^function present\()',
                       '', app, count=1, flags=re.M | re.S)
if removed != 1 or app.count('syncSatzfunkPlayer();') != 1:
    raise SystemExit("Private playback call mismatch")
app = app.replace(' syncSatzfunkPlayer();\n', '', 1)
app, removed = re.subn(r'^// An optional narrator adapter addresses.*?(?=^/\* A media leaf)',
                       '', app, count=1, flags=re.M | re.S)
if removed != 1: raise SystemExit("Narrator bridge shape changed")

# The stage used /estate/ as a private proxy root. Public root is /.
html = html.replace('/estate/', '/')
# Keep navigation to the separately owned Instruments domain, not a broken local route.
html = html.replace('href="/instruments/"', 'href="https://instruments.fountain.coach/"')
app = app.replace('/estate/', '/')
engine = engine.replace('/estate/', '/')
# Published source links to an original essay directory should remain ordinary links.
# The v140 reader's internal chapter links still navigate within the same document.

for filename, text in (("index.html", html), ("reading-first-app.js", app),
                       ("reading-first-press-engine.js", engine)):
    forbidden = ("private-wlan-rehearsal", "teatro-vergil-hearing.mjs",
                 "vergil-prologue-hearing.mjs", "soundEditionPromise",
                 "registerSatzfunkMedia", ".mp3", ".wav", "midi-reading.json",
                 "data-press-media=", "media/edition.json")
    hits = [word for word in forbidden if word.lower() in text.lower()]
    if hits: raise SystemExit("Unsafe material in " + filename + ": " + repr(hits))

OUT.mkdir(parents=True)
(OUT / "index.html").write_text(html)
assets = OUT / "assets/linotype"
assets.mkdir(parents=True)
(assets / "reading-first-app.js").write_text(app)
(assets / "reading-first-press-engine.js").write_text(engine)
for name in ("reading-first-shell.css", "reading-first-press-frame.css",
             "reading-first-press-host.css"):
    css = (SCEN / name).read_text().replace('/estate/', '/')
    (assets / name).write_text(css)
# Art already contained in the admitted Bookshelf and First Reading; positive image-only file list.
paths = sorted(set(re.findall(r'/estate/[A-Za-z0-9_./-]+\.(?:png|jpe?g|svg|webp|gif)', (SCEN / "index.html").read_text())))
if len(paths) < EXPECTED_IMAGES_MIN: raise SystemExit("Unexpected published image count")
paths.append("/estate/assets/fountain-coach-logo-transparent.png")
paths = sorted(set(paths))
for path in paths:
    relative = path.removeprefix("/estate/")
    if ".." in Path(relative).parts or not relative.startswith(("assets/", "essays/")):
        raise SystemExit("Not a publication illustration: " + relative)
    dest = OUT / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Trust is scoped to the previously accepted, HTTPS owner-WLAN stage.
    command = ["curl", "--fail", "--silent", "--show-error", "--location",
               "--max-time", "15", "--output", str(dest), SOURCE_ORIGIN + path]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode or not dest.is_file() or dest.stat().st_size < 50:
        raise SystemExit("Missing required published image " + relative + " / " + result.stderr[:100])
# Published Solstice Reading 01: require the exact source-published image digests.
solstice = json.loads((SCEN / "solstice-first-reading-manifest.json").read_text())
if solstice.get("publishedWorks") != 30:
    raise SystemExit("Published Solstice manifest membership changed")
images = [im for entry in solstice["entries"] for im in entry.get("images", [])]
if len(images) != 41:
    raise SystemExit("Unexpected Solstice illustration inventory")
for image in images:
    href = image["href"]
    if not href.startswith("/assets/edition/") or ".." in Path(href).parts:
        raise SystemExit("Unapproved Solstice image " + href)
    expected = image["sha256"].removeprefix("sha256:")
    relative = "solstice" + href
    destination = OUT / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = ["curl", "--fail", "--silent", "--show-error", "--location",
               "--max-time", "15", "--output", str(destination),
               SOURCE_ORIGIN + "/" + relative]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode or not destination.is_file():
        raise SystemExit("Missing Solstice image: " + relative + " " + result.stderr[:100])
    got = hashlib.sha256(destination.read_bytes()).hexdigest()
    if got != expected: raise SystemExit("Public Solstice image hash mismatch: " + relative)

# The retained open-source engine documentation is an already published exhibit.
for filename in ("CSOUND_CORE_LICENSE", "LICENSE", "THIRD_PARTY.md"):
    relative = "essays/the-door-is-a-score/assets/vendor/" + filename
    destination = OUT / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(["curl", "--fail", "--silent", "--show-error",
        "--location", "--max-time", "15", "--output", str(destination),
        SOURCE_ORIGIN + "/estate/" + relative], capture_output=True, text=True)
    if result.returncode or not destination.is_file():
        raise SystemExit("Third-party attribution file missing " + relative)
files = sorted(p for p in OUT.rglob("*") if p.is_file())
manifest = {"schema": "fountain.coach.public-reader-candidate.v1",
 "source": {"repository": "Fountain-Coach/fountain.coach", "commit": COMMIT},
 "releaseId": "reader-v140-public-text-only-candidate",
 "host": "fountain.coach", "status": "not-admitted-not-deployed",
 "publicReleaseAuthorized": False,
 "audioPlaybackIncluded": False, "midiReadingDataIncluded": False,
 "exclusions": ["private Vergil recordings", "MIDI timing and private narrated reading data",
  "Door sound-study rehearsal recordings", "Satzfunk private rehearsal grants",
  "WLAN media manifests", "staging-only server files and secrets"],
 "files": [{"path": str(p.relative_to(OUT)),
   "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
   "bytes": p.stat().st_size} for p in files]}
(OUT / "release-candidate-manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n")
print("CANDIDATE", OUT)
print("FILES",len(files),"IMAGES",len(paths), "SOURCE", COMMIT[:8])
