import re

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "r", encoding="utf-8") as f:
    text = f.read()

pattern = r'(    // CONFIDENCE CALIBRATION UI\s+AnimatedVisibility\(visible = pendingOptionId != null && selectedOptionId == null\) \{\s+Column\([\s\S]*?\}\s+\}\s+\}\s+\})'

# Replace multiple occurrences with just one
# Split the text
parts = re.split(pattern, text)
print(f"Parts length: {len(parts)}")

# The first part is text before the match.
# The second part is the match.
# The third part is text after the match (which might just be whitespace).
# ...

# We can just use re.sub but only replace from the second occurrence onward.
def replacer(match, state={"count": 0}):
    state["count"] += 1
    if state["count"] == 1:
        return match.group(0) # Keep first
    return "" # Delete the rest

new_text = re.sub(pattern, replacer, text)

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "w", encoding="utf-8") as f:
    f.write(new_text)

print("Done")
