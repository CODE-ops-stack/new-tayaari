import codecs

with codecs.open('app/src/main/java/com/example/ui/screens/ResultsScreen.kt', 'r', 'utf-8') as f:
    content = f.read()

content = content.replace(
    "score: Int,",
    "score: java.math.BigDecimal,"
)

content = content.replace(
    "fun ScoreHeader(score: Int, total: Int, textColor: Color)",
    "fun ScoreHeader(score: java.math.BigDecimal, total: Int, textColor: Color)"
)

content = content.replace(
    'text = "$score / $total",',
    'text = "${score.setScale(2, java.math.RoundingMode.HALF_UP).stripTrailingZeros().toPlainString()} / $total",'
)

content = content.replace(
    'val percentage = if (total > 0) (score.toFloat() / total * 100).toInt() else 0',
    'val percentage = if (total > 0) (score.toFloat() / total * 100).toInt() else 0'
)

with codecs.open('app/src/main/java/com/example/ui/screens/ResultsScreen.kt', 'w', 'utf-8') as f:
    f.write(content)
