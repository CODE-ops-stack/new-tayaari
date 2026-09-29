package dev.tools
import java.io.File
import java.util.regex.Pattern

fun main() {
    val mdContent = File("source-material/consolidated_grounding.md").readText()
    val blocks = mdContent.split(Regex("\\r?\\n## (?=\\d+\\. )"))
    println("Blocks: ${blocks.size}")
    
    var totalQuestions = 0
    for (i in 1 until blocks.size) {
        val block = blocks[i]
        val topicNumMatch = Regex("^(\\d+)\\. (.*?)\\r?\\n").find(block)
        if (topicNumMatch == null) {
            println("Topic match failed for block $i. Starts with: ${block.take(50)}")
            continue
        }
        
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
        var qsInBlock = 0
        while (matcher.find()) qsInBlock++
        totalQuestions += qsInBlock
    }
    println("Total questions parsed: $totalQuestions")
}
