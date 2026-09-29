with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

import re

# Add BookmarksViewModel import
if "import com.example.viewmodel.BookmarksViewModel" not in content:
    content = content.replace("import com.example.viewmodel.TopicSelectionViewModel", "import com.example.viewmodel.TopicSelectionViewModel\nimport com.example.viewmodel.BookmarksViewModel\nimport com.example.ui.screens.BookmarksScreen")

# Add factory for BookmarksViewModel
old_factories = """        val topicFactory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return TopicSelectionViewModel(localRepository, userPrefsRepo) as T
            }
        }"""

new_factories = """        val topicFactory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return TopicSelectionViewModel(localRepository, userPrefsRepo) as T
            }
        }
        
        val bookmarksFactory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T {
                return BookmarksViewModel(localRepository) as T
            }
        }"""

content = content.replace(old_factories, new_factories)

# Add route for bookmarks and handle click
old_nav = """                        composable("topics") {
                            TopicSelectionScreen(
                                topics = topics,
                                profile = selectedProfile,
                                onTopicSelected = { topicName ->
                                    navController.navigate("practice/${android.net.Uri.encode(topicName)}")
                                }
                            )
                        }"""

new_nav = """                        composable("topics") {
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
                        }
                        
                        composable("bookmarks") {
                            val bookmarksViewModel: BookmarksViewModel = viewModel(factory = bookmarksFactory)
                            BookmarksScreen(
                                viewModel = bookmarksViewModel,
                                onBack = { navController.popBackStack() }
                            )
                        }"""

content = content.replace(old_nav, new_nav)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(content)
