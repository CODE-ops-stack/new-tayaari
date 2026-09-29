import re

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "r", encoding="utf-8") as f:
    text = f.read()

prefix = text.split("    // CONFIDENCE CALIBRATION UI")[0]

suffix = """    // CONFIDENCE CALIBRATION UI
        AnimatedVisibility(visible = pendingOptionId != null && selectedOptionId == null) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 16.dp)
                    .background(deepBlue.copy(alpha = 0.05f), RoundedCornerShape(12.dp))
                    .border(1.dp, deepBlue.copy(alpha = 0.1f), RoundedCornerShape(12.dp))
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "How confident are you?",
                    color = deepBlue,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    val confidences = listOf("Certain", "Likely", "Unsure", "Guessing")
                    confidences.forEach { conf ->
                        Button(
                            onClick = { onSubmitAnswerWithConfidence(conf) },
                            colors = ButtonDefaults.buttonColors(containerColor = deepBlue),
                            shape = RoundedCornerShape(8.dp),
                            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 8.dp)
                        ) {
                            Text(text = conf, fontSize = 12.sp)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun FeedbackBox(title: String, message: String, color: Color, bgColor: Color) {
    Surface(
        color = bgColor,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, color.copy(alpha = 0.3f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.Top
        ) {
            Icon(
                Icons.Default.Lightbulb,
                contentDescription = null,
                tint = color,
                modifier = Modifier.size(20.dp).padding(top = 2.dp)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column {
                Text(
                    text = title,
                    color = color,
                    fontWeight = FontWeight.Black,
                    fontSize = 12.sp,
                    letterSpacing = 1.sp
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = message,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f),
                    fontSize = 14.sp,
                    lineHeight = 20.sp
                )
            }
        }
    }
}
"""

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "w", encoding="utf-8") as f:
    f.write(prefix + suffix)

print("Fixed!")
