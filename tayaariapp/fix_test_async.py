import re

file = 'app/src/test/java/com/example/viewmodel/MistakeReplayTest.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('viewModel.loadCandidate()', 'viewModel.loadCandidate()\n        kotlinx.coroutines.delay(100)')
text = text.replace('viewModel.proceedToAlternate()', 'viewModel.proceedToAlternate()\n        kotlinx.coroutines.delay(100)')
text = text.replace('viewModel.commitToRepair()', 'viewModel.commitToRepair()\n        kotlinx.coroutines.delay(100)')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
