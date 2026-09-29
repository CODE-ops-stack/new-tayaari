file = 'app/src/main/java/com/example/repository/LocalRepository.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('private val mcqAdapter = moshi.adapter(MCQQuestion::class.java)', 'val mistakeReplayEngine = MistakeReplayEngine(mistakeReplayDao, trapAnalyticsDao, confusionEventDao, questionAttemptDao, appDao, revisionDao)\n    private val mcqAdapter = moshi.adapter(MCQQuestion::class.java)')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
