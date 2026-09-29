import re

with open("source-material/consolidated_grounding.md", "r") as f:
    text = f.read()

pattern = r"(?s)(.*?)\s*\(?[aA]\)[ )\.](.*?)\s*\(?[bB]\)[ )\.](.*?)\s*\(?[cC]\)[ )\.](.*?)\s*\(?[dD]\)[ )\.](.*?)\s*Correct [Aa]nswer:\s*(?:[Oo]ption\s*)?([a-dA-D])"

ssc_qs = 0
ssc_extracted = 0

for block in re.split(r"\n## (?=\d+\. )", text):
    idx = block.find("### SSC Stenographer Data")
    if idx != -1:
        ssc_part = block[idx:]
        
        # count total sequence numbers
        ssc_qs += len(re.findall(r"- \*\*PDF-Sequence-Number\*\*: (\d+)", ssc_part))
        
        # find extracted blocks
        for match in re.finditer(r"- \*\*Question\*\*:\s*```(.*?)```", ssc_part, re.DOTALL):
            q_text = match.group(1).strip()
            if re.search(pattern, q_text):
                ssc_extracted += 1

print(f"Total SSC Sequence Numbers: {ssc_qs}")
print(f"Extracted & Parsed SSC Qs: {ssc_extracted}")
