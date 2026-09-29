with open("app/src/main/java/com/example/ui/screens/TopicSelectionScreen.kt", "r") as f:
    content = f.read()

import re

# Add IconButton to TopAppBar
old_topbar = """        topBar = {
            TopAppBar(
                title = { Text("Select Topic", fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = deepOceanBlue,
                    titleContentColor = parchmentColor
                )
            )
        },"""

new_topbar = """        topBar = {
            TopAppBar(
                title = { Text("Select Topic", fontWeight = FontWeight.Bold) },
                actions = {
                    IconButton(onClick = { onBookmarksClick() }) {
                        Icon(
                            imageVector = Icons.Default.Bookmark,
                            contentDescription = "Bookmarks",
                            tint = parchmentColor
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = deepOceanBlue,
                    titleContentColor = parchmentColor,
                    actionIconContentColor = parchmentColor
                )
            )
        },"""

content = content.replace(old_topbar, new_topbar)

# Add onBookmarksClick to signature
old_sig = """fun TopicSelectionScreen(
    topics: List<TopicUIModel>,
    profile: ExamProfile?,
    onTopicSelected: (String) -> Unit
)"""

new_sig = """fun TopicSelectionScreen(
    topics: List<TopicUIModel>,
    profile: ExamProfile?,
    onTopicSelected: (String) -> Unit,
    onBookmarksClick: () -> Unit = {}
)"""

content = content.replace(old_sig, new_sig)

# Add import for Icons.Default.Bookmark
if "import androidx.compose.material.icons.filled.Bookmark" not in content:
    content = content.replace("import androidx.compose.material.icons.filled.Warning", "import androidx.compose.material.icons.filled.Warning\nimport androidx.compose.material.icons.filled.Bookmark")

with open("app/src/main/java/com/example/ui/screens/TopicSelectionScreen.kt", "w") as f:
    f.write(content)
