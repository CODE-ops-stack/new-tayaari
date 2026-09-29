"""
Comprehensive Adversarial Stress Suite for Milestone 2 Iteration 3
Evaluates:
1. Long sentences (>150 words) and ReDoS/backtracking boundaries.
2. Formatting noise (ligatures, smart quotes, em-dashes, non-breaking spaces, zero-width spaces, markdown escapes, HTML entities, accented characters).
3. Tables and multi-column blocks (merged cells, multiline headers, irregular columns, interleaving).
4. Plural vs singular coreference chains across sentences in NormalizedBlock.
5. Rejection of false positives (headings, questions, bibliographic entries, incomplete fragments).
"""

import sys
import os
import time

# Ensure UTF-8 output encoding on Windows console
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Ensure project root is in sys.path
sys.path.insert(0, r"c:\Users\harsh\Downloads\tayaari\tayaariapp")

from v13_discovery.normalizer import DocumentNormalizer, LayoutDesegmenter, TableParser, WatermarkOcrCleaner, NormalizedBlock
from v13_discovery.semantic_extractor import (
    SemanticExtractor,
    DiscourseContext,
    NoiseFilterGate,
    LinguisticSemanticExtractor,
    KnowledgeNode
)


def run_all_challenges():
    print("======================================================================")
    print("STARTING ADVERSARIAL CHALLENGE SUITE (M2 ITERATION 3)")
    print("======================================================================\n")

    se = SemanticExtractor()
    norm = DocumentNormalizer()

    # ------------------------------------------------------------------
    # 1. BOUNDARY: LONG SENTENCES (>150 WORDS)
    # ------------------------------------------------------------------
    print("--- 1. Testing Long Sentences (>150 words) ---")
    
    # Truly >150 words:
    filler = "and continuously interacting with various geological structures across diverse geochemical conditions "
    long_s1 = "The rock cycle is a continuous geological process " + (filler * 12) + "whereby igneous rocks transform into metamorphic rocks."
    long_s2 = "The equatorial radius of the Earth measures approximately 6378 kilometres " + (filler * 12) + "resulting in an oblate spheroidal geometric shape."
    long_s3 = "Igneous rocks can be classified into two fundamental petrological categories: intrusive igneous rocks and extrusive igneous rocks " + (filler * 12) + "depending on the cooling rate of magma."

    long_sentences = [
        ("Process >150 words", long_s1),
        ("Quantity >150 words", long_s2),
        ("Classification >150 words", long_s3)
    ]

    for label, s in long_sentences:
        word_count = len(s.split())
        t0 = time.time()
        blocks = norm.normalize(s)
        norm_time = time.time() - t0
        
        t0 = time.time()
        nodes = []
        for b in blocks:
            nodes.extend(se.extract(b))
        ext_time = time.time() - t0
        
        print(f"[{label}] Words: {word_count} | Norm: {norm_time:.4f}s | Ext: {ext_time:.4f}s | Nodes: {len(nodes)}")
        for n in nodes:
            print(f"   -> Intent: {n.intent_type} | Entity: '{n.primary_entity}' | Pred: '{n.predicate[:60]}...'")

    # ------------------------------------------------------------------
    # 2. FORMATTING NOISE & UNICODE ANOMALIES
    # ------------------------------------------------------------------
    print("\n--- 2. Testing Formatting Noise & Unicode Anomalies ---")
    noise_cases = [
        ("Ligatures (fi, fl)", "The first layer of the atmosphere is the troposphere, which exhibits significant moisture fluxes."),
        ("Unicode Ligature chars", "The \ufb01rst layer of the atmosphere is the troposphere, which exhibits signi\ufb01cant moisture \ufb02uxes."),
        ("Smart Quotes", "\u201cThe lithosphere\u201d is defined as the rigid outer crust and upper mantle of the Earth."),
        ("Em-Dashes without space", "Igneous rocks\u2014formed through cooling of magma\u2014are classified into intrusive and extrusive types."),
        ("En-Dashes in ranges", "The mesosphere extends from 50\u201380 kilometres above the Earth surface."),
        ("Non-breaking spaces", "The\u00a0troposphere\u00a0is\u00a0the\u00a0lowest\u00a0layer\u00a0of the atmosphere."),
        ("Zero-width spaces", "The\u200btroposphere\u200bis\u200bthe\u200blowest\u200blayer\u200bof the atmosphere."),
        ("Markdown bold/italics in sentence", "The **lithosphere** is defined as the rigid outer shell of the Earth."),
        ("Markdown escape backslashes", "The \\*lithosphere\\* is defined as the rigid outer shell of the Earth."),
        ("HTML entity &amp;", "The crust &amp; upper mantle constitute the lithosphere."),
        ("Accented proper nouns", "The K\u00f6ppen climate classification system divides climates into five main vegetation groups.")
    ]

    for label, raw in noise_cases:
        blocks = norm.normalize(raw)
        nodes = []
        for b in blocks:
            nodes.extend(se.extract(b))
        clean_s = [s for b in blocks for s in b.clean_sentences]
        print(f"[{label}] -> Clean sentences count: {len(clean_s)}")
        print(f"   -> Extracted nodes: {len(nodes)}")
        for n in nodes:
            print(f"      Intent: {n.intent_type} | Entity: '{n.primary_entity}' | Pred: '{n.predicate[:50]}'")

    # ------------------------------------------------------------------
    # 3. TABLES & MULTI-COLUMN BLOCKS
    # ------------------------------------------------------------------
    print("\n--- 3. Testing Tables & Multi-Column Layouts ---")
    
    # 3a. Table with empty/merged cells
    table_merged = """
| Planet | Diameter (km) | Moons | Atmosphere |
|---|---|---|---|
| Mercury | 4879 | 0 | - |
| Venus | 12104 | 0 | Carbon dioxide |
| Earth | 12756 | 1 | Nitrogen and oxygen |
| Mars | 6792 | 2 | |
"""
    t_blocks = norm.normalize(table_merged, "table_doc")
    print(f"[Table with empty/dash cells] Blocks: {len(t_blocks)}")
    for b in t_blocks:
        print(f"   Type: {b.type} | Sentences: {b.clean_sentences}")
        nodes = se.extract(b)
        print(f"   Extracted {len(nodes)} nodes:")
        for n in nodes:
            print(f"      Entity: '{n.primary_entity}' | Pred: '{n.predicate}'")

    # 3b. Table with multi-word headers and units
    table_complex = """
| Rock Type | Primary Mineral Constituent | Formation Mechanism | Average Density (g/cm^3) |
|---|---|---|---|
| Basalt | Plagioclase and pyroxene | Rapid cooling of lava | 3.0 |
| Granite | Quartz and feldspar | Slow cooling of magma | 2.7 |
"""
    t_blocks2 = norm.normalize(table_complex, "table_complex")
    print(f"\n[Table with complex headers] Blocks: {len(t_blocks2)}")
    for b in t_blocks2:
        nodes = se.extract(b)
        print(f"   Extracted {len(nodes)} nodes:")
        for n in nodes:
            print(f"      Entity: '{n.primary_entity}' | Pred: '{n.predicate}'")

    # 3c. Multi-column wrap with hyphenated split
    multi_col_raw = """
The tropo-
sphere is the low-
est layer of the
atmosphere. It ex-
tends up to an aver-
age height of 13
kilometres.
"""
    mc_blocks = norm.normalize(multi_col_raw, "multicolumn_doc")
    print(f"\n[Narrow column wrapping with hyphens] Blocks: {len(mc_blocks)}")
    for b in mc_blocks:
        print(f"   Sentences: {b.clean_sentences}")
        nodes = se.extract(b)
        print(f"   Nodes: {len(nodes)}")
        for n in nodes:
            print(f"      Entity: '{n.primary_entity}' | Intent: {n.intent_type} | Pred: '{n.predicate}'")

    # ------------------------------------------------------------------
    # 4. PLURAL VS SINGULAR COREFERENCE PROPAGATION
    # ------------------------------------------------------------------
    print("\n--- 4. Testing Plural vs Singular Coreference Propagation ---")

    coref_tests = [
        ("Singular then Plural (Earth & Asteroids)", [
            "The Earth is the third planet from the Sun.",
            "It has one natural satellite known as the Moon.",
            "Asteroids are rocky bodies orbiting between Mars and Jupiter.",
            "They revolve around the Sun in elliptical paths."
        ]),
        ("Singular ending in 's' (Mars & Earth)", [
            "The Earth is the third planet from the Sun.",
            "Mars is the fourth planet from the Sun.",
            "It has two small moons named Phobos and Deimos."
        ]),
        ("Singular ending in 's' (Ganges & Indus)", [
            "The Indus is a trans-Himalayan river.",
            "The Ganges is a major river in northern India.",
            "It has a total length of 2525 kilometres."
        ]),
        ("Plural ending in 'as' (Alps & Himalayas)", [
            "The Alps are fold mountains in Europe.",
            "The Himalayas are young fold mountains in Asia.",
            "They have the highest peaks in the world."
        ]),
        ("Irregular plural (Tectonic Plates)", [
            "The continental crust is composed of granitic rock.",
            "Tectonic plates are massive slabs of solid rock.",
            "They move slowly across the underlying asthenosphere."
        ]),
        ("Isolated pronoun in prose block (Should NOT leak)", [
            "It is characterized by high atmospheric pressure and low precipitation."
        ])
    ]

    for label, sents in coref_tests:
        block = NormalizedBlock(
            id=f"coref_{label[:10]}",
            text=" ".join(sents),
            type="PROSE",
            clean_sentences=sents
        )
        nodes = se.extract(block)
        print(f"\n[{label}]")
        for idx, s in enumerate(sents):
            matching_nodes = [n for n in nodes if n.raw_evidence == s]
            if matching_nodes:
                for mn in matching_nodes:
                    print(f"   S{idx+1}: '{s}'\n      -> Extracted Entity: '{mn.primary_entity}' | Intent: {mn.intent_type}")
            else:
                print(f"   S{idx+1}: '{s}'\n      -> (Dropped / No node emitted)")

    # ------------------------------------------------------------------
    # 5. FALSE POSITIVE REJECTION (NOISE, HEADINGS, QUESTIONS)
    # ------------------------------------------------------------------
    print("\n--- 5. Testing False Positive Rejection ---")
    fp_candidates = [
        # Questions
        ("Question (What is)", "What is an earthquake?"),
        ("Question (Why does)", "Why does the wind blow from high to low pressure?"),
        ("Question (How are)", "How are metamorphic rocks formed in nature?"),
        ("Question (Which layer)", "Which atmospheric layer contains the ozone layer?"),
        ("Question (Can rocks)", "Can sedimentary rocks transform into igneous rocks?"),
        
        # Headings without punctuation
        ("Heading uppercase", "ORIGIN AND EVOLUTION OF THE EARTH"),
        ("Heading title case", "Major Landforms of the Earth"),
        ("Heading with numbers", "Section 4.2 Atmospheric Circulation"),
        ("Heading noun phrase (5 words)", "Types of Seismic Waves in Earth"),
        ("Heading topic", "Classification of Clouds"),
        
        # Bibliographic / Citation noise
        ("Citation author year", "Wegener, A. (1912). Die Entstehung der Kontinente. Petermanns Geographische Mitteilungen."),
        ("Citation in text", "According to Holmes (1944), convection currents operate in the mantle."),
        ("Reference entry", "Source: Ministry of Mines, Government of India, Annual Report 2021-22."),
        
        # Incomplete fragments
        ("Fragment dangling prep", "The continental shelf extends to a depth of"),
        ("Fragment conjunction", "Because the Earth rotates from west to east and"),
        ("Fragment verb missing", "The vast interior regions of the Asiatic continent"),
        ("Fragment isolated noun phrase", "High temperature and high humidity in equatorial regions"),
        ("Fragment trailing adverb", "The seismic waves propagate rapidly through the crust whereas")
    ]

    for cat, text in fp_candidates:
        # Test directly via SemanticExtractor
        nodes = se.extract(text)
        rejection_reason = NoiseFilterGate.audit(text, is_block_context=False)
        accepted = len(nodes) > 0
        status = "LEAKED (FALSE POSITIVE)" if accepted else "REJECTED (CORRECT)"
        print(f"[{status}] {cat}: '{text}'")
        if accepted:
            for n in nodes:
                print(f"   -> False Node: Entity='{n.primary_entity}', Intent={n.intent_type}, Pred='{n.predicate}'")
        else:
            print(f"   -> Noise Gate Verdict: {rejection_reason}")


if __name__ == "__main__":
    run_all_challenges()
