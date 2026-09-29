import re
import codecs

with codecs.open("app/src/main/java/com/example/model/ExamBlueprint.kt", "r", "utf-8") as f:
    content = f.read()

# 1. Add PenaltyRule enum
enum_str = """import java.math.RoundingMode

enum class PenaltyRule(val numerator: Long, val denominator: Long) {
    ONE_THIRD(1, 3),
    ONE_FOURTH(1, 4),
    NONE(0, 1)
}"""
content = content.replace("import java.math.RoundingMode", enum_str)

# 2. Update ExamBlueprint class
old_blueprint = """data class ExamBlueprint(
    val examId: String,
    val version: String,
    val displayName: String,
    val optionCount: Int = 4,
    val positiveMarks: BigDecimal = BigDecimal.ONE,
    val negativeMarks: BigDecimal = BigDecimal.ZERO,
    val unansweredPenalty: BigDecimal = BigDecimal.ZERO,"""

new_blueprint = """data class ExamBlueprint(
    val examId: String,
    val version: String,
    val displayName: String,
    val optionCount: Int = 4,
    val positiveMarks: BigDecimal = BigDecimal.ONE,
    val negativePenaltyRule: PenaltyRule = PenaltyRule.NONE,
    val unansweredPenaltyRule: PenaltyRule = PenaltyRule.NONE,"""
content = content.replace(old_blueprint, new_blueprint)

# 3. Replace all calcOneThirdNegative(BigDecimal("X")) with PenaltyRule.ONE_THIRD
content = re.sub(r'negativeMarks = calcOneThirdNegative\([^)]+\)', 'negativePenaltyRule = PenaltyRule.ONE_THIRD', content)
content = re.sub(r'negativeMarks = calcOneFourthNegative\([^)]+\)', 'negativePenaltyRule = PenaltyRule.ONE_FOURTH', content)
content = re.sub(r'unansweredPenalty = calcOneThirdNegative\([^)]+\)', 'unansweredPenaltyRule = PenaltyRule.ONE_THIRD', content)
content = re.sub(r'negativeMarks = BigDecimal\.ZERO', 'negativePenaltyRule = PenaltyRule.NONE', content)
content = re.sub(r'unansweredPenalty = BigDecimal\.ZERO', 'unansweredPenaltyRule = PenaltyRule.NONE', content)

# 4. Remove the helper functions calcOneThirdNegative and calcOneFourthNegative
content = re.sub(r'private fun calcOneThirdNegative.*?\}', '', content, flags=re.DOTALL)
content = re.sub(r'private fun calcOneFourthNegative.*?\}', '', content, flags=re.DOTALL)

with codecs.open("app/src/main/java/com/example/model/ExamBlueprint.kt", "w", "utf-8") as f:
    f.write(content)
