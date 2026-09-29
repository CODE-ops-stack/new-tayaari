import os
import re

matches = []
for root, dirs, files in os.walk("."):
    if ".git" in root or ".gradle" in root:
        continue
    for f in files:
        if f.endswith(".py") or f.endswith(".js"):
            path = os.path.join(root, f)
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as fl:
                    content = fl.read()
                    if "gemini" in content.lower() or "generativelanguage" in content.lower():
                        matches.append(path)
            except Exception:
                pass

print("Files referencing gemini / generativelanguage:")
for m in matches[:20]:
    print(" ", m)
