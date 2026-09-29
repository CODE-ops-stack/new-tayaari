package com.example.database

import androidx.room.Entity
import androidx.room.PrimaryKey
import com.example.model.QuestionFormat

@Entity(tableName = "bookmarks")
data class BookmarkedQuestionEntity(
    @PrimaryKey val id: String,
    val format: QuestionFormat,
    val payloadJson: String
)

@Entity(tableName = "trap_analytics")
data class TrapAnalyticsEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val trapType: String,
    val frequency: Int,
    val failedQuestionsJson: String = "[]"
)

@Entity(tableName = "topics")
data class Topic(
    @PrimaryKey val id: Int,
    val name: String,
    val source: String,
    val module: String = "Miscellaneous Topics"
)

@Entity(tableName = "questions")
data class Question(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val topicId: Int,
    val tier: String,
    val format: String,
    val examRelevance: String,
    val source: String,
    val specificExam: String,
    val questionText: String,
    val options: String, // Stored as JSON string
    val correctAnswer: String,
    val explanation: String,
    val distractorDissections: String = "[]",
    val imageUrl: String = "",
    val familyId: String? = null,
    val familyStage: String? = null
)



@Entity(tableName = "test_sessions")
data class TestSession(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val timestamp: Long,
    val examProfile: String,
    val score: Int,
    val totalQuestions: Int
)

@Entity(tableName = "revision_items")
data class RevisionItemEntity(
    @PrimaryKey val questionId: String,
    val firstAttemptTime: Long,
    val lastAttemptTime: Long,
    val attemptCount: Int,
    val correctCount: Int,
    val incorrectCount: Int,
    val masteryState: String, // NEW, DUE, IMPROVING, STRONG, MASTERED
    val nextRevisionDate: Long,
    val priority: Int, // 1 (Highest) to 5 (Lowest)
    val associatedTrap: String? = null
)

@Entity(tableName = "question_attempts")
data class QuestionAttemptEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val questionId: String,
    val timestamp: Long,
    val outcome: String,
    val confidence: String?, // "Certain", "Likely", "Unsure", "Guessing"
    val timeSpentSeconds: Int,
    val trapFallenInto: String?
)



@Entity(tableName = "replay_outcomes")
data class ReplayOutcomeEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val originalQuestionId: String,
    val transferQuestionId: String?,
    val replayTimestamp: Long,
    val initialEvidenceType: String,
    val outcomeState: String // IMPROVED, PARTIALLY_IMPROVED, STILL_STRUGGLING
)
