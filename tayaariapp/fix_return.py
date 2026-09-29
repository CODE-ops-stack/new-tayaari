file = 'app/src/main/java/com/example/viewmodel/MistakeReplayViewModel.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('return@launch', 'return')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
