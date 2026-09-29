with open("app/src/main/java/com/example/ui/screens/ResultsScreen.kt", "r") as f:
    content = f.read()

import re

# Update ReviewCard signature
old_sig = """@Composable
fun ReviewCard(
    question: MCQQuestion,
    userAnswerId: String?,
    isCorrect: Boolean,
    deepOceanBlue: Color,
    forestGreen: Color,
    terracotta: Color
)"""

new_sig = """@Composable
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

content = content.replace(old_sig, new_sig)

# Update ReviewCard content to add bookmark icon
old_card_content = """        Column(modifier = Modifier.padding(16.dp)) {
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

new_card_content = """        Column(modifier = Modifier.padding(16.dp)) {
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

content = content.replace(old_card_content, new_card_content)

# Add imports for Bookmark icons
if "import androidx.compose.material.icons.filled.Bookmark" not in content:
    content = content.replace("import androidx.compose.material.icons.filled.CheckCircle", "import androidx.compose.material.icons.filled.CheckCircle\nimport androidx.compose.material.icons.filled.Bookmark\nimport androidx.compose.material.icons.filled.BookmarkBorder")

if "import androidx.compose.foundation.clickable" not in content:
    content = content.replace("import androidx.compose.ui.Modifier", "import androidx.compose.ui.Modifier\nimport androidx.compose.foundation.clickable")
    
if "import androidx.compose.material3.IconButton" not in content:
    content = content.replace("import androidx.compose.material3.*", "import androidx.compose.material3.*\nimport androidx.compose.material3.IconButton")

with open("app/src/main/java/com/example/ui/screens/ResultsScreen.kt", "w") as f:
    f.write(content)
