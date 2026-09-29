import re

updates = {
    3: '''- **Topic**: 3. Motions of the Earth
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
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-302
- **Question**:
```
Q302. Consider the following statements regarding the Earth's motions:
1. The axis of the earth makes an angle of 66.5 degrees with its orbital plane.
2. The circle that divides the day from night on the globe is called the circle of illumination.
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
Q303. On 21st June, the Northern Hemisphere is tilted towards the sun. The sun's rays fall directly on the:
(a) Equator
(b) Tropic of Cancer
(c) Tropic of Capricorn
(d) Arctic Circle
Correct Answer: Option b
```
- **Topic**: 3. Motions of the Earth
- **Tier**: Medium
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-304
- **Question**:
```
Q304. The longest day and the shortest night at places in the Northern Hemisphere occur on:
(a) 21st March
(b) 23rd September
(c) 21st June
(d) 22nd December
Correct Answer: Option c
```
- **Topic**: 3. Motions of the Earth
- **Tier**: Advanced
- **Format**: Assertion-Reason
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: UPSC-Prelims
- **Trap-Type**: Conceptual Misdirection
- **PDF-Sequence-Number**: GEN-305
- **Question**:
```
Q305. Assertion (A): Regions near the poles experience about six months of day and six months of night.
Reason (R): The earth's axis is inclined towards the plane of its orbit.
Select the correct answer using the codes given below:
(a) Both A and R are true and R is the correct explanation of A
(b) Both A and R are true but R is not the correct explanation of A
(c) A is true but R is false
(d) A is false but R is true
Correct Answer: Option a
```''',

    4: '''- **Topic**: 4. Maps
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
Q402. A map showing the distribution of forests and industries is an example of a:
(a) Physical map
(b) Political map
(c) Thematic map
(d) Cadastral map
Correct Answer: Option c
```
- **Topic**: 4. Maps
- **Tier**: Medium
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
```''',

    5: '''- **Topic**: 5. Major Domains of the Earth
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
- **Topic**: 5. Major Domains of the Earth
- **Tier**: Medium
- **Format**: Statement-based
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-503
- **Question**:
```
Q503. Consider the following statements:
1. Europe is separated from Asia by the Ural mountains.
2. The combined landmass of Europe and Asia is called Eurasia.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option c
```''',

    6: '''- **Topic**: 6. Major Landforms of the Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-601
- **Question**:
```
Q601. The wearing away of the earth's surface is called:
(a) Deposition
(b) Erosion
(c) Aggradation
(d) Sedimentation
Correct Answer: Option b
```
- **Topic**: 6. Major Landforms of the Earth
- **Tier**: Medium
- **Format**: Matching Pairs
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-602
- **Question**:
```
Q602. Consider the following mountain types and their examples:
1. Fold Mountain : The Himalayas
2. Block Mountain : The Vosges
3. Volcanic Mountain : Mt. Kilimanjaro
How many pairs given above are correctly matched?
(a) Only one pair
(b) Only two pairs
(c) All three pairs
(d) None of the pairs
Correct Answer: Option c
```
- **Topic**: 6. Major Landforms of the Earth
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-603
- **Question**:
```
Q603. Which among the following is the highest plateau in the world?
(a) Deccan Plateau
(b) East African Plateau
(c) Tibet Plateau
(d) Western Plateau of Australia
Correct Answer: Option c
```''',

    8: '''- **Topic**: 8. India: Climate, Vegetation and Wildlife
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
Q802. Mangrove forests can thrive in:
(a) Fresh water
(b) Saline water
(c) Glacial regions
(d) Desert regions
Correct Answer: Option b
```
- **Topic**: 8. India: Climate, Vegetation and Wildlife
- **Tier**: Medium
- **Format**: Direct Fact
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 6 Generated
- **Specific-Exam**: UPSC-Prelims
- **Trap-Type**: Option Ambiguity
- **PDF-Sequence-Number**: GEN-803
- **Question**:
```
Q803. Mahogany and rosewood trees are found in:
(a) Tropical deciduous forests
(b) Tropical evergreen forests
(c) Mangrove forests
(d) Thorny bushes
Correct Answer: Option b
```''',

    14: '''- **Topic**: 14. Landforms and their Evolution
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-1401
- **Question**:
```
Q1401. A deep valley characterized by steep step-like side slopes is known as:
(a) U-shaped valley
(b) Gorge
(c) Canyon
(d) Blind valley
Correct Answer: Option c
```
- **Topic**: 14. Landforms and their Evolution
- **Tier**: Medium
- **Format**: Statement-based
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: UPSC-Prelims
- **Trap-Type**: Absolute word trap
- **PDF-Sequence-Number**: GEN-1402
- **Question**:
```
Q1402. Consider the following statements regarding groundwater erosional landforms:
1. Stalactites rise up from the floor of the caves.
2. Stalagmites hang as icicles of different diameters.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option d
```
- **Topic**: 14. Landforms and their Evolution
- **Tier**: Advanced
- **Format**: Matching Pairs
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-1403
- **Question**:
```
Q1403. Consider the following pairs of landforms and their geomorphic agent:
1. Playas - Wind
2. Cirque - Glacier
3. V-shaped Valley - Groundwater
How many of the above pairs are correctly matched?
(a) Only one pair
(b) Only two pairs
(c) All three pairs
(d) None of the pairs
Correct Answer: Option b
```''',

    18: '''- **Topic**: 18. Water in the Atmosphere
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-1801
- **Question**:
```
Q1801. The continuous exchange of water between the atmosphere, the oceans and the continents through the processes of evaporation, transpiration, condensation and precipitation is known as:
(a) Condensation
(b) Hydrological cycle
(c) Atmospheric circulation
(d) Vaporization
Correct Answer: Option b
```
- **Topic**: 18. Water in the Atmosphere
- **Tier**: Medium
- **Format**: Direct Fact
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-1802
- **Question**:
```
Q1802. Which of the following is the most important factor in determining the amount of water vapour the air can hold?
(a) Air pressure
(b) Temperature
(c) Wind speed
(d) Ocean currents
Correct Answer: Option b
```
- **Topic**: 18. Water in the Atmosphere
- **Tier**: Advanced
- **Format**: Statement-based
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-1803
- **Question**:
```
Q1803. Consider the following statements regarding Relative Humidity:
1. It is the ratio of the actual amount of water vapour present in the air to the air's capacity to hold water vapour at a given temperature.
2. With the increase of temperature, the relative humidity decreases.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option c
```''',

    21: '''- **Topic**: 21. Movements of Ocean Water
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-2101
- **Question**:
```
Q2101. The rhythmic rise and fall of ocean water twice in a day is called a:
(a) Tide
(b) Ocean current
(c) Wave
(d) Tsunami
Correct Answer: Option a
```
- **Topic**: 21. Movements of Ocean Water
- **Tier**: Medium
- **Format**: Statement-based
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-2102
- **Question**:
```
Q2102. Consider the following statements about Spring Tides:
1. They occur when the sun, the moon and the earth are in a straight line.
2. The height of the tide will be higher than normal.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option c
```
- **Topic**: 21. Movements of Ocean Water
- **Tier**: Advanced
- **Format**: Matching Pairs
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-2103
- **Question**:
```
Q2103. Consider the following pairs of Ocean Currents and their Nature:
1. Gulf Stream - Warm Current
2. Labrador Current - Cold Current
3. Kuroshio Current - Cold Current
How many pairs given above are correctly matched?
(a) Only one pair
(b) Only two pairs
(c) All three pairs
(d) None of the pairs
Correct Answer: Option b
```''',

    22: '''- **Topic**: 22. Biodiversity and Conservation
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-2201
- **Question**:
```
Q2201. Which one of the following regions is known for maximum biodiversity?
(a) Tropical Region
(b) Temperate Region
(c) Polar Region
(d) Desert Region
Correct Answer: Option a
```
- **Topic**: 22. Biodiversity and Conservation
- **Tier**: Medium
- **Format**: Direct Fact
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-2202
- **Question**:
```
Q2202. The concept of "Biodiversity Hotspots" was put forward by:
(a) Norman Myers
(b) Rachel Carson
(c) Eugene Odum
(d) Charles Darwin
Correct Answer: Option a
```
- **Topic**: 22. Biodiversity and Conservation
- **Tier**: Advanced
- **Format**: Statement-based
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 11 Generated
- **Specific-Exam**: UPSC-Prelims
- **Trap-Type**: Absolute word trap
- **PDF-Sequence-Number**: GEN-2203
- **Question**:
```
Q2203. Consider the following statements regarding biodiversity conservation:
1. In-situ conservation refers to the conservation of ecosystems and natural habitats.
2. Botanical gardens are an example of in-situ conservation.
Which of the statements given above is/are correct?
(a) 1 only
(b) 2 only
(c) Both 1 and 2
(d) Neither 1 nor 2
Correct Answer: Option a
```''',

    29: '''- **Topic**: 29. Human Geography Nature and Scope
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: Any
- **PDF-Sequence-Number**: GEN-2901
- **Question**:
```
Q2901. Which of the following is not a sub-field of Social Geography?
(a) Medical Geography
(b) Historical Geography
(c) Military Geography
(d) Geography of Leisure
Correct Answer: Option c
```
- **Topic**: 29. Human Geography Nature and Scope
- **Tier**: Medium
- **Format**: Direct Fact
- **Exam-Relevance**: Elite
- **Source**: NCERT Class 12 Generated
- **Specific-Exam**: UPSC-Prelims
- **PDF-Sequence-Number**: GEN-2902
- **Question**:
```
Q2902. The concept of 'Stop and Go Determinism' or 'Neo-determinism' was introduced by:
(a) Ratzel
(b) Ellen C. Semple
(c) Griffith Taylor
(d) Paul Vidal de la Blache
Correct Answer: Option c
```'''
}

file_path = 'app/src/main/assets/consolidated_grounding.md'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

for topic_id, new_content in updates.items():
    topic_header = f'## {topic_id}.'
    ssc_header = '### SSC Stenographer Data (925-Question Set)'
    
    # Find the topic block
    topic_start = content.find(topic_header)
    if topic_start == -1:
        print(f'Topic {topic_id} not found!')
        continue
    
    # Find the next topic block to bound our search
    next_topic_start = content.find('\\n## ', topic_start + 1)
    if next_topic_start == -1:
        next_topic_start = len(content)
        
    topic_block = content[topic_start:next_topic_start]
    
    # Find the SSC section within this topic
    ssc_start = topic_block.find(ssc_header)
    if ssc_start == -1:
        print(f'SSC header not found in topic {topic_id}!')
        continue
        
    ssc_end_idx = ssc_start + len(ssc_header)
    
    # Append the new content right after the SSC header
    modified_topic_block = topic_block[:ssc_end_idx] + '\\n' + new_content + topic_block[ssc_end_idx:]
    
    # Update the main content
    content = content[:topic_start] + modified_topic_block + content[next_topic_start:]
    print(f'Successfully updated topic {topic_id}')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('All updates applied successfully.')
