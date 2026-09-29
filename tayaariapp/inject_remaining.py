import re

with open('app/src/main/assets/consolidated_grounding.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Inject into remaining empty topics: 4, 30, 44
# Also need to check 8, 18 which were in our original list
REMAINING = {
    4: """- **Topic**: 4. Maps
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-401
- **Question**:
```
Q401. Maps showing natural features such as mountains and plains are called:
(a) Political maps
(b) Thematic maps
(c) Physical maps
(d) Topographic maps
Correct Answer: Option c
```
- **Topic**: 4. Maps
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-402
- **Question**:
```
Q402. The three main components of a map are:
(a) Distance, Direction and Symbol
(b) Distance, Direction and Scale
(c) Scale, Symbol and Location
(d) Direction, Distance and Relief
Correct Answer: Option a
```
""",
    30: """- **Topic**: 30. The World Population Distribution, Density and Growth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3001
- **Question**:
```
Q3001. Which continent has the highest population density?
(a) Europe
(b) Asia
(c) Africa
(d) North America
Correct Answer: Option b
```
- **Topic**: 30. The World Population Distribution, Density and Growth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3002
- **Question**:
```
Q3002. Population density is calculated as:
(a) Total area divided by total population
(b) Total population divided by total area
(c) Birth rate minus death rate
(d) Total population multiplied by total area
Correct Answer: Option b
```
""",
    44: """- **Topic**: 44. International Trade (India)
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-4401
- **Question**:
```
Q4401. Which is the largest port on the west coast of India?
(a) Kandla
(b) Marmagao
(c) Mumbai
(d) New Mangalore
Correct Answer: Option c
```
- **Topic**: 44. International Trade (India)
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-4402
- **Question**:
```
Q4402. Which sea port is on the East Coast of India?
(a) Kandla
(b) Marmagao
(c) New Mangalore
(d) Visakhapatnam
Correct Answer: Option d
```
"""
}

injected = 0
for topic_num, questions in REMAINING.items():
    # Find the SSC empty divider for this specific topic
    pattern = r'(## ' + str(topic_num) + r'\. [^\n]+\n[\s\S]*?### SSC Stenographer Data \(925-Question Set\)\n)(---)'
    m = re.search(pattern, content)
    if not m:
        print('NOT FOUND: topic', topic_num)
        continue
    
    # Check it's actually empty
    between = content[m.start(1)+len(m.group(1)):m.start(2)]
    if between.strip() != '':
        print('ALREADY HAS CONTENT: topic', topic_num)
        continue
    
    # Insert questions before the ---
    insert_pos = m.start(2)
    content = content[:insert_pos] + questions + content[insert_pos:]
    injected += 1
    print('INJECTED: topic', topic_num)

print('Total injected:', injected)
print('GEN- count:', content.count('GEN-'))

with open('app/src/main/assets/consolidated_grounding.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('Saved. Size:', len(content))
