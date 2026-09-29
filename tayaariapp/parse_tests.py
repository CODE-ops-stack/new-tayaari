import os
import xml.etree.ElementTree as ET

test_dir = "app/build/test-results/testDebugUnitTest"
if not os.path.exists(test_dir):
    print("Test directory not found")
    exit(1)

for root_dir, dirs, files in os.walk(test_dir):
    for file in files:
        if file.endswith(".xml"):
            path = os.path.join(root_dir, file)
            tree = ET.parse(path)
            root = tree.getroot()
            for testcase in root.findall('.//testcase'):
                class_name = testcase.get('classname')
                name = testcase.get('name')
                
                # Check for failure/error
                failure = testcase.find('failure')
                error = testcase.find('error')
                
                status = "PASS"
                if failure is not None or error is not None:
                    status = "FAIL"
                
                print(f"{class_name} > {name} : {status}")
