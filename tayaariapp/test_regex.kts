import java.util.regex.Pattern

val q137_upsc = """Q137. Variations in the length of daytime and nighttime from season to season are due
to
(a) the earth's rotation on its axis
(b) the earth's revolution round the sun in an elliptical manner
(c) latitudinal position of the place
(d) revolution of the earth on a tilted axis"""
val q140_ssc = """Q140. Which  of  the  following  rivers  is  an   east flowing river?
a) Mahi river
b) Narmada river
c) Godavari river
d) Tapi river
Correct answer: option c"""

val optionsPattern = java.util.regex.Pattern.compile(
    "(?s)(.*?)\\s*\\(?[aA]\\)[ )\\.](.*?)\\s*\\(?[bB]\\)[ )\\.](.*?)\\s*\\(?[cC]\\)[ )\\.](.*?)\\s*\\(?[dD]\\)[ )\\.](.*)"
)

var m = optionsPattern.matcher(q137_upsc)
println("Q137 matches: ${m.find()}")
if (m.matches()) {
    println("A: ${m.group(2)}")
    println("B: ${m.group(3)}")
}

m = optionsPattern.matcher(q140_ssc)
println("Q140 matches: ${m.find()}")
if (m.matches()) {
    println("A: ${m.group(2)}")
    println("B: ${m.group(3)}")
}
