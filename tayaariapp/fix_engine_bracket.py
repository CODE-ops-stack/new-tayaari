import codecs

with codecs.open('app/src/main/java/com/example/repository/QuestionSelectionEngine.kt', 'r', 'utf-8') as f:
    content = f.read()

import re

# We want to fix this block:
#                // Revision Due
#
#                // Revision Due
#                if (revisionItem.nextRevisionDate < System.currentTimeMillis()) {
#                    score += 25.0 // Huge boost if revision is due
#                }
#                }

content = content.replace("""                // Revision Due\n\n                // Revision Due\n                if (revisionItem.nextRevisionDate < System.currentTimeMillis()) {\n                    score += 25.0 // Huge boost if revision is due\n                }\n                }""", """                // Revision Due\n                if (revisionItem.nextRevisionDate < System.currentTimeMillis()) {\n                    score += 25.0 // Huge boost if revision is due\n                }""")


with codecs.open('app/src/main/java/com/example/repository/QuestionSelectionEngine.kt', 'w', 'utf-8') as f:
    f.write(content)
