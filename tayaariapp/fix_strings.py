import codecs

with codecs.open('app/src/main/java/com/example/repository/LocalRepository.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace("overMsg = \"You're frequently highly confident on questions you later miss (Accuracy: \\% when 'Certain').\"", 'overMsg = "You\'re frequently highly confident on questions you later miss (Accuracy: ${(accuracy * 100).toInt()}% when \'Certain\')."')
content = content.replace("underMsg = \"You're often unsure on questions you actually know (Accuracy: \\% when '').\"", 'underMsg = "You\'re often unsure on questions you actually know (Accuracy: ${(accuracy * 100).toInt()}% when \'${stat.selectedConfidence}\')."')

with codecs.open('app/src/main/java/com/example/repository/LocalRepository.kt', 'w', 'utf-8') as f:
    f.write(content)
