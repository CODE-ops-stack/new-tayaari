package com.example.repository

import com.example.database.QuestionAttemptEntity
import com.example.model.ExamBlueprint
import com.example.model.PenaltyRule
import java.math.BigDecimal

data class DebriefReport(
    val totalScore: Double,
    val positiveMarks: Double,
    val penaltyMarks: Double,
    val fixableMarks: Double,
    val actionableInsights: List<String>
)

class PostTestDebriefEngine {
    fun generateDebrief(attempts: List<QuestionAttemptEntity>, blueprint: ExamBlueprint): DebriefReport {
        var correct = 0
        var incorrect = 0
        var abstained = 0
        var unanswered = 0
        
        var trapMistakes = 0
        var carelessMistakes = 0
        var timeLostSeconds = 0
        
        for (a in attempts) {
            when(a.outcome) {
                "CORRECT" -> correct++
                "INCORRECT" -> {
                    incorrect++
                    if (a.timeSpentSeconds < 10) carelessMistakes++
                    if (a.confidence == "HIGH") trapMistakes++
                }
                "ABSTAINED" -> abstained++
                "UNANSWERED" -> unanswered++
            }
        }
        
        val pos = BigDecimal(correct).multiply(blueprint.positiveMarks)
        
        val negPenalty = when (blueprint.negativePenaltyRule) {
            PenaltyRule.ONE_THIRD -> blueprint.positiveMarks.divide(BigDecimal(3), java.math.MathContext.DECIMAL128)
            PenaltyRule.ONE_FOURTH -> blueprint.positiveMarks.divide(BigDecimal(4), java.math.MathContext.DECIMAL128)
            PenaltyRule.NONE -> BigDecimal.ZERO
        }
        val penalty = BigDecimal(incorrect).multiply(negPenalty)
        val score = pos.subtract(penalty)
        
        val fixablePenalty = BigDecimal(carelessMistakes + trapMistakes).multiply(negPenalty)
        val fixablePos = BigDecimal(carelessMistakes).multiply(blueprint.positiveMarks) // Could have gotten these
        val totalFixable = fixablePenalty.add(fixablePos)
        
        val insights = mutableListOf<String>()
        if (carelessMistakes > 0) insights.add("You lost ${carelessMistakes} questions due to rushing (<10s). Slow down.")
        if (trapMistakes > 0) insights.add("You fell for ${trapMistakes} high-confidence traps. Review Trap Training.")
        if (unanswered > 5) insights.add("You left ${unanswered} questions unanswered. Improve time management.")
        
        return DebriefReport(
            totalScore = score.toDouble(),
            positiveMarks = pos.toDouble(),
            penaltyMarks = penalty.toDouble(),
            fixableMarks = totalFixable.toDouble(),
            actionableInsights = insights
        )
    }
}
