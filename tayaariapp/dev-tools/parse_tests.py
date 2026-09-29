import os
import re

report_dir = 'app/build/reports/tests/testDebugUnitTest'
print("Test Results:")
print("-------------")

for root, dirs, files in os.walk(report_dir):
    for file in files:
        if file.endswith('.html') and file != 'index.html':
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if "<title>Test results" in content:
                    parts = filepath.split('/')
                    class_name = parts[-2]
                    method_name = file.replace('.html', '')
                    
                    if re.search(r'<div class="counter">\s*0\s*</div>\s*<p>failures</p>', content):
                        status = "PASSED"
                    else:
                        status = "FAILED"
                        
                    print(f"{class_name} > {method_name} {status}")
