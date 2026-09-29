file = 'app/src/main/java/com/example/repository/MistakeReplayEngine.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

old_rev_logic = """        val existingRev = revisionDao.getRevisionItem(candidate.originalQuestion.id.toString())
        if (existingRev != null) {
            val newNextReview = if (outcome == "IMPROVED") {
                System.currentTimeMillis() + 7L * 24 * 60 * 60 * 1000
            } else if (outcome == "PARTIALLY_IMPROVED") {
                System.currentTimeMillis() + 3L * 24 * 60 * 60 * 1000
            } else {
                System.currentTimeMillis() + 1L * 24 * 60 * 60 * 1000
            }
            revisionDao.insertRevision(existingRev.copy(nextReviewTime = newNextReview, confidenceLevel = outcome))
        } else {
            if (outcome == "STILL_STRUGGLING") {
                revisionDao.insertRevision(RevisionItemEntity(
                    questionId = candidate.originalQuestion.id.toString(),
                    nextReviewTime = System.currentTimeMillis() + 1L * 24 * 60 * 60 * 1000,
                    confidenceLevel = outcome
                ))
            }
        }"""

new_rev_logic = """        val existingRev = revisionDao.getRevisionItem(candidate.originalQuestion.id.toString())
        val newNextReview = if (outcome == "IMPROVED") {
            System.currentTimeMillis() + 7L * 24 * 60 * 60 * 1000
        } else if (outcome == "PARTIALLY_IMPROVED") {
            System.currentTimeMillis() + 3L * 24 * 60 * 60 * 1000
        } else {
            System.currentTimeMillis() + 1L * 24 * 60 * 60 * 1000
        }
        val newState = if (outcome == "IMPROVED") "IMPROVING" else if (outcome == "PARTIALLY_IMPROVED") "IMPROVING" else "DUE"
        
        if (existingRev != null) {
            revisionDao.insertOrUpdate(existingRev.copy(nextRevisionDate = newNextReview, masteryState = newState, priority = if (outcome == "STILL_STRUGGLING") 1 else 3))
        } else {
            if (outcome == "STILL_STRUGGLING") {
                revisionDao.insertOrUpdate(RevisionItemEntity(
                    questionId = candidate.originalQuestion.id.toString(),
                    firstAttemptTime = System.currentTimeMillis(),
                    lastAttemptTime = System.currentTimeMillis(),
                    attemptCount = 1,
                    correctCount = 0,
                    incorrectCount = 1,
                    masteryState = "NEW",
                    nextRevisionDate = newNextReview,
                    priority = 1,
                    associatedTrap = null
                ))
            }
        }"""
        
text = text.replace(old_rev_logic, new_rev_logic)

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
