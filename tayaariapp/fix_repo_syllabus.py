file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val learnerModelEngine = LearnerModelEngine(appDao, questionAttemptDao, revisionDao, trapAnalyticsDao, confusionEventDao, analyticsDao)', 'val learnerModelEngine = LearnerModelEngine(appDao, questionAttemptDao, revisionDao, trapAnalyticsDao, confusionEventDao, analyticsDao)\n    val syllabusEngine = SyllabusEngine(this)')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
