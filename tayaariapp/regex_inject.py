"""
DEFINITIVE injector - uses regex substitution per-topic to avoid any pattern mismatch issues.
Approach: for each topic, find its exact SSC section, check if it has content after 
the SSC header before the next --- separator. If not, inject our questions there.
"""
import re

with open('app/src/main/assets/consolidated_grounding.md', 'r', encoding='utf-8') as f:
    content = f.read()

print('File size:', len(content))
print('Empty SSC count before:', content.count('### SSC Stenographer Data (925-Question Set)\n---'))

# New questions per topic - keyed by topic number
NEW_QUESTIONS = {
    3: """- **Topic**: 3. Motions of the Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-301
- **Question**:
```
Q301. The movement of the earth on its axis is known as:
(a) Revolution
(b) Rotation
(c) Solstice
(d) Equinox
Correct Answer: Option b
```
- **Topic**: 3. Motions of the Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-303
- **Question**:
```
Q303. The longest day in the Northern Hemisphere occurs on:
(a) 21st March
(b) 23rd September
(c) 21st June
(d) 22nd December
Correct Answer: Option c
```
""",
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
    5: """- **Topic**: 5. Major Domains of the Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-501
- **Question**:
```
Q501. The solid portion of the earth on which we live is called the:
(a) Atmosphere
(b) Hydrosphere
(c) Lithosphere
(d) Biosphere
Correct Answer: Option c
```
- **Topic**: 5. Major Domains of the Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-502
- **Question**:
```
Q502. Which is the largest continent on Earth?
(a) Africa
(b) North America
(c) Asia
(d) Antarctica
Correct Answer: Option c
```
""",
    6: """- **Topic**: 6. Major Landforms of the Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-601
- **Question**:
```
Q601. The wearing away of the earth surface by water and wind is called:
(a) Deposition
(b) Erosion
(c) Aggradation
(d) Sedimentation
Correct Answer: Option b
```
- **Topic**: 6. Major Landforms of the Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-602
- **Question**:
```
Q602. Which is the highest plateau in the world?
(a) Deccan Plateau
(b) East African Plateau
(c) Tibetan Plateau
(d) Western Plateau of Australia
Correct Answer: Option c
```
""",
    7: """- **Topic**: 7. Our Country - India
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-701
- **Question**:
```
Q701. India is located in which hemisphere?
(a) Southern and Eastern
(b) Northern and Eastern
(c) Northern and Western
(d) Southern and Western
Correct Answer: Option b
```
- **Topic**: 7. Our Country - India
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-702
- **Question**:
```
Q702. Which is the largest state in India by area?
(a) Madhya Pradesh
(b) Maharashtra
(c) Uttar Pradesh
(d) Rajasthan
Correct Answer: Option d
```
- **Topic**: 7. Our Country - India
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-703
- **Question**:
```
Q703. The southernmost point of mainland India is:
(a) Indira Point
(b) Kanyakumari
(c) Pamban Island
(d) Rameswaram
Correct Answer: Option b
```
""",
    8: """- **Topic**: 8. India: Climate, Vegetation and Wildlife
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-801
- **Question**:
```
Q801. Day to day changes in the atmosphere are known as:
(a) Climate
(b) Weather
(c) Season
(d) Monsoon
Correct Answer: Option b
```
- **Topic**: 8. India: Climate, Vegetation and Wildlife
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-802
- **Question**:
```
Q802. Mangrove forests are found in:
(a) Desert regions
(b) Alpine regions
(c) Coastal and swampy areas
(d) Deciduous forest belts
Correct Answer: Option c
```
""",
    9: """- **Topic**: 9. Geography as a Discipline
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-901
- **Question**:
```
Q901. Who coined the term Geography?
(a) Herodotus
(b) Galileo
(c) Eratosthenes
(d) Aristotle
Correct Answer: Option c
```
- **Topic**: 9. Geography as a Discipline
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-902
- **Question**:
```
Q902. The word Geography is derived from which language?
(a) Latin
(b) Arabic
(c) Greek
(d) French
Correct Answer: Option c
```
""",
    10: """- **Topic**: 10. The Origin and Evolution of the Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-1001
- **Question**:
```
Q1001. The Big Bang Theory explains the origin of:
(a) Earth
(b) Moon
(c) Universe
(d) Solar system
Correct Answer: Option c
```
- **Topic**: 10. The Origin and Evolution of the Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-1002
- **Question**:
```
Q1002. The approximate age of the Earth is:
(a) 2.5 billion years
(b) 4.6 billion years
(c) 6.0 billion years
(d) 10 billion years
Correct Answer: Option b
```
""",
    12: """- **Topic**: 12. Distribution of Oceans and Continents
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
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-1202
- **Question**:
```
Q1202. Which is the largest ocean in the world?
(a) Atlantic Ocean
(b) Indian Ocean
(c) Arctic Ocean
(d) Pacific Ocean
Correct Answer: Option d
```
""",
    18: """- **Topic**: 18. Water in the Atmosphere
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-1801
- **Question**:
```
Q1801. The continuous exchange of water between atmosphere and earth surface is called:
(a) Condensation
(b) Hydrological cycle
(c) Atmospheric circulation
(d) Vaporization
Correct Answer: Option b
```
- **Topic**: 18. Water in the Atmosphere
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-1802
- **Question**:
```
Q1802. The most important factor determining how much water vapour air can hold is:
(a) Air pressure
(b) Temperature
(c) Wind speed
(d) Ocean currents
Correct Answer: Option b
```
""",
    29: """- **Topic**: 29. Human Geography Nature and Scope
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-2901
- **Question**:
```
Q2901. Human geography studies the relationship between:
(a) Humans and animals
(b) People and their environment
(c) Plants and soils
(d) Water and climate
Correct Answer: Option b
```
- **Topic**: 29. Human Geography Nature and Scope
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-2902
- **Question**:
```
Q2902. The concept of Neo-determinism was introduced by:
(a) Ratzel
(b) Ellen C. Semple
(c) Griffith Taylor
(d) Paul Vidal de la Blache
Correct Answer: Option c
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
    31: """- **Topic**: 31. Human Development
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3101
- **Question**:
```
Q3101. The Human Development Report is published by:
(a) World Bank
(b) IMF
(c) UNDP
(d) WHO
Correct Answer: Option c
```
- **Topic**: 31. Human Development
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3102
- **Question**:
```
Q3102. The Human Development Index was developed by:
(a) Amartya Sen
(b) Dr Mahbub-ul-Haq
(c) Griffith Taylor
(d) Ratzel
Correct Answer: Option b
```
""",
    32: """- **Topic**: 32. Primary Activities
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3201
- **Question**:
```
Q3201. Which of the following is an example of a primary activity?
(a) Manufacturing
(b) Banking
(c) Fishing
(d) Teaching
Correct Answer: Option c
```
- **Topic**: 32. Primary Activities
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3202
- **Question**:
```
Q3202. Primitive subsistence farming is also known as:
(a) Commercial farming
(b) Plantation farming
(c) Slash and burn farming
(d) Intensive farming
Correct Answer: Option c
```
""",
    33: """- **Topic**: 33. Secondary Activities
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3301
- **Question**:
```
Q3301. Which of the following is a secondary activity?
(a) Mining
(b) Fishing
(c) Manufacturing
(d) Teaching
Correct Answer: Option c
```
- **Topic**: 33. Secondary Activities
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3302
- **Question**:
```
Q3302. The first country to industrialise was:
(a) USA
(b) France
(c) Germany
(d) United Kingdom
Correct Answer: Option d
```
""",
    34: """- **Topic**: 34. Tertiary and Quaternary Activities
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3401
- **Question**:
```
Q3401. Which of the following is a tertiary activity?
(a) Agriculture
(b) Manufacturing
(c) Trading
(d) Mining
Correct Answer: Option c
```
- **Topic**: 34. Tertiary and Quaternary Activities
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3402
- **Question**:
```
Q3402. Transport and communication are examples of:
(a) Primary activities
(b) Secondary activities
(c) Tertiary activities
(d) Quaternary activities
Correct Answer: Option c
```
""",
    36: """- **Topic**: 36. International Trade
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3601
- **Question**:
```
Q3601. Trade between two countries is called:
(a) Internal trade
(b) Bilateral trade
(c) Retail trade
(d) Wholesale trade
Correct Answer: Option b
```
- **Topic**: 36. International Trade
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3602
- **Question**:
```
Q3602. The direct exchange of goods without money is known as:
(a) Free trade
(b) Balance of trade
(c) Barter system
(d) Bilateral trade
Correct Answer: Option c
```
""",
    38: """- **Topic**: 38. Human Settlements
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3801
- **Question**:
```
Q3801. Settlements where houses are clustered together are called:
(a) Dispersed settlements
(b) Compact settlements
(c) Linear settlements
(d) Isolated settlements
Correct Answer: Option b
```
- **Topic**: 38. Human Settlements
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-3802
- **Question**:
```
Q3802. Settlements formed along roads, rivers or canals follow which pattern?
(a) Rectangular pattern
(b) Circular pattern
(c) Linear pattern
(d) Star pattern
Correct Answer: Option c
```
""",
    42: """- **Topic**: 42. Planning and Sustainable Development in Indian Context
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
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-4202
- **Question**:
```
Q4202. The first Five Year Plan in India was launched in:
(a) 1947
(b) 1951
(c) 1956
(d) 1961
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

# Strategy: use re.sub with a function that tracks which topic we're in
# Split the file by topic blocks, inject into empty ones, and reassemble

topic_pattern = re.compile(r'(## (\d+)\. [^\n]+\n)(.*?)(### SSC Stenographer Data \(925-Question Set\)\n)(---)', re.DOTALL)

injected_count = 0

def inject_if_empty(m):
    global injected_count
    topic_header = m.group(1)
    topic_num = int(m.group(2))
    upsc_content = m.group(3)
    ssc_header = m.group(4)
    divider = m.group(5)
    
    # Check if SSC section is empty (divider immediately follows header)
    # The divider '---' follows the SSC header with nothing in between except whitespace
    if topic_num in NEW_QUESTIONS:
        injected_count += 1
        return topic_header + upsc_content + ssc_header + NEW_QUESTIONS[topic_num] + divider
    return m.group(0)

new_content = topic_pattern.sub(inject_if_empty, content)

print('Injected:', injected_count, 'topics')
print('GEN- IDs in new content:', new_content.count('GEN-'))

with open('app/src/main/assets/consolidated_grounding.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('File saved. New size:', len(new_content))
