with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "r", encoding="utf-8") as f:
    content = f.read()

replacement = """            val (titleText, color) = when (evidenceLevel) {
                com.example.repository.ConfusionEvidenceLevel.CONFIRMED_CONFUSION -> "Recurring confusion" to Color(0xFFD32F2F)
                com.example.repository.ConfusionEvidenceLevel.CONFIRMED_CONTEXT -> "Recurring confusion" to Color(0xFFD32F2F)
                com.example.repository.ConfusionEvidenceLevel.EMERGING_CONFUSION -> "Pattern emerging" to Color(0xFFF57C00)
                com.example.repository.ConfusionEvidenceLevel.POSSIBLE_CONFUSION -> "Possible confusion" to Color(0xFFFBC02D)
                else -> "None" to Color.Transparent
            }"""

content = content.replace(
    '            val (titleText, color) = when (evidenceLevel) {\n                com.example.repository.ConfusionEvidenceLevel.CONFIRMED_CONTEXT -> "Recurring Confusion" to Color(0xFFD32F2F)\n                com.example.repository.ConfusionEvidenceLevel.POSSIBLE_CONFUSION -> "Possible Confusion" to Color(0xFFF57C00)\n                else -> "None" to Color.Transparent\n            }',
    replacement
)

content = content.replace('pair.conceptA', 'pair.displayNameA')
content = content.replace('pair.conceptB', 'pair.displayNameB')

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "w", encoding="utf-8") as f:
    f.write(content)
