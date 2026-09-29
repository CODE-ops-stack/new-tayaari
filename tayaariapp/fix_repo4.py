with open("app/src/main/java/com/example/repository/LocalRepository.kt", "r", encoding="utf-8") as f:
    content = f.read()

methods = """

    suspend fun logConfusionEvent(
        pairId: String,
        questionId: String,
        selectedOptionText: String,
        evidenceLevel: com.example.repository.ConfusionEvidenceLevel
    ) {
        withContext(Dispatchers.IO) {
            val event = com.example.database.ConfusionEventEntity(
                pairId = pairId,
                questionId = questionId,
                selectedOptionText = selectedOptionText,
                timestamp = System.currentTimeMillis(),
                evidenceLevel = evidenceLevel.name
            )
            confusionEventDao.insertEvent(event)
        }
    }

    suspend fun getConfusionEventsForPair(pairId: String): List<com.example.database.ConfusionEventEntity> {
        return withContext(Dispatchers.IO) {
            confusionEventDao.getEventsForPair(pairId)
        }
    }
"""

content = content.replace(methods, "")
content = content.rstrip()
if content.endswith("}"):
    content = content[:-1] + methods + "}\n"

with open("app/src/main/java/com/example/repository/LocalRepository.kt", "w", encoding="utf-8") as f:
    f.write(content)
