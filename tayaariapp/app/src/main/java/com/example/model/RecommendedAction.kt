package com.example.model

sealed class RecommendedAction {
    data class SmartPractice(val topicName: String, val reason: String, val importance: String) : RecommendedAction()
    data class Revision(val pendingCount: Int, val reason: String, val importance: String) : RecommendedAction()
    data class MistakeReplay(val reason: String, val importance: String) : RecommendedAction()
    data class Contrast(val conceptA: String, val conceptB: String, val reason: String, val importance: String) : RecommendedAction()
    data class TrapTraining(val trapType: String, val reason: String, val importance: String) : RecommendedAction()
    data class PrerequisiteRepair(val reason: String, val importance: String) : RecommendedAction()
    data class TransferPractice(val reason: String, val importance: String) : RecommendedAction()
    data class TimedDrill(val reason: String, val importance: String) : RecommendedAction()
    data class ExamSimulation(val reason: String, val importance: String) : RecommendedAction()
    data class RecoveryMode(val reason: String, val importance: String) : RecommendedAction()
}
