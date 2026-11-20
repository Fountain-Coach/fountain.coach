#!/usr/bin/env python3
"""Focused source and safety tests for the proposed-essay preview compiler."""
from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compose_proposed_essay_preview import metadata, render_template

REPO = Path(__file__).resolve().parents[2]
MANUSCRIPT = REPO / "site/essays/before-we-can-work-together/source.md"
WORK_ID = "essay--before-we-can-work-together"


class ProposedPreviewTests(unittest.TestCase):
    def test_requires_unadmitted_source(self):
        text = MANUSCRIPT.read_text()
        self.assertEqual(metadata(text)["status"], "proposed")
        with self.assertRaisesRegex(ValueError, "Only unadmitted"):
            metadata(text.replace("status: proposed", "status: published", 1))

    def test_three_original_figures_and_original_text(self):
        with tempfile.TemporaryDirectory() as folder:
            stage = Path(folder)
            template, fields, figures = render_template(MANUSCRIPT, WORK_ID, stage)
            self.assertEqual(fields["title"], "Before We Can Work Together")
            self.assertEqual(len(figures), 3)
            self.assertIn('data-editorial-state="proposed"', template)
            self.assertIn("An AI can invoke a tool", template)
            self.assertIn('data-reader-volume="' + WORK_ID + '"', template)
            self.assertEqual(template.count('class="frame-reading-figure"'), 3)
            for figure in figures:
                original = REPO / figure["sourcePath"]
                projected = stage / figure["publishedPath"].lstrip("/")
                self.assertTrue(original.is_file())
                self.assertEqual(original.read_bytes(), projected.read_bytes())
                self.assertEqual(hashlib.sha256(projected.read_bytes()).hexdigest(),
                                 figure["sha256"])

    def test_missing_figure_is_refused(self):
        with tempfile.TemporaryDirectory() as folder:
            scratch = Path(folder)
            copied = scratch / "site/essays/before-we-can-work-together"
            (copied / "figures").mkdir(parents=True)
            (copied / "source.md").write_text(MANUSCRIPT.read_text())
            with self.assertRaisesRegex(ValueError, "Missing source-owned figure"):
                render_template(copied / "source.md", WORK_ID, scratch / "stage")


if __name__ == "__main__":
    unittest.main()
