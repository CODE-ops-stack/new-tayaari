#!/usr/bin/env python3
"""
tests/test_v13_challenger_it4_empirics.py
==========================================
Empirical Challenger Verification Suite for Milestone 2 Iteration 4.
Agent: teamwork_preview_challenger_m2_it4_2

Authoritative verification of:
1. False Positive Noise Rejection:
   - Terminal ? and wh-word questions -> 100% rejected, 0 leaked nodes
   - Incomplete fragments (composed of, consists of, known as, Scientists have discovered that...) -> 100% rejected
   - Ungrounded possessives (Its average temperature is...) -> 100% rejected
2. Discourse Context Number Agreement:
   - Mars moons: Phobos and Deimos attributed to Mars, NOT Earth
   - Ganges length: 2525 km attributed to Ganges, NOT Indus
   - Himalayas peaks: Highest peaks attributed to Himalayas, NOT Alps
   - Extended proper nouns (Venus, Thames, Andes, etc.) and reverse ordering
3. Soft-Hyphen Desegmentation:
   - Multi-line OCR column wrapping with hyphens stitches cleanly without fake headings or dropped words
4. Formatting Noise Sanitization:
   - Ligatures, smart quotes, em-dashes, en-dashes, markdown formatting, HTML entities
5. Anti-Overfitting Audit:
   - Zero hardcoded domain strings
"""

import os
import sys
import unittest
from typing import List, Dict, Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from v13_discovery.semantic_extractor import (
    SemanticExtractor,
    LinguisticSemanticExtractor,
    NoiseFilterGate,
    DiscourseContext,
    KnowledgeNode,
    canonicalize_intent,
)
from v13_discovery.normalizer import DocumentNormalizer, LayoutDesegmenter, NormalizedBlock


