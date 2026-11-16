"""Source-owned illustrated essay remains a complete original draft, not a deployment."""
import hashlib
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET

ROOT=Path(__file__).parent

class IllustratedProofEssayTests(unittest.TestCase):
    def test_all_six_named_editorial_plates_exist_and_parse_as_real_svg(self):
        source=(ROOT/'combined-essay.md').read_text()
        imgs=re.findall(r'!\[([^]]+)\]\(([^)]+)\)',source)
        self.assertEqual(len(imgs),6)
        self.assertEqual(len({x[1] for x in imgs}),6)
        for alt,target in imgs:
            self.assertGreater(len(alt),35)
            path=ROOT/target;self.assertTrue(path.is_file())
            svg=ET.parse(path).getroot()
            self.assertEqual(svg.tag,'{http://www.w3.org/2000/svg}svg')
            self.assertGreater(len(svg.findall('.//{http://www.w3.org/2000/svg}text')),4)
            self.assertNotIn('http://',''.join(el.attrib.get('href','') for el in svg.iter()))

    def test_proof_instrument_records_real_folio_source_lengths_without_replacing_reader(self):
        scanner=(ROOT.parents[2]/'scenarios/press-books/proof-press/run.mjs').read_text()
        for required in ('sourceBlockLengths:', 'trimmedLength:e.textContent.trim().length',
                         'linotype-sheet', 'sheet.screenshot('):
            self.assertIn(required,scanner)
        self.assertIn('const works=admitted.flatMap',scanner)
        self.assertIn('sourceBlocks:initial.sourceBlocks,sourceBlockLengths:initial.sourceBlockLengths',scanner)

    def test_specific_source_and_non_fabrication_boundaries_are_explicit(self):
        text=(ROOT/'combined-essay.md').read_text()
        for fragment in ('What Makes a Page Modern?', 'Client-Centered',
                         'v177', 'v178', 'Satzspiegel', 'Zeilenfall',
                         'a thousand', 'not, by that fact alone, a failure',
                         'not a reproduction', 'not findings from an actual thousand-page run'):
            self.assertIn(fragment.lower(),text.lower())
        receipt=json.loads((ROOT/'source-receipt.json').read_text())
        self.assertEqual(receipt['publicationState'],'source-editorial-draft-not-published')
        self.assertEqual(len(receipt['illustrations']),6)
        self.assertEqual(receipt['manuscriptSHA256'],hashlib.sha256((ROOT/'combined-essay.md').read_bytes()).hexdigest())
        for p,expected in receipt['illustrations'].items():
            self.assertEqual(hashlib.sha256((ROOT/p).read_bytes()).hexdigest(),expected)

if __name__=='__main__':unittest.main()
