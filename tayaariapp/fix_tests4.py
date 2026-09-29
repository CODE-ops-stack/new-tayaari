import re

files = [
    'app/src/test/java/com/example/repository/QuestionSelectionEngineTest.kt',
    'app/src/test/java/com/example/repository/QuestionSelectionScoringTest.kt'
]

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    text = re.sub(
        r'repo = LocalRepository\([\s\S]*?engine = QuestionSelectionEngine\(repo\)',
        r'repo = LocalRepository(\n            bookmarkDao = db.bookmarkDao(),\n            trapAnalyticsDao = db.trapAnalyticsDao(),\n            mistakeReplayDao = db.mistakeReplayDao(),\n            appDao = db.appDao(),\n            revisionDao = db.revisionDao(),\n            questionAttemptDao = db.questionAttemptDao(),\n            analyticsDao = db.analyticsDao(),\n            confusionEventDao = db.confusionEventDao()\n        )\n        engine = QuestionSelectionEngine(repo)',
        text
    )
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(text)