class TestFalsePositiveQuestionRejection(unittest.TestCase):
    """Empirical challenge on interrogative question rejection (terminal ? and wh-words)."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_interrogative_questions_with_terminal_question_mark_are_100_percent_rejected(self):
        """Verify all forms of interrogative questions emit 0 nodes."""
        questions = [
            "What is an earthquake?",
            "Why does the wind blow from high to low pressure?",
            "How are metamorphic rocks formed in nature?",
            "Which atmospheric layer contains the ozone layer?",
            "Can sedimentary rocks transform into igneous rocks?",
            "Do tectonic plates move across the asthenosphere?",
            "Does the ozone layer protect the biosphere from ultraviolet radiation?",
            "Is the oceanic crust primarily composed of basalt?",
            "Are fold mountains formed by compressional tectonic forces?",
            "Where are convective currents located in the Earth?",
            "When did the Pangea supercontinent begin to rift?",
            "Who discovered the continental drift hypothesis?",
            "Whose classification divided world climates into five vegetation groups?",
            "Whom did Alfred Wegener consult regarding paleoclimatic evidence?",
            "Will global sea levels continue to rise?",
            "Could seismic surface waves cause substantial structural damage?",
            "Should seismic building codes be strictly enforced?",
        ]
        for q in questions:
            nodes = self.extractor.extract(q)
            self.assertEqual(
                len(nodes), 0,
                f"Question leaked as factual node! Question: '{q}' emitted: {[(n.primary_entity, n.intent_type, n.predicate) for n in nodes]}"
            )
            audit_verdict = NoiseFilterGate.audit(q, is_block_context=False)
            self.assertEqual(
                audit_verdict, "interrogative_question",
                f"NoiseFilterGate failed to flag '{q}' as interrogative_question. Got: {audit_verdict}"
            )

    def test_quoted_and_parenthetical_questions_are_rejected(self):
        """Verify questions enclosed in quotes or parentheses emit 0 nodes."""
        quoted_questions = [
            '"What is an earthquake?"',
            '“Why does continental drift occur?”',
            "(How are metamorphic rocks formed in nature?)",
            "[Which atmospheric layer contains the ozone layer?]",
            "'Can sedimentary rocks transform into igneous rocks?'",
        ]
        for q in quoted_questions:
            nodes = self.extractor.extract(q)
            self.assertEqual(len(nodes), 0, f"Quoted question leaked: '{q}'")

    def test_interrogatives_ending_without_question_mark_are_rejected(self):
        """Verify wh-word question prompts ending with a period emit 0 nodes."""
        pseudo_questions = [
            "What is the equatorial circumference of Earth.",
            "Which atmospheric layer contains the ozone layer.",
            "Why convective currents operate in the mantle.",
            "How metamorphic rocks are formed in nature.",
            "Where convective cells operate in the mantle.",
            "Who discovered the continental drift hypothesis.",
        ]
        for pq in pseudo_questions:
            nodes = self.extractor.extract(pq)
            self.assertEqual(
                len(nodes), 0,
                f"Wh-word declarative prompt leaked as factual node: '{pq}' -> {[(n.primary_entity, n.predicate) for n in nodes]}"
            )

    def test_questions_inside_prose_block_do_not_leak_or_pollute_discourse(self):
        """Verify questions embedded inside a NormalizedBlock are dropped and do not pollute discourse."""
        block = NormalizedBlock(
            id="blk_q_mix",
            text="The Earth is the third planet from the Sun. What is the average density of Saturn? It has one natural satellite known as the Moon.",
            type="PROSE",
            clean_sentences=[
                "The Earth is the third planet from the Sun.",
                "What is the average density of Saturn?",
                "It has one natural satellite known as the Moon."
            ]
        )
        nodes = self.extractor.extract(block)
        self.assertEqual(len(nodes), 2, f"Expected 2 nodes (Earth definition & Earth attribute), got {len(nodes)}")
        self.assertEqual(nodes[0].primary_entity, "Earth")
        self.assertEqual(nodes[1].primary_entity, "Earth")
        self.assertNotIn("Saturn", [n.primary_entity for n in nodes])
        self.assertNotIn("What", [n.primary_entity for n in nodes])


class TestIncompleteFragmentRejection(unittest.TestCase):
    """Empirical challenge on incomplete fragments (composed of, consists of, known as, etc.)."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_dangling_relational_fragments_are_100_percent_rejected(self):
        """Verify sentences ending in relational connectors emit 0 nodes."""
        fragments = [
            "The oceanic crust is composed of",
            "The oceanic crust is composed of.",
            "The continental crust consists of",
            "The continental crust consists of.",
            "The lowest layer of the atmosphere is known as",
            "The lowest layer of the atmosphere is known as.",
            "The atmospheric envelope is defined as",
            "The boundary between crust and mantle is termed as",
            "The seismic discontinuity is referred to as",
            "Various types of rocks such as",
            "The continental shelf extends to a depth of",
            "The seismic waves propagate rapidly through the crust whereas",
            "Because the Earth rotates from west to east and",
        ]
        for frag in fragments:
            nodes = self.extractor.extract(frag)
            self.assertEqual(
                len(nodes), 0,
                f"Dangling fragment leaked as factual node! Fragment: '{frag}' emitted: {nodes}"
            )
            audit_verdict = NoiseFilterGate.audit(frag, is_block_context=False)
            self.assertIn(
                audit_verdict, ["syntactic_fragment"],
                f"NoiseFilterGate failed to flag '{frag}' as syntactic_fragment. Got: {audit_verdict}"
            )

    def test_incomplete_epistemic_embedded_clauses_are_rejected(self):
        """Verify 'Scientists have discovered that [noun phrase]' without verb is rejected."""
        epistemic_frags = [
            "Scientists have discovered that the inner core",
            "Scientists have discovered that the inner core.",
            "Geologists have found that mantle convection",
            "Seismologists have proved that S-waves",
            "Studies have shown that tectonic plates",
            "Researchers have revealed that oceanic crust",
            "Astronomers have demonstrated that comets",
            "Physicists have established that energy",
        ]
        for ef in epistemic_frags:
            nodes = self.extractor.extract(ef)
            self.assertEqual(
                len(nodes), 0,
                f"Incomplete epistemic clause leaked as factual node! Clause: '{ef}' emitted: {nodes}"
            )
            audit_verdict = NoiseFilterGate.audit(ef, is_block_context=False)
            self.assertEqual(
                audit_verdict, "syntactic_fragment",
                f"NoiseFilterGate failed to flag '{ef}' as syntactic_fragment. Got: {audit_verdict}"
            )

    def test_complete_epistemic_embedded_clauses_are_extracted(self):
        """Verify complete sentences with epistemic verbs are extracted (not rejected as noise)."""
        complete = [
            ("Scientists have discovered that the inner core is solid iron and nickel.", "scientists"),
            ("Geologists have proved that tectonic plates move continuously across the asthenosphere.", "geologists"),
        ]
        for sent, expected_entity in complete:
            nodes = self.extractor.extract(sent)
            self.assertGreaterEqual(len(nodes), 1, f"Failed to extract valid knowledge from: '{sent}'")
            self.assertIn(expected_entity.lower(), nodes[0].primary_entity.lower())


