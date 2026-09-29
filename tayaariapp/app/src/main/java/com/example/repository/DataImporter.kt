package com.example.repository

import android.content.Context
import android.util.Log
import com.example.database.AppDatabase
import com.example.database.Question
import com.example.database.Topic
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.regex.Pattern

object DataImporter {

    private const val TAG = "DataImporter"

    
    private fun getTopicModule(topicName: String): String {
        val normalized = topicName.substringAfter(". ").trim()
        return when {
            normalized in listOf("The Earth in the Solar System", "Globe: Latitudes and Longitudes", "Motions of the Earth", "Major Domains of the Earth", "Major Landforms of the Earth", "Interior of the Earth", "Geomorphic Processes", "Landforms and their Evolution", "Composition and Structure of Atmosphere", "Solar Radiation, Heat Balance and Temperature", "Atmospheric Circulation and Weather Systems", "Water in the Atmosphere", "World Climate and Climate Change", "Water (Oceans)", "Movements of Ocean Water", "Biodiversity and Conservation", "Natural Hazards and Disasters") -> "Physical Geography"
            normalized in listOf("Our Country - India", "India - Location", "Structure and Physiography", "Drainage System", "Climate", "Natural Vegetation", "Transport and Communication (India)", "Land Resources and Agriculture", "Water Resources", "Mineral and Energy Resources") -> "Indian Geography"
            normalized in listOf("Transport and Communication", "Population: Distribution, Density, Growth and Composition") -> "Human & Economic Geography"
            else -> "Miscellaneous Topics"
        }
    }

