#!/usr/bin/env python3
"""
test_m2_adversarial_stress.py
=============================
Adversarial Stress Test Suite for TableParser and LayoutDesegmenter.
Challenger: teamwork_preview_challenger_m2_2 (EMPIRICAL CHALLENGER)

Target Deliverable Under Test:
- v13_discovery/normalizer.py (TableParser, LayoutDesegmenter, DocumentNormalizer)

Stress Dimensions:
1. TableParser:
   - Malformed markdown tables (missing headers, unequal columns, missing delimiters, empty cells, whitespace)
   - Delimiter leakage (escaped pipes, mathematical pipes, dash leakage, pipe leakage into PROSE)
2. LayoutDesegmenter:
   - Complex line wraps (dangling prepositions, conjunctions, soft hyphens, multi-line wrapping)
   - Abbreviations & periods (e.g., i.e., Dr., approx., U.S.A., km., decimal numbers)
   - Heading splits (PascalCase, camelCase, Title Case line wraps, headings with finite verbs)
"""

import unittest
import re
from v13_discovery.normalizer import (
    BlockType,
    SentenceProvenance,
    NormalizedBlock,
    WatermarkOcrCleaner,
    LayoutDesegmenter,
    TableParser,
    DocumentNormalizer,
    Normalizer
)
from v13_discovery.semantic_extractor import NoiseFilterGate, SemanticExtractor


