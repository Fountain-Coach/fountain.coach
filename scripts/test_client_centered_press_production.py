"""Source-owned promotion of an accepted essay, without a second Press Reader."""
import json
import sys
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from build_client_centered_press_production import (
    SOURCE_REV, SOURCE_SHA, ENGINE_SHA, PREV, RELEASE,
    replace_one, extract_template
)


class ClientCenteredPublicationTests(unittest.TestCase):
    def test_approved_manuscript_and_immutable_stage_to_public_lineage(self):
        self.assertEqual(SOURCE_REV, '4a89ae5c2d822a0f594c382748277e2b818d82e4')
        self.assertEqual(SOURCE_SHA, '03e4497f6deabe173958bd632b721ac7f23ae95e3bbe0043a1204ad5039de78a')
        self.assertEqual(ENGINE_SHA, 'e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a')
        self.assertEqual(PREV, 'fcis-5f94d0f-ear-sing-20261107')
        self.assertEqual(RELEASE, 'fcis-client-centered-20261110-4a89ae5')

    def test_fail_closed_on_unexpected_public_catalogue_bytes(self):
        with self.assertRaises(ValueError):
            replace_one('abc', 'not-here', 'new', 'source')
        with self.assertRaises(ValueError):
            replace_one('abcabc', 'abc', 'new', 'source')

    def test_only_exact_source_template_is_selected(self):
        source = '<template data-reader-volume="other">OLD</template>' + (
            '<template data-reader-volume="essay--client-centered">'
            '<div data-source-block="client-centered.s1.p1">Author text</div></template>')
        selected = extract_template(source)
        self.assertIn('Author text', selected)
        self.assertNotIn('OLD', selected)

    def test_production_does_not_ship_review_engine_or_generated_prose(self):
        code = (HERE / 'build_client_centered_press_production.py').read_text()
        for required in (
            'sourceMarkupVerifiedEqualToStage',
            'reading-first-press-engine.',
            'data-inline-after-paragraph="13"',
            'editorial proem semantics',
            'socialRasterSHA256',
            'publicEssaysCount',
            'approvedDate',
            'Refuse overwrite of generated publication candidate',
        ):
            self.assertIn(required, code)
        self.assertIn('(dest / "index.html").write_text(page)', code)
        self.assertIn("assert 'client-centered-review.js' not in page", code)


if __name__ == '__main__':
    unittest.main()
