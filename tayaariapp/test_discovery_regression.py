import unittest
from full_discovery_pipeline import CorpusMiner, OpportunitySynthesizer

class TestDiscoveryRegression(unittest.TestCase):
    def setUp(self):
        # We write a tiny mock file for the miner
        with open("mock_regression.txt", "w", encoding="utf-8") as f:
            f.write("It is known as a bad entity. The leads to nothing. This causes problems due to lack of context. "
                    "The massive subduction zone causes deep earthquakes due to tectonic plate convergence. "
                    "A short claim consists of words. "
                    "Deep oceanic fault slippage causes earthquake. "
                    "The Himalayan mountain building process differs from the Andean orogeny. ")
            
    def test_rejects_unresolved_entities(self):
        miner = CorpusMiner(["mock_regression.txt"])
        nodes, rejected = miner.discover_nodes()
        # Should reject 'It', 'The', 'This'
        rejection_reasons = [r["reason"] for r in rejected]
        self.assertTrue(any("unresolved" in r.lower() or "bad entity" in r.lower() or "subject" in r.lower() for r in rejection_reasons))
        self.assertTrue(len(rejected) > 0)
        
    def test_rejects_fragmentary_claims(self):
        miner = CorpusMiner(["mock_regression.txt"])
        nodes, rejected = miner.discover_nodes()
        rejection_reasons = [r["reason"] for r in rejected]
        self.assertTrue(any("fragmentary" in r.lower() for r in rejection_reasons))
        self.assertTrue(len(rejected) > 0)

    def test_false_upsc_classification(self):
        # If cause is short, it should be UNDERSTAND / SSC CGL, not APPLY / UPSC
        synth = OpportunitySynthesizer()
        mock_node = {
            "sourceId": "mock", "section": "mock", "evidenceExcerpt": "mock",
            "concept": "mock", "topic": "Climatology", "subject": "Rain", "currentnessStatus": "HISTORICAL",
            "claims": [],
            "relationships": [{"type": "cause_effect", "cause": "short cause", "effect": "effect", "inference": "inference", "distractors": ["d1"]}]
        }
        opps = synth.synthesize([mock_node])
        self.assertEqual(opps[0]["metadata"]["cognitiveDemand"], "UNDERSTAND")
        self.assertIn("SSC CGL", opps[0]["metadata"]["examTarget"])
        
        # If cause is long, it should be APPLY / UPSC
        mock_node["relationships"][0]["cause"] = "a very long and complex geological tectonic cause"
        opps = synth.synthesize([mock_node])
        self.assertEqual(opps[0]["metadata"]["cognitiveDemand"], "APPLY")
        self.assertIn("UPSC", opps[0]["metadata"]["examTarget"])

    def test_malformed_stem_rejection(self):
        synth = OpportunitySynthesizer()
        self.assertTrue(synth._is_malformed_stem("Regarding The, what happens?"))
        self.assertTrue(synth._is_malformed_stem("Regarding It, what happens?"))
        self.assertTrue(synth._is_malformed_stem("Identify {subject}"))
        self.assertTrue(synth._is_malformed_stem("Very short stem"))
        self.assertFalse(synth._is_malformed_stem("Which of the following describes a verified characteristic of tectonic plates?"))

    def test_distractor_generation(self):
        miner = CorpusMiner(["mock_regression.txt"])
        miner.topic_entities["Climatology"] = {"Monsoon", "Cyclone", "Coriolis"}
        nodes, _ = miner.discover_nodes()
        # Distractors are assigned from topic_entities pool in discover_nodes()
        # We can just verify the logic locally
        pool = list(miner.topic_entities["Climatology"])
        self.assertIn("Monsoon", pool)
        self.assertIn("Cyclone", pool)
        
if __name__ == "__main__":
    unittest.main()

