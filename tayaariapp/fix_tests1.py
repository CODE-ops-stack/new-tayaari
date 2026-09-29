import os
import glob
import re

test_dir = "app/src/test/java/com/example"

for root, _, files in os.walk(test_dir):
    for f in files:
        if not f.endswith(".kt"): continue
        path = os.path.join(root, f)
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
        
        orig_content = content
        
        # 1. Fix LocalRepository instantiation
        content = re.sub(
            r'LocalRepository\(\s*database\.bookmarkDao\(\),\s*database\.trapAnalyticsDao\(\),\s*dao\s*\)',
            r'LocalRepository(database.bookmarkDao(), database.trapAnalyticsDao(), dao, database.revisionDao(), database.questionAttemptDao(), database.analyticsDao())',
            content
        )
        # some tests might use database.appDao() directly
        content = re.sub(
            r'LocalRepository\(\s*database\.bookmarkDao\(\),\s*database\.trapAnalyticsDao\(\),\s*database\.appDao\(\)\s*\)',
            r'LocalRepository(database.bookmarkDao(), database.trapAnalyticsDao(), database.appDao(), database.revisionDao(), database.questionAttemptDao(), database.analyticsDao())',
            content
        )
        
        # 2. Add ExamBlueprintRegistry import if needed
        if "ExamBlueprintRegistry" in content and "import com.example.model.ExamBlueprintRegistry" not in content:
            content = content.replace("package com.example.repository\n", "package com.example.repository\n\nimport com.example.model.ExamBlueprintRegistry\n")
            content = content.replace("package com.example.ui\n", "package com.example.ui\n\nimport com.example.model.ExamBlueprintRegistry\n")
            content = content.replace("package com.example.viewmodel\n", "package com.example.viewmodel\n\nimport com.example.model.ExamBlueprintRegistry\n")

        # 3. Add GeminiRepository import if needed
        if "GeminiRepository" in content and "import com.example.repository.GeminiRepository" not in content:
            content = content.replace("package com.example.repository\n", "package com.example.repository\n\nimport com.example.repository.GeminiRepository\n")

        # 4. Fix ExamBlueprintRegistry map lookups
        # ExamBlueprintRegistry.blueprints.find { it.examId == "..." } ?: ExamBlueprintRegistry.blueprints[0]
        # if they were using map get like `ExamBlueprintRegistry.blueprints["UPSC_CSE_2026"]` which expects V?
        content = re.sub(
            r'ExamBlueprintRegistry\.blueprints\["([^"]+)"\]',
            r'(ExamBlueprintRegistry.blueprints.find { it.examId == "\1" }!!)',
            content
        )
        content = re.sub(
            r'ExamBlueprintRegistry\.blueprints\[ExamBlueprintRegistry\.blueprints\.keys\.first\(\)\]',
            r'(ExamBlueprintRegistry.blueprints.first())',
            content
        )
        # Any .get() calls
        content = re.sub(
            r'ExamBlueprintRegistry\.getBlueprint\(([^)]+)\)',
            r'(ExamBlueprintRegistry.getBlueprint(\1)!!)',
            content
        )

        if content != orig_content:
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
            print(f"Fixed {f}")