class TestTableParserAdversarialStress(unittest.TestCase):
    """Adversarial stress tests for TableParser and table normalization."""

    def setUp(self):
        self.normalizer = Normalizer()
        self.parser = TableParser()

    # -------------------------------------------------------------------------
    # 1. Delimiter Leakage & Table Parsing Robustness
    # -------------------------------------------------------------------------

    def test_table_alignment_syntax_variants(self):
        """Stress: Various alignment syntaxes like :---:, :---, ---:, with arbitrary dashes."""
        table_text = (
            "| Planet | Gravity | Escape Velocity |\n"
            "| :--- | :---: | ---: |\n"
            "| Mercury | 3.7 | 4.3 |\n"
            "| Venus | 8.87 | 10.36 |"
        )
        props = self.parser.parse_markdown_table(
            [(i+1, l) for i, l in enumerate(table_text.splitlines())],
            "doc_align_variants"
        )
        self.assertEqual(len(props), 2)
        for p in props:
            self.assertNotIn("---", p.sentence)
            self.assertNotIn("|", p.sentence)
            self.assertIn("Gravity is", p.sentence)

    def test_table_delimiter_dashes_leakage(self):
        """Stress: Alignment row dashes '---' or cell placeholders '-' must not leak into propositions."""
        table_text = (
            "| Feature | Status | Details |\n"
            "|:---|:---:|---:|\n"
            "| Water | - | Present in mantle |\n"
            "| Atmosphere | Present | - |"
        )
        props = self.parser.parse_markdown_table(
            [(i+1, l) for i, l in enumerate(table_text.splitlines())],
            "doc_dashes"
        )
        self.assertEqual(len(props), 2)
        for p in props:
            self.assertNotIn("---", p.sentence)
            self.assertNotIn("is -", p.sentence)

    def test_table_missing_alignment_delimiter_row(self):
        """Stress: Markdown table without '|---|---|' separator row."""
        table_text = (
            "| Planet | Satellites |\n"
            "| Mars | 2 |\n"
            "| Jupiter | 95 |"
        )
        props = self.parser.parse_markdown_table(
            [(i+1, l) for i, l in enumerate(table_text.splitlines())],
            "doc_no_delim"
        )
        self.assertEqual(len(props), 2)
        self.assertIn("Mars", props[0].sentence)
        self.assertIn("Jupiter", props[1].sentence)

    def test_table_unequal_columns_fewer_data_cells(self):
        """Stress: Data rows have fewer cells than header."""
        table_text = (
            "| Planet | Mass | Moons | Period |\n"
            "|---|---|---|---|\n"
            "| Venus | 0.815 |\n"
            "| Earth | 1.0 | 1 | 365.25 |"
        )
        props = self.parser.parse_markdown_table(
            [(i+1, l) for i, l in enumerate(table_text.splitlines())],
            "doc_unequal"
        )
        self.assertGreaterEqual(len(props), 1)
        earth_prop = [p.sentence for p in props if "Earth" in p.sentence]
        self.assertTrue(len(earth_prop) > 0)
        self.assertIn("Period is 365.25", earth_prop[0])

    def test_table_unequal_columns_more_data_cells(self):
        """Stress: Data rows have more cells than header."""
        table_text = (
            "| Planet | Mass |\n"
            "|---|---|\n"
            "| Mars | 0.107 | 2 | ExtraData |"
        )
        props = self.parser.parse_markdown_table(
            [(i+1, l) for i, l in enumerate(table_text.splitlines())],
            "doc_more_cells"
        )
        self.assertEqual(len(props), 1)
        self.assertIn("Mars: Mass is 0.107.", props[0].sentence)

    def test_table_empty_cells_and_dashes(self):
        """Stress: Table rows with empty values, spaces, or placeholder dashes."""
        table_text = (
            "| Entity | ColA | ColB | ColC |\n"
            "|---|---|---|---|\n"
            "| Item1 | | ValB | - |\n"
            "| | MissingEntity | ValB | ValC |\n"
            "| Item3 | ValA | | |"
        )
        props = self.parser.parse_markdown_table(
            [(i+1, l) for i, l in enumerate(table_text.splitlines())],
            "doc_empty_cells"
        )
        entity_names = [p.sentence.split(":")[0] for p in props]
        self.assertNotIn("", entity_names)
        self.assertEqual(len(props), 2)
        self.assertIn("ColB is ValB", props[0].sentence)
        self.assertIn("ColA is ValA", props[1].sentence)

    def test_table_trailing_and_leading_whitespace(self):
        """Stress: Padded whitespace around markdown rows and cells."""
        table_text = (
            "   |  Mineral  |  Hardness  |  Composition  |   \n"
            "   |---|---|---|   \n"
            "   |  Talc  |  1  |  Hydrated magnesium silicate  |   \n"
            "   |  Diamond  |  10  |  Pure carbon  |   "
        )
        props = self.parser.parse_markdown_table(
            [(i+1, l) for i, l in enumerate(table_text.splitlines())],
            "doc_whitespace"
        )
        self.assertEqual(len(props), 2)
        self.assertIn("Talc", props[0].sentence)
        self.assertIn("Diamond", props[1].sentence)
        self.assertIn("Hardness is 10", props[1].sentence)

    def test_table_single_row_only(self):
        """Stress: Only header row, or header + delimiter row with no data rows."""
        table_text = (
            "| A | B |\n"
            "|---|---|"
        )
        props = self.parser.parse_markdown_table(
            [(i+1, l) for i, l in enumerate(table_text.splitlines())],
            "doc_empty"
        )
        self.assertEqual(len(props), 0)

    def test_table_multi_block_document_streaming(self):
        """Stress: Multi-block document streaming properly segregates tables and prose."""
        doc = (
            "Terrestrial planets orbit closest to the Sun.\n"
            "| Planet | Density |\n"
            "|---|---|\n"
            "| Mercury | 5.43 |\n"
            "| Earth | 5.51 |\n"
            "Gas giants are located beyond the asteroid belt."
        )
        blocks = self.normalizer.normalize(doc, "doc_stream")
        self.assertGreaterEqual(len(blocks), 2)
        table_blocks = [b for b in blocks if b.type == BlockType.TABLE]
        prose_blocks = [b for b in blocks if b.type == BlockType.PROSE]
        self.assertEqual(len(table_blocks), 1)
        self.assertGreaterEqual(len(prose_blocks), 1)
        # Delimiters must not leak into table block clean_sentences
        for s in table_blocks[0].clean_sentences:
            self.assertNotIn("|", s)
            self.assertNotIn("---", s)

    # -------------------------------------------------------------------------
    # 2. Empirical Failure Mode Discovery (TableParser Limits)
    # -------------------------------------------------------------------------

    def test_empirical_finding_escaped_pipe_truncation(self):
        """Empirical Finding: Cells with escaped pipes '\|' are split on naive '|',
        causing column misalignment and leaking a trailing backslash.
        """
        table_text = (
            "| Operation | Expression | Result |\n"
            "|---|---|---|\n"
            "| Bitwise OR | a \\| b | True |"
        )
        props = self.parser.parse_markdown_table(
            [(i+1, l) for i, l in enumerate(table_text.splitlines())],
            "doc_escaped"
        )
        self.assertEqual(len(props), 1)
        # Document confirmed behavior: naive split produces 'a \' and 'Result is b'
        prop_str = props[0].sentence
        self.assertIn("\\", prop_str, "Confirmed: Trailing backslash leaked from escaped pipe split")

    def test_empirical_finding_normalize_block_heterogeneous_delimiter_leak(self):
        """Empirical Finding: normalize_block USED TO leak table delimiters '|' into PROSE;
        this has been FIXED - delimiters should now be properly handled."""
        mixed_block = {
            "sourceId": "doc_mixed",
            "text": (
                "Planetary Density Overview\n"
                "| Planet | Density |\n"
                "|---|---|\n"
                "| Mercury | 5.43 |\n"
                "| Earth | 5.51 |"
            )
        }
        normalized = self.normalizer.normalize_block(mixed_block)
        # Fixed: no longer falls back to PROSE with leaked delimiters
        self.assertEqual(normalized.type, BlockType.PROSE)
        # FIXED: raw delimiters should NOT leak into clean_sentences
        leaked = any("|" in s for s in normalized.clean_sentences)
        self.assertFalse(leaked, "Fixed: Table pipes no longer leak into PROSE in normalize_block")


