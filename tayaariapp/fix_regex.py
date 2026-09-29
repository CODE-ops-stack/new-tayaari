with open("app/src/main/java/com/example/repository/ConfusionNetwork.kt", "r", encoding="utf-8") as f:
    content = f.read()

import re
content = re.sub(r'displayNameA = "El Ni.*o"', 'displayNameA = "El Niño"', content)
content = re.sub(r'displayNameB = "La Ni.*a"', 'displayNameB = "La Niña"', content)
content = re.sub(r'"el ni.*o"', '"el niño"', content)
content = re.sub(r'"la ni.*a"', '"la niña"', content)

with open("app/src/main/java/com/example/repository/ConfusionNetwork.kt", "w", encoding="utf-8") as f:
    f.write(content)
