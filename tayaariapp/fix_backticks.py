import re

with open('app/src/main/assets/consolidated_grounding.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the malformed GEN questions that have \` instead of `
# The broken pattern looks like: \`\`\`\nQ301. ...\n\`\`\`
# We need to replace those with ```\nQ301. ...\n```

# Fix escaped backticks
content = content.replace('\\`\\`\\`', '```')
# Also fix \Qxxx -> Qxxx (the line starting with backslash)
content = re.sub(r'\\(Q\d+\.)', r'\1', content)

print('GEN- count:', content.count('GEN-'))

# Now verify GEN-301 looks right
idx = content.find('GEN-301')
if idx > 0:
    print('GEN-301 context:')
    print(repr(content[max(0,idx-300):idx+200]))

with open('app/src/main/assets/consolidated_grounding.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed and saved.')
