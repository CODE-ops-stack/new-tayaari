package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.RecommendedAction

@Composable
fun NextBestActionCard(
    action: RecommendedAction,
    onTopicSelected: (String, String, String) -> Unit,
    onRevisionClick: () -> Unit,
    onAnalyticsClick: () -> Unit
) {
    val (title, reason, importance, onClick) = when (action) {
        is RecommendedAction.SmartPractice -> listOf("Smart Practice", action.reason, action.importance, { onTopicSelected("Mixed", "Advanced", "Smart Practice") })
        is RecommendedAction.Revision -> listOf("Revision", action.reason, action.importance, onRevisionClick)
        is RecommendedAction.MistakeReplay -> listOf("Mistake Replay", action.reason, action.importance, { onTopicSelected("Mistake Replay", "Advanced", "Mistake Replay") })
        is RecommendedAction.Contrast -> listOf("Contrast Lab", action.reason, action.importance, { onTopicSelected("Contrast", "Advanced", "Contrast Lab") })
        is RecommendedAction.TrapTraining -> listOf("Trap Training", action.reason, action.importance, { onTopicSelected("Trap Training", "Advanced", "Trap Training") })
        is RecommendedAction.PrerequisiteRepair -> listOf("Prerequisite Repair", action.reason, action.importance, { onTopicSelected("Prerequisites", "Foundation", "Prerequisite Repair") })
        is RecommendedAction.TransferPractice -> listOf("Transfer Practice", action.reason, action.importance, { onTopicSelected("Transfer", "Advanced", "Transfer Practice") })
        is RecommendedAction.TimedDrill -> listOf("Timed Drill", action.reason, action.importance, { onTopicSelected("Mixed", "Advanced", "Smart Practice") })
        is RecommendedAction.ExamSimulation -> listOf("Exam Simulation", action.reason, action.importance, { onTopicSelected("Mixed", "Advanced", "Smart Practice") })
        is RecommendedAction.RecoveryMode -> listOf("Recovery Mode", action.reason, action.importance, { onTopicSelected("Mixed", "Foundation", "Smart Practice") })
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 12.dp)
            .clickable { (onClick as () -> Unit).invoke() },
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.AutoAwesome, contentDescription = "AI", tint = MaterialTheme.colorScheme.onPrimaryContainer)
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "NEXT-BEST ACTION",
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.onPrimaryContainer,
                    letterSpacing = 1.sp
                )
            }
            Spacer(modifier = Modifier.height(12.dp))
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Text(
                    text = title as String,
                    fontSize = 20.sp,
                    fontWeight = FontWeight.SemiBold,
                    color = MaterialTheme.colorScheme.onPrimaryContainer
                )
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(4.dp))
                        .background(
                            when (importance as String) {
                                "CRITICAL" -> Color(0xFFD32F2F)
                                "HIGH" -> Color(0xFFF57C00)
                                else -> Color(0xFF388E3C)
                            }
                        )
                        .padding(horizontal = 6.dp, vertical = 2.dp)
                ) {
                    Text(text = importance as String, color = Color.White, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = reason as String,
                fontSize = 14.sp,
                color = MaterialTheme.colorScheme.onPrimaryContainer.copy(alpha = 0.8f),
                lineHeight = 20.sp
            )
        }
    }
}
