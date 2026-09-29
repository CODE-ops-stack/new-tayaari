import re
from v13_discovery.normalizer import LayoutDesegmenter

desegmenter = LayoutDesegmenter()

test_lines = [
    'FUNDAMENTALS OF PHYSICAL GEOGRAPHY',
    '1. Geography as a Discipline 2',
    '2. The Origin and Evolution of the Earth 14',
    '3. Interior of the Earth 21',
    '4. Distribution of Oceans and Continents 30',
    'UNIT I : GEOGRAPHY AS A DISCIPLINE 1-12',
    '1. Geography as a Discipline 2',
    '2. The Origin and Evolution of the Earth 14',
    '3. Interior of the Earth 21',
    '4. Distribution of Oceans and Continents 30',
    'UNIT I : GEOGRAPHY AS A DISCIPLINE 1-12',
    'UNIT II : THE EARTH 13-38',
    'UNIT III : LANDFORMS 36-62',
]

for line in test_lines:
    print(f'{line}: {LayoutDesegmenter.is_heading(line)}')