import codecs
import re

with codecs.open('app/src/main/assets/consolidated_grounding.md', 'r', 'utf-8') as f:
    content = f.read()

# Remove all injected trap lines
content = re.sub(r"- \*\*Trap-Type\*\*: [^\r\n]*\r?\n", "", content)

with codecs.open('app/src/main/assets/consolidated_grounding.md', 'w', 'utf-8') as f:
    f.write(content)
