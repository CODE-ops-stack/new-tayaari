package com.example.repository

import com.example.model.ExamBlueprint
import com.example.model.ExamQuestion
import com.example.model.MCQQuestion
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray

enum class ShockProfile {
    FORMAT_SHOCK,
    DIFFICULTY_SHOCK,
    TIME_SHOCK,
    WORDING_SHOCK,
    COMBINED_SHOCK
}

class PatternShockEngine(
    private val localRepository: LocalRepository,
    private val pressureLadderEngine: PressureLadderEngine
) {
    suspend fun generateShockPaper(
        profile: ExamBlueprint, 
        shockProfile: ShockProfile, 
        targetCount: Int = 15
    ): GeneratedPaper = withContext(Dispatchers.IO) {
        val allDbQuestions = localRepository.getQuestionsForProfile("Global", profile, 1000)
        
        val shockDbQuestions = mutableListOf<com.example.database.Question>()
        var requestedShockCount = 0
        var actualShockCount = 0
        
        val pressureLevel = if (shockProfile == ShockProfile.TIME_SHOCK || shockProfile == ShockProfile.COMBINED_SHOCK) 4 else 2
        val pressureConfig = pressureLadderEngine.getPressureConfig(pressureLevel)
        
        when (shockProfile) {
            ShockProfile.FORMAT_SHOCK -> {
                requestedShockCount = targetCount
                val formatShockQ = allDbQuestions.filter { it.format.contains("Statement", ignoreCase = true) || it.format.contains("Assertion", ignoreCase = true) }
                shockDbQuestions.addAll(formatShockQ.shuffled().take(targetCount))
                actualShockCount = shockDbQuestions.size
                
                // Fill remaining with normal if short
                if (shockDbQuestions.size < targetCount) {
                    shockDbQuestions.addAll(allDbQuestions.filter { it !in shockDbQuestions }.shuffled().take(targetCount - shockDbQuestions.size))
                }
            }
            ShockProfile.DIFFICULTY_SHOCK -> {
                requestedShockCount = targetCount
                val diffShockQ = allDbQuestions.filter { it.tier == "Elite" || it.tier == "Advanced" }
                shockDbQuestions.addAll(diffShockQ.shuffled().take(targetCount))
                actualShockCount = shockDbQuestions.size
                
                if (shockDbQuestions.size < targetCount) {
                    shockDbQuestions.addAll(allDbQuestions.filter { it !in shockDbQuestions }.shuffled().take(targetCount - shockDbQuestions.size))
                }
            }
            ShockProfile.TIME_SHOCK -> {
                requestedShockCount = targetCount
                // Time shock uses representative questions but intense time limit
                shockDbQuestions.addAll(allDbQuestions.shuffled().take(targetCount))
                actualShockCount = shockDbQuestions.size
            }
            ShockProfile.WORDING_SHOCK -> {
                requestedShockCount = targetCount
                val wordingQ = allDbQuestions.filter { it.questionText.contains("NOT") || it.questionText.contains("INCORRECT") }
                shockDbQuestions.addAll(wordingQ.shuffled().take(targetCount))
                actualShockCount = shockDbQuestions.size
                
                if (shockDbQuestions.size < targetCount) {
                    shockDbQuestions.addAll(allDbQuestions.filter { it !in shockDbQuestions }.shuffled().take(targetCount - shockDbQuestions.size))
                }
            }
            ShockProfile.COMBINED_SHOCK -> {
                requestedShockCount = targetCount
                val combined = allDbQuestions.filter { 
                    (it.tier == "Elite" || it.tier == "Advanced") && 
                    (it.format.contains("Statement", ignoreCase = true))
                }
                shockDbQuestions.addAll(combined.shuffled().take(targetCount))
                actualShockCount = shockDbQuestions.size
                
                if (shockDbQuestions.size < targetCount) {
                    shockDbQuestions.addAll(allDbQuestions.filter { it !in shockDbQuestions }.shuffled().take(targetCount - shockDbQuestions.size))
                }
            }
        }
        
        val shockPaper = mutableListOf<ExamQuestion>()
        for (q in shockDbQuestions.shuffled()) {
            val parsedOptions = mutableListOf<com.example.model.Option>()
            try {
                val arr = JSONArray(q.options)
                for (i in 0 until arr.length()) {
                    val obj = arr.getJSONObject(i)
                    parsedOptions.add(com.example.model.Option(id = obj.getString("id"), text = obj.getString("text")))
                }
            } catch (e: Exception) {}
            
            if (parsedOptions.size < 2) continue
            
            val parsedDistractors = mutableListOf<com.example.model.DistractorDissection>()
            try {
                if (q.distractorDissections.isNotEmpty() && q.distractorDissections != "[]") {
                    val dArr = JSONArray(q.distractorDissections)
                    for (i in 0 until dArr.length()) {
                        val obj = dArr.getJSONObject(i)
                        parsedDistractors.add(com.example.model.DistractorDissection(
                            optionId = obj.getString("optionId"),
                            trapType = obj.getString("trapType"),
                            dissection = obj.getString("dissection")
                        ))
                    }
                }
            } catch (e: Exception) {}
            
            shockPaper.add(
                MCQQuestion(
                    id = q.id.toString(),
                    chapterCode = q.source ?: "UNVERIFIED",
                    questionText = q.questionText,
                    questionFormatType = q.format,
                    options = parsedOptions,
                    correctAnswerId = q.correctAnswer,
                    correctExplanation = q.explanation,
                    distractorDissections = parsedDistractors,
                    familyId = q.familyId,
                    familyStage = q.familyStage,
                    timeLimitSeconds = pressureConfig.timeLimitSecondsPerQuestion
                )
            )
        }
        
        val status = when {
            actualShockCount == 0 -> "INSUFFICIENT_DATA"
            actualShockCount < requestedShockCount -> "PARTIAL"
            else -> "PASS"
        }
        
        // Use actualTiers to report validation metadata in a generic way without changing PaperValidationReport structure
        val metaMap = mapOf(
            "requested_shock" to requestedShockCount,
            "actual_shock" to actualShockCount,
            "status_pass" to if (status == "PASS") 1 else 0,
            "status_partial" to if (status == "PARTIAL") 1 else 0,
            "status_insufficient" to if (status == "INSUFFICIENT_DATA") 1 else 0
        )
        
        val report = PaperValidationReport(
            targetCount = targetCount,
            actualCount = shockPaper.size,
            targetTiers = listOf(shockProfile.name),
            actualTiers = metaMap,
            passedValidation = (status == "PASS" || status == "PARTIAL")
        )
        
        GeneratedPaper(
            examId = profile.examId + "_SHOCK_" + shockProfile.name,
            questions = shockPaper,
            report = report
        )
    }
}
