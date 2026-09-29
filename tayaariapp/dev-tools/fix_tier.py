import re

with open("/app/applet/source-material/consolidated_grounding.md", "r") as f:
    content = f.read()

# We need to replace Tier based on Format
# Format Type: Direct Fact | Tier: Advanced -> Tier: Basic
# Format Type: Statement-based | Tier: Advanced -> Tier: Medium
# Format Type: Matching Pairs | Tier: Advanced -> Tier: Medium
# Format Type: Assertion-Reason | Tier: Advanced -> Tier: Advanced

def replacer(match):
    fmt = match.group(1)
    tier = "Advanced"
    if fmt == "Direct Fact":
        tier = "Basic"
    elif fmt == "Statement-based":
        tier = "Medium"
    elif fmt == "Matching Pairs":
        tier = "Medium"
    elif fmt == "Assertion-Reason":
        tier = "Advanced"
    
    return f"**Format Type**: {fmt} | **Tier**: {tier} | **Exam-Relevance**: Elite | **Source**: Real-PYQ | **Specific-Exam**: UPSC-Prelims"

new_content = re.sub(
    r"\*\*Format Type\*\*: (.*?) \| \*\*Tier\*\*: Advanced \| \*\*Exam-Relevance\*\*: Elite \| \*\*Source\*\*: Real-PYQ \| \*\*Specific-Exam\*\*: UPSC-Prelims",
    replacer,
    content
)

with open("/app/applet/source-material/consolidated_grounding.md", "w") as f:
    f.write(new_content)

print("Tiers updated.")
