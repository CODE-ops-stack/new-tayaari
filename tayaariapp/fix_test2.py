file = 'app/src/test/java/com/example/viewmodel/MistakeReplayTest.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('            confusionEventDao = db.confusionEventDao(),\n            revisionDao = db.revisionDao()\n        )', '            confusionEventDao = db.confusionEventDao()\n        )')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
