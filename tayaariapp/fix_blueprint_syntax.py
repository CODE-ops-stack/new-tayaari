import codecs

with codecs.open("app/src/main/java/com/example/model/ExamBlueprint.kt", "r", "utf-8") as f:
    content = f.read()

content = content.replace("PenaltyRule.ONE_THIRD)),", "PenaltyRule.ONE_THIRD,")
content = content.replace("PenaltyRule.ONE_FOURTH)),", "PenaltyRule.ONE_FOURTH,")
content = content.replace("PenaltyRule.ONE_THIRD),", "PenaltyRule.ONE_THIRD,")
content = content.replace("PenaltyRule.ONE_FOURTH),", "PenaltyRule.ONE_FOURTH,")
content = content.replace("PenaltyRule.NONE,", "PenaltyRule.NONE,")

with codecs.open("app/src/main/java/com/example/model/ExamBlueprint.kt", "w", "utf-8") as f:
    f.write(content)
