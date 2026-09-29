package com.example.database

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow
import com.example.model.QuestionFormat

@Dao
interface BookmarkDao {
    @Query("SELECT * FROM bookmarks")
    fun getAllBookmarks(): Flow<List<BookmarkedQuestionEntity>>
    
    @Query("SELECT * FROM bookmarks WHERE format = :format")
    fun getBookmarksByFormat(format: QuestionFormat): Flow<List<BookmarkedQuestionEntity>>
    
    @Query("SELECT * FROM bookmarks WHERE id = :id LIMIT 1")
    fun getBookmarkById(id: String): BookmarkedQuestionEntity?
    
    @Query("SELECT EXISTS(SELECT 1 FROM bookmarks WHERE id = :id)")
    fun isBookmarked(id: String): Flow<Boolean>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBookmark(bookmark: BookmarkedQuestionEntity)
    
    @Query("DELETE FROM bookmarks WHERE id = :id")
    suspend fun deleteBookmark(id: String)
}

@Dao
interface TrapAnalyticsDao {
    @Query("SELECT * FROM trap_analytics")
    fun getAllTraps(): Flow<List<TrapAnalyticsEntity>>
    
    @Query("SELECT * FROM trap_analytics")
    suspend fun getAllTrapsSync(): List<TrapAnalyticsEntity>
    
    @Query("SELECT * FROM trap_analytics WHERE trapType = :trapType LIMIT 1")
    suspend fun getTrap(trapType: String): TrapAnalyticsEntity?

    @Query("UPDATE trap_analytics SET frequency = frequency + 1 WHERE trapType = :trapType")
    suspend fun incrementTrap(trapType: String)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTrap(trap: TrapAnalyticsEntity)
}

@Dao
interface AppDao {
    @Query("SELECT * FROM questions WHERE familyId = :familyId")
    suspend fun getQuestionsByFamilyId(familyId: String): List<Question>

    @Query("SELECT * FROM questions WHERE topicId = :topicId LIMIT :limit")
    suspend fun getQuestionsByTopic(topicId: Int, limit: Int): List<Question>

    @Query("SELECT COUNT(*) FROM topics")
    suspend fun getTopicsCount(): Int

    @Query("SELECT * FROM questions WHERE id IN (:ids)")
    suspend fun getQuestionsByIds(ids: List<Int>): List<Question>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTopics(topics: List<Topic>)

    @Query("SELECT * FROM topics ORDER BY id ASC")
    fun getAllTopics(): Flow<List<Topic>>

    @Query("SELECT * FROM topics ORDER BY id ASC")
    suspend fun getAllTopicsUnwrapped(): List<Topic>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertQuestions(questions: List<Question>)
    
    
    
    @Query("SELECT * FROM questions")
    suspend fun getAllQuestions(): List<Question>
    
    @Query("SELECT COUNT(*) FROM questions")
    suspend fun getQuestionCount(): Int
    
    @Query("DELETE FROM questions")
    suspend fun clearAllQuestions(): Int
    
    @Query("DELETE FROM questions WHERE examRelevance = 'Elite'")
    suspend fun deleteUpscQuestions(): Int

    @Query("SELECT * FROM questions WHERE examRelevance = 'Elite' ORDER BY RANDOM() LIMIT 5")
    suspend fun getRandomUpscQuestions(): List<Question>

    @Query("SELECT COUNT(*) FROM questions WHERE examRelevance = 'Elite'")
    suspend fun getUpscQuestionCount(): Int

    @Query("SELECT * FROM questions WHERE topicId = (SELECT id FROM topics WHERE name LIKE :topicName || '%' LIMIT 1) AND tier = :tier ORDER BY RANDOM() LIMIT :limit")
    suspend fun getQuestionsByTopicAndTier(topicName: String, tier: String, limit: Int): List<Question>

    @Query("SELECT * FROM questions WHERE topicId = (SELECT id FROM topics WHERE name LIKE :topicName || '%' LIMIT 1) AND tier IN (:allowedTiers) AND (:allowElite = 1 OR examRelevance != 'Elite') ORDER BY RANDOM() LIMIT :limit")
    suspend fun getQuestionsForProfile(topicName: String, allowedTiers: List<String>, allowElite: Boolean, limit: Int): List<Question>

    @Query("SELECT * FROM questions WHERE tier IN (:allowedTiers) AND (:allowElite = 1 OR examRelevance != 'Elite') ORDER BY RANDOM() LIMIT :limit")
    suspend fun getAllQuestionsForProfile(allowedTiers: List<String>, allowElite: Boolean, limit: Int): List<Question>

    @Query("SELECT * FROM questions WHERE topicId = (SELECT id FROM topics WHERE name LIKE :topicName || '%' LIMIT 1) AND tier IN (:allowedTiers) AND format = :format AND (:allowElite = 1 OR examRelevance != 'Elite') ORDER BY RANDOM() LIMIT :limit")
    suspend fun getQuestionsForProfileWithFormat(topicName: String, allowedTiers: List<String>, format: String, allowElite: Boolean, limit: Int): List<Question>

    @Query("SELECT COUNT(*) FROM questions WHERE topicId = (SELECT id FROM topics WHERE name LIKE :topicName || '%' LIMIT 1) AND tier IN (:allowedTiers) AND (:allowElite = 1 OR examRelevance != 'Elite')")
    suspend fun getQuestionCountForTopicAndProfile(topicName: String, allowedTiers: List<String>, allowElite: Boolean): Int


    @Query("SELECT * FROM questions WHERE topicId = (SELECT id FROM topics WHERE name LIKE :topicName || '%' LIMIT 1) AND tier = :tier AND format = :format ORDER BY RANDOM() LIMIT :limit")
    suspend fun getFewShotExamples(topicName: String, tier: String, format: String, limit: Int = 3): List<Question>

