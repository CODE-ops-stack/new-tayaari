with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    "detectedConfusionPair: com.example.repository.ConfusionPair? = null,",
    "detectedConfusionPair: com.example.repository.ConfusionDetectionResult? = null,"
)

old_ui_block = """    // CONFUSION PAIR DISAMBIGUATION
        detectedConfusionPair?.let { pair ->
            AnimatedVisibility(visible = true) {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(top = 16.dp)
                        .background(Color(0xFFFFF8E1), RoundedCornerShape(12.dp))
                        .border(1.dp, Color(0xFFFFC107), RoundedCornerShape(12.dp))
                        .padding(16.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Filled.CompareArrows, contentDescription = "Confusion Pair", tint = Color(0xFFF57C00))
                        Spacer(modifier = Modifier.width(8.dp))
                        Text("Confusion Detected", fontWeight = FontWeight.Bold, color = Color(0xFFF57C00))
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                    Text("It seems you might be confusing two related concepts. Let's disambiguate:", fontSize = 14.sp, color = Color.DarkGray)
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Column(modifier = Modifier.weight(1f)) {
                            Text(pair.conceptA, fontWeight = FontWeight.Bold, color = deepBlue)
                            Text(pair.descriptionA, fontSize = 13.sp, color = Color.Gray)
                        }
                        Spacer(modifier = Modifier.width(16.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(pair.conceptB, fontWeight = FontWeight.Bold, color = deepBlue)
                            Text(pair.descriptionB, fontSize = 13.sp, color = Color.Gray)
                        }
                    }
                }
            }
        }"""

new_ui_block = """    // CONFUSION PAIR DISAMBIGUATION
        detectedConfusionPair?.let { result ->
            val pair = result.pair
            val evidenceLevel = result.evidenceLevel
            
            val (titleText, color) = when (evidenceLevel) {
                com.example.repository.ConfusionEvidenceLevel.CONFIRMED_CONTEXT -> "Recurring Confusion" to Color(0xFFD32F2F)
                com.example.repository.ConfusionEvidenceLevel.POSSIBLE_CONFUSION -> "Possible Confusion" to Color(0xFFF57C00)
                else -> "None" to Color.Transparent
            }

            if (evidenceLevel != com.example.repository.ConfusionEvidenceLevel.NONE) {
                AnimatedVisibility(visible = true) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 16.dp)
                            .background(Color(0xFFFFF8E1), RoundedCornerShape(12.dp))
                            .border(1.dp, color, RoundedCornerShape(12.dp))
                            .padding(16.dp)
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Filled.CompareArrows, contentDescription = "Confusion Pair", tint = color)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(titleText, fontWeight = FontWeight.Bold, color = color)
                        }
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("It seems you might be confusing two related concepts. Let's disambiguate:", fontSize = 14.sp, color = Color.DarkGray)
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(pair.conceptA, fontWeight = FontWeight.Bold, color = deepBlue)
                                Text(pair.descriptionA, fontSize = 13.sp, color = Color.Gray)
                            }
                            Spacer(modifier = Modifier.width(16.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(pair.conceptB, fontWeight = FontWeight.Bold, color = deepBlue)
                                Text(pair.descriptionB, fontSize = 13.sp, color = Color.Gray)
                            }
                        }
                    }
                }
            }
        }"""

if old_ui_block in content:
    content = content.replace(old_ui_block, new_ui_block)
else:
    print("Could not find the UI block!")

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "w", encoding="utf-8") as f:
    f.write(content)
