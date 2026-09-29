file = 'app/src/test/java/com/example/viewmodel/MistakeReplayTest.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('viewModel.commitToRepairSync()', 'viewModel.commitToRepair()')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
