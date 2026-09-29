with open("app/src/main/java/com/example/repository/ConfusionNetwork.kt", "r", encoding="utf-8") as f:
    content = f.read()

import re

new_block = """        ConfusionPair(
            id = "el_nino_la_nina",
            conceptA = "el nino",
            conceptB = "la nina",
            displayNameA = "El Niño",
            displayNameB = "La Niña",
            descriptionA = "Warming of the central/eastern equatorial Pacific. Suppresses Indian Monsoon.",
            descriptionB = "Cooling of the central/eastern equatorial Pacific. Strengthens Indian Monsoon.",
            keywordsA = listOf("el nino", "el niño", "warming", "suppresses monsoon"),
            keywordsB = listOf("la nina", "la niña", "cooling", "strengthens monsoon")
        ),"""

content = re.sub(r'ConfusionPair\(\s*id = "el_nino_la_nina",.*?\),', new_block, content, flags=re.DOTALL)

with open("app/src/main/java/com/example/repository/ConfusionNetwork.kt", "w", encoding="utf-8") as f:
    f.write(content)
