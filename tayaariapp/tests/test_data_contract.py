"""Regression tests for the locked Android question data contract."""

import unittest

from v13_discovery.data_contract import (
    is_legacy_bare_letter_options,
    reject_legacy_mismatch,
    validate_locked_question,
)
from v13_discovery.question_synthesizer import (
    CandidateQuestion,
    DistractorVerificationGate,
    OntologyRegistry,
    QuestionSynthesizer,
)
from types import SimpleNamespace


LOCKED = {
    "stem": "Which of the following is defined as a crescent-shaped lake formed when a river meander is cut off?",
    "options": [
        {"id": "opt_a", "text": "Oxbow lake"},
        {"id": "opt_b", "text": "Meander"},
        {"id": "opt_c", "text": "Gorge"},
        {"id": "opt_d", "text": "Alluvial fan"},
    ],
    "correctAnswer": "opt_a",
    "explanation": "Option (A) is correct. Oxbow lake: Crescent-shaped lake formed when a river meander is cut off from the main channel.",
    "distractorDissections": [
        {"optionId": "opt_b", "trapType": "CONCEPT_MIX", "dissection": "Meander is the bend, not the cutoff lake."},
        {"optionId": "opt_c", "trapType": "FACT_DISTORTION", "dissection": "A gorge is a steep valley."},
        {"optionId": "opt_d", "trapType": "FAMILIARITY_TRAP", "dissection": "An alluvial fan forms at a slope break."},
    ],
    "format": "Direct Fact",
    "tier": "Medium",
}


class TestLockedDataContract(unittest.TestCase):
    def test_locked_shape_passes(self):
        self.assertEqual(validate_locked_question(LOCKED), [])

    def test_bare_letter_dict_fails(self):
        bad = dict(LOCKED)
        bad["options"] = {"a": "Oxbow lake", "b": "Meander", "c": "Gorge", "d": "Alluvial fan"}
        errors = validate_locked_question(bad)
        self.assertTrue(any("list" in e for e in errors))
        self.assertTrue(reject_legacy_mismatch(bad["options"], "opt_a"))

    def test_correct_answer_must_be_option_id(self):
        bad = dict(LOCKED)
        bad["correctAnswer"] = "a"
        errors = validate_locked_question(bad)
        self.assertTrue(any("correctAnswer" in e for e in errors))

    def test_legacy_mismatch_detector(self):
        opts = {"a": "x", "b": "y", "c": "z", "d": "w"}
        self.assertTrue(is_legacy_bare_letter_options(opts))
        self.assertTrue(reject_legacy_mismatch(opts, "opt_b"))

    def test_constructed_candidate_invariant(self):
        cq = CandidateQuestion(
            id="q_probe",
            stem=LOCKED["stem"],
            options=LOCKED["options"],
            correctAnswer="opt_a",
            explanation=LOCKED["explanation"],
            distractorDissections=LOCKED["distractorDissections"],
            provenance={},
            cognitiveDemand="UNDERSTAND",
        )
        ids = [o["id"] for o in cq.options]
        self.assertIn(cq.correctAnswer, ids)
        ok, errs = DistractorVerificationGate.verify_all(cq.options, cq.correctAnswer, cq.stem)
        self.assertTrue(ok, errs)

    def test_unknown_entity_is_rejected_not_guessed(self):
        synth = QuestionSynthesizer()
        node = SimpleNamespace(
            node_id="n_unknown",
            intent_type="definition",
            primary_entity="Industrial Revolution",
            raw_evidence="The industrial revolution began in Britain.",
            predicate="",
            primaryEntity="Industrial Revolution",
            rawEvidence="The industrial revolution began in Britain.",
            intentType="definition",
            nodeId="n_unknown",
        )
        cq = synth.synthesize(node, shuffle=False)
        self.assertFalse(cq.valid)
        self.assertIn("Unknown category", cq.explanation)

    def test_no_substring_star_started(self):
        ont = OntologyRegistry()
        self.assertIsNone(ont.find_category_for_entity("started"))
        self.assertIsNone(ont.find_category_for_entity("industrial"))

    def test_no_silent_sibling_fallback(self):
        ont = OntologyRegistry()
        self.assertEqual(ont.get_siblings("Industrial Revolution"), [])


if __name__ == "__main__":
    unittest.main()
