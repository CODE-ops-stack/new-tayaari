with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

import re

old_topic = """                        composable("topics") {
                            TopicSelectionScreen(
                                topics = topics,
                                profile = selectedProfile,
                                onTopicSelected = { topicName ->
                                    navController.navigate("practice/${android.net.Uri.encode(topicName)}")
                                },
                                onBookmarksClick = {
                                    navController.navigate("bookmarks")
                                }
                            )
                        }"""

new_topic = """                        composable("topics") {
                            TopicSelectionScreen(
                                topics = topics,
                                profile = selectedProfile,
                                onTopicSelected = { topicName ->
                                    navController.navigate("practice/${android.net.Uri.encode(topicName)}")
                                },
                                onBookmarksClick = {
                                    navController.navigate("bookmarks")
                                },
                                onAnalyticsClick = {
                                    navController.navigate("dashboard")
                                }
                            )
                        }"""
content = content.replace(old_topic, new_topic)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(content)