class TestUngroundedPossessivesRejection(unittest.TestCase):
    """Empirical challenge on ungrounded possessives and anaphoric determiners."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_isolated_ungrounded_possessives_return_zero_nodes(self):
        """Verify sentences starting with ungrounded possessives emit 0 nodes."""
        ungrounded = [
            "Its average temperature is minus 60 degrees Celsius.",
            "Their diameter exceeds 100 kilometres.",
            "His hypothesis proposed continental drift in 1912.",
            "Her discovery of the inner core occurred in 1936.",
            "Their orbits maintain high eccentricities across centuries.",
            "Its atmosphere is composed primarily of carbon dioxide and nitrogen.",
        ]
        for sent in ungrounded:
            nodes = self.extractor.extract(sent)
            self.assertEqual(
                len(nodes), 0,
                f"Ungrounded possessive leaked as node! Sentence: '{sent}' emitted: {nodes}"
            )

    def test_prose_block_without_antecedent_starting_with_possessive_returns_zero_nodes(self):
        """Verify multi-sentence block starting with ungrounded possessive emits 0 nodes."""
        block = NormalizedBlock(
            id="blk_ungrounded_poss",
            text="Its atmosphere is composed primarily of carbon dioxide. Their surface temperatures vary widely.",
            type="PROSE",
            clean_sentences=[
                "Its atmosphere is composed primarily of carbon dioxide.",
                "Their surface temperatures vary widely."
            ]
        )
        nodes = self.extractor.extract(block)
        self.assertEqual(len(nodes), 0, f"Leaked nodes from ungrounded possessive block: {nodes}")

    def test_grounded_possessives_resolve_antecedent_cleanly(self):
        """Verify grounded possessives properly resolve and attribute facts."""
        # Mars
        block_mars = NormalizedBlock(
            id="blk_mars_poss",
            text="Mars is the fourth planet from the Sun. Its atmosphere is composed of carbon dioxide.",
            type="PROSE",
            clean_sentences=[
                "Mars is the fourth planet from the Sun.",
                "Its atmosphere is composed of carbon dioxide."
            ]
        )
        nodes_mars = self.extractor.extract(block_mars)
        self.assertEqual(len(nodes_mars), 2)
        self.assertEqual(nodes_mars[0].primary_entity, "Mars")
        self.assertEqual(nodes_mars[1].primary_entity, "Mars's atmosphere")

        # Himalayas
        block_him = NormalizedBlock(
            id="blk_him_poss",
            text="The Himalayas are young fold mountains in Asia. Their peaks are covered with permanent snow.",
            type="PROSE",
            clean_sentences=[
                "The Himalayas are young fold mountains in Asia.",
                "Their peaks are covered with permanent snow."
            ]
        )
        nodes_him = self.extractor.extract(block_him)
        self.assertEqual(len(nodes_him), 2)
        self.assertEqual(nodes_him[0].primary_entity, "Himalayas")
        self.assertEqual(nodes_him[1].primary_entity, "Himalayas's peaks")


class TestDiscourseCoreferenceNumberAgreement(unittest.TestCase):
    """Empirical challenge on DiscourseContext number agreement across proper nouns ending in 's'."""

    def setUp(self):
        self.extractor = SemanticExtractor()

    def test_mars_moons_attributed_to_mars_not_earth(self):
        """Verify Phobos and Deimos are attributed to Mars, NOT Earth."""
        block = NormalizedBlock(
            id="blk_mars_earth",
            text="The Earth is the third planet from the Sun. Mars is the fourth planet from the Sun. It has two small moons named Phobos and Deimos.",
            type="PROSE",
            clean_sentences=[
                "The Earth is the third planet from the Sun.",
                "Mars is the fourth planet from the Sun.",
                "It has two small moons named Phobos and Deimos."
            ]
        )
        nodes = self.extractor.extract(block)
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].primary_entity, "Earth")
        self.assertEqual(nodes[1].primary_entity, "Mars")
        self.assertEqual(
            nodes[2].primary_entity, "Mars",
            f"FACTUAL DISTORTION: Mars moons resolved to {nodes[2].primary_entity} instead of Mars!"
        )
        self.assertIn("two small moons", nodes[2].predicate)

    def test_ganges_length_attributed_to_ganges_not_indus(self):
        """Verify 2525 km length is attributed to Ganges, NOT Indus."""
        block = NormalizedBlock(
            id="blk_ganges_indus",
            text="The Indus is a trans-Himalayan river. The Ganges is a major river in northern India. It has a total length of 2525 kilometres.",
            type="PROSE",
            clean_sentences=[
                "The Indus is a trans-Himalayan river.",
                "The Ganges is a major river in northern India.",
                "It has a total length of 2525 kilometres."
            ]
        )
        nodes = self.extractor.extract(block)
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].primary_entity, "Indus")
        self.assertEqual(nodes[1].primary_entity, "Ganges")
        self.assertEqual(
            nodes[2].primary_entity, "Ganges",
            f"FACTUAL DISTORTION: Ganges length resolved to {nodes[2].primary_entity} instead of Ganges!"
        )
        self.assertIn("2525 kilometres", nodes[2].predicate)

    def test_himalayas_peaks_attributed_to_himalayas_not_alps(self):
        """Verify highest peaks are attributed to Himalayas, NOT Alps."""
        block = NormalizedBlock(
            id="blk_himalayas_alps",
            text="The Alps are fold mountains in Europe. The Himalayas are young fold mountains in Asia. They have the highest peaks in the world.",
            type="PROSE",
            clean_sentences=[
                "The Alps are fold mountains in Europe.",
                "The Himalayas are young fold mountains in Asia.",
                "They have the highest peaks in the world."
            ]
        )
        nodes = self.extractor.extract(block)
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].primary_entity, "Alps")
        self.assertEqual(nodes[1].primary_entity, "Himalayas")
        self.assertEqual(
            nodes[2].primary_entity, "Himalayas",
            f"FACTUAL DISTORTION: Himalayas peaks resolved to {nodes[2].primary_entity} instead of Himalayas!"
        )
        self.assertIn("highest peaks", nodes[2].predicate)

    def test_reverse_ordering_proper_nouns(self):
        """Verify reverse ordering: Mars first, Earth second -> Moon resolves to Earth."""
        block = NormalizedBlock(
            id="blk_rev_order",
            text="Mars is the fourth planet from the Sun. The Earth is the third planet from the Sun. It has one natural satellite known as the Moon.",
            type="PROSE",
            clean_sentences=[
                "Mars is the fourth planet from the Sun.",
                "The Earth is the third planet from the Sun.",
                "It has one natural satellite known as the Moon."
            ]
        )
        nodes = self.extractor.extract(block)
        self.assertEqual(len(nodes), 3)
        self.assertEqual(nodes[0].primary_entity, "Mars")
        self.assertEqual(nodes[1].primary_entity, "Earth")
        self.assertEqual(nodes[2].primary_entity, "Earth")

    def test_proper_nouns_ending_in_s_in_discourse_context(self):
        """Verify DiscourseContext classification of singular and plural proper nouns ending in 's'."""
        ctx = DiscourseContext()
        # Singular proper noun ending in 's'
        ctx.register_entity("Venus", sentence="Venus is the second planet from the Sun.")
        # Plural proper noun ending in 's'
        ctx.register_entity("Andes", sentence="The Andes are fold mountains in South America.")
        
        # When both are present: 'it' resolves to Venus (singular), 'they' resolves to Andes (plural)
        self.assertEqual(ctx.resolve("it"), "Venus")
        self.assertEqual(ctx.resolve("they"), "Andes")

        # Register another singular: Thames
        ctx.register_entity("Thames", sentence="The Thames is a river in southern England.")
        # 'it' should now resolve to most recent singular: Thames
        self.assertEqual(ctx.resolve("it"), "Thames")
        # 'they' should still resolve to Andes
        self.assertEqual(ctx.resolve("they"), "Andes")

        # Register another plural: Himalayas
        ctx.register_entity("Himalayas", sentence="The Himalayas are young fold mountains in Asia.")
        # 'they' should now resolve to most recent plural: Himalayas
        self.assertEqual(ctx.resolve("they"), "Himalayas")
        # 'it' should still resolve to Thames
        self.assertEqual(ctx.resolve("it"), "Thames")


class TestSoftHyphenDesegmentation(unittest.TestCase):
    """Empirical challenge on OCR narrow-column soft-hyphen desegmentation."""

    def setUp(self):
        self.normalizer = DocumentNormalizer()
        self.extractor = SemanticExtractor()

    def test_ocr_wrapped_trailing_hyphens_stitch_cleanly(self):
        """Verify narrow-column text with trailing hyphens reconstructs cleanly without fake headings or dropped words."""
        multi_col_raw = """
