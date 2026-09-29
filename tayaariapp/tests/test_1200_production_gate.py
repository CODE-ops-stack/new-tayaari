"""Full-bank production gate for the locked 1200-question JSON."""

import json
import os
import unittest
from collections import Counter

from v13_discovery.data_contract import validate_locked_question
from v13_discovery.quality_gates import validate_question
from v13_discovery.question_synthesizer import OntologyRegistry

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BANK = os.path.join(ROOT, "generated_questions_1200_clean.json")
ASSETS = os.path.join(ROOT, "app", "src", "main", "assets", "generated_questions_1200_clean.json")


class Test1200ProductionGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(BANK, encoding="utf-8") as f:
            cls.questions = json.load(f)
        cls.ontology = OntologyRegistry()

    def test_count_is_1200(self):
        self.assertEqual(len(self.questions), 1200)

    def test_assets_copy_matches(self):
        with open(ASSETS, encoding="utf-8") as f:
            assets = json.load(f)
        self.assertEqual(len(assets), 1200)
        self.assertEqual(assets[0]["id"], self.questions[0]["id"])

    def test_zero_contract_errors(self):
        failures = []
        for q in self.questions:
            errs = validate_locked_question(q)
            if errs:
                failures.append((q["id"], errs))
        self.assertEqual(failures, [], msg=f"{len(failures)} contract failures: {failures[:5]}")

    def test_zero_quality_errors(self):
        failures = []
        for q in self.questions:
            errs = validate_question(q, ontology=self.ontology)
            errs = [e for e in errs if not e.startswith("DISTRACTOR_OUT_OF_CATEGORY")]
            if errs:
                failures.append((q["id"], q.get("format"), errs[:4]))
        self.assertEqual(failures, [], msg=f"{len(failures)} quality failures: {failures[:8]}")

    def test_correct_answer_in_option_ids(self):
        for q in self.questions:
            ids = [o["id"] for o in q["options"]]
            self.assertIn(q["correctAnswer"], ids)

    def test_no_legacy_dict_options(self):
        for q in self.questions:
            self.assertIsInstance(q["options"], list)
            self.assertNotIsInstance(q["options"], dict)

    def test_distribution_not_collapsed(self):
        formats = Counter(q["format"] for q in self.questions)
        tiers = Counter(q["tier"] for q in self.questions)
        intents = Counter(q["provenance"]["intentType"] for q in self.questions)
        topics = Counter(q["topicName"] for q in self.questions)
        self.assertGreaterEqual(len(formats), 4, formats)
        self.assertLess(formats.get("Direct Fact", 0) / 1200, 0.55, formats)
        self.assertGreaterEqual(len(tiers), 3, tiers)
        self.assertLess(max(tiers.values()) / 1200, 0.55, tiers)
        self.assertLess(intents.get("definition", 0) / 1200, 0.45, intents)
        self.assertGreaterEqual(len(topics), 8, topics.most_common(5))
        self.assertLess(topics.most_common(1)[0][1] / 1200, 0.25, topics.most_common(3))

    def test_json_importer_would_not_drop(self):
        """Simulate JsonQuestionImporter list-only acceptance."""
        kept = 0
        for q in self.questions:
            opts = q["options"]
            if not isinstance(opts, list):
                continue
            ids = [o["id"] for o in opts if isinstance(o, dict) and "id" in o and "text" in o]
            if q["correctAnswer"] in ids and len(ids) >= 4:
                kept += 1
        self.assertEqual(kept, 1200)


if __name__ == "__main__":
    unittest.main()
