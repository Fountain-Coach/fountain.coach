#!/usr/bin/env python3
"""Check the author-led homepage and adjacent Essays collection against the
adopted canonical estate reel. Source checks are not staging or Safari proof.
"""
from html.parser import HTMLParser
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
REEL = ROOT.parent / "estate/navigation/canonical-reel.v1.json"

class Shell(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.reel = []
        self.footer_links = []
        self.meta = {}
        self.headings = []
        self.gallery = []
        self.features = []
        self.skip = False
        self.info = False
        self.banners = 0
        self.footers = 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        class_names = set(a.get("class", "").split())
        self.stack.append((tag, a))
        if tag == "meta":
            self.meta[a.get("name", "")] = a.get("content", "")
        if tag == "header" and ("site-header" in class_names or a.get("role") == "banner"):
            self.banners += 1
        if tag == "footer" and (a.get("role") == "contentinfo" or a.get("id") == "footer"):
            self.footers += 1
        inside = lambda name, value: any(name == k and value == v.get(k) for k, v in self.stack)
        nav = any(t == "nav" and "estate-nav" in v.get("class", "").split() for t, v in self.stack)
        foot = any(t == "footer" for t, _ in self.stack)
        if tag == "a":
            if "skip-link" in class_names and a.get("href") == "#main": self.skip = True
            if nav and a.get("data-estate-id"): self.reel.append((a["data-estate-id"], a.get("href")))
            if foot: self.footer_links.append(a.get("href", ""))
        if tag == "button" and nav and "estate-info" in class_names: self.info = True
        if tag == "h1": self.headings.append("h1")
        if tag == "article" and "essay-gallery-card" in class_names:
            if a.get("data-essay-route"): self.gallery.append(a["data-essay-route"])
            else: self.features.append(True)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for i in range(len(self.stack)-1, -1, -1):
            if self.stack[i][0] == tag:
                del self.stack[i:]
                return

def check():
    reel = json.loads(REEL.read_text())
    expected = [(e["id"], e["url"]) for e in reel["entries"]]
    assert len(expected) == 9, "Require the current adopted nine-entry reel"
    pages = [("home", SITE/"index.html"), ("essays", SITE/"essays/index.html")]
    parsed = {}
    for label, path in pages:
        source = path.read_text(encoding="utf8")
        p = Shell(source)
        assert p.banners == 1, (label, "masthead")
        assert p.footers == 1, (label, "footer")
        assert p.skip, (label, "accessible skip")
        assert p.info, (label, "footer Info action")
        assert p.reel == expected, (label, "reel contract", p.reel)
        assert p.meta.get("fountain:publication-role"), (label, "publication role")
        assert p.headings.count("h1") == 1, (label, "heading")
        for url in ("https://status.fountain.coach/","https://governance.fountain.coach/legal/",
                    "https://governance.fountain.coach/privacy/","https://governance.fountain.coach/accessibility/",
                    "https://governance.fountain.coach/copyright/","https://governance.fountain.coach/compliance/"):
            assert url in p.footer_links, (label, "missing legal or provenance", url)
        parsed[label] = p
        print("SOURCE_SHELL",label,len(p.reel),"reel",len(p.footer_links),"footer links")
    h, e = parsed["home"], parsed["essays"]
    assert h.reel == e.reel
    assert h.footer_links == e.footer_links, "Both entrances must share the same footer route graph"
    assert len(h.features) == 4, "Landing selects four real essays"
    assert len(e.gallery) == 7, "The complete public gallery has seven works"
    assert len(set(e.gallery)) == len(e.gallery)
    assert h.meta["fountain:publication-role"] == "author-led estate identity"
    assert e.meta["fountain:publication-role"] == "essay collection index"
    assert "href=\"/editions/\"" in (SITE/"index.html").read_text()
    assert "data-linotype-state=\"bookshelf\"" in (SITE/"editions/index.html").read_text()
    for slug in ("the-door-is-a-score", "the-ear-that-learns", "the-composable-book",
                 "reframe-and-the-business-value-of-the-estate"):
        assert f'href="/essays/{slug}/"' in (SITE/"index.html").read_text(), slug
    print("EDITORIAL_ENTRANCES_ACCEPTED",len(h.features),"features",len(e.gallery),"gallery works")

if __name__ == "__main__":
    check()
