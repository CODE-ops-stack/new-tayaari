file = 'app/src/main/java/com/example/model/TestModels.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('val currentScore: java.math.BigDecimal = java.math.BigDecimal.ZERO', 'val currentScore: ExactFraction = ExactFraction.ZERO')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
