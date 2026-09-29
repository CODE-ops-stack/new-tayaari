fun testStatementBasedContent(text: String) {
    val lines = text.lines()
    val statements = mutableListOf<String>()
    var mainQuestion = ""
    var trailingQuestion = ""
    var inStatements = false
    
    val statementRegex = Regex("^(?:\\*?\\*?)?(?:[IVXivx]+|\\d+|[a-d])[.)](?:\\*?\\*?)?\\s+(.*)")
    
    for (line in lines) {
        val trimmed = line.trim()
        if (trimmed.isEmpty()) continue
        
        val match = statementRegex.find(trimmed)
        if (match != null) {
            statements.add(trimmed)
            inStatements = true
        } else {
            if (!inStatements) {
                mainQuestion += trimmed + "\n"
            } else {
                val lower = trimmed.lowercase()
                if (lower.startsWith("which") || lower.startsWith("choose") || lower.startsWith("select") || lower.contains("is/are correct") || lower.contains("are correct") || lower.contains("is correct")) {
                    trailingQuestion += trimmed + "\n"
                } else if (trailingQuestion.isNotEmpty()) {
                    trailingQuestion += trimmed + "\n"
                } else {
                    val lastIdx = statements.lastIndex
                    if (lastIdx >= 0) {
                        statements[lastIdx] = statements[lastIdx] + " " + trimmed
                    } else {
                        mainQuestion += trimmed + "\n"
                    }
                }
            }
        }
    }
    
    println("Main Question:\n" + mainQuestion.trim())
    println("Statements:")
    statements.forEach { println(" - " + it) }
    println("Trailing Question:\n" + trailingQuestion.trim())
    println("---")
}

fun main() {
    val q25 = """Q25. Consider the following statements:
1. Gujarat has the largest solar park in India.
2. Kerala has a fully solar powered International Airport.
3. Goa has the largest ﬂoating solar photovoltaic project in India.
Which of the statements given above is/are correct?"""

    val q86 = """Q86. Consider the following statements:
1. The Barren Island volcano is an active volcano located in Indian territory.
2. Barren Island lies about 140 km east of Great Nicobar.
3. The last time the Barren Island volcano erupted was in 1991 and it has remained
inactive since then.
Which of the statements given above is/are correct?"""

    testStatementBasedContent(q25)
    testStatementBasedContent(q86)
}

main()
