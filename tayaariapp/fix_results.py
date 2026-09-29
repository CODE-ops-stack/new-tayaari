import codecs

with codecs.open('app/src/main/java/com/example/ui/screens/ResultsScreen.kt', 'r', 'utf-8') as f:
    content = f.read()

# Fix ElevationProfileVisualization
elevation_old = '''                    val isCorrect = mcq != null && userAnswers[mcq.id] == mcq.correctAnswerId
                    val isSkipped = mcq != null && userAnswers[mcq.id] == null
                    
                    val barColor = when {
                        isSkipped -> Color.LightGray
                        isCorrect -> forestGreen
                        else -> terracotta
                    }
                    val height = if (isCorrect) 60.dp else if (isSkipped) 20.dp else 10.dp'''

elevation_new = '''                    val ans = userAnswers[mcq?.id]
                    val isSkipped = mcq != null && ans == null
                    val option = mcq?.options?.find { it.id == ans }
                    val isAbstain = option?.role == com.example.model.OptionRole.ABSTAIN
                    val isCorrect = mcq != null && ans == mcq.correctAnswerId
                    
                    val barColor = when {
                        isSkipped -> Color.LightGray
                        isAbstain -> Color.Gray
                        isCorrect -> forestGreen
                        else -> terracotta
                    }
                    val height = if (isCorrect) 60.dp else if (isAbstain) 30.dp else if (isSkipped) 20.dp else 10.dp'''

content = content.replace(elevation_old, elevation_new)

# Fix BreakdownSection
breakdown_old = '''    questions.forEach { q ->
        val mcq = q as? MCQQuestion
        if (mcq != null) {
            val isCorrect = userAnswers[mcq.id] == mcq.correctAnswerId
            val format = mcq.questionFormatType
            
            val current = formatStats.getOrDefault(format, Pair(0, 0))
            formatStats[format] = Pair(
                current.first + (if (isCorrect) 1 else 0),
                current.second + 1
            )
        }
    }'''

breakdown_new = '''    questions.forEach { q ->
        val mcq = q as? MCQQuestion
        if (mcq != null) {
            val ans = userAnswers[mcq.id]
            val option = mcq.options.find { it.id == ans }
            val isAbstain = option?.role == com.example.model.OptionRole.ABSTAIN
            val isSkipped = ans == null
            
            if (!isAbstain && !isSkipped) {
                val isCorrect = ans == mcq.correctAnswerId
                val format = mcq.questionFormatType
                
                val current = formatStats.getOrDefault(format, Pair(0, 0))
                formatStats[format] = Pair(
                    current.first + (if (isCorrect) 1 else 0),
                    current.second + 1
                )
            }
        }
    }'''

content = content.replace(breakdown_old, breakdown_new)

with codecs.open('app/src/main/java/com/example/ui/screens/ResultsScreen.kt', 'w', 'utf-8') as f:
    f.write(content)
