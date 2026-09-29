import java.io.File

fun main() {
    val mdContent = "\n" + File("/app/applet/source-material/consolidated_grounding.md").readText()
    val blocks = mdContent.split(Regex("\\n## (?=\\d+\\. )"))
    println("Blocks: ${blocks.size}")
    
    var count = 0
    for (i in 1 until blocks.size) {
        val block = blocks[i]
        val topicNumMatch = Regex("^(\\d+)\\. (.*?)\\n").find(block)
        if (topicNumMatch == null) {
            println("No match for block \$i: \${block.take(50).replace("\n", "\\n")}")
            continue
        }
        count++
    }
    println("Matched: \$count")
}