    suspend fun importFromMarkdown(context: Context, mdContent: String) = withContext(Dispatchers.IO) {
        val database = AppDatabase.getDatabase(context)
        val dao = database.appDao()
        val topics = mutableListOf<Topic>()
        val questions = mutableListOf<Question>()

        var totalQuestionsFound = 0
        var totalQuestionsAccepted = 0
        var totalQuestionsRejected = 0

        Log.d(TAG, "STARTING IMPORT")
        
        // Clear old questions only (not learner attempts / revision / confusion).
        dao.clearAllQuestions()
        
        val blocks = mdContent.split(Regex("\\r?\\n## (?=\\d+\\. )"))
        
        for (i in 1 until blocks.size) {
            val block = blocks[i]
            val topicNumMatch = Regex("^(\\d+)\\. (.*?)\\r?\\n").find(block)
            if (topicNumMatch == null) continue
            
            val tNum = topicNumMatch.groupValues[1].toInt()
            val tName = topicNumMatch.groupValues[2].trim()
            
            topics.add(Topic(tNum, "$tNum. $tName", "Mapped Source", getTopicModule(tName)))
            
            val qPattern = Pattern.compile(
                "- \\*\\*Topic\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
                "- \\*\\*Tier\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
                "- \\*\\*Format\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
                "- \\*\\*Exam-Relevance\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
                "- \\*\\*Source\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
                "- \\*\\*Specific-Exam\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
                "(?:- \\*\\*Trap-Type\\*\\*: ([^\\r\\n]*?)\\s*\\n)?" + 
                "- \\*\\*PDF-Sequence-Number\\*\\*: ([^\\r\\n]*?)\\s*\\n" +
                "- \\*\\*Question\\*\\*:\\s*`\\s*(.*?)\\s*`", Pattern.DOTALL
            )
            
            val matcher = qPattern.matcher(block)
            while (matcher.find()) {
                totalQuestionsFound++
                
                val tier = matcher.group(2)?.trim() ?: ""

                val rawFormat = matcher.group(3)?.trim() ?: ""
                val format = when (val norm = rawFormat.lowercase().replace("-", " ").replace("_", " ")) {
                    "statement", "statement based", "multi statement" -> "Statement-based"
                    "direct fact", "simple", "direct" -> "Direct Fact"
                    "matching", "match the following", "matching pair" -> "Matching"
                    "assertion reason", "assertion" -> "Assertion-Reason"
                    "application", "scenario", "concept application" -> "Application"
                    "" -> "UNCLASSIFIED"
                    else -> "UNCLASSIFIED" // Fallback to avoid guessing
                }
                val relevance = matcher.group(4)?.trim() ?: ""
                val source = matcher.group(5)?.trim() ?: ""
                val exam = matcher.group(6)?.trim() ?: ""

                val rawTrapType = matcher.group(7)?.trim() ?: ""
                val trapType = when {
                    rawTrapType.isEmpty() || rawTrapType.equals("none", ignoreCase = true) -> ""
                    rawTrapType.lowercase().contains("absolute wording") || rawTrapType.lowercase().contains("extreme wording") -> "ABSOLUTE_WORDING"
                    rawTrapType.lowercase().contains("fact distortion") || rawTrapType.lowercase().contains("fact manipulation") -> "FACT_DISTORTION"
                    rawTrapType.lowercase().contains("familiarity") -> "FAMILIARITY_TRAP"
                    rawTrapType.lowercase().contains("concept mix") || rawTrapType.lowercase().contains("concept blending") -> "CONCEPT_MIX"
                    rawTrapType.lowercase().contains("false correlation") -> "FALSE_CORRELATION"
                    rawTrapType.lowercase().contains("partial truth") -> "PARTIAL_TRUTH"
                    rawTrapType.lowercase().contains("anachronism") || rawTrapType.lowercase().contains("timeline") -> "TIMELINE_MISMATCH"
                    else -> "UNCLASSIFIED_TRAP"
                }
                val seqNum = matcher.group(8)?.trim() ?: ""
                var rawQText = matcher.group(9)?.trim() ?: ""
                
                var imageUrl = ""
                val imageMatcher = Regex("\\[IMAGE:\\s*(.*?)]").find(rawQText)
                if (imageMatcher != null) {
                    imageUrl = imageMatcher.groupValues[1].trim()
                    rawQText = rawQText.replace(imageMatcher.value, "").trim()
                }

                // Extract Correct Answer
                val ansMatcher = Pattern.compile("(?i)Correct [Aa]nswer:\\s*(?:Option\\s*)?([a-eA-E])").matcher(rawQText)
                if (!ansMatcher.find()) {
                    Log.w(TAG, "Rejected Q$seqNum: Missing or malformed Correct Answer.")
                    totalQuestionsRejected++
                    continue
                }
                val correctAnswerLetter = ansMatcher.group(1)!!.lowercase().trim()
                val correctAnswerStr = "opt_$correctAnswerLetter"
                rawQText = rawQText.substring(0, ansMatcher.start()).trim() // Remove correct answer from qText

                // Extract Explanation
                var explanationText = "No explanation"
                val expMatcher = Pattern.compile("(?i)Explanation:\\s*(.*)", Pattern.DOTALL).matcher(rawQText)
                if (expMatcher.find()) {
                    explanationText = expMatcher.group(1)!!.trim()
                    rawQText = rawQText.substring(0, expMatcher.start()).trim()
                }

                // Parse Options using Regex
                // Looking for (A), (B), (C), (D), (E) or A), B), C), D), E)
                val optionsRegex = Regex("(?s)\\s*\\(?([a-eA-E])\\)\\s+(.*?)(?=\\s*\\(?[a-eA-E]\\)\\s+|$)")
                val optionMatches = optionsRegex.findAll(rawQText).toList()
                
                if (optionMatches.size < 2) {
                    Log.w(TAG, "Rejected Q$seqNum: Less than 2 options found.")
                    totalQuestionsRejected++
                    continue
                }

                val optionsList = mutableListOf<String>()
                val optionIds = mutableListOf<String>()
                var firstOptionIndex = -1
                
                for (match in optionMatches) {
                    if (firstOptionIndex == -1) {
                        firstOptionIndex = match.range.first
                    }
                    val letter = match.groupValues[1].lowercase()
                    var optText = match.groupValues[2].trim()
                    
                    // JSON escape
                    optText = optText.replace("\"", "\\\"").replace("\n", " ")
                    val optId = "opt_$letter"
                    optionIds.add(optId)
                    optionsList.add("{\"id\":\"$optId\",\"text\":\"$optText\"}")
                }
                
                val qText = if (firstOptionIndex != -1) {
                    rawQText.substring(0, firstOptionIndex).trim()
                } else {
                    rawQText.trim()
                }
                
                if (qText.isEmpty()) {
                    Log.w(TAG, "Rejected Q$seqNum: Empty question text.")
                    totalQuestionsRejected++
                    continue
                }

                if (correctAnswerStr !in optionIds) {
                    Log.w(TAG, "Rejected Q$seqNum: correctAnswer $correctAnswerStr not in $optionIds")
                    totalQuestionsRejected++
                    continue
                }

                val optionsStr = "[" + optionsList.joinToString(",") + "]"
                
                var distractorJson = "[]"
                if (trapType.isNotEmpty()) {
                    val dissectionParts = optionIds.filter { it != correctAnswerStr }.map { oid ->
                        "{\"optionId\":\"$oid\",\"trapType\":\"$trapType\",\"dissection\":\"Parsed from md\"}"
                    }
                    distractorJson = "[" + dissectionParts.joinToString(",") + "]"
                }

                questions.add(Question(
                    topicId = tNum,
                    tier = tier,
                    format = format,
                    examRelevance = relevance,
                    source = source,
                    specificExam = exam,
                    questionText = qText,
                    options = optionsStr,
                    correctAnswer = correctAnswerStr,
                    explanation = explanationText,
                    distractorDissections = distractorJson,
                    imageUrl = imageUrl
                ))
                totalQuestionsAccepted++
            }
        }
        
        Log.d(TAG, "IMPORT COMPLETED. Found: $totalQuestionsFound, Accepted: $totalQuestionsAccepted, Rejected: $totalQuestionsRejected")
        
        dao.insertTopics(topics)
        dao.insertQuestions(questions)
    }
}
