import sys
sys.path.insert(0, r"c:\Users\harsh\Downloads\tayaari\tayaariapp")

import pytest
import test_complete_challenger2_remediation

ret = pytest.main(['tests/'])
sys.exit(ret)
