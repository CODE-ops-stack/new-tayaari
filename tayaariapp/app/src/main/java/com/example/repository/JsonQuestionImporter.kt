package com.example.repository

import android.content.Context
import android.util.Log
import com.example.database.AppDatabase
import com.example.database.Question
import com.example.database.Topic
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import com.google.gson.Gson
import com.google.gson.JsonArray
import com.google.gson.JsonElement
import com.google.gson.JsonObject
import com.google.gson.reflect.TypeToken
import java.io.InputStreamReader

object JsonQuestionImporter {

    private const val TAG = "JsonQuestionImporter"

    private val topicDefinitions = listOf(
        Topic(1, "1. The Earth in the Solar System", "NCERT Class VI", "Physical Geography"),
        Topic(2, "2. Globe: Latitudes and Longitudes", "NCERT Class VI", "Physical Geography"),
        Topic(3, "3. Motions of the Earth", "NCERT Class VI", "Physical Geography"),
        Topic(4, "4. Maps", "NCERT Class VI", "Physical Geography"),
        Topic(5, "5. Major Domains of the Earth", "NCERT Class VI", "Physical Geography"),
        Topic(6, "6. Major Landforms of the Earth", "NCERT Class VI", "Physical Geography"),
        Topic(7, "7. Our Country - India", "NCERT Class VI", "Indian Geography"),
        Topic(8, "8. India: Climate, Vegetation and Wildlife", "NCERT Class VI", "Indian Geography"),
        Topic(9, "9. Resources and Development", "NCERT Class X", "Indian Geography"),
        Topic(10, "10. Contemporary India - I", "NCERT Class IX", "Indian Geography"),
        Topic(11, "11. Fundamentals of Physical Geography", "NCERT Class XI", "Physical Geography"),
        Topic(12, "12. India Physical Environment", "NCERT Class XI", "Indian Geography"),
        Topic(13, "13. Fundamentals of Human Geography", "NCERT Class XII", "Human Geography"),
        Topic(14, "14. India People and Economy", "NCERT Class XII", "Indian Geography"),
        Topic(15, "15. SSC/UPSC PYQ Geography", "Previous Year Questions", "Mixed"),
        Topic(16, "16. Geomorphology", "Advanced", "Physical Geography"),
        Topic(17, "17. Climatology", "Advanced", "Physical Geography"),
        Topic(18, "18. Oceanography", "Advanced", "Physical Geography"),
        Topic(19, "19. Biogeography", "Advanced", "Physical Geography"),
        Topic(20, "20. Human & Economic Geography", "Advanced", "Human Geography"),
    )

    suspend fun importFromJson(context: Context, jsonFileName: String = "generated_questions_1200_clean.json") = withContext(Dispatchers.IO) {
        val database = AppDatabase.getDatabase(context)
        val dao = database.appDao()

        Log.d(TAG, "Starting JSON import from $jsonFileName")

        dao.deleteUpscQuestions()
        dao.insertTopics(topicDefinitions)

        val inputStream = context.assets.open(jsonFileName)
        val reader = InputStreamReader(inputStream)
        val gson = Gson()
        val raw: JsonArray = gson.fromJson(reader, JsonArray::class.java)

        Log.d(TAG, "Parsed ${raw.size()} questions from JSON")

        val roomQuestions = mutableListOf<Question>()
        var imported = 0
        var skipped = 0

        for (el in raw) {
            if (!el.isJsonObject) {
                skipped++
                continue
            }
            val obj = el.asJsonObject
            try {
                val optionsEl = obj.get("options")
                if (optionsEl == null || !optionsEl.isJsonArray) {
                    Log.w(TAG, "Rejected ${optString(obj, "id")}: options is not a JSON array of {id,text}")
                    skipped++
                    continue
                }
                val lockedOptions = JsonArray()
                var optionsOk = true
                for (optEl in optionsEl.asJsonArray) {
                    if (!optEl.isJsonObject) {
                        optionsOk = false
                        break
                    }
                    val o = optEl.asJsonObject
                    if (!o.has("id") || !o.has("text")) {
                        optionsOk = false
                        break
                    }
                    lockedOptions.add(o)
                }
                if (!optionsOk || lockedOptions.size() < 2) {
                    Log.w(TAG, "Rejected ${optString(obj, "id")}: malformed options list")
                    skipped++
                    continue
                }
                val ids = (0 until lockedOptions.size()).map { lockedOptions[it].asJsonObject.get("id").asString }
                val correctAnswer = optString(obj, "correctAnswer")
                if (correctAnswer.isEmpty() || correctAnswer !in ids) {
                    Log.w(TAG, "Rejected ${optString(obj, "id")}: correctAnswer $correctAnswer not in $ids")
                    skipped++
                    continue
                }

                val dissectionsEl = obj.get("distractorDissections")
                val dissectionsJson = if (dissectionsEl != null && dissectionsEl.isJsonArray) {
                    gson.toJson(dissectionsEl)
                } else {
                    "[]"
                }

                val topicId = if (obj.has("topicId") && obj.get("topicId").isJsonPrimitive) {
                    obj.get("topicId").asInt
                } else {
                    1
                }
                val provenance = obj.getAsJsonObject("provenance")
                val familyId = firstNonBlank(
                    optString(obj, "familyId"),
                    if (provenance != null) optString(provenance, "knowledgeNodeId") else ""
                )
                val familyStage = firstNonBlank(
                    optString(obj, "familyStage"),
                    if (provenance != null) optString(provenance, "intentType") else ""
                )

                val roomQuestion = Question(
                    topicId = topicId,
                    tier = optString(obj, "tier").ifBlank { "Medium" },
                    format = optString(obj, "format").ifBlank { "Direct Fact" },
                    examRelevance = "Core",
                    source = if (provenance != null) optString(provenance, "sourceFile") else "generated",
                    specificExam = optString(obj, "examTarget").ifBlank { "General" },
                    questionText = optString(obj, "stem"),
                    options = gson.toJson(lockedOptions),
                    correctAnswer = correctAnswer,
                    explanation = optString(obj, "explanation"),
                    distractorDissections = dissectionsJson,
                    imageUrl = "",
                    familyId = familyId.ifBlank { null },
                    familyStage = familyStage.ifBlank { null }
                )
                roomQuestions.add(roomQuestion)
                imported++
            } catch (e: Exception) {
                Log.w(TAG, "Failed to convert question: ${e.message}")
                skipped++
            }
        }

        Log.d(TAG, "Converted $imported questions, skipped $skipped")

        if (roomQuestions.isNotEmpty()) {
            dao.insertQuestions(roomQuestions)
            Log.d(TAG, "Successfully inserted ${roomQuestions.size} questions into database")
        }

        val count = dao.getQuestionCount()
        Log.d(TAG, "Total questions in database: $count")

        ImportResult(success = true, importedCount = imported, skippedCount = skipped, totalInDb = count)
    }

    private fun optString(obj: JsonObject, key: String): String {
        val el: JsonElement? = obj.get(key)
        if (el == null || el.isJsonNull) return ""
        return try {
            if (el.isJsonPrimitive) el.asString else el.toString()
        } catch (e: Exception) {
            ""
        }
    }

    private fun firstNonBlank(vararg values: String): String {
        return values.firstOrNull { it.isNotBlank() } ?: ""
    }

    data class ImportResult(
        val success: Boolean,
        val importedCount: Int,
        val skippedCount: Int,
        val totalInDb: Int
    )
}
