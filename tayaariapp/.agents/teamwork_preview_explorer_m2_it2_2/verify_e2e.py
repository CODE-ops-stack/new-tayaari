"""
E2E verification script:
Verifies that run_e2e_tests.py passes 202/202 tests with the proposed extractor.
"""

import os
import sys

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

# Apply proposed implementation
orig_mod.NoiseFilterGate = ProposedNoiseFilterGate
orig_mod.LinguisticSemanticExtractor = ProposedLinguisticSemanticExtractor
orig_mod.SemanticExtractor = ProposedSemanticExtractor

from tests.e2e.runner import run_e2e_suite
sys.exit(run_e2e_suite())
