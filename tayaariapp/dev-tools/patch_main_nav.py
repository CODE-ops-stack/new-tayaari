with open("app/src/main/java/com/example/MainActivity.kt", "r") as f:
    content = f.read()

import re

nav_code = """                    NavHost(navController = navController, startDestination = "topics") {
                        composable("topics") {
                            TopicSelectionScreen(
                                topics = topics,
                                profile = selectedProfile,
                                onTopicSelected = { topicName ->
                                    navController.navigate("practice/${android.net.Uri.encode(topicName)}")
                                }
                            )
                        }
                        composable("practice/{topicName}") { backStackEntry ->
                            val topicName = android.net.Uri.decode(backStackEntry.arguments?.getString("topicName") ?: "")
                            
                            androidx.compose.runtime.LaunchedEffect(topicName, selectedProfile) {
                                if (selectedProfile != null) {
                                    viewModel.startPractice(topicName, selectedProfile!!)
                                }
                            }
                            
                            PracticeScreen(
                                uiState = uiState,
                                onOptionSelected = viewModel::onOptionSelected,
                                onBookmarkToggle = viewModel::toggleBookmark,
                                onSkip = viewModel::skipQuestion,
                                onNext = viewModel::generateNextQuestion,
                                onDashboardClick = { navController.navigate("dashboard") }
                            )
                        }
"""

content = re.sub(r'                    NavHost\(navController = navController, startDestination = "topics"\) \{.*?composable\("dashboard"\) \{', nav_code + '                        composable("dashboard") {', content, flags=re.DOTALL)

with open("app/src/main/java/com/example/MainActivity.kt", "w") as f:
    f.write(content)
