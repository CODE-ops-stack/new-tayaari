import re
with open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', encoding='utf-8') as f:
    text = f.read()

match = re.search(r'private fun computeScore.*?return score\s*\}', text, re.DOTALL)
if match:
    print("Found computeScore!")
    old = match.group(0)
    new = "companion object {\n    " + old.replace("private fun computeScore", "fun computeScore").replace("\n", "\n    ") + "\n}"
    with open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', encoding='utf-8') as f:
        f.write(text.replace(old, new))
    print("Successfully replaced.")
else:
    print("Not found.")
