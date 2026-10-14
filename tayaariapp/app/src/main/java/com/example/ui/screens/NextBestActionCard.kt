package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
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
        is RecommendedAction.SmartPractice -> listOf("⛰️ Dynamic Field Transect", action.reason, action.importance, { onTopicSelected("Mixed", "Advanced", "Smart Practice") })
        is RecommendedAction.Revision -> listOf("📍 Spaced Cadastre Revision", action.reason, action.importance, onRevisionClick)
        is RecommendedAction.MistakeReplay -> listOf("🧭 Course Correction Lab", action.reason, action.importance, { onTopicSelected("Mistake Replay", "Advanced", "Mistake Replay") })
        is RecommendedAction.Contrast -> listOf("🗺️ Comparative Terrain Lab", action.reason, action.importance, { onTopicSelected("Contrast", "Advanced", "Contrast Lab") })
        is RecommendedAction.TrapTraining -> listOf("⚠️ Hazard Radar Drills", action.reason, action.importance, { onTopicSelected("Trap Training", "Advanced", "Trap Training") })
        is RecommendedAction.PrerequisiteRepair -> listOf("🌲 Basal Geomorphology Foundation", action.reason, action.importance, { onTopicSelected("Prerequisites", "Foundation", "Prerequisite Repair") })
        is RecommendedAction.TransferPractice -> listOf("🛰️ Geodetic Transfer Drills", action.reason, action.importance, { onTopicSelected("Transfer", "Advanced", "Transfer Practice") })
        is RecommendedAction.TimedDrill -> listOf("⏱️ High-Altitude Timed Climb", action.reason, action.importance, { onTopicSelected("Mixed", "Advanced", "Smart Practice") })
        is RecommendedAction.ExamSimulation -> listOf("🏔️ Full Commission Expedition Simulation", action.reason, action.importance, { onTopicSelected("Mixed", "Advanced", "Smart Practice") })
        is RecommendedAction.RecoveryMode -> listOf("⛺ Basecamp Recovery Transect", action.reason, action.importance, { onTopicSelected("Mixed", "Foundation", "Smart Practice") })
    }

    com.example.ui.components.AtlasCard(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp)
            .clickable { (onClick as () -> Unit).invoke() },
        borderColor = com.example.ui.theme.SunstoneGold.copy(alpha = 0.5f)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("🧭", fontSize = 16.sp)
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "EXPEDITION NAVIGATOR // RECOMMENDED WAYPOINT",
                    fontSize = 11.sp,
                    fontFamily = com.example.ui.theme.CoordinatesMonospace,
                    fontWeight = FontWeight.Bold,
                    color = com.example.ui.theme.GlacierAzure,
                    letterSpacing = 1.sp
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            Row(
                verticalAlignment = Alignment.CenterVertically, 
                horizontalArrangement = Arrangement.SpaceBetween, 
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = title as String,
                    fontSize = 17.sp,
                    fontFamily = com.example.ui.theme.CartographicSerif,
                    fontWeight = FontWeight.Bold,
                    color = com.example.ui.theme.SummitGold
                )
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(4.dp))
                        .background(
                            when (importance as String) {
                                "CRITICAL" -> com.example.ui.theme.MagmaCrimson
                                "HIGH" -> com.example.ui.theme.SunstoneGold
                                else -> com.example.ui.theme.ContourEmerald
                            }
                        )
                        .padding(horizontal = 6.dp, vertical = 2.dp)
                ) {
                    Text(
                        text = importance as String, 
                        color = com.example.ui.theme.AbyssNavy, 
                        fontSize = 10.sp, 
                        fontFamily = com.example.ui.theme.CoordinatesMonospace,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = reason as String,
                fontSize = 13.sp,
                color = com.example.ui.theme.TopoContourMuted,
                lineHeight = 18.sp
            )
        }
    }
}
