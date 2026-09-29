import java.util.regex.Pattern

fun main() {
    val text = """Q137. Variations in the length of daytime and nighttime from season to season are dueto
(a) the earth's rotation on its axis
(b) the earth's revolution round the sun in an elliptical manner
(c) latitudinal position of the place
(d) revolution of the earth on a tilted axis""""
    
    val optionsPattern = Pattern.compile(
        "(?s)(.*?)\\s*\\(?[aA]\\)[ )\\.](.*?)\\s*\\(?[bB]\\)[ )\\.](.*?)\\s*\\(?[cC]\\)[ )\\.](.*?)\\s*\\(?[dD]\\)[ )\\.](.*?)(?:\\s*Correct [Aa]nswer:|$)"
    )
    val matcher = optionsPattern.matcher(text)
    if (matcher.find()) {
        println("MATCHED: " + matcher.group(5))
    } else {
        println("NO MATCH")
    }
}
