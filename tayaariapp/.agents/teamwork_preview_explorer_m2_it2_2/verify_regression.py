"""
Regression test script:
Verifies that all 25 unit tests in tests/test_v13_semantic_extractor.py
pass 100% when using the proposed extractor and noise gate classes.
"""

import os
import sys
import unittest

REPO_ROOT = r"c:\Users\harsh\Downloads\tayaari\tayaariapp"
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

AGENTS_DIR = os.path.dirname(os.path.abspath(__file__))
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

import v13_discovery.semantic_extractor as orig_mod
from prototype_extractor import (
    ProposedNoiseFilterGate,
    ProposedLinguisticSemanticExtractor,
    ProposedSemanticExtractor,
)

# Apply monkey patch for regression testing in-memory
orig_mod.NoiseFilterGate = ProposedNoiseFilterGate
orig_mod.LinguisticSemanticExtractor = ProposedLinguisticSemanticExtractor
orig_mod.SemanticExtractor = ProposedSemanticExtractor

# Now import test suite and run
from tests.test_v13_semantic_extractor import (
    TestV13SemanticExtractorIntents,
    TestV13NoiseRejection,
    TestV13Normalizer,
)

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestV13SemanticExtractorIntents))
    suite.addTests(loader.loadTestsFromTestCase(TestV13NoiseRejection))
    suite.addTests(loader.loadTestsFromTestCase(TestV13Normalizer))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