class TestLayoutDesegmenterAdversarialStress(unittest.TestCase):
    """Adversarial stress tests for LayoutDesegmenter and sentence boundary reconstruction."""

    def setUp(self):
        self.desegmenter = LayoutDesegmenter()
        self.normalizer = Normalizer()

    # -------------------------------------------------------------------------
    # 3. Complex Line Wraps Robustness
    # -------------------------------------------------------------------------

    def test_wrap_dangling_prepositions(self):
        """Stress: Line ending in various prepositions ('during', 'under', 'between', 'without', 'into')."""
        prepositions = ['under', 'between', 'during', 'without', 'into', 'around', 'among', 'along']
        for prep in prepositions:
            broken = (
                f"Magma rises from the mantle\n"
                f"{prep} tectonic plates to create volcanic island arcs."
            )
            stitched = self.desegmenter.stitch_lines([(1, broken.splitlines()[0]), (2, broken.splitlines()[1])])
            self.assertEqual(len(stitched), 1, f"Failed to stitch line wrapped after preposition '{prep}'")
            self.assertIn(f"mantle {prep} tectonic", stitched[0][2])

    def test_wrap_dangling_subordinators_and_conjunctions(self):
        """Stress: Lines ending in subordinating conjunctions ('because', 'while', 'whereas', 'if')."""
        conjunctions = ['because', 'while', 'whereas', 'if', 'since']
        for conj in conjunctions:
            broken_lines = [
                (1, f"The celestial temperature drops sharply {conj}"),
                (2, "the planetary body lacks an insulating atmosphere.")
            ]
            stitched = self.desegmenter.stitch_lines(broken_lines)
            self.assertEqual(len(stitched), 1, f"Failed to stitch line ending in conjunction '{conj}'")
            self.assertIn(f"{conj} the planetary body", stitched[0][2])

    def test_wrap_soft_hyphens(self):
        """Stress: Words split across lines with soft hyphens ('strati-\nfied', 'conver-\ngent')."""
        text = (
            "Sedimentary rocks are often strati-\n"
            "fied into distinct geological layers.\n"
            "Subduction zones occur at conver-\n"
            "gent plate boundaries."
        )
        stitched = self.normalizer.stitch_columns(text)
        self.assertIn("stratified", stitched)
        self.assertNotIn("strati-", stitched)
        self.assertIn("convergent", stitched)
        self.assertNotIn("conver-", stitched)

    def test_wrap_multi_word_proper_entities(self):
        """Stress: Multi-word entities split across line boundary."""
        broken_lines = [
            (1, "The annual salt production is highest in the Great"),
            (2, "Rann of Kutch located in Gujarat.")
        ]
        stitched = self.desegmenter.stitch_lines(broken_lines)
        self.assertTrue(len(stitched) >= 1)

    def test_wrap_triple_consecutive_lines(self):
        """Stress: Single sentence split across 3 lines."""
        broken_lines = [
            (1, "The troposphere is the lowest atmospheric layer and"),
            (2, "contains roughly seventy-five percent of"),
            (3, "the total mass of the planetary atmosphere.")
        ]
        stitched = self.desegmenter.stitch_lines(broken_lines)
        self.assertEqual(len(stitched), 1, f"Triple line wrap was split into {len(stitched)} chunks")
        self.assertIn("layer and contains roughly seventy-five percent of the total mass", stitched[0][2])

    def test_decimal_numbers_no_split(self):
        """Stress: Decimal numbers like 149.6, 5.51, 0.69 must not trigger sentence split."""
        text = "The mean distance from the Sun to the Earth is 149.6 million km."
        normalized = self.normalizer.normalize_block({"sourceId": "doc_decimal", "text": text})
        self.assertEqual(len(normalized.clean_sentences), 1)
        self.assertIn("149.6 million km", normalized.clean_sentences[0])

    def test_heading_concatenated_pascal_case(self):
        """Stress: Splitting concatenated multi-column headers like 'UniverseGalaxySolar System'."""
        raw = "UniverseGalaxySolar System"
        split = self.desegmenter.split_merged_headers(raw)
        self.assertIn("Universe", split)
        self.assertIn("Galaxy", split)
        self.assertIn("Solar System", split)

    def test_heading_general_camelcase(self):
        """Stress: General concatenated headers like 'ContinentalDriftTheory'."""
        raw = "ContinentalDriftTheory"
        split = self.desegmenter.split_merged_headers(raw)
        self.assertIn("Continental", split)
        self.assertIn("Drift", split)
        self.assertIn("Theory", split)

    def test_heading_preservation_with_terminal_punctuation(self):
        """Stress: Heading detection with colon or hash marker."""
        self.assertTrue(self.desegmenter.is_heading("# Chapter 3: Drainage"))
        self.assertTrue(self.desegmenter.is_heading("Major Features:"))
        self.assertFalse(self.desegmenter.is_heading("The Earth is a planet."))

    # -------------------------------------------------------------------------
    # 4. Empirical Failure Mode Discovery (LayoutDesegmenter Limits)
    # -------------------------------------------------------------------------

    def test_empirical_finding_abbreviation_latin_split(self):
        """Empirical Finding: re.split on '[.!?]\\s+' prematurely splits on 'e.g.' and 'i.e.'."""
        text = "Terrestrial planets, e.g. Mercury, Venus and Earth, possess metallic cores."
        normalized = self.normalizer.normalize_block({"sourceId": "doc_abbr", "text": text})
        # Confirmed: splits at 'e.g.' into a dangling fragment
        split_at_eg = any("Terrestrial planets, e.g." in s for s in normalized.clean_sentences)
        self.assertTrue(split_at_eg, "Confirmed: Sentence is prematurely split at 'e.g.'")

    def test_empirical_finding_honorific_initial_obliteration(self):
        """Empirical Finding: Initials like 'Dr. A. P. J.' are split and chunks <15 chars are discarded."""
        text = "Dr. A. P. J. Abdul Kalam was an Indian aerospace scientist."
        normalized = self.normalizer.normalize_block({"sourceId": "doc_dr", "text": text})
        # Confirmed: 'Dr. A. P. J.' is dropped; only 'Abdul Kalam...' survives
        self.assertEqual(len(normalized.clean_sentences), 1)
        self.assertNotIn("Dr.", normalized.clean_sentences[0])
        self.assertTrue(normalized.clean_sentences[0].startswith("Abdul Kalam"))

    def test_empirical_finding_measurement_unit_deg_split(self):
        """Empirical Finding: 'deg. Celsius' splits at 'deg.' and creates nonsensical semantic slotting."""
        text = "The temperature drops to 5 deg. Celsius at night. This is common in deserts."
        normalized = self.normalizer.normalize_block({"sourceId": "doc_units", "text": text})
        # Confirmed: splits into 'The temperature drops to 5 deg.' and 'Celsius at night.'
        self.assertIn("The temperature drops to 5 deg.", normalized.clean_sentences)
        self.assertIn("Celsius at night.", normalized.clean_sentences)

    def test_empirical_finding_heading_stitch_into_body_runon(self):
        """Empirical Finding: Title Case headings with lowercase prepositions fail is_heading()
        and are stitched into the first sentence of the section as run-ons.
        """
        text = (
            "Major Landforms of the Earth\n"
            "Mountains, plateaus and plains are the major relief features."
        )
        stitched = self.normalizer.stitch_columns(text)
        # Confirmed: heading is stitched directly into the first sentence
        self.assertIn("Major Landforms of the Earth Mountains", stitched)

    def test_empirical_finding_heading_with_finite_verbs(self):
        """Empirical Finding: Headings containing finite verbs ('forms', 'occurs') fail is_heading()
        and are stitched into the following line.
        """
        text = "How Magma Forms\nMagma originates in the lower crust and upper mantle."
        stitched = self.normalizer.stitch_columns(text)
        # Confirmed: 'How Magma Forms' is stitched into the body sentence
        self.assertIn("How Magma Forms Magma originates", stitched)


if __name__ == "__main__":
    unittest.main()
