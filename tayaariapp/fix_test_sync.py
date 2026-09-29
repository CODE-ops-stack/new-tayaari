file = 'app/src/test/java/com/example/viewmodel/MistakeReplayTest.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('viewModel.loadCandidate()\n        kotlinx.coroutines.delay(100)', 'viewModel.loadCandidateSync()')
text = text.replace('viewModel.proceedToAlternate()\n        kotlinx.coroutines.delay(100)', 'viewModel.proceedToAlternateSync()')
text = text.replace('viewModel.commitToRepair()\n        kotlinx.coroutines.delay(100)', 'viewModel.commitToRepairSync()')
text = text.replace('viewModel.submitAlternateAnswer(isCorrect = true)', 'viewModel.submitAlternateAnswerSync(isCorrect = true)')

# Also replace the ones without delay if they exist
text = text.replace('viewModel.loadCandidate()', 'viewModel.loadCandidateSync()')
text = text.replace('viewModel.proceedToAlternate()', 'viewModel.proceedToAlternateSync()')
text = text.replace('viewModel.commitToRepair()', 'viewModel.commitToRepairSync()')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
