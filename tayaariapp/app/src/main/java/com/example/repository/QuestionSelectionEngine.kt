package com.example.repository

import android.util.Log
import com.example.model.ExamBlueprint
import com.example.database.AppDao
import com.example.model.ExamQuestion
import com.example.model.MCQQuestion
import com.example.model.Option
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONArray
import org.json.JSONObject

class QuestionSelectionEngine(
    private val localRepository: LocalRepository
) {
    suspend fun getQuestionsForProfile(
        topicName: String,
        examBlueprint: ExamBlueprint,
        targetCount: Int,
        preferredFormat: String = "Statement-based",
        documentContext: String? = null
    ): List<ExamQuestion> = withContext(Dispatchers.IO) {
        val selectedQuestions = mutableListOf<ExamQuestion>()
        
        val isTrapTraining = preferredFormat.startsWith("Trap Training")
        val recentFamilyAttempts = if (isTrapTraining) emptyList() else localRepository.getRecentFamilyAttempts(24 * 60 * 60 * 1000L)
        
        // Dynamic Practice Mode Handling: Weak Area, Trap Training, Revision, Paper Twin
        var dbQuestions = if (preferredFormat == "Paper Twin") {
            // Paper Twin logic: sample exactly based on Exam DNA weightages
            val allQ = localRepository.getQuestionsForProfile(topicName, examBlueprint, 100) // fetch a lot
            val mapped = mutableListOf<com.example.database.Question>()
            
            if (examBlueprint.examDna.isNotEmpty()) {
                var remainingTarget = targetCount
                val formats = listOf("Statement-based", "Direct Fact", "Assertion-Reason", "Matching Pairs")
                
                // Map themes roughly to formats to satisfy the query structurally
                // Real implementation would have explicit tag maps.
                val themeToFormatMap = examBlueprint.examDna.mapIndexed { index, theme -> 
                    theme to formats[index % formats.size]
                }
                
                for ((theme, mappedFormat) in themeToFormatMap) {
                    val countForTheme = Math.round((theme.historicalWeightage / 100.0) * targetCount).toInt()
                    val actualToTake = minOf(countForTheme, remainingTarget)
                    if (actualToTake > 0) {
                        val available = allQ.filter { it.format == mappedFormat || it.format?.contains(mappedFormat, ignoreCase=true) == true }
                        if (available.isNotEmpty()) {
                            val taken = available.shuffled().take(actualToTake)
                            mapped.addAll(taken)
                            remainingTarget -= taken.size
                        }
                    }
                }
                
                // If we didn't fill the target due to missing formats, fill with whatever
                if (remainingTarget > 0) {
                    val leftover = allQ.filter { it !in mapped }.shuffled().take(remainingTarget)
                    mapped.addAll(leftover)
                }
                mapped
            } else {
                allQ.shuffled().take(targetCount)
            }
        } else if (preferredFormat == "Smart Revision") {
            localRepository.getRevisionDueQuestions(targetCount)
        } else if (preferredFormat.startsWith("Trap Training:")) {
            val trapType = preferredFormat.substringAfter("Trap Training:").trim()
            localRepository.getQuestionsByTrapType(trapType, targetCount * 2) // Over-fetch to allow filtering
        } else {
            val targetFormat = if (preferredFormat == "Smart Practice" || preferredFormat == "Trap Training") "" else preferredFormat
            if (targetFormat.isNotEmpty()) {
                localRepository.getQuestionsForProfileWithFormat(topicName, examBlueprint, targetFormat, targetCount * 2)
            } else {
                localRepository.getQuestionsForProfile(topicName, examBlueprint, targetCount * 2)
            }
        }
        
        for (q in dbQuestions) {
            val parsedOptions = mutableListOf<Option>()
            try {
                val arr = JSONArray(q.options)
                for (i in 0 until arr.length()) {
                    val obj = arr.getJSONObject(i)
                    parsedOptions.add(Option(id = obj.getString("id"), text = obj.getString("text")))
                }
                while (parsedOptions.size > examBlueprint.optionCount) {
                    parsedOptions.removeLast()
                }
                
                // Add Abstain option if blueprint demands it
                if (examBlueprint.synthesizeAbstainOption && parsedOptions.size == examBlueprint.optionCount - 1) {
                    parsedOptions.add(Option(
                        id = "opt_abstain", 
                        text = examBlueprint.abstainOptionLabel,
                        role = com.example.model.OptionRole.ABSTAIN
                    ))
                }
                
                // Do not add question if it doesn't have at least 2 options
                if (parsedOptions.size < 2) continue
                
            } catch (e: Exception) {
                Log.e("QuestionSelectionEngine", "Skipping question {q.id} due to invalid options JSON")
                continue
            }
            
            val parsedDistractors = mutableListOf<com.example.model.DistractorDissection>()
            try {
                if (!q.distractorDissections.isNullOrEmpty()) {
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
            } catch (e: Exception) {
                Log.e("QuestionSelectionEngine", "Error parsing distractors for question {q.id}", e)
            }
            
            selectedQuestions.add(
                MCQQuestion(
                    id = q.id.toString(),
                    chapterCode = q.source ?: "UNVERIFIED",
                    questionText = q.questionText,
                    questionFormatType = q.format,
                    imageUrl = q.imageUrl,
                    timeLimitSeconds = 90,
                    options = parsedOptions,
                    correctAnswerId = q.correctAnswer,
                    correctExplanation = q.explanation ?: "No explanation provided.",
                    distractorDissections = parsedDistractors,
                    familyId = q.familyId,
                    familyStage = q.familyStage
                )
            )
        }
        
        // Shuffle to ensure variety

        // Next-Best Question Engine Scoring
        // Score factors: Weakness (incorrectCount), RevisionDue, Freshness (-attemptCount)
        val scoredQuestions = selectedQuestions.map { q ->
            val revisionItem = localRepository.getRevisionItem(q.id)
            var score = 0.0
            
            if (revisionItem == null) {
                score += 10.0 // Freshness bonus for unseen questions
            } else {
                // Weakness
                val totalAttempts = revisionItem.attemptCount.coerceAtLeast(1)
                val errorRate = revisionItem.incorrectCount.toDouble() / totalAttempts

                // Redundancy/Repeated Failure Guard
                // If they recently failed it (e.g., attemptCount is high but it's not due for revision), 
                // penalize it slightly to prefer "neighbors" rather than hammering the EXACT same question.
                if (errorRate > 0.6 && revisionItem.nextRevisionDate > System.currentTimeMillis()) {
                    score -= 5.0 // Test the concept via a different question instead
                } else {
                    score += errorRate * 15.0 // Max 15 points for high error rate
                }
                
                // Revision Due
                if (revisionItem.nextRevisionDate < System.currentTimeMillis()) {
                    score += 25.0 // Huge boost if revision is due
                }
                
                // Overexposure penalty
                score -= (revisionItem.attemptCount * 2.0).coerceAtMost(20.0)
            }
            
            // Random noise to prevent completely deterministic loops
            score += Math.random() * 5.0
            
                        // Family penalty / progression logic
            if (!isTrapTraining && q.familyId != null) {
                val familyAttempt = recentFamilyAttempts.firstOrNull { it.familyId == q.familyId }
                if (familyAttempt != null) {
                    val lastStage = familyAttempt.familyStage
                    val outcome = familyAttempt.outcome
                    
                    // RECENT_FAMILY_REPETITION moderate penalty
                    score -= 5.0
                    
                    // EXACT_REPETITION strong penalty
                    if (familyAttempt.questionId.toString() == q.id.toString()) {
                        score -= 20.0
                    } else if (q.familyStage == lastStage) {
                        // FAMILY_STAGE_REPETITION moderate penalty
                        score -= 10.0
                    } else {
                        // DIFFERENT STAGE: apply progression logic
                        if (outcome == "INCORRECT") {
                            if (lastStage == "FOUNDATION" && q.familyStage == "REINFORCEMENT") score += 20.0
                            if (lastStage == "APPLICATION" && (q.familyStage == "FOUNDATION" || q.familyStage == "STANDARD")) score += 20.0
                            if (lastStage == "TRAP" && q.familyStage == "TRAP") score += 15.0
                        } else if (outcome == "CORRECT") {
                            if (lastStage == "FOUNDATION" && q.familyStage == "STANDARD") score += 20.0
                            if (lastStage == "TRANSFER" && q.familyStage == "EXAM_STYLE") score += 20.0
                        }
                    }
                }
            }
Pair(q, score)
        }
        
        // Sort descending by score
        val sortedQuestions = scoredQuestions.sortedByDescending { it.second }.map { it.first }
        
        return@withContext sortedQuestions.take(targetCount)
        
    }
}




