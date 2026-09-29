import sys
import os
import trace
import unittest

cwd = os.getcwd()
if cwd not in sys.path:
    sys.path.insert(0, cwd)

# Trace execution of tests

tracer = trace.Trace(count=1, trace=0)
tracer.runctx("unittest.main(module='tests.test_v13_semantic_extractor', argv=[''], exit=False)", globals(), locals())
results = tracer.results()

v13_lines = {k: v for k, v in results.counts.items() if 'v13_discovery' in k[0]}
files = set(k[0] for k in v13_lines)

print("=" * 60)
print("DYNAMIC TRACE EXECUTION AUDIT")
print("=" * 60)
for f in files:
    file_lines = [k[1] for k in v13_lines if k[0] == f]
    print(f"File: {os.path.basename(f)} -> {len(file_lines)} lines actively executed during unit tests.")
print(f"Total unique line executions in v13_discovery: {len(v13_lines)}")
print("=" * 60)
