import re
from collections import defaultdict

with open('app/src/main/assets/consolidated_grounding.md', 'r', encoding='utf-8') as f:
    content = f.read()

qPattern = re.compile(
    r'- \*\*Topic\*\*: ([^\r\n]*?)\s*\n'
    r'- \*\*Tier\*\*: ([^\r\n]*?)\s*\n'
    r'- \*\*Format\*\*: ([^\r\n]*?)\s*\n'
    r'- \*\*Exam-Relevance\*\*: ([^\r\n]*?)\s*\n'
    r'- \*\*Source\*\*: ([^\r\n]*?)\s*\n'
    r'- \*\*Specific-Exam\*\*: ([^\r\n]*?)\s*\n'
    r'(?:- \*\*Trap-Type\*\*: ([^\r\n]*?)\s*\n)?'
    r'- \*\*PDF-Sequence-Number\*\*: ([^\r\n]*?)\s*\n'
    r'- \*\*Question\*\*:\s*```\s*(.*?)\s*```',
    re.DOTALL
)

topic_stats = defaultdict(lambda: {'A': 0, 'B': 0, 'C': 0})

for m in qPattern.finditer(content):
    topic = m.group(1).strip()
    tier = m.group(2).strip()
    relevance = m.group(4).strip()
    is_elite = relevance == 'Elite'
    
    topic_stats[topic]['A'] += 1
    if tier in ['Basic', 'Medium'] and not is_elite:
        topic_stats[topic]['B'] += 1
    if tier == 'Basic' and not is_elite:
        topic_stats[topic]['C'] += 1

zero_c = [(t, s) for t, s in topic_stats.items() if s['C'] == 0]
zero_b = [(t, s) for t, s in topic_stats.items() if s['B'] == 0]
zero_a = [(t, s) for t, s in topic_stats.items() if s['A'] == 0]

print('Topics with 0 questions for GROUP_C (Basic, non-Elite): ' + str(len(zero_c)))
for t, s in zero_c[:15]:
    print('  ' + t + ': A=' + str(s['A']) + ', B=' + str(s['B']) + ', C=' + str(s['C']))

print('Topics with 0 questions for GROUP_B (Basic+Medium, non-Elite): ' + str(len(zero_b)))
for t, s in zero_b[:10]:
    print('  ' + t + ': A=' + str(s['A']) + ', B=' + str(s['B']) + ', C=' + str(s['C']))

print('Topics with 0 questions for GROUP_A (All): ' + str(len(zero_a)))