    @Query("SELECT * FROM questions WHERE distractorDissections LIKE '%' || :trapType || '%' ORDER BY RANDOM() LIMIT :limit")
    suspend fun getQuestionsByTrapType(trapType: String, limit: Int): List<Question>
}

@Dao
interface RevisionDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOrUpdate(item: RevisionItemEntity)

    @Query("SELECT * FROM revision_items WHERE questionId = :questionId")
    suspend fun getRevisionItem(questionId: String): RevisionItemEntity?

    @Query("SELECT * FROM revision_items WHERE nextRevisionDate <= :currentTime ORDER BY priority ASC, nextRevisionDate ASC LIMIT :limit")
    suspend fun getDueItems(currentTime: Long, limit: Int): List<RevisionItemEntity>

    @Query("SELECT * FROM revision_items WHERE masteryState != 'MASTERED' AND priority <= 2 ORDER BY priority ASC, nextRevisionDate ASC LIMIT :limit")
    suspend fun getHighPriorityItems(limit: Int): List<RevisionItemEntity>

    @Query("SELECT * FROM revision_items WHERE masteryState = 'NEW' OR masteryState = 'IMPROVING' ORDER BY lastAttemptTime DESC LIMIT :limit")
    suspend fun getRecentlyStudiedItems(limit: Int): List<RevisionItemEntity>
    
    @Query("SELECT COUNT(*) FROM revision_items WHERE nextRevisionDate <= :currentTime")
    fun getDueItemsCount(currentTime: Long): kotlinx.coroutines.flow.Flow<Int>
    @Query("SELECT COUNT(*) FROM revision_items WHERE nextRevisionDate <= :currentTime")
    suspend fun getDueItemsCountSync(currentTime: Long): Int

    @Query("SELECT * FROM revision_items")
    suspend fun getAllRevisionItems(): List<RevisionItemEntity>
}

@Dao
data class FamilyAttemptRecord(
    val familyId: String,
    val familyStage: String?,
    val outcome: String,
    val timestamp: Long,
    val questionId: Int
)

@Dao
interface QuestionAttemptDao {
    @Insert
    suspend fun insertAttempt(attempt: QuestionAttemptEntity)

    @Query("SELECT * FROM question_attempts ORDER BY timestamp DESC")
    suspend fun getAllAttempts(): List<QuestionAttemptEntity>

    @Query("SELECT * FROM question_attempts WHERE questionId = :questionId ORDER BY timestamp DESC")
    suspend fun getAttemptsForQuestion(questionId: String): List<QuestionAttemptEntity>

    @Query("SELECT q.familyId, q.familyStage, qa.outcome, qa.timestamp, q.id as questionId FROM question_attempts qa INNER JOIN questions q ON qa.questionId = CAST(q.id AS TEXT) WHERE q.familyId IS NOT NULL AND qa.timestamp > :since ORDER BY qa.timestamp DESC")
    suspend fun getRecentFamilyAttempts(since: Long): List<FamilyAttemptRecord>
}

data class TopicFormatStats(
    val topicId: Int,
    val topicName: String,
    val simpleCorrect: Int,
    val simpleTotal: Int,
    val complexCorrect: Int,
    val complexTotal: Int
)


data class ConfidenceCalibrationStats(
    val selectedConfidence: String,
    val totalAttempts: Int,
    val correctAttempts: Int
)

@Dao
interface AnalyticsDao {
    @Query("SELECT confidence as selectedConfidence, SUM(CASE WHEN outcome IN ('CORRECT', 'INCORRECT') THEN 1 ELSE 0 END) as totalAttempts, SUM(CASE WHEN outcome = 'CORRECT' THEN 1 ELSE 0 END) as correctAttempts FROM question_attempts WHERE confidence != 'None' AND confidence IS NOT NULL GROUP BY confidence")
    suspend fun getConfidenceCalibration(): List<ConfidenceCalibrationStats>

    @Query("""
        SELECT q.topicId, 
               t.name as topicName,
               SUM(CASE WHEN q.format IN ('Direct Fact', 'Matching') AND qa.outcome = 'CORRECT' THEN 1 ELSE 0 END) as simpleCorrect,
               SUM(CASE WHEN q.format IN ('Direct Fact', 'Matching') AND qa.outcome IN ('CORRECT', 'INCORRECT') THEN 1 ELSE 0 END) as simpleTotal,
               SUM(CASE WHEN q.format IN ('Assertion-Reason', 'Statement-based') AND qa.outcome = 'CORRECT' THEN 1 ELSE 0 END) as complexCorrect,
               SUM(CASE WHEN q.format IN ('Assertion-Reason', 'Statement-based') AND qa.outcome IN ('CORRECT', 'INCORRECT') THEN 1 ELSE 0 END) as complexTotal
        FROM question_attempts qa
        INNER JOIN questions q ON qa.questionId = CAST(q.id AS TEXT)
        INNER JOIN topics t ON q.topicId = t.id
        GROUP BY q.topicId
        HAVING simpleTotal > 0 AND complexTotal > 0
    """)
    suspend fun getTopicFormatStats(): List<TopicFormatStats>
}






@Dao
interface MistakeReplayDao {
    @Insert
    suspend fun insertOutcome(outcome: ReplayOutcomeEntity)

    @Query("SELECT * FROM replay_outcomes ORDER BY replayTimestamp DESC")
    suspend fun getAllOutcomes(): List<ReplayOutcomeEntity>

    @Query("SELECT * FROM replay_outcomes WHERE originalQuestionId = :questionId ORDER BY replayTimestamp DESC")
    suspend fun getOutcomesForQuestion(questionId: String): List<ReplayOutcomeEntity>
}
