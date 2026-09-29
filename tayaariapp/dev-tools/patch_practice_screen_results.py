with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "r") as f:
    content = f.read()

import re

# Insert the ResultsScreen conditional display inside PracticeScreen
practice_screen_code = """@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PracticeScreen(
    uiState: TestUiState,
    onOptionSelected: (String) -> Unit,
    onBookmarkToggle: () -> Unit,
    onSkip: () -> Unit,
    onNext: () -> Unit,
    onDashboardClick: () -> Unit
) {
    if (uiState.isTestFinished) {
        ResultsScreen(
            questions = uiState.allQuestions,
            userAnswers = uiState.userAnswers,
            score = uiState.currentScore,
            onDashboardClick = onDashboardClick
        )
        return
    }

    val targetQuestion = uiState.currentQuestion
"""

content = content.replace("""@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PracticeScreen(
    uiState: TestUiState,
    onOptionSelected: (String) -> Unit,
    onBookmarkToggle: () -> Unit,
    onSkip: () -> Unit,
    onNext: () -> Unit,
    onDashboardClick: () -> Unit
) {
    val targetQuestion = uiState.currentQuestion""", practice_screen_code)

with open("app/src/main/java/com/example/ui/screens/PracticeScreen.kt", "w") as f:
    f.write(content)
