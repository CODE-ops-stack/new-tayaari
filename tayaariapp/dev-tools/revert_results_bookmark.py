with open("app/src/main/java/com/example/ui/screens/ResultsScreen.kt", "r") as f:
    content = f.read()

import re

old_sig = """@Composable
fun ReviewCard(
    question: MCQQuestion,
    userAnswerId: String?,
    isCorrect: Boolean,
    deepOceanBlue: Color,
    forestGreen: Color,
    terracotta: Color,
    isBookmarked: Boolean,
    onBookmarkToggle: () -> Unit
)"""

new_sig = """@Composable
fun ReviewCard(
    question: MCQQuestion,
    userAnswerId: String?,
    isCorrect: Boolean,
    deepOceanBlue: Color,
    forestGreen: Color,
    terracotta: Color
)"""

content = content.replace(old_sig, new_sig)

old_card_content = """        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = if (isCorrect) Icons.Filled.CheckCircle else Icons.Filled.Cancel,
                        contentDescription = if (isCorrect) "Correct" else "Incorrect",
                        tint = if (isCorrect) forestGreen else terracotta
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "Format: ${question.questionFormatType}",
                        style = MaterialTheme.typography.labelSmall,
                        color = Color.Gray
                    )
                }
                IconButton(onClick = onBookmarkToggle, modifier = Modifier.size(24.dp)) {
                    Icon(
                        imageVector = if (isBookmarked) Icons.Filled.Bookmark else Icons.Filled.BookmarkBorder,
                        contentDescription = "Toggle Bookmark",
                        tint = deepOceanBlue
                    )
                }
            }"""

new_card_content = """        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = if (isCorrect) Icons.Filled.CheckCircle else Icons.Filled.Cancel,
                    contentDescription = if (isCorrect) "Correct" else "Incorrect",
                    tint = if (isCorrect) forestGreen else terracotta
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Format: ${question.questionFormatType}",
                    style = MaterialTheme.typography.labelSmall,
                    color = Color.Gray
                )
            }"""

content = content.replace(old_card_content, new_card_content)

# We also need to remove the added parameters when ReviewCard is called
# In items(questions) loop
call_old = """                    ReviewCard(
                        question = mcq,
                        userAnswerId = userAnswerId,
                        isCorrect = isCorrect,
                        deepOceanBlue = deepOceanBlue,
                        forestGreen = forestGreen,
                        terracotta = terracotta,
                        isBookmarked = false, // WE PROBABLY MISSED THIS ANYWAY! Wait, I didn't even patch the caller!
                        onBookmarkToggle = {} // WE PROBABLY MISSED THIS ANYWAY!
                    )"""
                    
# Wait, I didn't even patch the caller in the previous python script! 
# So it wouldn't have compiled anyway.

with open("app/src/main/java/com/example/ui/screens/ResultsScreen.kt", "w") as f:
    f.write(content)
