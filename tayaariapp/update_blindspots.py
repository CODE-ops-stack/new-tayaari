import codecs
with codecs.open('app/src/main/java/com/example/repository/LocalRepository.kt', 'r', 'utf-8') as f:
    content = f.read()

old_func = '''    suspend fun getBlindSpots(): List<com.example.database.TopicFormatStats> = withContext(Dispatchers.IO) {
        val stats = analyticsDao.getTopicFormatStats()
        // Filter for "Fragile Knowledge": Strong in simple formats, weak in complex formats
        stats.filter { stat ->
            val simpleRate = if (stat.simpleTotal > 0) stat.simpleCorrect.toDouble() / stat.simpleTotal else 0.0
            val complexRate = if (stat.complexTotal > 0) stat.complexCorrect.toDouble() / stat.complexTotal else 0.0
            simpleRate > 0.6 && complexRate < 0.4
        }
    }'''

new_func = '''
    enum class EvidenceConfidence {
        INSUFFICIENT, EARLY_SIGNAL, EMERGING, CONFIRMED
    }

    data class BlindSpotDetail(
        val topicName: String,
        val simpleCorrect: Int,
        val simpleTotal: Int,
        val complexCorrect: Int,
        val complexTotal: Int,
        val confidence: EvidenceConfidence
    )

    suspend fun getBlindSpots(): List<BlindSpotDetail> = withContext(Dispatchers.IO) {
        val stats = analyticsDao.getTopicFormatStats()
        val blindSpots = mutableListOf<BlindSpotDetail>()
        
        for (stat in stats) {
            val simpleRate = if (stat.simpleTotal > 0) stat.simpleCorrect.toDouble() / stat.simpleTotal else 0.0
            val complexRate = if (stat.complexTotal > 0) stat.complexCorrect.toDouble() / stat.complexTotal else 0.0
            
            // Meaningful gap: At least 30% difference between simple and complex formats, where simple is strong (>60%)
            val hasGap = simpleRate >= 0.6 && (simpleRate - complexRate) >= 0.3
            
            if (hasGap) {
                val totalSamples = stat.simpleTotal + stat.complexTotal
                
                val confidence = when {
                    totalSamples < 5 -> EvidenceConfidence.INSUFFICIENT
                    totalSamples in 5..9 -> EvidenceConfidence.EARLY_SIGNAL
                    totalSamples in 10..19 -> EvidenceConfidence.EMERGING
                    else -> EvidenceConfidence.CONFIRMED
                }
                
                if (confidence != EvidenceConfidence.INSUFFICIENT) {
                    blindSpots.add(
                        BlindSpotDetail(
                            topicName = stat.topicName,
                            simpleCorrect = stat.simpleCorrect,
                            simpleTotal = stat.simpleTotal,
                            complexCorrect = stat.complexCorrect,
                            complexTotal = stat.complexTotal,
                            confidence = confidence
                        )
                    )
                }
            }
        }
        
        // Sort by confidence (Confirmed first) then by gap size
        blindSpots.sortedByDescending { 
            val gap = (it.simpleCorrect.toDouble()/it.simpleTotal) - (it.complexCorrect.toDouble()/it.complexTotal)
            it.confidence.ordinal * 100 + gap
        }
    }'''

content = content.replace(old_func, new_func)

with codecs.open('app/src/main/java/com/example/repository/LocalRepository.kt', 'w', 'utf-8') as f:
    f.write(content)
