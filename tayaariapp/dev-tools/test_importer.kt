package dev.tools
import java.io.File
import java.util.regex.Pattern

fun main() {
    val mdContent = File("source-material/consolidated_grounding.md").readText()
    val blocks = mdContent.split(Regex("\\r?\\n## (?=\\d+\\. )"))
    
    var count = 0
    for (i in 1 until blocks.size) {
        val block = blocks[i]
        val qPattern = Pattern.compile(
            "- \\*\\*Topic\\*\\*: (.*?)\\r?\\n" +
            "- \\*\\*Tier\\*\\*: (.*?)\\r?\\n" +
            "- \\*\\*Format\\*\\*: (.*?)\\r?\\n" +
            "- \\*\\*Exam-Relevance\\*\\*: (.*?)\\r?\\n" +
            "- \\*\\*Source\\*\\*: (.*?)\\r?\\n" +
            "- \\*\\*Specific-Exam\\*\\*: (.*?)\\r?\\n" +
            "(?:- \\*\\*Trap-Type\\*\\*: (.*?)\\r?\\n)?" + 
            "- \\*\\*PDF-Sequence-Number\\*\\*: (.*?)\\r?\\n" +
            "- \\*\\*Question\\*\\*:\\r?\\n```\\r?\\n(.*?)\\r?\\n```", Pattern.DOTALL
        )
        
        val matcher = qPattern.matcher(block)
        while (matcher.find()) {
            val rawQText = matcher.group(9)?.trim() ?: ""
            var qText = rawQText
            var optionsStr = "[]"
            var correctAnswerStr = "opt_a"
            
            val ansMatcher = java.util.regex.Pattern.compile("(?i)Correct [Aa]nswer:\\s*(?:Option\\s*)?([a-d])").matcher(rawQText)
            if (ansMatcher.find()) {
                correctAnswerStr = "opt_" + ansMatcher.group(1).lowercase().trim()
            }
            
            val optionsPattern = java.util.regex.Pattern.compile(
                "(?s)(.*?)\\s*\\(?[aA]\\)[ )\\.](.*?)\\s*\\(?[bB]\\)[ )\\.](.*?)\\s*\\(?[cC]\\)[ )\\.](.*?)\\s*\\(?[dD]\\)[ )\\.](.*)"
            )
            val optMatcher = optionsPattern.matcher(rawQText)
            if (optMatcher.find()) {
                qText = optMatcher.group(1)?.trim() ?: rawQText
                val optA = optMatcher.group(2)?.trim()?.replace("\"", "\\\"")?.replace("\n", " ") ?: ""
                val optB = optMatcher.group(3)?.trim()?.replace("\"", "\\\"")?.replace("\n", " ") ?: ""
                val optC = optMatcher.group(4)?.trim()?.replace("\"", "\\\"")?.replace("\n", " ") ?: ""
                var optD = optMatcher.group(5)?.trim()?.replace("\"", "\\\"")?.replace("\n", " ") ?: ""
                
                val caRegex = Regex("(?i)\\s*Correct [Aa]nswer:.*")
                optD = optD.replace(caRegex, "").trim()
                
                optionsStr = "[{\"id\":\"opt_a\",\"text\":\"" + optA + "\"},{\"id\":\"opt_b\",\"text\":\"" + optB + "\"},{\"id\":\"opt_c\",\"text\":\"" + optC + "\"},{\"id\":\"opt_d\",\"text\":\"" + optD + "\"}]"
            }
            
            println("Question:")
            println("  Text: $qText")
            println("  Options: $optionsStr")
            println("  Correct: $correctAnswerStr")
            println("--------------------------")
            count++
            if (count >= 3) return
        }
    }
}
