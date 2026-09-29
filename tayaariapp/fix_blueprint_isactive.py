import codecs

content = '''package com.example.model

import java.math.BigDecimal
import java.math.RoundingMode

data class ExamBlueprint(
    val examId: String,
    val version: String,
    val displayName: String,
    val optionCount: Int = 4,
    val positiveMarks: BigDecimal = BigDecimal.ONE,
    val negativeMarks: BigDecimal = BigDecimal.ZERO,
    val defaultRelevance: String = "Core",
    val recommendedPracticeMode: String = "Standard Practice",
    val allowedTiers: List<String> = emptyList(),
    val effectiveDate: String = "",
    val sourceReference: String = "",
    val lastVerificationDate: String = "",
    val isActive: Boolean = false
)

object ExamBlueprintRegistry {
    private fun calcOneThirdNegative(positive: BigDecimal): BigDecimal {
        return positive.divide(BigDecimal("3"), 4, RoundingMode.HALF_UP)
    }

    private fun calcOneFourthNegative(positive: BigDecimal): BigDecimal {
        return positive.divide(BigDecimal("4"), 4, RoundingMode.HALF_UP)
    }

    val blueprints = listOf(
        ExamBlueprint(
            examId = "UPSC_CSE_2026",
            version = "2026",
            displayName = "UPSC Civil Services (Prelims)",
            optionCount = 4,
            positiveMarks = BigDecimal("2.0"),
            negativeMarks = calcOneThirdNegative(BigDecimal("2.0")),
            defaultRelevance = "Elite",
            recommendedPracticeMode = "Deep Concept + Elimination",
            allowedTiers = listOf("Medium", "Advanced", "Elite"),
            effectiveDate = "2026",
            sourceReference = "UPSC Civil Services Notification 2026",
            lastVerificationDate = "2026-08-20",
            isActive = true
        ),
        ExamBlueprint(
            examId = "BPSC_CCE_72ND_2026",
            version = "72nd",
            displayName = "BPSC 72nd CCE (Prelims)",
            optionCount = 5,
            positiveMarks = BigDecimal("1.0"),
            negativeMarks = calcOneThirdNegative(BigDecimal("1.0")),
            defaultRelevance = "Core",
            recommendedPracticeMode = "General Studies + Bihar Focus",
            allowedTiers = listOf("Medium", "Advanced"),
            effectiveDate = "2026",
            sourceReference = "72nd BPSC CCE Notification 2026",
            lastVerificationDate = "2026-08-20",
            isActive = true
        ),
        ExamBlueprint(
            examId = "BPSC_CCE_71ST",
            version = "71st",
            displayName = "BPSC 71st (Historical)",
            optionCount = 4,
            positiveMarks = BigDecimal("1.0"),
            negativeMarks = calcOneThirdNegative(BigDecimal("1.0")),
            defaultRelevance = "Core",
            recommendedPracticeMode = "General Studies + Bihar Focus",
            allowedTiers = listOf("Medium", "Advanced"),
            effectiveDate = "2025",
            sourceReference = "71st BPSC Notification",
            lastVerificationDate = "2026-08-20",
            isActive = false
        ),
        ExamBlueprint(
            examId = "BPSC_CCE_70TH",
            version = "70th",
            displayName = "BPSC 70th (Historical)",
            optionCount = 4,
            positiveMarks = BigDecimal("1.0"),
            negativeMarks = calcOneThirdNegative(BigDecimal("1.0")),
            defaultRelevance = "Core",
            recommendedPracticeMode = "General Studies + Bihar Focus",
            allowedTiers = listOf("Medium", "Advanced"),
            effectiveDate = "2024",
            sourceReference = "70th BPSC Notification",
            lastVerificationDate = "2026-08-20",
            isActive = false
        ),
        ExamBlueprint(
            examId = "BPSC_CCE_69TH",
            version = "69th",
            displayName = "BPSC 69th (Historical)",
            optionCount = 4,
            positiveMarks = BigDecimal("1.0"),
            negativeMarks = calcOneThirdNegative(BigDecimal("1.0")),
            defaultRelevance = "Core",
            recommendedPracticeMode = "General Studies + Bihar Focus",
            allowedTiers = listOf("Medium", "Advanced"),
            effectiveDate = "2023",
            sourceReference = "69th BPSC Notification",
            lastVerificationDate = "2026-08-20",
            isActive = false
        ),
        ExamBlueprint(
            examId = "BPSC_CCE_68TH",
            version = "68th",
            displayName = "BPSC 68th (Historical)",
            optionCount = 5,
            positiveMarks = BigDecimal("1.0"),
            negativeMarks = calcOneFourthNegative(BigDecimal("1.0")),
            defaultRelevance = "Core",
            recommendedPracticeMode = "General Studies + Bihar Focus",
            allowedTiers = listOf("Medium", "Advanced"),
            effectiveDate = "2023",
            sourceReference = "68th BPSC Notification",
            lastVerificationDate = "2026-08-20",
            isActive = false
        ),
        ExamBlueprint(
            examId = "SSC_CGL_2025",
            version = "2025",
            displayName = "SSC CGL (Tier-1)",
            optionCount = 4,
            positiveMarks = BigDecimal("2.0"),
            negativeMarks = calcOneFourthNegative(BigDecimal("2.0")), // 0.5
            defaultRelevance = "Core",
            recommendedPracticeMode = "Speed + Accuracy",
            allowedTiers = listOf("Basic", "Medium"),
            effectiveDate = "2025",
            sourceReference = "SSC CGL Official Notification",
            lastVerificationDate = "2026-08-20",
            isActive = true
        ),
        ExamBlueprint(
            examId = "SSC_CHSL_2025",
            version = "2025",
            displayName = "SSC CHSL (Tier-1)",
            optionCount = 4,
            positiveMarks = BigDecimal("2.0"),
            negativeMarks = calcOneFourthNegative(BigDecimal("2.0")), // 0.5
            defaultRelevance = "Foundation",
            recommendedPracticeMode = "Fast Fundamentals",
            allowedTiers = listOf("Basic"),
            effectiveDate = "2025",
            sourceReference = "SSC CHSL Official Notification",
            lastVerificationDate = "2026-08-20",
            isActive = true
        ),
        ExamBlueprint(
            examId = "RRB_NTPC_2024",
            version = "2024",
            displayName = "RRB NTPC (CBT-1)",
            optionCount = 4,
            positiveMarks = BigDecimal("1.0"),
            negativeMarks = calcOneThirdNegative(BigDecimal("1.0")),
            defaultRelevance = "Foundation",
            recommendedPracticeMode = "Speed + Balanced Practice",
            allowedTiers = listOf("Basic", "Medium"),
            effectiveDate = "2024",
            sourceReference = "RRB NTPC Notification CEN 05/2024",
            lastVerificationDate = "2026-08-20",
            isActive = true
        ),
        ExamBlueprint(
            examId = "RRB_GROUP_D_2024",
            version = "2024",
            displayName = "RRB Group D (CBT)",
            optionCount = 4,
            positiveMarks = BigDecimal("1.0"),
            negativeMarks = calcOneThirdNegative(BigDecimal("1.0")),
            defaultRelevance = "Foundation",
            recommendedPracticeMode = "Foundation + Speed",
            allowedTiers = listOf("Basic"),
            effectiveDate = "2024",
            sourceReference = "RRB Group D Notification CEN 08/2024",
            lastVerificationDate = "2026-08-20",
            isActive = true
        )
    )

    fun getBlueprint(examId: String): ExamBlueprint? {
        return blueprints.find { it.examId == examId }
    }
}
'''

with codecs.open('app/src/main/java/com/example/model/ExamBlueprint.kt', 'w', 'utf-8') as f:
    f.write(content)
