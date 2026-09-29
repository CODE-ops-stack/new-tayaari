with open("app/src/main/java/com/example/model/TestModels.kt", "r") as f:
    content = f.read()

content = content.replace("    val questionFormatType: String = \"Direct Fact\",", "    override val questionFormatType: String = \"Direct Fact\",")

with open("app/src/main/java/com/example/model/TestModels.kt", "w") as f:
    f.write(content)

with open("app/src/main/java/com/example/ui/screens/ResultsScreen.kt", "r") as f:
    res = f.read()

if "import androidx.compose.foundation.BorderStroke" not in res:
    res = res.replace("import androidx.compose.foundation.background", "import androidx.compose.foundation.background\nimport androidx.compose.foundation.BorderStroke")

with open("app/src/main/java/com/example/ui/screens/ResultsScreen.kt", "w") as f:
    f.write(res)
