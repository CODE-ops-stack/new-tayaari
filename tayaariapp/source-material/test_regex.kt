import java.util.regex.Pattern

fun main() {
    val qText = """Q1. What  are  the  streams  of  charged   particles  ejected  by  the  Sun  into  space   called ?
a) Sunspots
b) Solar wind
c) Solar flares
d) Coronal loops
Correct answer: option b"""

    val parsedQPattern = java.util.regex.Pattern.compile("(?s)(.*?)\\s*\\(?[aA]\\)[ )\\.](.*?)\\s*\\(?[bB]\\)[ )\\.](.*?)\\s*\\(?[cC]\\)[ )\\.](.*?)\\s*\\(?[dD]\\)[ )\\.](.*?)\\s*Correct [Aa]nswer:\\s*(?:[Oo]ption\\s*)?([a-dA-D])")
    
    val matcher = parsedQPattern.matcher(qText)
    if (matcher.find()) {
        println("Match!")
        println(matcher.group(1))
        println(matcher.group(2))
    } else {
        println("No match.")
    }
}
