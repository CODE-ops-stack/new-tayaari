import json
import unittest

class TestGoldenEvalSet(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open("data/golden_eval_set.json", "r", encoding="utf-8") as f:
            cls.dataset = json.load(f)
            
    def test_schema_metadata(self):
        self.assertIn("version", self.dataset)
        self.assertIn("metadata", self.dataset)
        self.assertIn("examples", self.dataset)
        self.assertGreaterEqual(self.dataset["metadata"]["total_examples"], 100)

    def test_positive_count_and_intents(self):
        positives = [e for e in self.dataset["examples"] if e["expected_label"] == "positive"]
        self.assertGreaterEqual(len(positives), 50, f"Expected >= 50 positives, got {len(positives)}")
        
        required_intents = [
            "definition", "attribute", "cause/effect", "comparison",
            "spatial", "distribution", "classification", "quantity",
            "sequence", "condition", "exception", "process",
            "part-of", "member-of"
        ]
        
        intent_counts = {}
        for p in positives:
            intent = p["intent"]
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
            
        for req in required_intents:
            self.assertIn(req, intent_counts, f"Missing required intent: {req}")
            self.assertGreaterEqual(intent_counts[req], 1, f"Intent {req} has 0 instances")
            print(f"Positive Intent [{req}]: {intent_counts[req]} instances")

    def test_negative_count_and_categories(self):
        negatives = [e for e in self.dataset["examples"] if e["expected_label"] == "negative"]
        self.assertGreaterEqual(len(negatives), 50, f"Expected >= 50 negatives, got {len(negatives)}")
        
        required_categories = [
            "mcq_leakage", "watermark_header", "syntactic_fragment",
            "broken_reading_order", "table_formatting_artifact", "anaphoric_unresolved"
        ]
        
        cat_counts = {}
        for n in negatives:
            cat = n["rejection_category"]
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
            
        for req in required_categories:
            self.assertIn(req, cat_counts, f"Missing required rejection category: {req}")
            self.assertGreaterEqual(cat_counts[req], 1, f"Category {req} has 0 instances")
            print(f"Negative Category [{req}]: {cat_counts[req]} instances")

    def test_provenance_integrity(self):
        for e in self.dataset["examples"]:
            self.assertIn("id", e)
            self.assertIn("text", e)
            self.assertTrue(len(e["text"]) > 0)
            self.assertIn("provenance", e)
            self.assertIn("source_file", e["provenance"])
            self.assertIn("line_or_page", e["provenance"])
            self.assertTrue(len(e["provenance"]["source_file"]) > 0)
            self.assertTrue(len(e["provenance"]["line_or_page"]) > 0)
            
            if e["expected_label"] == "positive":
                self.assertIsNone(e["rejection_category"])
                self.assertIsNotNone(e["semantic_entities"])
                self.assertIn("primary_entity", e["semantic_entities"])
            else:
                self.assertIsNotNone(e["rejection_category"])
                self.assertIsNotNone(e["rejection_reason"])

if __name__ == "__main__":
    unittest.main()
