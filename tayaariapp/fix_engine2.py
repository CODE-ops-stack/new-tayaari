with open("app/src/main/java/com/example/repository/QuestionSelectionEngine.kt", "r", encoding="utf-8") as f:
    content = f.read()

replacement = """                    // EXACT_REPETITION strong penalty
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
                    }"""

content = content.replace(
    '                    // RECENT_EXACT_REPETITION penalty\n                    if (q.familyStage == lastStage) {\n                        score -= 10.0\n                    }\n                    \n                    // Progression Logic\n                    if (outcome == "INCORRECT") {\n                        if (lastStage == "FOUNDATION" && q.familyStage == "REINFORCEMENT") score += 20.0\n                        if (lastStage == "APPLICATION" && (q.familyStage == "FOUNDATION" || q.familyStage == "STANDARD")) score += 20.0\n                        if (lastStage == "TRAP" && q.familyStage == "TRAP") score += 15.0\n                    } else if (outcome == "CORRECT") {\n                        if (lastStage == "FOUNDATION" && q.familyStage == "STANDARD") score += 20.0\n                        if (lastStage == "TRANSFER" && q.familyStage == "EXAM_STYLE") score += 20.0\n                    }',
    replacement
)

with open("app/src/main/java/com/example/repository/QuestionSelectionEngine.kt", "w", encoding="utf-8") as f:
    f.write(content)
