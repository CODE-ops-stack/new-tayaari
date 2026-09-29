import codecs
with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace("SELECT selectedConfidence, COUNT(*) as totalAttempts", "SELECT confidence as selectedConfidence, COUNT(*) as totalAttempts")
content = content.replace("WHERE selectedConfidence != 'None' GROUP BY selectedConfidence", "WHERE confidence != 'None' AND confidence IS NOT NULL GROUP BY confidence")

with codecs.open('app/src/main/java/com/example/database/Daos.kt', 'w', 'utf-8') as f:
    f.write(content)
