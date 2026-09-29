with open("app/src/main/java/com/example/repository/ConfusionNetwork.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("enum class ConfusionEvidenceLevel {\n    NONE,\n    POSSIBLE_CONFUSION,\n    CONFIRMED_CONTEXT\n}",
"enum class ConfusionEvidenceLevel {\n    NONE,\n    POSSIBLE_CONFUSION,\n    EMERGING_CONFUSION,\n    CONFIRMED_CONFUSION,\n    CONFIRMED_CONTEXT\n}")

content = content.replace(
"""data class ConfusionPair(
    val id: String,
    val conceptA: String,
    val conceptB: String,
    val descriptionA: String,
    val descriptionB: String,
    val keywordsA: List<String>,
    val keywordsB: List<String>
)""",
"""data class ConfusionPair(
    val id: String,
    val conceptA: String,
    val conceptB: String,
    val displayNameA: String = conceptA,
    val displayNameB: String = conceptB,
    val descriptionA: String,
    val descriptionB: String,
    val keywordsA: List<String>,
    val keywordsB: List<String>
)"""
)

content = content.replace(
"""        ConfusionPair(
            id = "el_nino_la_nina",
            conceptA = "El Nio",
            conceptB = "La Nia",
            descriptionA = "Warming of the central/eastern equatorial Pacific. Suppresses Indian Monsoon.",
            descriptionB = "Cooling of the central/eastern equatorial Pacific. Strengthens Indian Monsoon.",
            keywordsA = listOf("el nino", "warming", "suppresses monsoon"),
            keywordsB = listOf("la nina", "cooling", "strengthens monsoon")
        ),""",
"""        ConfusionPair(
            id = "el_nino_la_nina",
            conceptA = "el nino",
            conceptB = "la nina",
            displayNameA = "El Niño",
            displayNameB = "La Niña",
            descriptionA = "Warming of the central/eastern equatorial Pacific. Suppresses Indian Monsoon.",
            descriptionB = "Cooling of the central/eastern equatorial Pacific. Strengthens Indian Monsoon.",
            keywordsA = listOf("el nino", "el niño", "warming", "suppresses monsoon"),
            keywordsB = listOf("la nina", "la niña", "cooling", "strengthens monsoon")
        ),"""
)

with open("app/src/main/java/com/example/repository/ConfusionNetwork.kt", "w", encoding="utf-8") as f:
    f.write(content)
