import codecs

with codecs.open('app/src/main/java/com/example/ui/screens/PracticeScreen.kt', 'r', 'utf-8') as f:
    content = f.read()

ui_update = '''
                        Text(
                            "You scored  out of ",
                            color = deepBlue.copy(alpha = 0.7f),
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Spacer(modifier = Modifier.height(24.dp))
                        
                        if (uiState.marksLostReport.isNotEmpty()) {
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                colors = CardDefaults.cardColors(containerColor = Color.White),
                                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                            ) {
                                Column(modifier = Modifier.padding(16.dp)) {
                                    Text("Marks-Lost Analysis", style = MaterialTheme.typography.titleMedium, color = deepBlue)
                                    Spacer(modifier = Modifier.height(8.dp))
                                    uiState.marksLostReport.forEach { report ->
                                        Text("- ", style = MaterialTheme.typography.bodySmall, color = Color.DarkGray)
                                        Spacer(modifier = Modifier.height(4.dp))
                                    }
                                }
                            }
                            Spacer(modifier = Modifier.height(24.dp))
                        }

'''

# We replace the score display logic and append this
content = content.replace('''Text(
                            "You scored  out of ",
                            color = deepBlue.copy(alpha = 0.7f),
                            fontSize = 18.sp,
                        )''', ui_update) # careful matching!

# Let's match more carefully
old_str = '''Text(
                            "You scored  out of ",
                            color = deepBlue.copy(alpha = 0.7f),
                            fontSize = 18.sp,
                        )'''

# I'll just use Regex
import re
content = re.sub(
    r'Text\(\s*"You scored \$\{uiState\.currentScore\.stripTrailingZeros\(\)\.toPlainString\(\)\} out of \$\{uiState\.totalQuestionsInSet\}",\s*color = deepBlue\.copy\(alpha = 0\.7f\),\s*fontSize = 18\.sp,\s*\)',
    ui_update,
    content
)

with codecs.open('app/src/main/java/com/example/ui/screens/PracticeScreen.kt', 'w', 'utf-8') as f:
    f.write(content)
