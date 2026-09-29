package com.example.repository

import android.content.Context
import com.example.database.AppDatabase
import com.example.database.Question
import com.example.database.Topic
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.util.regex.Pattern

object DataImporter {

    suspend fun importFromMarkdown(context: Context, mdContent: String) = withContext(Dispatchers.IO) {
        val database = AppDatabase.getDatabase(context)
        val dao = database.appDao()
        val topics = mutableListOf<Topic>()
        val questions = mutableListOf<Question>()

        println("STARTING IMPORT")
        
        // Clear old database first
        dao.deleteUpscQuestions()
        
        val blocks = mdContent.split(Regex("\\n## (?=\\d+\\. )"))
        
        for (i in 1 until blocks.size) {
            val block = blocks[i]
            val topicNumMatch = Regex("^(\\d+)\\. (.*?)\\n").find(block)
            if (topicNumMatch == null) continue
            
            val tNum = topicNumMatch.groupValues[1].toInt()
            val tName = topicNumMatch.groupValues[2].trim()
            
            topics.add(Topic(tNum, "$tNum. $tName", "Mapped Source"))
            
            // Now parse ALL questions in this topic block, regardless of UPSC/SSC
            // They all have the same format now!
            val qPattern = Pattern.compile(
                "- \\*\\*Topic\\*\\*: (.*?)\\n" +
                "- \\*\\*Tier\\*\\*: (.*?)\\n" +
                "- \\*\\*Format\\*\\*: (.*?)\\n" +
                "- \\*\\*Exam-Relevance\\*\\*: (.*?)\\n" +
                "- \\*\\*Source\\*\\*: (.*?)\\n" +
                "- \\*\\*Specific-Exam\\*\\*: (.*?)\\n" +
                "(?:- \\*\\*Trap-Type\\*\\*: (.*?)\\n)?" + // Optional Trap-Type
                "- \\*\\*PDF-Sequence-Number\\*\\*: (.*?)\\n" +
                "- \\*\\*Question\\*\\*:\\n```\\n(.*?)\\n```", Pattern.DOTALL
            )
            
            val matcher = qPattern.matcher(block)
            while (matcher.find()) {
                val tier = matcher.group(2)?.trim() ?: ""
                val format = matcher.group(3)?.trim() ?: ""
                val relevance = matcher.group(4)?.trim() ?: ""
                val source = matcher.group(5)?.trim() ?: ""
                val exam = matcher.group(6)?.trim() ?: ""
                val trapType = matcher.group(7)?.trim() ?: "" // This is where we extract trap type!
                val seqNum = matcher.group(8)?.trim() ?: ""
                val rawQText = matcher.group(9)?.trim() ?: ""
                
                val parsedQPattern = java.util.regex.Pattern.compile(
                    "(?s)(.*?)\\s*\\(?[aA]\\)[ )\\.](.*?)\\s*\\(?[bB]\\)[ )\\.](.*?)\\s*\\(?[cC]\\)[ )\\.](.*?)\\s*\\(?[dD]\\)[ )\\.](.*?)\\s*Correct [Aa]nswer:\\s*(?:[Oo]ption\\s*)?([a-dA-D])"
                )
                val qMatcher = parsedQPattern.matcher(rawQText)
                var qText = rawQText
                var optionsStr = "[]"
                var correctAnswerStr = "A"
                var distractorJson = "[]"
                
                if (trapType.isNotEmpty()) {
                    distractorJson = "[{\"optionId\":\"opt_distractor\",\"trapType\":\"$trapType\",\"dissection\":\"Parsed from md\"}]"
                }

                if (qMatcher.find()) {
                    qText = qMatcher.group(1)?.trim() ?: rawQText
                    val optA = qMatcher.group(2)?.trim()?.replace("\"", "\\\"") ?: ""
                    val optB = qMatcher.group(3)?.trim()?.replace("\"", "\\\"") ?: ""
                    val optC = qMatcher.group(4)?.trim()?.replace("\"", "\\\"") ?: ""
                    val optD = qMatcher.group(5)?.trim()?.replace("\"", "\\\"") ?: ""
                    
                    optionsStr = "[{\"id\":\"opt_a\",\"text\":\"" + optA + "\"},{\"id\":\"opt_b\",\"text\":\"" + optB + "\"},{\"id\":\"opt_c\",\"text\":\"" + optC + "\"},{\"id\":\"opt_d\",\"text\":\"" + optD + "\"}]"
                    
                    val ansLetter = qMatcher.group(6)?.lowercase()?.trim() ?: "a"
                    correctAnswerStr = "opt_" + ansLetter
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
                    explanation = "No explanation",
                    distractorDissections = distractorJson
                ))
            }
        }
        
        // Use a transaction or just insert them all if dao supports it.
        // Wait, dao.insertTopics/insertQuestions. Let's assume it exists.
        dao.insertTopics(topics)
        dao.insertQuestions(questions)
    }
}
