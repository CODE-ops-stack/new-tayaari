import codecs
import re

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'r', 'utf-8') as f:
    content = f.read()

# Make computeScore part of companion object
old_str = '''    private fun computeScore(
        answers: Map<String, String>,
        skipped: Set<String>,
        questions: List<com.example.model.ExamQuestion>,
        profile: com.example.model.ExamBlueprint?
    ): java.math.BigDecimal {'''

new_str = '''    companion object {
        fun computeScore(
            answers: Map<String, String>,
            skipped: Set<String>,
            questions: List<com.example.model.ExamQuestion>,
            profile: com.example.model.ExamBlueprint?
        ): java.math.BigDecimal {'''

# Find the end of computeScore block. 
# It's at the end of the file. The file ends with:
#                 score = score.subtract(unansweredPen)
#             }
#         }
#         return score
#     }
# }

content = content.replace(old_str, new_str)
content = content.replace('        return score\n    }\n}', '        return score\n    }\n    }\n}')

with codecs.open('app/src/main/java/com/example/viewmodel/PracticeViewModel.kt', 'w', 'utf-8') as f:
    f.write(content)
