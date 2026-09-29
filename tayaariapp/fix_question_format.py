import re

with open('app/src/main/assets/consolidated_grounding.md', 'r', encoding='utf-8') as f:
    content = f.read()

# The GEN questions currently look like:
# - **Question**:
# Q301. The movement...
# (a)...
# Correct Answer: Option b
# \- **Topic**: ...  (or just - **Topic**)
#
# They need to look like:
# - **Question**:
# ```
# Q301. The movement...
# Correct Answer: Option b
# ```

# Pattern: find - **Question**:\n followed by Q\d+ (not wrapped in backticks)
# and wrap it properly

def fix_unwrapped_question(m):
    question_body = m.group(1)
    # Remove any trailing backslash from the end
    question_body = question_body.rstrip('\\ \n')
    return '- **Question**:\n```\n' + question_body + '\n```\n'

# Match - **Question**:\n (not followed by ```) and capture until next - **Topic** or ---
pattern = re.compile(
    r'- \*\*Question\*\*:\n(?!```)' +  # Question header NOT followed by ```
    r'((?:(?!- \*\*Topic\*\*|---|```).)+)',  # capture everything until next marker
    re.DOTALL
)

count = 0
new_content = pattern.sub(lambda m: fix_unwrapped_question(m), content)
count = len(pattern.findall(content))
print('Fixed', count, 'unwrapped questions')

# Verify GEN-301 now
idx = new_content.find('GEN-301')
if idx > 0:
    print('\nGEN-301 context after fix:')
    print(repr(new_content[max(0,idx-50):idx+300]))

with open('app/src/main/assets/consolidated_grounding.md', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Saved.')
