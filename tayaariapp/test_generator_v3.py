import unittest
from generator_v3 import QualityAuditor, GeneratorV3

class TestGeneratorV3(unittest.TestCase):
    def test_boilerplate_explanation_rejected(self):
        q = {"explanation": "This is known as the right answer because it is.", "metadata": {}}
        passed, reason = QualityAuditor.audit_explanation(q)
        self.assertFalse(passed)
        self.assertIn("Boilerplate", reason)

        q2 = {"explanation": "Just a small sentence.", "metadata": {}}
        passed2, reason2 = QualityAuditor.audit_explanation(q2)
        self.assertFalse(passed2)
        self.assertIn("too short", reason2)

    def test_plausible_vs_absurd_distractor(self):
        q1 = {"validation": {"distractorLogic": "Some absurd options used"}, "metadata": {"distractorCategoryMatched": True}}
        passed1, reason1 = QualityAuditor.audit_distractor_plausibility(q1)
        self.assertFalse(passed1)
        self.assertIn("Absurd", reason1)
        
        q2 = {"validation": {"distractorLogic": "Semantic neighbors based on X"}, "metadata": {"distractorCategoryMatched": True}}
        passed2, reason2 = QualityAuditor.audit_distractor_plausibility(q2)
        self.assertTrue(passed2)

    def test_provenance_missing_page(self):
        q = {"metadata": {"provenance": ["OXFORD_ATLAS"]}}
        passed, reason = QualityAuditor.audit_provenance(q)
        self.assertFalse(passed)
        self.assertIn("lacks concrete page", reason)
        
        q2 = {"metadata": {"provenance": ["OXFORD_ATLAS_PAGE10"]}}
        passed2, reason2 = QualityAuditor.audit_provenance(q2)
        self.assertTrue(passed2)

    def test_unsupported_current_fact(self):
        q = {"metadata": {"currentness": "INVALID_STATE"}}
        passed, reason = QualityAuditor.audit_currentness(q)
        self.assertFalse(passed)
        self.assertIn("Invalid currentness", reason)

    def test_upsc_recall_rejection(self):
        q = {"metadata": {"examTarget": ["UPSC"], "cognitiveDemand": "RECALL"}}
        passed, reason = QualityAuditor.audit_exam_standards(q)
        self.assertFalse(passed)
        self.assertIn("UPSC target requires higher order", reason)

    def test_leakage_candidate_removed(self):
        gen = GeneratorV3(10)
        q1 = {
            "text": "What is the capital of the country north of Spain?", "options": ["Paris", "London", "Berlin"], "correctIndex": 0, 
            "metadata": {"concept": "c1", "examTarget": [], "cognitiveDemand": "RECALL"}, "validation": {}
        }
        q2 = {
            "text": "Which city is Paris located in?", "options": ["France", "UK", "Germany"], "correctIndex": 0,
            "metadata": {"concept": "c2", "examTarget": [], "cognitiveDemand": "RECALL"}, "validation": {}
        }
        gen.questions = [q1, q2]
        res = gen.finalize_batch()
        self.assertEqual(res["accepted"], 1)
        self.assertEqual(res["rejected"], 1)

    def test_same_fact_different_template_rejected(self):
        gen = GeneratorV3(10)
        q1 = {"text": "A", "options": ["1", "2"], "correctIndex": 0, "metadata": {"concept": "fact1", "templateId": "t1", "examTarget": [], "cognitiveDemand": "RECALL"}, "validation": {}}
        q2 = {"text": "B", "options": ["1", "2"], "correctIndex": 0, "metadata": {"concept": "fact1", "templateId": "t2", "examTarget": [], "cognitiveDemand": "RECALL"}, "validation": {}}
        gen.questions = [q1, q2]
        res = gen.finalize_batch()
        self.assertEqual(res["accepted"], 1)
        self.assertEqual(res["rejected"], 1)
        self.assertIn("Concept 'fact1' repeated", res["template_details"][0])

    def test_quality_stop(self):
        gen = GeneratorV3(100) # Asking for 100
        gen.generate()
        self.assertEqual(len(gen.questions) <= 30, True) # It should stop naturally at 30, the number of opportunities

if __name__ == '__main__':
    unittest.main()
