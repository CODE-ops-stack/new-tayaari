import codecs

with codecs.open('app/src/main/java/com/example/ui/screens/ResultsScreen.kt', 'r', 'utf-8') as f:
    content = f.read()

caller_old = '''                if (mcq != null) {
                    val userAnswerId = userAnswers[mcq.id]
                    val isCorrect = userAnswerId == mcq.correctAnswerId
                    ReviewCard(
                        question = mcq,
                        userAnswerId = userAnswerId,
                        isCorrect = isCorrect,
                        deepOceanBlue = deepOceanBlue,
                        forestGreen = forestGreen,
                        terracotta = terracotta
                    )
                }'''

caller_new = '''                if (mcq != null) {
                    val userAnswerId = userAnswers[mcq.id]
                    val isSkipped = userAnswerId == null
                    val opt = mcq.options.find { it.id == userAnswerId }
                    val isAbstain = opt?.role == com.example.model.OptionRole.ABSTAIN
                    
                    val outcome = when {
                        isSkipped -> com.example.model.AttemptOutcome.UNANSWERED
                        isAbstain -> com.example.model.AttemptOutcome.ABSTAINED
                        userAnswerId == mcq.correctAnswerId -> com.example.model.AttemptOutcome.CORRECT
                        else -> com.example.model.AttemptOutcome.INCORRECT
                    }

                    ReviewCard(
                        question = mcq,
                        userAnswerId = userAnswerId,
                        outcome = outcome,
                        deepOceanBlue = deepOceanBlue,
                        forestGreen = forestGreen,
                        terracotta = terracotta
                    )
                }'''

content = content.replace(caller_old, caller_new)

reviewcard_old = '''fun ReviewCard(
    question: MCQQuestion,
    userAnswerId: String?,
    isCorrect: Boolean,
    deepOceanBlue: Color,
    forestGreen: Color,
    terracotta: Color
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        border = BorderStroke(1.dp, if (isCorrect) forestGreen else terracotta),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = if (isCorrect) Icons.Filled.CheckCircle else Icons.Filled.Cancel,
                    contentDescription = if (isCorrect) "Correct" else "Incorrect",
                    tint = if (isCorrect) forestGreen else terracotta
                )'''

reviewcard_new = '''fun ReviewCard(
    question: MCQQuestion,
    userAnswerId: String?,
    outcome: com.example.model.AttemptOutcome,
    deepOceanBlue: Color,
    forestGreen: Color,
    terracotta: Color
) {
    val borderColor = when (outcome) {
        com.example.model.AttemptOutcome.CORRECT -> forestGreen
        com.example.model.AttemptOutcome.INCORRECT -> terracotta
        com.example.model.AttemptOutcome.ABSTAINED -> Color.Gray
        com.example.model.AttemptOutcome.UNANSWERED -> Color.LightGray
    }
    val icon = when (outcome) {
        com.example.model.AttemptOutcome.CORRECT -> Icons.Filled.CheckCircle
        com.example.model.AttemptOutcome.ABSTAINED -> Icons.Filled.RemoveCircleOutline
        else -> Icons.Filled.Cancel
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        border = BorderStroke(1.dp, borderColor),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = icon,
                    contentDescription = outcome.name,
                    tint = borderColor
                )'''

content = content.replace(reviewcard_old, reviewcard_new)

with codecs.open('app/src/main/java/com/example/ui/screens/ResultsScreen.kt', 'w', 'utf-8') as f:
    f.write(content)
