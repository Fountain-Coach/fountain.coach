#!/usr/bin/env python3
"""Source-owned narrow home-page feature for an already published estate portal.

The live homepage differs intentionally from the future Bookshelf candidate in
site/index.html. Preserve those separate revisions: this projection takes one
pinned, byte-verbatim published homepage and inserts one linked essay card.
"""
from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "content/deployment-baselines/fountain.coach-home-predecessor-20261018.html"
PREDECESSOR_SHA256 = "e5d4c2a2ef3471a05c4d53c22374fd2bf67be6be336e99519a148329152dd3fb"
ROUTE = "/essays/the-composable-book/"
CARD = ('<article class="estate-card essay-entry" data-essay-feature="the-composable-book">'
        '<div class="estate-card-head"><svg viewBox="0 0 24 24" aria-hidden="true">'
        '<path d="M5 4h14v16H5zM8 8h8M8 12h8M8 16h5"/></svg>'
        '<small>09 · NEW ESSAY</small></div>'
        '<strong><a href="/essays/the-composable-book/">The Composable Book</a></strong>'
        '<span>How a writer and model can compose the form of a book: semantic languages, the DOM, and shared authority.</span>'
        '</article>')
ANCHOR = ('<strong><a href="/essays/">Why the estate matters</a></strong>'
          '<span>Enter the essay collection and its latest authored addition.</span></article>')


def baseline() -> bytes:
    source = BASELINE.read_bytes()
    if hashlib.sha256(source).hexdigest() != PREDECESSOR_SHA256:
        raise ValueError("Pinned live homepage baseline has changed")
    return source


def project_home(source: bytes) -> bytes:
    if hashlib.sha256(source).hexdigest() != PREDECESSOR_SHA256:
        raise ValueError("Home projection requires reviewed exact live predecessor")
    text = source.decode("utf-8")
    if text.count(ANCHOR) != 1 or 'data-essay-feature="the-composable-book"' in text:
        raise ValueError("Homepage entry context changed")
    return text.replace(ANCHOR, ANCHOR + CARD, 1).encode("utf-8")


def check_home(candidate: bytes, predecessor: bytes) -> None:
    if predecessor != baseline():
        raise ValueError("Homepage predecessor drift; refuse unrelated edits")
    text = candidate.decode("utf-8")
    if text.count(CARD) != 1 or text.replace(CARD, "", 1).encode("utf-8") != predecessor:
        raise ValueError("Homepage change is not exactly the admitted essay card")


if __name__ == "__main__":
    base = baseline()
    page = project_home(base)
    check_home(page, base)
    print("HOME_FEATURE_PREPARED", len(page), hashlib.sha256(page).hexdigest())
