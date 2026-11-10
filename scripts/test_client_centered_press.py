#!/usr/bin/env python3
"""Fountain Press source-fidelity and published-reader inheritance tests."""
from pathlib import Path
import importlib.util,unittest,json,hashlib,html,re
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("build_client_centered_press_stage",ROOT/"scripts/build_client_centered_press_stage.py")
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
class ClientCenteredPressContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        builder.build()
        cls.out=builder.OUT
        cls.page=(cls.out/"index.html").read_text()
        cls.man=json.loads((cls.out/"edition-manifest.json").read_text())
    def test_exact_source_and_noninflated_paragraphs(self):
        text,groups=builder.parse_source()
        self.assertEqual(self.man["sourceSHA256"],hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual([g["heading"] for g in groups],
                         ["Another Person's Purpose","The Method and the Situation",
                          "Intelligence in the Relationship","What Becomes Possible"])
        self.assertEqual(sum(len(g["paragraphs"]) for g in groups),self.man["paragraphCount"])
        self.assertEqual(self.man["paragraphCount"],22)
        for block in self.man["blocks"]:
            self.assertIn("data-source-block=\""+block["id"]+"\"",self.page)
            self.assertIn(html.escape(block["text"]),self.page)
        self.assertIn(html.escape(groups[-1]["paragraphs"][-1]),self.page)
        self.assertNotIn("<br",self.page[self.page.index('<template data-reader-volume="essay--client-centered"'):self.page.index('<script type="application/json" id="reader-gallery-data"')])
    def test_original_publication_reader_unchanged(self):
        builder.assert_pinned()
        self.assertEqual(builder.filehash(self.out/"assets/press/reading-first-press-engine.e38301452ef0f07aa9440953d898dcf9ae13fcb828a7d4a97fac163976261d9a.js"),
                         builder.BASELINE["engineSHA256"])
        original=(builder.FIXTURE/"reading-first-app.js").read_text()
        staged=(self.out/"assets/press/reading-first-app.client-centered-review.js").read_text()
        self.assertEqual(staged.replace(" 'essay--client-centered', // review-only, not a fifth/sixth published essay\n",""),original)
        self.assertIn("essaySequence.length!==5",staged)
        self.assertIn("galleries.essays.length!==5",staged)
        self.assertEqual(self.page.count('<template data-reader-volume="essay--client-centered"'),1)
        self.assertIn('data-initial-volume="essay--client-centered"',self.page)
    def test_source_owned_two_score_figures(self):
        self.assertEqual(len(self.man["figures"]),2)
        new_work=self.page.split('<template data-reader-volume="essay--client-centered"',1)[1].split("</template>",1)[0]
        self.assertEqual(new_work.count('data-source-plate-sha256='),2)
        for figure in self.man["figures"]:
            b=(self.out/"assets/images"/figure["file"]).read_bytes()
            self.assertEqual(hashlib.sha256(b).hexdigest(),figure["sha256"])
            self.assertIn(html.escape(figure["alt"],quote=True),self.page)
        self.assertNotIn('a_clean_modern_two_page',self.page)
    def test_review_not_production(self):
        self.assertFalse(self.man["productionAuthorized"])
        self.assertEqual(self.man["publicationState"],"private-owner-WLAN-review")
        self.assertIn('name="robots" content="noindex,nofollow"',self.page)
        self.assertNotIn('rel="canonical" href="https://fountain.coach/estate/read/essay--the-ear-that-learns/"',self.page)
        self.assertNotIn('<meta property="og:image"',self.page)
        self.assertEqual(self.man["sourceOwner"],"Fountain-Coach/fountain.coach")
if __name__=="__main__":unittest.main()
