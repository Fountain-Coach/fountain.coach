"""Current Essays latest link follows the admitted, not an invented, work list."""
import unittest

from published_frontend import add_latest_essay_link, STYLE


ANCHOR = "   header.append(direct);\n   if(bookById.get(id).subtitle){"


class LatestEssaysLinkTests(unittest.TestCase):
    def test_latest_is_derived_from_essays_contents_and_opens_in_same_reader(self):
        actual = add_latest_essay_link(ANCHOR)
        for s in ("id==='essays'", "contents[id][contents[id].length-1]",
                  "bookById.get(id).orderedWorkIDs.includes(newestID)",
                  "link.dataset.readerTarget=newestID", "link.href='#/read/'",
                  "labels.get(newestID)", "Latest essay"):
            self.assertIn(s, actual)
        self.assertEqual(actual.count("header.append(link)"), 1)

    def test_no_second_source_of_essay_membership(self):
        actual = add_latest_essay_link(ANCHOR)
        self.assertNotIn('essay--the-proof-of-the-page', actual)
        self.assertNotIn('contents[id].reverse()', actual)
        self.assertNotIn('contents[id].sort()', actual)

    def test_refuse_missing_or_duplicate_projection(self):
        with self.assertRaisesRegex(ValueError, 'source anchor'):
            add_latest_essay_link('unrelated app')
        with self.assertRaisesRegex(ValueError, 'duplicate latest-essay'):
            add_latest_essay_link(add_latest_essay_link(ANCHOR))

    def test_print_typography_and_accessibility(self):
        self.assertIn('.reader-latest-essay-link', STYLE)
        self.assertIn('.reader-latest-essay-link:focus-visible', STYLE)
        self.assertIn('.reader-latest-essay-prefix', STYLE)
        self.assertNotIn('position:fixed', STYLE)
        actual = add_latest_essay_link(ANCHOR)
        self.assertIn("link.setAttribute('aria-label'", actual)


if __name__ == "__main__":
    unittest.main()
