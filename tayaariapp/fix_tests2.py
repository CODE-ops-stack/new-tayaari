import re
import glob

files = [
    'app/src/test/java/com/example/repository/ConfusionEvidenceTest.kt',
    'app/src/test/java/com/example/repository/QuestionSelectionEngineTest.kt',
    'app/src/test/java/com/example/repository/QuestionSelectionScoringTest.kt'
]

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    text = re.sub(
        r'repo = LocalRepository\([^)]+\)',
        r'repo = LocalRepository(\n            bookmarkDao = db.bookmarkDao(),\n            mistakeReplayDao = db.mistakeReplayDao(),\n            appDao = db.appDao(),\n            revisionDao = db.revisionDao(),\n            questionAttemptDao = db.questionAttemptDao(),\n            trapAnalyticsDao = db.trapAnalyticsDao(),\n            confusionEventDao = db.confusionEventDao()\n        )',
        text
    )
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(text)
