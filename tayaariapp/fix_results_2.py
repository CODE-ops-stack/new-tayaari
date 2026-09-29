import codecs
import re

with codecs.open('app/src/main/java/com/example/ui/screens/ResultsScreen.kt', 'r', 'utf-8') as f:
    content = f.read()

# Replace if (isCorrect) forestGreen else terracotta with borderColor
content = content.replace(
    'color = if (isCorrect) forestGreen else terracotta,',
    'color = borderColor,'
)

# Replace if (!isCorrect) { with if (outcome != com.example.model.AttemptOutcome.CORRECT) {
content = content.replace(
    'if (!isCorrect) {',
    'if (outcome != com.example.model.AttemptOutcome.CORRECT) {'
)

# Any other usages of isCorrect?
# Let's check for any remaining 'isCorrect' in the ReviewCard.
# The previous errors were at 310, 322, 335.
# 310: color = if (isCorrect) forestGreen else terracotta, -> Replaced with color = borderColor,
# 322: if (!isCorrect) { -> Replaced with if (outcome != com.example.model.AttemptOutcome.CORRECT) {
# 335: if (!isCorrect) { -> Wait, is there another one?
# Let's replace ALL remaining 'isCorrect' in the file with 'outcome == com.example.model.AttemptOutcome.CORRECT' where appropriate? No, wait. 
# There is `val isCorrect = ans == mcq.correctAnswerId` inside BreakdownSection. That is a local variable, so it shouldn't be an unresolved reference!

with codecs.open('app/src/main/java/com/example/ui/screens/ResultsScreen.kt', 'w', 'utf-8') as f:
    f.write(content)
