import re

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "r", encoding="utf-8") as f:
    lines = f.readlines()

# find the CONFIDENCE block start
conf_idx = -1
for i, line in enumerate(lines):
    if "// CONFIDENCE CALIBRATION UI" in line:
        conf_idx = i
        break

print(f"Conf block starts at {conf_idx}")

# find the end of AnimatedVisibility
# The AnimatedVisibility starts at conf_idx + 1
# Let's just truncate the file at conf_idx + 1 and manually append the correct code.
