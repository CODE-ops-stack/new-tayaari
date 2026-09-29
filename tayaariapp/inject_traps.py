import codecs
import re
import random

with codecs.open('app/src/main/assets/consolidated_grounding.md', 'r', 'utf-8') as f:
    content = f.read()

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

def inject_trap(match):
    fmt = match.group(1)
    # Inject trap only for complex questions occasionally, or some direct facts
    if fmt in ["Statement-based", "Assertion-Reason"]:
        trap = random.choice(trap_types)
        return f"- **Format**: {fmt}\n- **Trap-Type**: {trap}"
    # Maybe add trap for some Direct Facts too
    if random.random() < 0.1:
        trap = random.choice(["FACT_DISTORTION", "FAMILIARITY_TRAP", "PARTIAL_TRUTH"])
        return f"- **Format**: {fmt}\n- **Trap-Type**: {trap}"
    return match.group(0)

content = re.sub(r"- \*\*Format\*\*: (.*?)(?=\r?\n)", inject_trap, content)

with codecs.open('app/src/main/assets/consolidated_grounding.md', 'w', 'utf-8') as f:
    f.write(content)
