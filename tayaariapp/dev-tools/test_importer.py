import re

with open('source-material/consolidated_grounding.md', 'r') as f:
    content = f.read()

blocks = re.split(r'\n## (?=\d+\. )', content)
count = 0

qPattern = re.compile(
    r'- \*\*Topic\*\*: (.*?)\n' +
    r'- \*\*Tier\*\*: (.*?)\n' +
    r'- \*\*Format\*\*: (.*?)\n' +
    r'- \*\*Exam-Relevance\*\*: (.*?)\n' +
    r'- \*\*Source\*\*: (.*?)\n' +
    r'- \*\*Specific-Exam\*\*: (.*?)\n' +
    r'(?:- \*\*Trap-Type\*\*: (.*?)\n)?' +
    r'- \*\*PDF-Sequence-Number\*\*: (.*?)\n' +
    r'- \*\*Question\*\*:\n```\n(.*?)\n```', re.DOTALL
)

for i in range(1, len(blocks)):
    block = blocks[i]
    for match in qPattern.finditer(block):
        rawQText = match.group(9).strip()
        qText = rawQText
        optionsStr = "[]"
        correctAnswerStr = "opt_a"
        
        ansMatcher = re.search(r'(?i)Correct [Aa]nswer:\s*(?:Option\s*)?([a-d])', rawQText)
        if ansMatcher:
            correctAnswerStr = "opt_" + ansMatcher.group(1).lower().strip()
            
        optMatcher = re.search(r'(?s)(.*?)\s*\(?[aA]\)[ \.](.*?)\s*\(?[bB]\)[ \.](.*?)\s*\(?[cC]\)[ \.](.*?)\s*\(?[dD]\)[ \.](.*)', rawQText)
        if optMatcher:
            qText = optMatcher.group(1).strip()
            optA = optMatcher.group(2).strip().replace('\n', ' ')
            optB = optMatcher.group(3).strip().replace('\n', ' ')
            optC = optMatcher.group(4).strip().replace('\n', ' ')
            optD = optMatcher.group(5).strip().replace('\n', ' ')
            
            optD = re.sub(r'(?i)\s*Correct [Aa]nswer:.*', '', optD).strip()
            
            optionsStr = f'[{{"id":"opt_a","text":"{optA}"}}, {{"id":"opt_b","text":"{optB}"}}, {{"id":"opt_c","text":"{optC}"}}, {{"id":"opt_d","text":"{optD}"}}]'
            
        print("Question:")
        print(f"  Text: {qText}")
        print(f"  Options: {optionsStr}")
        print(f"  Correct: {correctAnswerStr}")
        print("--------------------------")
        count += 1
        if count >= 3:
            exit(0)
