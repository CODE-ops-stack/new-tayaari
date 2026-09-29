import re

with open("app/src/main/java/com/example/repository/QuestionSelectionEngine.kt", "r", encoding="utf-8") as f:
    content = f.read()

# Replace recentlyFailedFamilyIds with recentFamilyAttempts
content = re.sub(
    r"val recentlyFailedFamilyIds =.*?\n",
    'val recentFamilyAttempts = if (isTrapTraining) emptyList() else localRepository.getRecentFamilyAttempts(24 * 60 * 60 * 1000L)\n',
    content
)

family_logic = '''            // Family penalty / progression logic
            if (!isTrapTraining && q.familyId != null) {
                val familyAttempt = recentFamilyAttempts.firstOrNull { it.familyId == q.familyId }
                if (familyAttempt != null) {
                    val lastStage = familyAttempt.familyStage
                    val outcome = familyAttempt.outcome
                    
                    // RECENT_FAMILY_REPETITION moderate penalty
                    score -= 5.0
                    
                    // RECENT_EXACT_REPETITION penalty
                    if (q.familyStage == lastStage) {
                        score -= 10.0
                    }
                    
                    // Progression Logic
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
'''

content = re.sub(
    r"// Family penalty\s+if \(!isTrapTraining.*?\}\s+",
    family_logic,
    content,
    flags=re.DOTALL
)

with open("app/src/main/java/com/example/repository/QuestionSelectionEngine.kt", "w", encoding="utf-8") as f:
    f.write(content)
