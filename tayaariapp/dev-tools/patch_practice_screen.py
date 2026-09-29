with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "r") as f:
    content = f.read()

import re

# We will modify QuestionCard to format text beautifully based on format type
question_card_code = """@Composable
fun QuestionCard(
    question: ExamQuestion,
    isBookmarked: Boolean,
    onBookmarkClick: () -> Unit
) {
    val mcqQuestion = question as? MCQQuestion
    val format = mcqQuestion?.questionFormatType ?: "Direct Fact"

    Surface(
        color = MaterialTheme.colorScheme.surface,
        shape = RoundedCornerShape(16.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .background(MaterialTheme.colorScheme.primary.copy(alpha = 0.1f), RoundedCornerShape(4.dp))
                            .padding(horizontal = 6.dp, vertical = 2.dp)
                    ) {
                        Text(
                            text = format,
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.primary,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = question.chapterCode,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f),
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
                Icon(
                    imageVector = if (isBookmarked) Icons.Filled.Bookmark else Icons.Filled.BookmarkBorder,
                    contentDescription = "Bookmark",
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.clickable { onBookmarkClick() }
                )
            }
            Spacer(modifier = Modifier.height(16.dp))
            
            // Format specific rendering
            when (format) {
                "Assertion-Reason" -> AssertionReasonContent(question.questionText)
                "Statement-based" -> StatementBasedContent(question.questionText)
                "Matching Pairs" -> MatchingPairsContent(question.questionText)
                else -> {
                    Text(
                        text = question.questionText,
                        color = MaterialTheme.colorScheme.onBackground,
                        fontSize = 18.sp,
                        fontWeight = FontWeight.Medium,
                        lineHeight = 24.sp
                    )
                }
            }
        }
    }
}

@Composable
fun AssertionReasonContent(text: String) {
    // Attempt to split into Assertion and Reason parts
    val parts = text.split(Regex("(?i)Reason \\\\(R\\\\):|Reason:|R:"))
    if (parts.size == 2) {
        val assertionPart = parts[0].replace(Regex("(?i)Assertion \\\\(A\\\\):|Assertion:|A:"), "").trim()
        val reasonPart = parts[1].trim()
        
        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Surface(color = Color(0xFFF0F4F8), shape = RoundedCornerShape(8.dp)) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("Assertion (A)", fontWeight = FontWeight.Bold, color = Color(0xFF1B3B5A), fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(assertionPart, fontSize = 16.sp, lineHeight = 22.sp)
                }
            }
            Surface(color = Color(0xFFF9F0EB), shape = RoundedCornerShape(8.dp)) {
                Column(modifier = Modifier.padding(12.dp)) {
                    Text("Reason (R)", fontWeight = FontWeight.Bold, color = Color(0xFFE07A5F), fontSize = 14.sp)
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(reasonPart, fontSize = 16.sp, lineHeight = 22.sp)
                }
            }
        }
    } else {
        Text(text, fontSize = 18.sp, lineHeight = 24.sp)
    }
}

@Composable
fun StatementBasedContent(text: String) {
    // Look for numbered statements like "1. statement" or "1) statement"
    val lines = text.lines()
    val statements = mutableListOf<String>()
    var mainQuestion = ""
    
    val statementRegex = Regex("^\\\\d+[.)]\\\\s*(.*)")
    
    for (line in lines) {
        val match = statementRegex.find(line.trim())
        if (match != null) {
            statements.add(line.trim())
        } else {
            mainQuestion += line + "\\n"
        }
    }
    
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        if (mainQuestion.trim().isNotEmpty()) {
            Text(mainQuestion.trim(), fontSize = 18.sp, fontWeight = FontWeight.Medium, lineHeight = 24.sp)
        }
        
        if (statements.isNotEmpty()) {
            Surface(
                border = BorderStroke(1.dp, Color.LightGray),
                shape = RoundedCornerShape(8.dp),
                color = Color.White
            ) {
                Column(modifier = Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    statements.forEach { stmt ->
                        Row {
                            Text("•", modifier = Modifier.padding(end = 8.dp), color = MaterialTheme.colorScheme.primary)
                            Text(stmt, fontSize = 16.sp, lineHeight = 22.sp)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun MatchingPairsContent(text: String) {
    // Render similarly to statement based but maybe side-by-side or clear list
    StatementBasedContent(text) // We can reuse statement parsing since pairs are usually listed 1. X - Y
}
"""

content = re.sub(r'@Composable\nfun QuestionCard.*?\{.*?\n\}\n\}', question_card_code, content, flags=re.DOTALL)

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "w") as f:
    f.write(content)
