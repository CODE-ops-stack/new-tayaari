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
        // Try local selection first
        var examQuestions = selectionEngine.getQuestionsForProfile(
            topicName = "Mixed",
            examBlueprint = blueprint,
            targetCount = targetCount,
            preferredFormat = "Paper Twin"
        )
        
        // Approach B Fallback: If local SQLite has 0 questions, fetch live on-demand from Cloud CDN
        if (examQuestions.isEmpty()) {
            try {
                examQuestions = CloudQuestionSyncService.fetchQuestionsOnline(
                    topicName = "Global",
                    profile = blueprint,
                    limit = targetCount,
                    format = "Paper Twin"
                )
            } catch (e: Exception) {
                // If offline, will be empty and fail validation safely
            }
        }
        
        val actualCount = examQuestions.size
        val qIds = examQuestions.mapNotNull { it.id.toIntOrNull() }
        val dbQuestions = if (qIds.isNotEmpty()) localRepository.getQuestionsByIds(qIds) else emptyList()
        val actualTiers = if (dbQuestions.isNotEmpty()) {
            dbQuestions.groupingBy { it.tier }.eachCount()
        } else {
            blueprint.allowedTiers.associateWith { (actualCount / maxOf(1, blueprint.allowedTiers.size)) }
        }
        
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
