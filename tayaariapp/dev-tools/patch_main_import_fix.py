with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

import re

old = """                androidx.compose.runtime.LaunchedEffect(Unit) {
                    kotlinx.coroutines.Dispatchers.IO.invoke {
                        try {
                            val isDbEmpty = com.example.database.AppDatabase.getDatabase(applicationContext).appDao().getTopicsCount() == 0
                            if (isDbEmpty) {
                                val mdContent = applicationContext.assets.open("consolidated_grounding.md").bufferedReader().use { it.readText() }
                                com.example.repository.DataImporter.importFromMarkdown(applicationContext, mdContent)
                            }
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }
                }"""

new = """                androidx.compose.runtime.LaunchedEffect(Unit) {
                    kotlinx.coroutines.withContext(kotlinx.coroutines.Dispatchers.IO) {
                        try {
                            val isDbEmpty = com.example.database.AppDatabase.getDatabase(applicationContext).appDao().getTopicsCount() == 0
                            if (isDbEmpty) {
                                val mdContent = applicationContext.assets.open("consolidated_grounding.md").bufferedReader().use { it.readText() }
                                com.example.repository.DataImporter.importFromMarkdown(applicationContext, mdContent)
                            }
                        } catch (e: Exception) {
                            e.printStackTrace()
                        }
                    }
                }"""

content = content.replace(old, new)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(content)
