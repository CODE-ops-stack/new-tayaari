import unittest
import sys
import os

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

from v13_discovery.normalizer import DocumentNormalizer, BlockType
from v13_discovery.semantic_extractor import SemanticExtractor, KnowledgeNode, NoiseFilterGate, LinguisticSemanticExtractor, canonicalize_intent

class AdversarialStressTest(unittest.TestCase):
    def setUp(self):
        self.extractor = SemanticExtractor()
        self.normalizer = DocumentNormalizer()
        self.noise_gate = NoiseFilterGate()

    def test_empty_and_whitespace_inputs(self):
        """Stress test: Empty and degenerate string inputs should not raise exceptions."""
        for degenerate in ["", "   ", "\n\n\t", "....", "!!!???"]:
            res = self.extractor.extract(degenerate)
            self.assertEqual(res, [], f"Expected empty extraction for '{degenerate}', got {res}")

    def test_unseen_domain_propositions(self):
        """Stress test: Generalization on completely unseen NCERT/UPSC facts."""
        unseen_test_cases = [
            # Definition
            ("A glacier is defined as a persistent body of dense ice constantly moving under its own gravity.", "definition", "glacier"),
            # Attribute
            ("Basalt has the lowest mean density among mafic extrusive rocks.", "attribute", "Basalt"),
            # Cause/Effect
            ("Excessive groundwater extraction causes significant ground subsidence in alluvial plains.", "cause_effect", "Excessive groundwater extraction"),
            # Comparison
            ("Unlike metamorphic rocks, sedimentary rocks are characterized by distinct stratification.", "comparison", "sedimentary rocks"),
            # Spatial
            ("The Brahmaputra River flows through Tibet before entering Arunachal Pradesh.", "spatial", "Brahmaputra River"),
            # Quantity
            ("The equatorial diameter measures approximately 12756 kilometres.", "quantity", "equatorial diameter"),
            # Classification
            ("Geologists classify sedimentary rocks into clastic, chemical, and organic categories.", "classification", "sedimentary rocks"),
            # Condition
            ("Tropical cyclones can occur only if sea surface temperatures exceed 27 degrees Celsius.", "condition", "Tropical cyclones"),
            # Exception
            ("All terrestrial planets have solid rocky surfaces, except the dwarf planets which exhibit icy mantles.", "exception", "terrestrial planets"),
        ]

        for text, expected_intent, expected_entity in unseen_test_cases:
            nodes = self.extractor.extract(text)
            self.assertGreaterEqual(len(nodes), 1, f"Failed to extract unseen fact: '{text}'")
            actual_intent = canonicalize_intent(nodes[0].intent_type)
            self.assertEqual(
                actual_intent, canonicalize_intent(expected_intent),
                f"Intent mismatch on unseen text '{text}': expected {expected_intent}, got {actual_intent}"
            )
            self.assertIn(
                expected_entity.lower(), nodes[0].primary_entity.lower(),
                f"Primary entity mismatch on unseen text '{text}': expected '{expected_entity}' in '{nodes[0].primary_entity}'"
            )

    def test_adversarial_noise_variations(self):
        """Stress test: Subtly disguised noise should be rejected by NoiseFilterGate."""
        subtle_noise = [
            # Disguised MCQ
            "Option D: All of the above are valid characteristics of the mantle.",
            # Isolated heading / reading order collision
            "UniverseGalaxySolar SystemMilkyWay",
            # Truncated conjunction fragment
            "The continental shelf descends steeply towards the abyssal plain and",
            # Dangling preposition
            "Most seismic activity in the circum-Pacific belt occurs along",
            # Unresolved anaphoric pronoun
            "They absorb large amounts of solar radiation in the upper atmosphere.",
            # Table formatting debris
            "|---|---|---|---|",
        ]

        for noise in subtle_noise:
            audit_result = self.noise_gate.audit(noise)
            extracted = self.extractor.extract(noise)
            self.assertTrue(
                audit_result is not None or len(extracted) == 0,
                f"Adversarial noise not rejected: '{noise}', extracted: {extracted}"
            )

    def test_normalizer_malformed_tables(self):
        """Stress test: Malformed, ragged, or empty markdown tables should be handled gracefully."""
        ragged_table = (
            "| Mineral | Hardness |\n"
            "|---|---|\n"
            "| Talc | 1 |\n"
            "| Diamond |\n"  # missing column cell
            "| Quartz | 7 | Extra | Cell |\n" # extra columns
        )
        block = {
            "sourceId": "test_ragged",
            "text": ragged_table
        }
        normalized = self.normalizer.normalize_block(block)
        self.assertEqual(normalized.type, BlockType.TABLE)
        # Should cleanly extract Talc and Quartz rows without crashing
        self.assertTrue(any("Talc" in s for s in normalized.clean_sentences))
        self.assertTrue(any("Quartz" in s for s in normalized.clean_sentences))

    def test_performance_throughput(self):
        """Stress test: Process 500 sentences rapidly to verify no latency or memory leaks."""
        sample_sentence = "The sun, the moon and all those objects shining in the night sky are called celestial bodies."
        import time
        t0 = time.perf_counter()
        for _ in range(500):
            res = self.extractor.extract(sample_sentence)
            assert len(res) == 1
        elapsed = time.perf_counter() - t0
        rate = 500 / elapsed
        print(f"\nThroughput: {rate:.1f} sentences/sec (elapsed: {elapsed:.3f}s for 500 extractions)")
        self.assertGreater(rate, 200, f"Extraction throughput too low: {rate:.1f} sent/sec")

if __name__ == "__main__":
    unittest.main()
