import os
import glob

test_dir = "app/src/test/java/com/example"

# We want to keep PracticeScoringRegressionTest.kt
keep = ["PracticeScoringRegressionTest.kt"]

for root, _, files in os.walk(test_dir):
    for f in files:
        if f.endswith(".kt") and f not in keep:
            path = os.path.join(root, f)
            os.remove(path)
            print(f"Removed {f}")
