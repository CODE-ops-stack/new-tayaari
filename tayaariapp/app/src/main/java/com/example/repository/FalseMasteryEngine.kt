package com.example.repository

enum class KnowledgeState {
    STABLE, FRAGILE, INSUFFICIENT, FALSE_MASTERY
}

data class TransferAnalytics(
    val topicName: String,
    val directAccuracy: Double,
    val statementAccuracy: Double,
    val state: KnowledgeState,
    val recommendation: String
)

class FalseMasteryEngine(private val localRepository: LocalRepository) {
    suspend fun evaluateTransfer(): List<TransferAnalytics> {
        val blindSpots = localRepository.getBlindSpots()
        return blindSpots.map { bs ->
            val direct = if (bs.simpleTotal > 0) bs.simpleCorrect.toDouble() / bs.simpleTotal else 0.0
            val statement = if (bs.complexTotal > 0) bs.complexCorrect.toDouble() / bs.complexTotal else 0.0
            
            val state = when {
                direct > 0.7 && statement < 0.4 -> KnowledgeState.FALSE_MASTERY
                direct > 0.5 && statement < 0.5 -> KnowledgeState.FRAGILE
                direct > 0.7 && statement > 0.6 -> KnowledgeState.STABLE
                else -> KnowledgeState.INSUFFICIENT
            }
            
            val msg = when (state) {
                KnowledgeState.FALSE_MASTERY -> "High recall, low transfer. You are memorizing facts instead of understanding mechanisms."
                KnowledgeState.FRAGILE -> "Fragile understanding. You struggle when concepts are combined in statements."
                KnowledgeState.STABLE -> "Good transferability."
                KnowledgeState.INSUFFICIENT -> "Insufficient baseline knowledge."
            }
            
            TransferAnalytics(bs.topicName, direct, statement, state, msg)
        }
    }
}
