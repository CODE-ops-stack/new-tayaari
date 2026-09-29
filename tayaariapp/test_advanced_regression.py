import unittest
from advanced_discovery_pipeline import AdvancedCorpusMiner, AdvancedOpportunitySynthesizer

class TestDiscoveryRegression(unittest.TestCase):
    def setUp(self):
        with open("mock_regression.txt", "w", encoding="utf-8") as f:
            f.write("It is known as a bad entity. The leads to nothing. This causes problems due to lack of context. "
                    "The massive subduction zone causes deep earthquakes due to tectonic plate convergence. "
                    "A short claim consists of words. "
                    "The Himalayan mountain building process differs from the Andean orogeny. ")
            
    def test_multiword_entity_preservation(self):
        miner = AdvancedCorpusMiner(["mock_regression.txt"])
        res = miner._extract_entities("The Chota Nagpur Plateau is large.")
        self.assertTrue(any("Chota Nagpur Plateau" in r for r in res))
        pass
        
    def test_rejects_unresolved_entities(self):
        miner = AdvancedCorpusMiner(["mock_regression.txt"])
        nodes, rejected = miner.discover_nodes()
        reasons = [r["reason"] for r in rejected]
        self.assertTrue(any("Unresolved pronoun" in r for r in reasons))

    def test_false_upsc_classification(self):
        synth = AdvancedOpportunitySynthesizer()
        mock_node = {
            "sourceId": "mock", "section": "mock", "evidenceExcerpt": "mock",
            "concept": "mock", "topic": "Climatology", "subject": "Rain", "currentnessStatus": "HISTORICAL",
            "claims": [],
            "relationships": [{"type": "cause_effect", "cause": "short cause", "effect": "effect", "inference": "inference", "distractors": ["d1"]}]
        }
        opps = synth.synthesize([mock_node])
        if opps:
            self.assertEqual(opps[0]["metadata"]["cognitiveDemand"], "RECALL") # very short downgraded to RECALL
        
    def test_malformed_stem_rejection(self):
        synth = AdvancedOpportunitySynthesizer()
        pass
        self.assertTrue(synth._is_malformed_stem("Identify {subject}", "ok ok ok"))
        self.assertTrue(synth._is_malformed_stem("Very short stem", "ok ok ok"))
        self.assertFalse(synth._is_malformed_stem("Based on geographical processes, what is the direct consequence of the fact that plate tectonics occur?", "ok ok ok"))

if __name__ == "__main__":
    unittest.main()

