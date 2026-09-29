package com.example.repository

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

enum class MasteryLevel {
    NOT_STARTED, PRACTICING, WEAK, UNSTABLE, STRONG, COVERED
}

data class SyllabusTopicNode(
    val topicId: Int,
    val topicName: String,
    val moduleName: String,
    val masteryLevel: MasteryLevel,
    val attemptCount: Int,
    val accuracy: Double
)

class SyllabusEngine(
    private val localRepository: LocalRepository
) {
    suspend fun getSyllabusMap(): List<SyllabusTopicNode> = withContext(Dispatchers.IO) {
        val profile = localRepository.getLearnerProfile()
        
        val nodes = mutableListOf<SyllabusTopicNode>()
        for ((_, perf) in profile.topicPerformances) {
            val module = getTopicModule(perf.topicName)
            
            val level = when {
                perf.total == 0 -> MasteryLevel.NOT_STARTED
                perf.total < 10 -> MasteryLevel.PRACTICING
                perf.total >= 10 && perf.accuracy < 0.5 -> MasteryLevel.WEAK
                perf.total >= 10 && perf.accuracy >= 0.8 -> MasteryLevel.STRONG
                perf.total >= 20 && perf.accuracy >= 0.6 -> MasteryLevel.COVERED
                else -> MasteryLevel.UNSTABLE
            }
            
            nodes.add(SyllabusTopicNode(perf.topicId, perf.topicName, module, level, perf.total, perf.accuracy))
        }
        
        nodes
    }

    private fun getTopicModule(topicName: String): String {
        val normalized = topicName.substringAfter(". ").trim()
        return when {
            normalized in listOf("The Earth in the Solar System", "Globe: Latitudes and Longitudes", "Motions of the Earth", "Major Domains of the Earth", "Major Landforms of the Earth", "Interior of the Earth", "Geomorphic Processes", "Landforms and their Evolution", "Composition and Structure of Atmosphere", "Solar Radiation, Heat Balance and Temperature", "Atmospheric Circulation and Weather Systems", "Water in the Atmosphere", "World Climate and Climate Change", "Water (Oceans)", "Movements of Ocean Water", "Biodiversity and Conservation", "Natural Hazards and Disasters") -> "Physical Geography"
            normalized in listOf("Our Country - India", "India - Location", "Structure and Physiography", "Drainage System", "Climate", "Natural Vegetation", "Transport and Communication (India)", "Land Resources and Agriculture", "Water Resources", "Mineral and Energy Resources") -> "Indian Geography"
            normalized in listOf("Transport and Communication", "Population: Distribution, Density, Growth and Composition") -> "Human & Economic Geography"
            else -> "Miscellaneous Topics"
        }
    }
}
