import codecs
with codecs.open('app/src/main/java/com/example/ui/screens/PracticeScreen.kt', 'r', 'utf-8') as f:
    lines = f.readlines()

def fix_options(lines):
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if 'val isSelected = selectedOptionId == option.id' in line:
            new_lines.append(line)
            new_lines.append('              val isPending = pendingOptionId == option.id\n')
        elif 'isAnswerSubmitted && isCorrect -> successGreen.copy(alpha = 0.5f)' in line:
            new_lines.append(line)
            new_lines.append('                  isPending -> deepBlue\n')
        elif 'isAnswerSubmitted && isSelected && !isCorrect -> errorRed.copy(alpha = 0.05f)' in line:
            new_lines.append(line)
            new_lines.append('                  isPending -> deepBlue.copy(alpha = 0.1f)\n')
        elif 'border = if (isAnswerSubmitted && (isSelected || isCorrect)) BorderStroke(2.dp,' in line:
            new_lines.append(line.replace('if (isAnswerSubmitted && (isSelected || isCorrect))', 'if ((isAnswerSubmitted && (isSelected || isCorrect)) || isPending)'))
        else:
            new_lines.append(line)
        i += 1
    return new_lines

lines = fix_options(lines)
with codecs.open('app/src/main/java/com/example/ui/screens/PracticeScreen.kt', 'w', 'utf-8') as f:
    f.writelines(lines)
