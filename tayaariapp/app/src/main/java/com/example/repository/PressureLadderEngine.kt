package com.example.repository

data class PressureConfig(
    val level: Int,
    val description: String,
    val timeLimitSecondsPerQuestion: Int,
    val penaltyMultiplier: Double
)

class PressureLadderEngine {
    fun getPressureConfig(level: Int): PressureConfig {
        return when (level) {
            1 -> PressureConfig(1, "Relaxed Practice", 120, 1.0)
            2 -> PressureConfig(2, "Exam Pace", 60, 1.0)
            3 -> PressureConfig(3, "Speed Drill", 45, 1.5)
            4 -> PressureConfig(4, "High Pressure Lab", 30, 2.0)
            else -> PressureConfig(1, "Relaxed Practice", 120, 1.0)
        }
    }
}
