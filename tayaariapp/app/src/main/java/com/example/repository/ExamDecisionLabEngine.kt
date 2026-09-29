package com.example.repository

import com.example.model.ExamBlueprint

data class DecisionLabFeedback(
    val actionTaken: String, // ATTEMPTED, SKIPPED, ABSTAINED, RETURNED
    val timeSpentSeconds: Int,
    val isCorrect: Boolean,
    val questionTier: String,
    val blueprint: ExamBlueprint,
    val feedbackMessage: String,
    val riskScore: Int // 0 to 100, lower is better
)

class ExamDecisionLabEngine {
    fun evaluateDecision(
        actionTaken: String,
        timeSpentSeconds: Int,
        isCorrect: Boolean,
        questionTier: String,
        blueprint: ExamBlueprint,
        isTrap: Boolean
    ): DecisionLabFeedback {
        var risk = 50
        var msg = ""

        if (actionTaken == "SKIPPED") {
            if (isTrap) {
                msg = "Excellent skip. This was a high-risk trap question."
                risk = 10
            } else if (questionTier == "Elite") {
                msg = "Good skip. Elite questions have low ROI if you are unsure."
                risk = 20
            } else {
                msg = "Missed opportunity. This was a ${questionTier} question, you should attempt these."
                risk = 70
            }
        } else if (actionTaken == "ATTEMPTED") {
            if (isCorrect) {
                if (timeSpentSeconds > 120) {
                    msg = "Correct, but you spent too long (${timeSpentSeconds}s). Time allocation risk is high."
                    risk = 60
                } else {
                    msg = "Solid attempt. Good accuracy and time management."
                    risk = 10
                }
            } else {
                if (isTrap) {
                    msg = "You fell for a trap. Negative marking (${blueprint.negativePenaltyRule}) applies."
                    risk = 90
                } else {
                    msg = "Incorrect. Review your fundamentals."
                    risk = 70
                }
            }
        } else if (actionTaken == "ABSTAINED") {
            msg = "Strategic abstain. You avoided negative marking."
            risk = 30
        } else {
            msg = "Decision recorded."
        }

        return DecisionLabFeedback(actionTaken, timeSpentSeconds, isCorrect, questionTier, blueprint, msg, risk)
    }
}
