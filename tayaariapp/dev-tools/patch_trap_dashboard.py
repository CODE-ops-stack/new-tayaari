with open("app/src/main/java/com/example/ui/screens/TrapDashboardScreen.kt", "r") as f:
    content = f.read()

import re

new_card = """@Composable
fun TrapStatCard(trap: TrapAnalyticsEntity, maxFreq: Int) {
    val fraction = if (maxFreq > 0) trap.frequency.toFloat() / maxFreq else 0f
    
    Surface(
        color = MaterialTheme.colorScheme.surface,
        shape = RoundedCornerShape(12.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = trap.trapType,
                    color = MaterialTheme.colorScheme.onBackground,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Medium
                )
                Text(
                    text = "${trap.frequency} times",
                    color = MaterialTheme.colorScheme.primary,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Bold
                )
            }
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(8.dp)
                    .background(Color.LightGray.copy(alpha = 0.5f), RoundedCornerShape(4.dp))
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth(fraction)
                        .height(8.dp)
                        .background(MaterialTheme.colorScheme.error, RoundedCornerShape(4.dp))
                )
            }
        }
    }
}"""

content = re.sub(r'@Composable\s+fun TrapStatCard.*', new_card, content, flags=re.DOTALL)

old_items = """                items(trapAnalytics) { trap ->
                    TrapStatCard(trap = trap)
                }"""
                
new_items = """                val maxFreq = trapAnalytics.maxOfOrNull { it.frequency } ?: 1
                items(trapAnalytics.sortedByDescending { it.frequency }) { trap ->
                    TrapStatCard(trap = trap, maxFreq = maxFreq)
                }"""

content = content.replace(old_items, new_items)

if "import androidx.compose.foundation.background" not in content:
    content = content.replace("import androidx.compose.foundation.layout.*", "import androidx.compose.foundation.layout.*\nimport androidx.compose.foundation.background\nimport androidx.compose.ui.graphics.Color")

with open("app/src/main/java/com/example/ui/screens/TrapDashboardScreen.kt", "w") as f:
    f.write(content)
