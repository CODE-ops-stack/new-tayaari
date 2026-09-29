package dev.tools
import java.io.File
import java.util.regex.Pattern

fun main() {
    val mdContent = File("source-material/consolidated_grounding.md").readText()
    val blocks = mdContent.split(Regex("\\r?\\n## (?=\\d+\\. )"))
    
    println("Blocks: ${blocks.size}")
    if (blocks.size > 1) {
        val topicNumMatch = Regex("^(\\d+)\\. (.*?)\\r?\\n").find(blocks[1])
        println("Topic Match 1: ${topicNumMatch?.groupValues}")
    }
}
