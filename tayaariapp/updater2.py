import re

updates = {
    9: '''- **Topic**: 9. Geography as a Discipline
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-901
- **Question**:
```
Q901. Who among the following scholars coined the term 'Geography'?
(a) Herodotus
(b) Galileo
(c) Eratosthenes
(d) Aristotle
Correct Answer: Option c
```
- **Topic**: 9. Geography as a Discipline
- **Tier**: Medium
- **Format**: Statement-based
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-902
- **Question**:
```
Q902. Consider the following statements regarding the approaches to geography:
1. Systematic geography approach was introduced by Alexander Von Humboldt.
2. Regional geography approach was developed by Carl Ritter.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option c
```''',

    10: '''- **Topic**: 10. The Origin and Evolution of the Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-1001
- **Question**:
```
Q1001. The Big Bang Theory, which explains the origin of the universe, is also called:
(a) Nebular Hypothesis
(b) Steady State Theory
(c) Expanding Universe Hypothesis
(d) Binary Theory
Correct Answer: Option c
```
- **Topic**: 10. The Origin and Evolution of the Earth
- **Tier**: Medium
- **Format**: Statement-based
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-1002
- **Question**:
```
Q1002. Consider the following statements about the evolution of the Earth's atmosphere:
1. The first stage was marked by the loss of the primordial atmosphere.
2. The early atmosphere largely contained water vapour, nitrogen, carbon dioxide, methane, ammonia, and very little of free oxygen.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option c
```''',

    12: '''- **Topic**: 12. Distribution of Oceans and Continents
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-1201
- **Question**:
```
Q1201. Who proposed the Continental Drift Theory?
(a) Alfred Wegener
(b) Abraham Ortelius
(c) Arthur Holmes
(d) Harry Hess
Correct Answer: Option a
```
- **Topic**: 12. Distribution of Oceans and Continents
- **Tier**: Advanced
- **Format**: Assertion-Reason
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-1202
- **Question**:
```
Q1202. Assertion (A): The age of the rocks increases as one moves away from the crest of the mid-oceanic ridge.
Reason (R): Seafloor spreading constantly erupts new basaltic crust at the mid-oceanic ridge crests, pushing older crust outwards.
Select the correct answer using the codes given below:
(a) Both A and R are true and R is the correct explanation of A
(b) Both A and R are true but R is not the correct explanation of A
(c) A is true but R is false
(d) A is false but R is true
Correct Answer: Option a
```''',

    30: '''- **Topic**: 30. The World Population Distribution, Density and Growth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3001
- **Question**:
```
Q3001. Which one of the following continents has the highest population density?
(a) Europe
(b) Asia
(c) Africa
(d) North America
Correct Answer: Option b
```
- **Topic**: 30. The World Population Distribution, Density and Growth
- **Tier**: Medium
- **Format**: Statement-based
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-3002
- **Question**:
```
Q3002. Consider the following statements regarding population growth:
1. The difference between births and deaths in a particular region is called natural growth of population.
2. When the population decreases between two points of time, it is known as negative growth of population.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option c
```''',

    31: '''- **Topic**: 31. Human Development
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3101
- **Question**:
```
Q3101. The concept of Human Development was introduced by:
(a) Amartya Sen
(b) Ellen C. Semple
(c) Dr Mahbub-ul-Haq
(d) Ratzel
Correct Answer: Option c
```
- **Topic**: 31. Human Development
- **Tier**: Medium
- **Format**: Matching Pairs
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-3102
- **Question**:
```
Q3102. Consider the following pairs regarding the pillars of human development:
1. Equity : Making equal access to opportunities available to everybody.
2. Sustainability : Continuity in the availability of opportunities.
3. Productivity : Human labour productivity or productivity in terms of human work.
How many of the above pairs are correctly matched?
(a) Only one pair
(b) Only two pairs
(c) All three pairs
(d) None of the pairs
Correct Answer: Option c
```''',

    32: '''- **Topic**: 32. Primary Activities
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3201
- **Question**:
```
Q3201. People engaged in primary activities are often referred to as:
(a) Blue-collar workers
(b) White-collar workers
(c) Red-collar workers
(d) Gold-collar workers
Correct Answer: Option c
```
- **Topic**: 32. Primary Activities
- **Tier**: Medium
- **Format**: Statement-based
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-3202
- **Question**:
```
Q3202. Consider the following statements about nomadic herding:
1. It is a primitive subsistence activity.
2. The herders rely on animals for food, clothing, shelter, tools, and transport.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option c
```''',

    33: '''- **Topic**: 33. Secondary Activities
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3301
- **Question**:
```
Q3301. Secondary activities refer to:
(a) Extraction of raw materials from the earth
(b) Adding value to natural resources by transforming raw materials into valuable products
(c) Providing services like transport and communication
(d) High-level decision making and research
Correct Answer: Option b
```
- **Topic**: 33. Secondary Activities
- **Tier**: Advanced
- **Format**: Assertion-Reason
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-3302
- **Question**:
```
Q3302. Assertion (A): Footloose industries can be located in a wide variety of places.
Reason (R): They are not dependent on any specific raw material, weight losing or otherwise.
Select the correct answer using the codes given below:
(a) Both A and R are true and R is the correct explanation of A
(b) Both A and R are true but R is not the correct explanation of A
(c) A is true but R is false
(d) A is false but R is true
Correct Answer: Option a
```''',

    34: '''- **Topic**: 34. Tertiary and Quaternary Activities
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3401
- **Question**:
```
Q3401. Which of the following is considered a tertiary activity?
(a) Agriculture
(b) Manufacturing
(c) Trading
(d) Hunting and gathering
Correct Answer: Option c
```
- **Topic**: 34. Tertiary and Quaternary Activities
- **Tier**: Medium
- **Format**: Statement-based
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-3402
- **Question**:
```
Q3402. Consider the following statements:
1. Quaternary activities involve the collection, production and dissemination of information.
2. Quinary activities are services that focus on the creation, re-arrangement and interpretation of new and existing ideas.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option c
```''',

    36: '''- **Topic**: 36. International Trade
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3601
- **Question**:
```
Q3601. The direct exchange of goods without the use of money is known as:
(a) Free trade
(b) Balance of trade
(c) Barter system
(d) Bilateral trade
Correct Answer: Option c
```
- **Topic**: 36. International Trade
- **Tier**: Medium
- **Format**: Statement-based
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-3602
- **Question**:
```
Q3602. Consider the following statements:
1. The difference between the value of exports and imports of a country is called balance of trade.
2. A negative balance of trade occurs when the value of imports is greater than the value of exports.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option c
```''',

    38: '''- **Topic**: 38. Human Settlements
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3801
- **Question**:
```
Q3801. Settlements in which houses are spaced far apart and often interspersed with fields are called:
(a) Compact settlements
(b) Dispersed settlements
(c) Nucleated settlements
(d) Urban settlements
Correct Answer: Option b
```
- **Topic**: 38. Human Settlements
- **Tier**: Medium
- **Format**: Matching Pairs
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-3802
- **Question**:
```
Q3802. Consider the following rural settlement patterns and their typical locations:
1. Linear pattern : Along a road, railway line, or river
2. Rectangular pattern : Plain areas or wide inter-montane valleys
3. Circular pattern : Around lakes or tanks
How many of the above pairs are correctly matched?
(a) Only one pair
(b) Only two pairs
(c) All three pairs
(d) None of the pairs
Correct Answer: Option c
```''',

    42: '''- **Topic**: 42. Planning and Sustainable Development in Indian Context
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-4201
- **Question**:
```
Q4201. Which institution replaced the Planning Commission in India in 2015?
(a) Finance Commission
(b) NITI Aayog
(c) National Development Council
(d) Central Statistical Organisation
Correct Answer: Option b
```
- **Topic**: 42. Planning and Sustainable Development in Indian Context
- **Tier**: Advanced
- **Format**: Assertion-Reason
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-4202
- **Question**:
```
Q4202. Assertion (A): The introduction of Indira Gandhi Canal Irrigation in dry regions of Rajasthan transformed its ecology and economy.
Reason (R): It led to the greening of the desert but also brought problems of waterlogging and soil salinity.
Select the correct answer using the codes given below:
(a) Both A and R are true and R is the correct explanation of A
(b) Both A and R are true but R is not the correct explanation of A
(c) A is true but R is false
(d) A is false but R is true
Correct Answer: Option a
```''',

    44: '''- **Topic**: 44. International Trade (India)
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-4401
- **Question**:
```
Q4401. Which one of the following is a major sea port on the East Coast of India?
(a) Kandla
(b) Marmagao
(c) New Mangalore
(d) Visakhapatnam
Correct Answer: Option d
```
- **Topic**: 44. International Trade (India)
- **Tier**: Medium
- **Format**: Statement-based
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-4402
- **Question**:
```
Q4402. Consider the following statements regarding India's foreign trade:
1. Most of India's foreign trade by volume and value is carried through ocean routes.
2. Manufactured goods constitute the largest bulk of India's export.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option c
```'''
}

file_path = 'app/src/main/assets/consolidated_grounding.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

for topic_id, new_content in updates.items():
    topic_header = f'## {topic_id}.'
    ssc_header = '### SSC Stenographer Data (925-Question Set)'
    
    topic_start = content.find(topic_header)
    if topic_start == -1:
        print(f'Topic {topic_id} not found!')
        continue
    
    next_topic_start = content.find('\n## ', topic_start + 1)
    if next_topic_start == -1:
        next_topic_start = len(content)
        
    topic_block = content[topic_start:next_topic_start]
    
    ssc_start = topic_block.find(ssc_header)
    if ssc_start == -1:
        print(f'SSC header not found in topic {topic_id}!')
        continue
        
    ssc_end_idx = ssc_start + len(ssc_header)
    modified_topic_block = topic_block[:ssc_end_idx] + '\n' + new_content + topic_block[ssc_end_idx:]
    
    content = content[:topic_start] + modified_topic_block + content[next_topic_start:]
    print(f'Successfully updated topic {topic_id}')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('All 24 final updates applied successfully.')
