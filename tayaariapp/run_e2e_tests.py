"""
Convenience entry point for running the E2E Test Suite from project root.
Usage: python run_e2e_tests.py
"""

import sys
from tests.e2e.runner import run_e2e_suite

if __name__ == "__main__":
    sys.exit(run_e2e_suite())
