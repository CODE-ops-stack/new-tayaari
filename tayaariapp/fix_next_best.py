file = 'app/src/main/java/com/example/repository/NextBestActionEngine.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val confirmedConfusion = profile.activeConfusions.find { it.evidenceLevel == "CONFIRMED_CONFUSION" }
        if (confirmedConfusion != null) {
            return@withContext RecommendedAction.Contrast(
                conceptA = confirmedConfusion.conceptA,
                conceptB = confirmedConfusion.conceptB,
                reason = "You have a confirmed confusion between \'${confirmedConfusion.conceptA}\' and \'${confirmedConfusion.conceptB}\'. Contrast Lab will fix this.",', 'val confirmedConfusion = profile.activeConfusions.find { it.evidenceLevel == "CONFIRMED_CONFUSION" }
        if (confirmedConfusion != null) {
            val parts = confirmedConfusion.pairId.split("_")
            val cA = if (parts.isNotEmpty()) parts[0] else "A"
            val cB = if (parts.size > 1) parts[1] else "B"
            return@withContext RecommendedAction.Contrast(
                conceptA = cA,
                conceptB = cB,
                reason = "You have a confirmed confusion between \'${cA}\' and \'${cB}\'. Contrast Lab will fix this.",')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
