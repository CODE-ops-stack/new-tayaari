with open("app/src/main/java/com/example/repository/ConfusionNetwork.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("El NiAo", "El Niño")
content = content.replace("La NiAa", "La Niña")
content = content.replace("el niAo", "el niño")
content = content.replace("la niAa", "la niña")

with open("app/src/main/java/com/example/repository/ConfusionNetwork.kt", "w", encoding="utf-8") as f:
    f.write(content)
