package com.example.repository

data class ConfusionPair(
    val id: String,
    val conceptA: String,
    val conceptB: String,
    val displayNameA: String = conceptA,
    val displayNameB: String = conceptB,
    val descriptionA: String,
    val descriptionB: String,
    val keywordsA: List<String>,
    val keywordsB: List<String>
)

enum class ConfusionEvidenceLevel {
    NONE,
    POSSIBLE_CONFUSION,
    EMERGING_CONFUSION,
    CONFIRMED_CONFUSION,
    CONFIRMED_CONTEXT
}

data class ConfusionDetectionResult(
    val pair: ConfusionPair,
    val evidenceLevel: ConfusionEvidenceLevel
)

object ConfusionNetwork {
    val pairs = listOf(
        ConfusionPair(
            id = "el_nino_la_nina",
            conceptA = "el nino",
            conceptB = "la nina",
            displayNameA = "El Niño",
            displayNameB = "La Niña",
            descriptionA = "Warming of the central/eastern equatorial Pacific. Suppresses Indian Monsoon.",
            descriptionB = "Cooling of the central/eastern equatorial Pacific. Strengthens Indian Monsoon.",
            keywordsA = listOf("el nino", "el niño", "warming", "suppresses monsoon"),
            keywordsB = listOf("la nina", "la niña", "cooling", "strengthens monsoon")
        ),
        ConfusionPair(
            id = "bhabar_terai",
            conceptA = "Bhabar",
            conceptB = "Terai",
            descriptionA = "Porous, gravel-rich plain at foothills where streams disappear.",
            descriptionB = "Marshy, damp region south of Bhabar where streams re-emerge.",
            keywordsA = listOf("bhabar", "porous", "gravel", "disappear"),
            keywordsB = listOf("terai", "tarai", "marshy", "damp", "re-emerge")
        ),
        ConfusionPair(
            id = "fr_dpsp",
            conceptA = "Fundamental Rights",
            conceptB = "Directive Principles",
            descriptionA = "Justiciable. Protects political democracy. Negative obligations on State.",
            descriptionB = "Non-justiciable. Promotes social and economic democracy. Positive obligations.",
            keywordsA = listOf("fundamental rights", "justiciable", "political democracy"),
            keywordsB = listOf("directive principles", "dpsp", "non-justiciable", "social democracy")
        ),
        ConfusionPair(
            id = "khadar_bangar",
            conceptA = "Khadar",
            conceptB = "Bangar",
            descriptionA = "New alluvial soil. Found in lower areas flooded annually. More fertile.",
            descriptionB = "Old alluvial soil. Found in higher terraces. Contains kankar (calcareous nodules).",
            keywordsA = listOf("khadar", "new alluvial", "flooded", "fertile"),
            keywordsB = listOf("bangar", "bhangar", "old alluvial", "kankar")
        )
    )

    fun detectConfusion(questionText: String, selectedOptionText: String): ConfusionDetectionResult? {
        val qText = questionText.lowercase()
        val oText = selectedOptionText.lowercase()

        for (pair in pairs) {
            val qHasA = pair.keywordsA.any { qText.contains(it) }
            val qHasB = pair.keywordsB.any { qText.contains(it) }
            
            val optHasA = pair.keywordsA.any { oText.contains(it) }
            val optHasB = pair.keywordsB.any { oText.contains(it) }

            if ((qHasA && optHasB) || (qHasB && optHasA)) {
                return ConfusionDetectionResult(pair, ConfusionEvidenceLevel.CONFIRMED_CONTEXT)
            } else if ((qHasA || qHasB) && (optHasA || optHasB)) {
                return ConfusionDetectionResult(pair, ConfusionEvidenceLevel.POSSIBLE_CONFUSION)
            } else if (qHasA || qHasB || optHasA || optHasB) {
                 // ONLY ONE KEYWORD -> NO DIAGNOSIS
                 continue
            }
        }
        return null
    }
}
