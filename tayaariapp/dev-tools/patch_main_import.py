with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

import re

old_onboarding = """                if (isLoading) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator()
                    }
                } else if (selectedProfile == null) {"""

new_onboarding = """                androidx.compose.runtime.LaunchedEffect(Unit) {
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
                }
                
                if (isLoading) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator()
                    }
                } else if (selectedProfile == null) {"""

content = content.replace(old_onboarding, new_onboarding)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(content)
