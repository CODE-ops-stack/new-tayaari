fun main() {
    val optionsPattern = java.util.regex.Pattern.compile("(?s)(.*?)\\s*\\(?[aA]\\)[ )\\.](.*?)\\s*\\(?[bB]\\)[ )\\.](.*?)\\s*\\(?[cC]\\)[ )\\.](.*?)\\s*\\(?[dD]\\)[ )\\.](.*)")
    val text1 = "Question\na) 1 only\nb) 2\nc) 3\nd) 4"
    println(optionsPattern.matcher(text1).find())
    val text2 = "Question\na. 1 only\nb. 2\nc. 3\nd. 4"
    println(optionsPattern.matcher(text2).find())
}
