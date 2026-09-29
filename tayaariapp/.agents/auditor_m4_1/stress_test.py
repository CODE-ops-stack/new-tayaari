import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.question_synthesizer import (
    QuestionSynthesizer,
    DistractorVerificationGate,
    NaturalStemSynthesizer,
    DistractorDissector,
    OntologyRegistry,
    VALID_ROOM_TRAP_TYPES,
)
from v13_discovery.semantic_extractor import KnowledgeNode
from v13_discovery.provenance import verify_provenance_chain, audit_provenance_integrity


class TestAdversarialIntegrityStress(unittest.TestCase):
    def setUp(self):
        self.synth = QuestionSynthesizer()

    def test_adv_01_unknown_entity_graceful_fallback(self):
        """Unknown entity not in 38 categories should gracefully resolve without crashing."""
        node = KnowledgeNode(
            node_id="kn_unk_01",
            intent_type="definition",
            primary_entity="Quasar 3C 273",
            predicate="is",
            secondary_entities=[],
            conditions=[],
            quantitative_data=None,
            raw_evidence="Quasar 3C 273 is an astronomical object.",
            source_location={"sourceId": "test.txt", "line": 1, "offset": 0}
        )
        cq = self.synth.synthesize(node)
        self.assertEqual(len(cq.options), 4)
        self.assertIn(cq.correctAnswer, ["opt_a", "opt_b", "opt_c", "opt_d"])
        self.assertEqual(len(cq.distractorDissections), 3)

    def test_adv_02_quote_cleansing_and_sanitization(self):
        """Evidence with nested, single, double, and smart quotes must be completely stripped."""
        node = KnowledgeNode(
            node_id="kn_quotes_01",
            intent_type="definition",
            primary_entity="Granite",
            predicate="is",
            secondary_entities=[],
            conditions=[],
            quantitative_data=None,
            raw_evidence='“Granite” is a \'common\' type of "felsic intrusive igneous rock".',
            source_location={"sourceId": "test.txt", "line": 1, "offset": 0}
        )
        cq = self.synth.synthesize(node)
        for q_char in ['"', "'", "“", "”"]:
            self.assertNotIn(q_char, cq.stem, f"Found quote character {q_char} in stem: {cq.stem}")

    def test_adv_03_null_category_handled(self):
        """DistractorVerificationGate should handle None category gracefully."""
        opts = {"a": "Basalt", "b": "Granite", "c": "Sandstone", "d": "Shale"}
        valid, errs = DistractorVerificationGate.check_category_compatibility(opts, None)
        self.assertTrue(valid)
        self.assertEqual(len(errs), 0)

    def test_adv_04_gate_detects_extreme_length_outlier(self):
        """Gate must reject option that is >= 3x longer than average."""
        opts = {
            "a": "Basalt",
            "b": "Granite",
            "c": "Sandstone",
            "d": "This is an extraordinarily long option that exceeds the average length of other options by more than three times for outlier detection"
        }
        valid, errs = DistractorVerificationGate.check_absence_of_clueing(opts, "opt_a", "Which rock is this?")
        self.assertFalse(valid)
        self.assertTrue(any("length outlier" in e for e in errs))

    def test_adv_05_gate_detects_stem_leakage(self):
        """Gate must reject when correct answer is leaked in the question stem."""
        opts = {"a": "Troposphere", "b": "Stratosphere", "c": "Mesosphere", "d": "Thermosphere"}
        valid, errs = DistractorVerificationGate.check_absence_of_clueing(opts, "opt_a", "Why is the troposphere so low?")
        self.assertFalse(valid)
        self.assertTrue(any("Stem leakage detected" in e for e in errs))

    def test_adv_06_case_auto_repair(self):
        """Lowercase entity input must result in capitalized options via auto-repair."""
        node = KnowledgeNode(
            node_id="kn_case_01",
            intent_type="attribute",
            primary_entity="troposphere",
            predicate="is",
            secondary_entities=[],
            conditions=[],
            quantitative_data=None,
            raw_evidence="troposphere is the lowest atmospheric layer.",
            source_location={"sourceId": "test.txt", "line": 1, "offset": 0}
        )
        cq = self.synth.synthesize(node)
        for k, opt in cq.options.items():
            self.assertTrue(opt[0].isupper(), f"Option '{k}' is not capitalized: {opt}")

    def test_adv_07_all_8_trap_types_valid_format(self):
        """All 8 trap types produce valid pedagogical dissections for distractors."""
        reg = OntologyRegistry()
        cat = reg.get_category("atmospheric_layers")
        for trap in VALID_ROOM_TRAP_TYPES:
            res = DistractorDissector.dissect(
                option_id="opt_b",
                distractor_text="Stratosphere",
                correct_text="Troposphere",
                category=cat,
                intent_type="definition",
                evidence="evidence text",
                forced_trap_type=trap
            )
            self.assertEqual(res["optionId"], "opt_b")
            self.assertEqual(res["trapType"], trap)
            self.assertGreaterEqual(len(res["dissection"]), 15)

    def test_adv_08_provenance_tamper_detection(self):
        """Mutating any field in CandidateQuestion provenance causes verification failure."""
        node = KnowledgeNode(
            node_id="kn_prov_01",
            intent_type="definition",
            primary_entity="Troposphere",
            predicate="is",
            secondary_entities=[],
            conditions=[],
            quantitative_data=None,
            raw_evidence="The troposphere is the lowest atmospheric layer.",
            source_location={"sourceId": "test.txt", "line": 10, "offset": 5}
        )
        cq = self.synth.synthesize(node)
        
        # Test 1: untampered passes
        res1 = verify_provenance_chain(cq.provenance)
        self.assertTrue(res1.is_valid)

        # Test 2: mutated stem fails
        mut_prov = dict(cq.provenance)
        mut_prov["questionStem"] = "Tampered stem?"
        res2 = verify_provenance_chain(mut_prov)
        self.assertFalse(res2.is_valid)
        self.assertTrue(res2.tampered)


if __name__ == "__main__":
    unittest.main()