The tropo-
sphere is the low-
est layer of the
atmosphere. It ex-
tends up to an aver-
age height of 13
kilometres.
"""
        blocks = self.normalizer.normalize(multi_col_raw, "multicolumn_doc")
        self.assertEqual(len(blocks), 1, f"Expected 1 normalized block, got {len(blocks)}")
        b = blocks[0]
        self.assertIsNone(
            b.metadata.get("section_heading"),
            f"Corrupted section heading: '{b.metadata.get('section_heading')}'"
        )
        self.assertEqual(len(b.clean_sentences), 2)
        self.assertEqual(b.clean_sentences[0], "The troposphere is the lowest layer of the atmosphere.")
        self.assertEqual(b.clean_sentences[1], "It extends up to an average height of 13 kilometres.")

        nodes = self.extractor.extract(b)
        self.assertGreaterEqual(len(nodes), 2)
        self.assertEqual(nodes[0].primary_entity, "troposphere")
        self.assertEqual(nodes[1].primary_entity, "atmosphere")

    def test_hyphenated_line_wrap_is_never_heading(self):
        """Verify LayoutDesegmenter.is_heading returns False for trailing hyphens."""
        hyphen_lines = [
            "The tropo-",
            "atmo-",
            "litho-",
            "strati-",
            "contin-",
            "The tropo\u00ad",
        ]
        for hl in hyphen_lines:
            self.assertFalse(
                LayoutDesegmenter.is_heading(hl),
                f"LayoutDesegmenter.is_heading incorrectly returned True for: '{hl}'"
            )


class TestFormattingNoiseSanitization(unittest.TestCase):
    """Empirical challenge on formatting noise, ligatures, quotes, and markdown."""

    def setUp(self):
        self.normalizer = DocumentNormalizer()
        self.extractor = SemanticExtractor()

    def test_unicode_ligatures_sanitize_and_extract(self):
        """Verify ligatures (fi, fl) decompose and extract valid nodes."""
        raw = "The \ufb01rst layer of the atmosphere is the troposphere, which exhibits signi\ufb01cant moisture \ufb02uxes."
        blocks = self.normalizer.normalize(raw)
        self.assertEqual(len(blocks), 1)
        nodes = self.extractor.extract(blocks[0])
        self.assertGreaterEqual(len(nodes), 1)
        self.assertIn("first layer", nodes[0].primary_entity.lower())

    def test_smart_quotes_sanitize_and_extract(self):
        """Verify smart quotes are stripped and extract valid nodes."""
        raw = "“The lithosphere” is defined as the rigid outer crust and upper mantle of the Earth."
        blocks = self.normalizer.normalize(raw)
        self.assertEqual(len(blocks), 1)
        nodes = self.extractor.extract(blocks[0])
        self.assertGreaterEqual(len(nodes), 1)
        self.assertIn("lithosphere", nodes[0].primary_entity.lower())
        self.assertNotIn('"', nodes[0].primary_entity)

    def test_em_dashes_and_en_dashes_sanitize_and_extract(self):
        """Verify em-dashes and en-dashes normalize cleanly."""
        raw_em = "Igneous rocks—formed through cooling of magma—are classified into intrusive and extrusive types."
        blocks_em = self.normalizer.normalize(raw_em)
        nodes_em = self.extractor.extract(blocks_em[0])
        self.assertGreaterEqual(len(nodes_em), 1)
        self.assertEqual(canonicalize_intent(nodes_em[0].intent_type), "classification")

        raw_en = "The mesosphere extends from 50–80 kilometres above the Earth surface."
        blocks_en = self.normalizer.normalize(raw_en)
        nodes_en = self.extractor.extract(blocks_en[0])
        self.assertGreaterEqual(len(nodes_en), 1)
        self.assertEqual(canonicalize_intent(nodes_en[0].intent_type), "spatial")

    def test_markdown_formatting_and_escapes_sanitize_and_extract(self):
        """Verify markdown bold, italics, and backslash escapes extract cleanly."""
        raw_bold = "The **lithosphere** is defined as the rigid outer shell of the Earth."
        blocks_bold = self.normalizer.normalize(raw_bold)
        nodes_bold = self.extractor.extract(blocks_bold[0])
        self.assertGreaterEqual(len(nodes_bold), 1)
        self.assertEqual(nodes_bold[0].primary_entity.strip(), "lithosphere")
        self.assertNotIn("*", nodes_bold[0].primary_entity)

        raw_esc = "The \\*lithosphere\\* is defined as the rigid outer shell of the Earth."
        blocks_esc = self.normalizer.normalize(raw_esc)
        nodes_esc = self.extractor.extract(blocks_esc[0])
        self.assertGreaterEqual(len(nodes_esc), 1)
        self.assertEqual(nodes_esc[0].primary_entity.strip(), "lithosphere")

    def test_html_entities_sanitize_and_extract(self):
        """Verify HTML entities like &amp; unescape and extract cleanly."""
        raw = "The lithosphere is composed of the crust &amp; upper mantle of the Earth."
        blocks = self.normalizer.normalize(raw)
        nodes = self.extractor.extract(blocks[0])
        self.assertGreaterEqual(len(nodes), 1)
        self.assertEqual(canonicalize_intent(nodes[0].intent_type), "part_of")
        self.assertIn("crust and upper mantle", nodes[0].predicate)

    def test_accented_characters_sanitize_and_extract(self):
        """Verify accented characters decompose and extract cleanly."""
        raw = "The Köppen climate classification system divides climates into five main vegetation groups."
        blocks = self.normalizer.normalize(raw)
        nodes = self.extractor.extract(blocks[0])
        self.assertGreaterEqual(len(nodes), 1)
        self.assertEqual(canonicalize_intent(nodes[0].intent_type), "classification")


class TestAntiOverfittingBannedStrings(unittest.TestCase):
    """Verify zero hardcoded golden strings in extractor and normalizer."""

    def test_zero_hardcoded_golden_strings(self):
        banned = [
            "longitudinal compressional",
            "lowest mean density",
            "very big and hot",
            "comprises immense reserves",
            "yellow dwarf",
            "satellite container port",
            "nearly all planets in",
            "denudational process in which",
            "tectonic process of",
            "plunges beneath",
            "transported and deposited by",
        ]
        for filename in ["semantic_extractor.py", "normalizer.py"]:
            path = os.path.join(REPO_ROOT, "v13_discovery", filename)
            with open(path, "r", encoding="utf-8") as f:
                code = f.read().lower()
            found = [b for b in banned if b.lower() in code]
            self.assertEqual(found, [], f"Banned golden strings found in {filename}: {found}")


if __name__ == "__main__":
    unittest.main()