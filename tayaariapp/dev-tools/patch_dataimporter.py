with open("app/src/main/java/com/example/repository/DataImporter.kt", "r") as f:
    text = f.read()

text = text.replace("\\n", "\\r?\\n")

with open("app/src/main/java/com/example/repository/DataImporter.kt", "w") as f:
    f.write(text)
