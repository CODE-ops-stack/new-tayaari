import os
import sys
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, REPO_ROOT)

# Load existing files
with open(os.path.join(REPO_ROOT, "v13_discovery", "semantic_extractor.py"), encoding="utf-8") as f:
    se_code = f.read()

with open(os.path.join(REPO_ROOT, "v13_discovery", "normalizer.py"), encoding="utf-8") as f:
    norm_code = f.read()

# Apply full remediations
se_mod = se_code.replace(
    'maintains a constant tilt of|measures approximately|originated approximately',
    r'(?:has|have|had|maintains?|maintained|exhibits?|possesses?)\s+(?:an?|a\s+constant)?\s*(?:[a-z\-]+\s+)?(?:radius|diameter|circumference|elevation|altitude|depth|density|mass|volume|area|tilt|inclination|angle)\s+of|measures approximately|originated approximately'
)
se_mod = se_mod.replace(
    'commenced approximately.*followed by|arrive(?:s)? first.*followed sequentially by',
    r'(?:arrive(?:s|d)?|form(?:s|ed)?|condense(?:s|d)?|begin(?:s)?|began|commence(?:s|d)?)\b.*?\bfollowed\s+(?:by|sequentially\s+by|in\s+turn\s+by)'
)
se_mod = se_mod.replace(
    r'(?:highest|lowest|greatest|smallest|largest|thickest|thinnest|deepest|shallowest|fastest|slowest|densest|hottest|coldest|longest|shortest|oldest|youngest|heaviest|lightest|strongest|weakest|maximum|minimum)',
    r'(?:[a-z\-]+est|highest|lowest|greatest|smallest|largest|thickest|thinnest|deepest|shallowest|fastest|slowest|densest|hottest|coldest|longest|shortest|oldest|youngest|heaviest|lightest|strongest|weakest|maximum|minimum)'
)
se_mod = se_mod.replace(
    '(?:has|have|had|exhibits?|exhibited|possesses?|possessed|displays?|displayed)',
    '(?:has|have|had|exhibits?|exhibited|possesses?|possessed|displays?|displayed|produced|generated|emitted|yielded)'
)
se_mod = se_mod.replace(
    'orbits?|rotates?|flows?)',
    'orbits?|rotates?|flows?|produced?|generated?|emitted?|yielded?)'
)
se_mod = se_mod.replace(
    r'(?:are|is)\s+(?:very|extremely|highly|mostly)?\s*[a-z\-]+\s+and\s+[a-z\-]+',
    r'(?:are|is)\s+(?:[a-z\-]+ly\s+|very\s+|mostly\s+)?\s*[a-z\-]+\s+and\s+[a-z\-]+'
)
se_mod = se_mod.replace(
    'attr_verbs = {"exhibits", "possesses", "displays", "maintains", "features", "contains", "demonstrates", "reveals"}',
    'attr_verbs = {"exhibits", "possesses", "displays", "maintains", "features", "contains", "demonstrates", "reveals", "produced", "produce", "generated", "generate", "emitted", "emit", "yielded", "yield"}'
)
se_mod = se_mod.replace(
    r"r'^\s*(?:In addition to|As well as|Out of total water resources|Due to which)\s*[\.\,]?\s*$',",
    r"r'^\s*(?:In addition to|As well as|Due to which|Out of\s+(?:the\s+|total\s+)?[a-z\s]+)\s*[\.\,]?\s*$',"
)
se_mod = se_mod.replace(
    r"r'\b(?:[A-Z][a-z]+\s+){5,}',",
    r"r'^(?![^.\n]*\b(?:is|are|was|were|has|have|orbits?|contains?|features?)\b)(?:[A-Z][a-z]+\s+){4,}[A-Z][a-z]+[\.\s]*$',"
)
old_norm_block = """        s = re.sub(r'UniverseGalaxySolar System', 'Universe. Galaxy. Solar System.', s)
        s = re.sub(r'Planetesimal TheoryNebular HypothesisCopernicus Theory', 'Planetesimal Theory. Nebular Hypothesis. Copernicus Theory.', s)
        s = re.sub(r'MeteoroidMeteorMeteorite', 'Meteoroid. Meteor. Meteorite.', s)
        s = re.sub(r'PhotosphereChromosphereCorona', 'Photosphere. Chromosphere. Corona.', s)
        s = re.sub(r'Terrestrial PlanetsJovian Planets', 'Terrestrial Planets vs Jovian Planets.', s)
        s = re.sub(r'Three Types of Plate BoundariesThree Types of Plate Boundaries', 'Three Types of Plate Boundaries:', s)"""
new_norm_block = """        s = re.sub(r'\\b(.{10,200}?)\\s*\\1\\b', r'\\1', s)
        s = re.sub(r'([a-z])([A-Z])', r'\\1 \\2', s)
        s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\\1 \\2', s)"""
norm_mod = norm_code.replace(old_norm_block, new_norm_block)
se_mod = se_mod.replace(
    r'(?:part|component|constituent|element|fraction|segment|envelope|layer|zone|shell|core|sphere|portion)',
    r'(?:part|component|constituent|element|fraction|segment|envelope|layer|zone|shell|core|sphere|portion|shield|barrier|reservoir|body|mass)'
)

# Patch sys.modules dynamically
import types
norm_mod_obj = types.ModuleType("v13_discovery.normalizer")
exec(norm_mod, norm_mod_obj.__dict__)
sys.modules["v13_discovery.normalizer"] = norm_mod_obj

se_mod_obj = types.ModuleType("v13_discovery.semantic_extractor")
se_mod_obj.__dict__["DocumentNormalizer"] = norm_mod_obj.DocumentNormalizer
se_mod_obj.__dict__["NormalizedBlock"] = norm_mod_obj.NormalizedBlock
exec(se_mod, se_mod_obj.__dict__)
sys.modules["v13_discovery.semantic_extractor"] = se_mod_obj

# Now import tests
import tests.test_v13_challenger_it4_stress as t

# Verify Part 1 & Part 2
suite = unittest.TestSuite()
suite.addTest(unittest.makeSuite(t.TestPastTenseSuperlatives))
suite.addTest(unittest.makeSuite(t.TestOpenTaxonomicMemberOf))
suite.addTest(unittest.makeSuite(t.TestComparisonWithTrailingClauses))
suite.addTest(unittest.makeSuite(t.TestCompoundAttributeParticiples))
suite.addTest(unittest.makeSuite(t.TestThousandsCommaNumbersInQuantity))
suite.addTest(unittest.makeSuite(t.TestSequenceColonItems))
suite.addTest(unittest.makeSuite(t.TestGeneralizedPassiveVoiceInversion))
suite.addTest(unittest.makeSuite(t.TestSpatialPrepositionsInPartOf))
suite.addTest(unittest.makeSuite(t.TestDiscourseAgreementAndPronounShield))
suite.addTest(unittest.makeSuite(t.TestAntiOverfittingAudit))

runner = unittest.TextTestRunner(verbosity=2)
result = runner.run(suite)
print(f"\nRan {result.testsRun} tests. Errors: {len(result.errors)}, Failures: {len(result.failures)}")
assert len(result.errors) == 0 and len(result.failures) == 0, "Challenger test suite failed!"
print("\n>>> ALL TEST_V13_CHALLENGER_IT4_STRESS CORE TESTS PASSED 100%! <<<")
