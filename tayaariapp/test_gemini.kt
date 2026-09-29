import java.net.HttpURLConnection
import java.net.URL
import java.io.OutputStreamWriter
import java.io.InputStreamReader
import java.io.BufferedReader

fun main() {
    val apiKey = System.getenv("GEMINI_API_KEY")
    if (apiKey == null) {
        println("API Key is null")
        return
    }

    val url = URL("https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key=$apiKey")
    val conn = url.openConnection() as HttpURLConnection
    conn.requestMethod = "POST"
    conn.setRequestProperty("Content-Type", "application/json")
    conn.doOutput = true

    val prompt = """
        You are an expert UPSC/SSC Geography question-setter with deep experience designing real exam PYQs. 
        Generate one new practice question for Topic: 13. Geomorphic Processes, Format: Statement-based, Tier: Advanced.
        
        REQUIREMENTS:
        1. Exactly 4 options.
        2. Exactly 3 distractor dissections (one for each incorrect option).
        
        Return ONLY a valid, raw JSON object with this exact structure (no markdown tags, no backticks):
        {
            "questionText": "Question string",
            "options": [
                {"id": "opt_A", "text": "Option A text"},
                {"id": "opt_B", "text": "Option B text"},
                {"id": "opt_C", "text": "Option C text"},
                {"id": "opt_D", "text": "Option D text"}
            ],
            "correctAnswerId": "opt_B",
            "correctExplanation": "Explanation for the correct answer",
            "distractorDissections": [
                {"optionId": "opt_A", "trapType": "Factual Inversion", "dissection": "Why it's wrong"},
                {"optionId": "opt_C", "trapType": "Absolute Wording", "dissection": "Why it's wrong"},
                {"optionId": "opt_D", "trapType": "Irrelevant Fact", "dissection": "Why it's wrong"}
            ],
            "topic": "13. Geomorphic Processes",
            "tier": "Advanced",
            "format": "Statement-based",
            "sourceGrounding": "NCERT/Reference Book chapter"
        }
    """.trimIndent().replace("\"", "\\\"").replace("\n", "\\n")

    val jsonBody = """
        {
            "contents": [{
                "parts": [{"text": "$prompt"}]
            }],
            "generationConfig": {
                "responseMimeType": "application/json",
                "maxOutputTokens": 8192
            }
        }
    """.trimIndent()

    val writer = OutputStreamWriter(conn.outputStream)
    writer.write(jsonBody)
    writer.flush()
    writer.close()

    val responseCode = conn.responseCode
    if (responseCode == 200) {
        val reader = BufferedReader(InputStreamReader(conn.inputStream))
        val response = reader.readText()
        reader.close()
        println(response)
    } else {
        println("Failed: ${conn.responseCode}")
        val reader = BufferedReader(InputStreamReader(conn.errorStream))
        println(reader.readText())
        reader.close()
    }
}
