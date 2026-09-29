with open("app/src/main/java/com/example/ui/screens/TopicSelectionScreen.kt", "r") as f:
    content = f.read()

import re

old_sig = """fun TopicSelectionScreen(
    topics: List<TopicUIModel>,
    profile: ExamProfile?,
    onTopicSelected: (String) -> Unit,
    onBookmarksClick: () -> Unit = {}
)"""

new_sig = """fun TopicSelectionScreen(
    topics: List<TopicUIModel>,
    profile: ExamProfile?,
    onTopicSelected: (String) -> Unit,
    onBookmarksClick: () -> Unit = {},
    onAnalyticsClick: () -> Unit = {}
)"""

content = content.replace(old_sig, new_sig)

old_actions = """                actions = {
                    IconButton(onClick = { onBookmarksClick() }) {
                        Icon(
                            imageVector = Icons.Default.Bookmark,
                            contentDescription = "Bookmarks",
                            tint = parchmentColor
                        )
                    }
                },"""

new_actions = """                actions = {
                    IconButton(onClick = { onAnalyticsClick() }) {
                        Icon(
                            imageVector = Icons.Default.Analytics,
                            contentDescription = "Analytics",
                            tint = parchmentColor
                        )
                    }
                    IconButton(onClick = { onBookmarksClick() }) {
                        Icon(
                            imageVector = Icons.Default.Bookmark,
                            contentDescription = "Bookmarks",
                            tint = parchmentColor
                        )
                    }
                },"""

content = content.replace(old_actions, new_actions)

if "import androidx.compose.material.icons.filled.Analytics" not in content:
    content = content.replace("import androidx.compose.material.icons.filled.Bookmark", "import androidx.compose.material.icons.filled.Bookmark\nimport androidx.compose.material.icons.filled.Analytics")

with open("app/src/main/java/com/example/ui/screens/TopicSelectionScreen.kt", "w") as f:
    f.write(content)
