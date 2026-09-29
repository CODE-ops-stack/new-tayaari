import os
import xml.etree.ElementTree as ET
import glob

test_dir = "app/build/test-results/testDebugUnitTest"
xml_files = glob.glob(os.path.join(test_dir, "**/*.xml"), recursive=True)

tests = 0
failures = 0
skipped = 0

for file in xml_files:
    tree = ET.parse(file)
    root = tree.getroot()
    tests += int(root.attrib.get('tests', 0))
    failures += int(root.attrib.get('failures', 0))
    skipped += int(root.attrib.get('skipped', 0))

print(f"Tests discovered: {tests}")
print(f"Tests executed: {tests - skipped}")
print(f"Tests passed: {tests - failures - skipped}")
print(f"Tests failed: {failures}")
print(f"Tests skipped: {skipped}")
