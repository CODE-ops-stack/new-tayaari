import java.util.regex.Pattern

val text = """1. The Earth in the Solar System
### UPSC Prelims Data (150-Question Set)
*Total Questions Mapped:* 0
### SSC Stenographer Data (925-Question Set)
- **Topic**: 1. The Earth in the Solar System
- **Tier**: Basic
- **Format**: Direct Fact
- **Exam-Relevance**: General-Competitive
- **Source**: Real-PYQ
- **Specific-Exam**: SSC-Stenographer
- **PDF-Sequence-Number**: 617
- **Question**:
```
Q617. Which
```"""

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

val matcher = qPattern.matcher(text)
var count = 0
while(matcher.find()) {
    count++
    println("Found match: " + matcher.group(1))
}
println("Count: " + count)
