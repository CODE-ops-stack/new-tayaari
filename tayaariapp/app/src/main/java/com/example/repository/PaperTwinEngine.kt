package com.example.repository

import com.example.model.ExamBlueprint
import com.example.database.Question
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

data class PaperValidationReport(
    val targetCount: Int,
    val actualCount: Int,
    val targetTiers: List<String>,
    val actualTiers: Map<String, Int>,
    val passedValidation: Boolean
)

data class GeneratedPaper(
    val examId: String,
    val questions: List<com.example.model.ExamQuestion>,
    val report: PaperValidationReport
)

class PaperTwinEngine(
    private val localRepository: LocalRepository
) {
    suspend fun generatePaperTwin(examId: String, targetCount: Int): GeneratedPaper = withContext(Dispatchers.IO) {
        val blueprint = com.example.model.ExamBlueprintRegistry.getBlueprint(examId) 
            ?: throw IllegalArgumentException("Unknown exam ID")
            
        val selectionEngine = QuestionSelectionEngine(localRepository)
        // Use real production question selection logic
        val examQuestions = selectionEngine.getQuestionsForProfile(
            topicName = "Mixed",
            examBlueprint = blueprint,
            targetCount = targetCount,
            preferredFormat = "Paper Twin"
        )
        
        val actualCount = examQuestions.size
        val qIds = examQuestions.map { it.id.toInt() }
        val dbQuestions = localRepository.getQuestionsByIds(qIds)
        val actualTiers = dbQuestions.groupingBy { it.tier }.eachCount()
        
        val passed = actualCount > 0 && actualCount >= (targetCount * 0.8).toInt()
        
        val report = PaperValidationReport(
            targetCount = targetCount,
            actualCount = actualCount,
            targetTiers = blueprint.allowedTiers,
            actualTiers = actualTiers,
            passedValidation = passed
        )
        
        GeneratedPaper(examId, examQuestions, report)
    }
}
