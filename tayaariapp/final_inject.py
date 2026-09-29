"""
Bulletproof question injector.
For each empty-SSC topic, we find the EXACT offset of the SSC divider
WITHIN the topic's block using absolute file positions.
"""

with open('app/src/main/assets/consolidated_grounding.md', 'r', encoding='utf-8') as f:
    content = f.read()

print('File length: ' + str(len(content)))

EMPTY_SSC = '### SSC Stenographer Data (925-Question Set)\n---\n'

# Map of topic header -> questions to inject
INJECTIONS = {
    '## 3. Motions of the Earth\n': """- **Topic**: 3. Motions of the Earth
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
- **Tier**: Medium
- **Format**: Statement-based
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-302
- **Question**:
```
Q302. Consider the following statements regarding the Earth's motions:
1. The axis of the earth makes an angle of 66.5 degrees with its orbital plane.
2. The circle that divides the day from night is called the circle of illumination.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option c
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
    '## 4. Maps\n': """- **Topic**: 4. Maps
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-401
- **Question**:
```
Q401. Maps showing natural features of the earth such as mountains, plateaus, and plains are called:
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
Q402. A map showing the distribution of forests and industries is called a:
(a) Physical map
(b) Political map
(c) Thematic map
(d) Cadastral map
Correct Answer: Option c
```
- **Topic**: 4. Maps
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-403
- **Question**:
```
Q403. What are the three main components of a map?
(a) Distance, Direction and Symbol
(b) Distance, Direction and Scale
(c) Scale, Symbol and Location
(d) Direction, Distance and Relief
Correct Answer: Option a
```
""",
    '## 5. Major Domains of the Earth\n': """- **Topic**: 5. Major Domains of the Earth
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
    '## 6. Major Landforms of the Earth\n': """- **Topic**: 6. Major Landforms of the Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-601
- **Question**:
```
Q601. The wearing away of the earth surface by water, wind and ice is called:
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
Q602. Which among the following is the highest plateau in the world?
(a) Deccan Plateau
(b) East African Plateau
(c) Tibetan Plateau
(d) Western Plateau of Australia
Correct Answer: Option c
```
""",
    '## 7. Our Country - India\n': """- **Topic**: 7. Our Country - India
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
    '## 8. India: Climate, Vegetation and Wildlife\n': """- **Topic**: 8. India: Climate, Vegetation and Wildlife
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
    '## 18. Water in the Atmosphere\n': """- **Topic**: 18. Water in the Atmosphere
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-1801
- **Question**:
```
Q1801. The continuous exchange of water between the atmosphere and the earth's surface is known as:
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
Q1802. Which of the following is the most important factor determining how much water vapour the air can hold?
(a) Air pressure
(b) Temperature
(c) Wind speed
(d) Ocean currents
Correct Answer: Option b
```
""",
    '## 9. Geography as a Discipline\n': """- **Topic**: 9. Geography as a Discipline
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-901
- **Question**:
```
Q901. Who coined the term 'Geography'?
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
Q902. The word 'Geography' is derived from which language?
(a) Latin
(b) Arabic
(c) Greek
(d) French
Correct Answer: Option c
```
""",
    '## 10. The Origin and Evolution of the Earth\n': """- **Topic**: 10. The Origin and Evolution of the Earth
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
    '## 12. Distribution of Oceans and Continents\n': """- **Topic**: 12. Distribution of Oceans and Continents
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
    '## 29. Human Geography Nature and Scope\n': """- **Topic**: 29. Human Geography Nature and Scope
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-2901
- **Question**:
```
Q2901. Human geography is the study of the interrelationship between:
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
    '## 30. The World Population Distribution, Density and Growth\n': """- **Topic**: 30. The World Population Distribution, Density and Growth
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
    '## 31. Human Development\n': """- **Topic**: 31. Human Development
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
Q3102. The Human Development Index (HDI) was developed by:
(a) Amartya Sen
(b) Dr Mahbub-ul-Haq
(c) Griffith Taylor
(d) Ratzel
Correct Answer: Option b
```
""",
    '## 32. Primary Activities\n': """- **Topic**: 32. Primary Activities
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
    '## 33. Secondary Activities\n': """- **Topic**: 33. Secondary Activities
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
    '## 34. Tertiary and Quaternary Activities\n': """- **Topic**: 34. Tertiary and Quaternary Activities
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
    '## 36. International Trade\n': """- **Topic**: 36. International Trade
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
    '## 38. Human Settlements\n': """- **Topic**: 38. Human Settlements
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
    '## 42. Planning and Sustainable Development in Indian Context\n': """- **Topic**: 42. Planning and Sustainable Development in Indian Context
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
    '## 44. International Trade (India)\n': """- **Topic**: 44. International Trade (India)
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
Q4402. Which one of the following is a major sea port on the East Coast of India?
(a) Kandla
(b) Marmagao
(c) New Mangalore
(d) Visakhapatnam
Correct Answer: Option d
```
"""
}

total_injected = 0
for topic_header, questions in INJECTIONS.items():
    # Find topic position in file
    topic_idx = content.find(topic_header)
    if topic_idx == -1:
        print('NOT FOUND: ' + topic_header.strip())
        continue
    
    # Find the next topic header to bound the search
    next_topic_idx = content.find('\n## ', topic_idx + len(topic_header))
    if next_topic_idx == -1:
        next_topic_idx = len(content)
    
    # Within the topic block, find the SSC divider
    topic_block = content[topic_idx:next_topic_idx]
    ssc_divider_local = topic_block.find(EMPTY_SSC)
    
    if ssc_divider_local == -1:
        # Check if questions already injected (SSC section not empty)
        if 'GEN-' + topic_header.split('.')[0].replace('## ', '').strip() in topic_block:
            print('ALREADY DONE: ' + topic_header.strip())
        else:
            # SSC section might already have content (non-empty)
            ssc_local = topic_block.find('### SSC Stenographer Data (925-Question Set)\n')
            if ssc_local != -1:
                print('SSC NOT EMPTY (has existing content): ' + topic_header.strip())
            else:
                print('SSC HEADER NOT FOUND: ' + topic_header.strip())
        continue
    
    # Replace the empty SSC divider with questions + divider
    ssc_abs_idx = topic_idx + ssc_divider_local
    new_ssc_content = '### SSC Stenographer Data (925-Question Set)\n' + questions + '---\n'
    content = content[:ssc_abs_idx] + new_ssc_content + content[ssc_abs_idx + len(EMPTY_SSC):]
    total_injected += 1
    print('INJECTED: ' + topic_header.strip())

print('\nTotal injected: ' + str(total_injected))

with open('app/src/main/assets/consolidated_grounding.md', 'w', encoding='utf-8') as f:
    f.write(content)

print('File saved.')
