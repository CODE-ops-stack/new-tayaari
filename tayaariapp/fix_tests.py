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
    
    # In these tests, LocalRepository is usually instantiated like:
    # repository = LocalRepository(
    #     bookmarkDao = ...,
    #     appDao = ...,
    #     revisionDao = ...,
    #     ...
    # )
    # But since it's missing mistakeReplayDao, let's inject it.
    
    text = re.sub(
        r'repository = LocalRepository\(\s*bookmarkDao = db\.bookmarkDao\(\),\s*appDao = db\.appDao\(\),\s*revisionDao = db\.revisionDao\(\),\s*questionAttemptDao = db\.questionAttemptDao\(\),\s*trapAnalyticsDao = db\.trapAnalyticsDao\(\),\s*confusionEventDao = db\.confusionEventDao\(\)\s*\)',
        r'repository = LocalRepository(\n            bookmarkDao = db.bookmarkDao(),\n            mistakeReplayDao = db.mistakeReplayDao(),\n            appDao = db.appDao(),\n            revisionDao = db.revisionDao(),\n            questionAttemptDao = db.questionAttemptDao(),\n            trapAnalyticsDao = db.trapAnalyticsDao(),\n            confusionEventDao = db.confusionEventDao()\n        )',
        text
    )
    
    # Just in case it's instantiated without named parameters:
    # LocalRepository(db.bookmarkDao(), db.appDao(), ...)
    text = re.sub(
        r'LocalRepository\(\s*db\.bookmarkDao\(\),\s*db\.appDao\(\),\s*db\.revisionDao\(\),\s*db\.questionAttemptDao\(\),\s*db\.trapAnalyticsDao\(\),\s*db\.confusionEventDao\(\)\s*\)',
        r'LocalRepository(db.bookmarkDao(), db.mistakeReplayDao(), db.appDao(), db.revisionDao(), db.questionAttemptDao(), db.trapAnalyticsDao(), db.confusionEventDao())',
        text
    )
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(text)
