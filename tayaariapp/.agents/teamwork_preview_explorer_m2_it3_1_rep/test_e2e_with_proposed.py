import sys, os
sys.path.insert(0, os.path.abspath("."))
import unittest
import re

from v13_discovery import semantic_extractor
from test_full_suite_with_proposed import PROPOSED_PATTERNS, patched_extract

semantic_extractor.LinguisticSemanticExtractor.PATTERNS = PROPOSED_PATTERNS
semantic_extractor.LinguisticSemanticExtractor.extract = patched_extract

from tests.e2e.runner import run_e2e_suite
exit_code = run_e2e_suite()
print("E2E EXIT CODE:", exit_code)
sys.exit(exit_code)
