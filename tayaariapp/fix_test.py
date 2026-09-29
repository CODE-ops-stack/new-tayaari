file = 'app/src/test/java/com/example/viewmodel/MistakeReplayTest.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('            confusionEventDao = db.confusionEventDao()\n        )', '            confusionEventDao = db.confusionEventDao(),\n            revisionDao = db.revisionDao()\n        )')
text = text.replace('db.appDao()\n        )', 'db.appDao(),\n            db.revisionDao()\n        )')
text = text.replace('viewModel = MistakeReplayViewModel(repo, selectionEngine, replayEngine)', 'viewModel = MistakeReplayViewModel(repo)')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
