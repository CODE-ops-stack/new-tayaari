file = 'app/src/test/java/com/example/viewmodel/PracticeScoringRegressionTest.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

import_exact = "import com.example.model.ExactFraction\n"
if "ExactFraction" not in text:
    text = text.replace("import com.example.model.ExamBlueprint", import_exact + "import com.example.model.ExamBlueprint")

text = text.replace('assertEquals(0, BigDecimal("10").compareTo(scoreA))', 'assertEquals(ExactFraction(10, 1), scoreA)')
text = text.replace('val expectedB = BigDecimal("-10").divide(BigDecimal("3"), MathContext.DECIMAL128)\n        assertEquals(0, expectedB.compareTo(scoreB))', 'assertEquals(ExactFraction(-10, 3), scoreB)')
text = text.replace('assertEquals(0, BigDecimal.ZERO.compareTo(scoreC))', 'assertEquals(ExactFraction.ZERO, scoreC)')
text = text.replace('assertEquals(0, BigDecimal.ZERO.compareTo(scoreD))', 'assertEquals(ExactFraction.ZERO, scoreD)')
text = text.replace('val expectedE = BigDecimal("16").divide(BigDecimal("3"), MathContext.DECIMAL128)\n        assertEquals(0, expectedE.compareTo(scoreE))', 'assertEquals(ExactFraction(16, 3), scoreE)')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
