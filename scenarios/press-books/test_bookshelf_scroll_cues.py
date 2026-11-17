"""The current Linotype Reader has two independent vertical scrollports.

A cue must come from measured overflow, not hard-coded Bookshelf counts.
"""
import unittest

from published_frontend import add_bookshelf_vertical_cues, STYLE


ANCHOR = "   vertical.append(tiles);gallery.append(vertical);pair.append(gallery);book.append(pair);scroll.append(book);"


class BookshelfScrollCueTests(unittest.TestCase):
    def test_existing_reader_panes_get_one_measured_cue_each(self):
        app = add_bookshelf_vertical_cues("before\n" + ANCHOR + "\nafter")
        self.assertEqual(app.count("panel.append(cue)"), 1)
        self.assertEqual(app.count("[[list,statement],[vertical,gallery]]"), 1)
        self.assertIn("region.scrollHeight-region.scrollTop-region.clientHeight>5", app)
        self.assertIn("region.scrollBy", app)
        self.assertIn("region.addEventListener('scroll',update", app)
        self.assertIn("ResizeObserver(update)", app)
        self.assertIn("aria-label", app)
        self.assertIn("More below", app)
        self.assertIn("before", app)
        self.assertIn("after", app)

    def test_source_anchor_must_exist_exactly_once(self):
        for original in ("no renderer body", ANCHOR + "\n" + ANCHOR):
            with self.subTest(original=original[:15]):
                with self.assertRaisesRegex(ValueError, "source anchor"):
                    add_bookshelf_vertical_cues(original)

    def test_repeated_injection_is_a_refusal(self):
        app = add_bookshelf_vertical_cues(ANCHOR)
        with self.assertRaisesRegex(ValueError, "duplicate Bookshelf"):
            add_bookshelf_vertical_cues(app)

    def test_cue_is_print_like_and_only_visible_with_more_below(self):
        self.assertIn('.reader-shelf-scroll-cue[data-more="false"]{visibility:hidden}', STYLE)
        self.assertIn(".reader-shelf-scroll-cue:focus-visible", STYLE)
        self.assertIn(".reader-shelf-scroll-cue-mark", STYLE)
        self.assertIn("font:normal clamp(.72rem", STYLE)
        self.assertNotIn("position:fixed", STYLE)
        self.assertNotIn("position:absolute", STYLE)
        self.assertIn("reader-shelf-scroll-cue{display:none!important}", STYLE)


if __name__ == "__main__":
    unittest.main()
