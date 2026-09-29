import unittest
from v5_discovery_pipeline import SourceParser, ClaimExtractor, QuestionSynthesizer

class TestHardeningRegression(unittest.TestCase):
    def test_reject_mcq_options(self):
        # A. "(d) India experiences comparatively stronger winters..."
        blocks = [{"sourceId": "test", "text": "(d) India experiences comparatively stronger winters as compared to central Asia."}]
        extractor = ClaimExtractor()
        claims, rejected = extractor.extract(blocks)
        self.assertEqual(len(claims), 0)
        self.assertTrue(any("Option marker artifact detected" in r["reason"] for r in rejected))
        
    def test_reject_in_rural(self):
        # B. "In Rural, Himachal Pradesh..."
        blocks = [{"sourceId": "test", "text": "In Rural, Himachal Pradesh has the maximum female workforce."}]
        extractor = ClaimExtractor()
        claims, rejected = extractor.extract(blocks)
        self.assertEqual(len(claims), 0)
        self.assertTrue(any("Invalid subject start" in r["reason"] for r in rejected))

    def test_reject_plateaus_malformed(self):
        # C. "Plateaus can be formed due to..." 
        # If it's a claim, it shouldn't produce "It results in Plateaus can be formed."
        blocks = [{"sourceId": "test", "text": "Plateaus can be formed due to volcanic activity."}]
        extractor = ClaimExtractor()
        claims, rejected = extractor.extract(blocks)
        self.assertEqual(len(claims), 0) # Our strict rules don't match "can be formed due to"
        
    def test_structural_geology_block(self):
        # D. the full Structural geology MCQ block
        text = """Structural geology deals with:
(a) the age of rocks
(b) the components and chemical nature of soil
(c) the form, classification, mechanism, and causes of rock structures evolution
(d) the cause of volcano formation"""
        
        # SourceParser should strip (a)-(d) out because they are MCQ options.
        with open("mock_mcq.txt", "w") as f: f.write(text)
        parser = SourceParser()
        blocks = parser.parse(["mock_mcq.txt"])
        # Should not extract a claim spanning all options
        extractor = ClaimExtractor()
        claims, rejected = extractor.extract(blocks)
        self.assertEqual(len(claims), 0)
        
    def test_valid_chota_nagpur(self):
        # E. "The Chota Nagpur plateau comprises..."
        blocks = [{"sourceId": "test", "text": "The Chota Nagpur plateau comprises immense reserves of metallic minerals."}]
        extractor = ClaimExtractor()
        claims, rejected = extractor.extract(blocks)
        self.assertEqual(len(claims), 1)
        self.assertIn(claims[0]["subject"], ["The Chota Nagpur", "The Chota Nagpur plateau"])
        self.assertEqual(claims[0]["verb"], "comprises")
        self.assertTrue("immense reserves" in claims[0]["object"])

if __name__ == "__main__":
    unittest.main()
