import java.io.File
import java.util.regex.Pattern

fun main() {
    val mdContent = File("source-material/consolidated_grounding.md").readText()
    
    val sscPattern = Pattern.compile("### SSC Stenographer Data \\(925-Question Set\\).*?(?=(?:## |\\z))", Pattern.DOTALL)
    val sscMatcher = sscPattern.matcher(mdContent)
    
    var sscQs = 0
    var sscExtractedQs = 0
    
    val parsedQPattern = Pattern.compile(
        "(?s)(.*?)\\s*\\(?[aA]\\)[ )\\.](.*?)\\s*\\(?[bB]\\)[ )\\.](.*?)\\s*\\(?[cC]\\)[ )\\.](.*?)\\s*\\(?[dD]\\)[ )\\.](.*?)\\s*Correct [Aa]nswer:\\s*(?:[Oo]ption\\s*)?([a-dA-D])"
    )

    while (sscMatcher.find()) {
        val block = sscMatcher.group()
        
        // Count total raw sequence blocks
        val rawPattern = Pattern.compile("- \\*\\*PDF-Sequence-Number\\*\\*: (\\d+)")
        val rawMatcher = rawPattern.matcher(block)
        while (rawMatcher.find()) {
            sscQs++
        }
        
        val qBlockPattern = Pattern.compile("- \\*\\*Question\\*\\*:\\s*```(.*?)```", Pattern.DOTALL)
        val qBlockMatcher = qBlockPattern.matcher(block)
        
        while (qBlockMatcher.find()) {
            val qText = qBlockMatcher.group(1).trim()
            val matcher = parsedQPattern.matcher(qText)
            if (matcher.find()) {
                sscExtractedQs++
            }
        }
    }
    
    println("Total SSC Qs: \$sscQs")
    println("Extracted & Parsed SSC Qs: \$sscExtractedQs")
}
