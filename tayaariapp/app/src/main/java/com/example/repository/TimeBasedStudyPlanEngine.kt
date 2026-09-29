package com.example.repository

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

data class StudyPlan(
    val durationMinutes: Int,
    val tasks: List<StudyTask>
)

data class StudyTask(
    val title: String,
    val description: String,
    val expectedMinutes: Int
)

class TimeBasedStudyPlanEngine(
    private val localRepository: LocalRepository
) {
    suspend fun generatePlans(): Map<Int, StudyPlan> = withContext(Dispatchers.IO) {
        val profile = localRepository.getLearnerProfile()
        
        val plan15 = StudyPlan(15, listOf(
            StudyTask("Clear Revision Debt", "Quick review of ${profile.revisionDebt} due concepts", 10),
            StudyTask("Single Topic Practice", "5 quick questions on a mixed topic", 5)
        ))
        
        val plan30 = StudyPlan(30, listOf(
            StudyTask("Mistake Replay", "Review recent errors", 10),
            StudyTask("Clear Revision Debt", "Review due items", 10),
            StudyTask("Targeted Practice", "10 questions on weak topics", 10)
        ))
        
        val plan60 = StudyPlan(60, listOf(
            StudyTask("Contrast Lab & Mistake Replay", "Resolve confusions", 15),
            StudyTask("Revision", "Review spaced repetition items", 15),
            StudyTask("Weak Topic Deep Dive", "Focus on ${profile.weakTopics.firstOrNull()?.topicName ?: "new concepts"}", 30)
        ))
        
        val plan120 = StudyPlan(120, listOf(
            StudyTask("Full Mini-Test", "50 questions timed test", 60),
            StudyTask("Post-Test Debrief", "Analyze mistakes from the test", 20),
            StudyTask("Revision", "Clear full learning debt", 20),
            StudyTask("Trap Training", "Build immunity to frequent traps", 20)
        ))
        
        mapOf(15 to plan15, 30 to plan30, 60 to plan60, 120 to plan120)
    }
}
