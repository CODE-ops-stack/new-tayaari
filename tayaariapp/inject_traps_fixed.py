import codecs
import re

with codecs.open('app/src/main/assets/consolidated_grounding.md', 'r', 'utf-8') as f:
    content = f.read()

# I messed up by inserting Trap-Type right after Format.
# Let's fix this by finding Trap-Type, removing it, and then inserting it at the correct place.

# Find all blocks of Trap-Type and remove them, while remembering what they were? No, I'll just remove all of them.
content = re.sub(r"- \*\*Trap-Type\*\*: [^\r\n]*\r?\n", "", content)

# Now inject correctly after Specific-Exam
import random
trap_types = [
    "ABSOLUTE_WORDING",
    "FACT_DISTORTION",
    "FAMILIARITY_TRAP",
    "CONCEPT_MIX",
    "FALSE_CORRELATION",
    "PARTIAL_TRUTH",
    "TIMELINE_MISMATCH"
]
random.seed(42)

def inject_trap_after_exam(match):
    # match is the entire Specific-Exam line
    # but I also need to know the Format.
    # actually, I can just use a larger regex that captures Format, Exam-Relevance, Source, Specific-Exam
    pass

# We will match from Format to Specific-Exam
def inject_trap(match):
    fmt = match.group(1)
    relevance = match.group(2)
    source = match.group(3)
    exam = match.group(4)
    
    trap_line = ""
    if fmt in ["Statement-based", "Assertion-Reason"]:
        trap = random.choice(trap_types)
        trap_line = f"- **Trap-Type**: {trap}\n"
    elif random.random() < 0.1:
        trap = random.choice(["FACT_DISTORTION", "FAMILIARITY_TRAP", "PARTIAL_TRUTH"])
        trap_line = f"- **Trap-Type**: {trap}\n"
        
    return f"- **Format**: {fmt}\n- **Exam-Relevance**: {relevance}\n- **Source**: {source}\n- **Specific-Exam**: {exam}\n{trap_line}"

pattern = r"- \*\*Format\*\*: (.*?)\r?\n- \*\*Exam-Relevance\*\*: (.*?)\r?\n- \*\*Source\*\*: (.*?)\r?\n- \*\*Specific-Exam\*\*: (.*?)\r?\n"

content = re.sub(pattern, inject_trap, content)

with codecs.open('app/src/main/assets/consolidated_grounding.md', 'w', 'utf-8') as f:
    f.write(content)
