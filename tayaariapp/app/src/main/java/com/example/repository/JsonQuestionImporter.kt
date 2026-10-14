package com.example.repository

import android.content.Context
import android.util.Log
import com.example.database.AppDatabase
import com.example.database.Question
import com.example.database.Topic
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken
import java.lang.reflect.Type
import java.io.InputStreamReader

object JsonQuestionImporter {

    private const val TAG = "JsonQuestionImporter"

    // Mapping from source file names to topic IDs
    private val sourceToTopicMap = mapOf(
        "geography_extracted.txt" to 1,
        "geography_extracted_2.txt" to 2,
        "ncert_xi_physical_geo.txt" to 3,
        "ncert_xi_india_env.txt" to 4,
        "ncert_xii_human_geo.txt" to 5,
        "ncert_xii_india_economy.txt" to 6,
        "ncert_x_geo.txt" to 7,
        "ncert_ix_geo.txt" to 8,
    )

    // Topic definitions
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

    
    suspend fun importFromJson(context: android.content.Context, jsonFileName: String = "generated_questions_1200_clean.json") = kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
        val database = com.example.database.AppDatabase.getDatabase(context)
        val dao = database.appDao()

        android.util.Log.d("JsonQuestionImporter", "Starting JSON import from $jsonFileName")

        // Clear existing questions and topics
        dao.deleteUpscQuestions()
        dao.deleteAllTopics()

        // Read JSON from assets
        val inputStream = context.assets.open(jsonFileName)
        val reader = java.io.InputStreamReader(inputStream)
        
        val gson = com.google.gson.Gson()
        val type: java.lang.reflect.Type = com.google.gson.reflect.TypeToken.getParameterized(List::class.java, GeneratedQuestion::class.java).type
        val questions = gson.fromJson<List<GeneratedQuestion>>(reader, type)

        android.util.Log.d("JsonQuestionImporter", "Parsed ${questions.size} questions from JSON")

        // DYNAMIC TOPIC EXTRACTION
        val topicMap = mutableMapOf<Int, com.example.database.Topic>()
        for (q in questions) {
            val tId = q.topicId
            if (!topicMap.containsKey(tId)) {
                val tName = q.topicName ?: "Unknown Topic"
                val lowerName = tName.lowercase()
                val module = when {
                    lowerName.contains("india") || lowerName.contains("monsoon") -> "Indian Geography"
                    lowerName.contains("geomorphology") || lowerName.contains("ocean") || lowerName.contains("climat") || lowerName.contains("earth") -> "Physical Geography"
                    lowerName.contains("population") || lowerName.contains("urban") || lowerName.contains("trade") || lowerName.contains("econom") || lowerName.contains("farm") || lowerName.contains("industr") || lowerName.contains("resourc") -> "Human & Economic Geography"
                    lowerName.contains("map") || lowerName.contains("spatial") -> "Spatial Geography"
                    else -> "Miscellaneous Topics"
                }
                topicMap[tId] = com.example.database.Topic(tId, tName, "Generated", module)
            }
        }
        dao.insertTopics(topicMap.values.toList())

        // Convert to Room entities
        val roomQuestions = mutableListOf<com.example.database.Question>()
        var imported = 0
        var skipped = 0

        for ((index, q) in questions.withIndex()) {
            try {
                val tier = q.tier ?: "Medium"
                val format = q.format ?: "Direct Fact"
                val examRelevance = "Core"
                val specificExam = "General"

                val roomQuestion = com.example.database.Question(
                    topicId = q.topicId,
                    tier = tier,
                    format = format,
                    examRelevance = examRelevance,
                    source = q.provenance?.sourceFile ?: "",
                    specificExam = specificExam,
                    questionText = q.stem,
                    options = gson.toJson(q.options.map { mapEntry -> 
                        mapOf("id" to mapEntry.key, "text" to mapEntry.value)
                    }),
                    correctAnswer = q.correctAnswer,
                    explanation = q.explanation,
                    distractorDissections = gson.toJson(q.distractorDissections ?: emptyList<Any>()),
                    imageUrl = q.imageUrl ?: "",
                    familyId = q.provenance?.knowledgeNodeId ?: "",
                    familyStage = q.provenance?.intentType ?: ""
                )
                
                roomQuestions.add(roomQuestion)
                imported++
            } catch (e: Exception) {
                android.util.Log.w("JsonQuestionImporter", "Failed to convert question ${q.id}: ${e.message}")
                skipped++
            }
        }

        dao.insertQuestions(roomQuestions)
        android.util.Log.d("JsonQuestionImporter", "Imported $imported questions, skipped $skipped")
    }

    data class GeneratedQuestion(
        val id: String,
        val stem: String,
        val options: Map<String, String>,
        val correctAnswer: String,
        val explanation: String,
        val distractorDissections: List<DistractorDissection>?,
        val provenance: ProvenanceData?,
        val cognitiveDemand: String? = null,
        val examTarget: String? = null,
        val tier: String? = null,
        val format: String? = null,
        val topicId: Int = 0,
        val topicName: String? = null,
        val pdfSequenceNumber: String? = null,
        val imageUrl: String? = null,
        val needsMapDiagram: Boolean? = null,
        val valid: Boolean = true
    )

    data class DistractorDissection(
        val optionId: String,
        val trapType: String,
        val dissection: String
    )

    data class ProvenanceData(
        val questionId: String,
        val questionStem: String,
        val intentType: String,
        val knowledgeNodeId: String,
        val evidenceText: String,
        val sourceFile: String,
        val sourceLocation: SourceLocation,
        val provenanceHash: String,
        val createdAt: String,
        val schemaVersion: String,
        val metadata: Map<String, Any>?,
        val linkHashes: Map<String, String>?
    )

    data class SourceLocation(
        val sourceId: String,
        val sentence_count: Int,
        val section_heading: String,
        val concept: String,
        val sentence_idx: Int,
        val block_id: String,
        val has_antecedent: Boolean
    )
}