package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Assignment
import androidx.compose.material.icons.automirrored.filled.MenuBook
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ExamBlueprint
import com.example.model.ExamBlueprintRegistry
import com.example.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OnboardingScreen(
    onProfilesSelected: (List<ExamBlueprint>) -> Unit
) {
    var selectedExams by remember { mutableStateOf(setOf<String>()) }
    val haptic = LocalHapticFeedback.current

    com.example.ui.components.AtlasBackground {
        com.example.ui.components.TopographicBackground(lineColor = ContourEmerald.copy(alpha = 0.035f)) {
            Scaffold(
                containerColor = Color.Transparent,
                topBar = {
                    TopAppBar(
                        title = {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text(
                                    "🧭",
                                    fontSize = 24.sp
                                )
                                Spacer(modifier = Modifier.width(10.dp))
                                Column {
                                    Text(
                                        "Civil Services Geography Cadastre",
                                        color = SummitGold,
                                        fontFamily = CartographicSerif,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 18.sp
                                    )
                                    Text(
                                        "COMMISSION EXPEDITION CALIBRATION",
                                        color = GlacierAzure,
                                        fontFamily = CoordinatesMonospace,
                                        fontSize = 10.sp,
                                        letterSpacing = 1.sp
                                    )
                                }
                            }
                        },
                        colors = TopAppBarDefaults.topAppBarColors(
                            containerColor = OceanicDark.copy(alpha = 0.9f)
                        )
                    )
                }
            ) { paddingValues ->
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues)
                        .padding(horizontal = 20.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Spacer(modifier = Modifier.height(12.dp))
                    com.example.ui.components.CartographicCoordinatesBanner(
                        coordinatesText = "📍 EXPEDITION BLUEPRINT // 82°30′E IST"
                    )
                    Spacer(modifier = Modifier.height(10.dp))
                    Text(
                        text = "Select Your Target Expedition 🧭",
                        style = MaterialTheme.typography.headlineSmall,
                        fontFamily = CartographicSerif,
                        fontWeight = FontWeight.Bold,
                        color = AtlasParchment,
                        textAlign = TextAlign.Center
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "Calibrate syllabus transects, elevation tiers, and geomorphic distractor traps for your target commission.",
                        style = MaterialTheme.typography.bodySmall,
                        textAlign = TextAlign.Center,
                        color = TopoContourMuted
                    )

                    // Dynamic Cadre Glory Preview Banner when an exam is active
                    AnimatedVisibility(visible = selectedExams.isNotEmpty()) {
                        val firstExam = selectedExams.first()
                        val (gloryBadge, gloryQuote, cadreColor) = when {
                            firstExam.contains("UPSC", ignoreCase = true) -> Triple(
                                "🏛️ MISSION LBSNAA • CIVIL SERVICES CADRE",
                                "Sardar Patel's Steel Frame: 1 MCQ mastered today = 1 step closer to Mussoorie.",
                                SunstoneGold
                            )
                            firstExam.contains("BPSC", ignoreCase = true) -> Triple(
                                "🌾 70TH/72ND BPSC CCE • BIHAR ADMINISTRATIVE (SDM/DSP)",
                                "From Patna Secretariat to Sub-Divisional Magistrate: Every question builds your rank.",
                                ContourEmerald
                            )
                            firstExam.contains("SSC", ignoreCase = true) -> Triple(
                                "⭐ CENTRAL SECRETARIAT (ASO) • MERIT RANK CORPS",
                                "High-Speed Precision: 1 question saved from negative penalty = 5,000 ranks gained.",
                                HydrosphereCyan
                            )
                            else -> Triple(
                                "🚆 INDIAN RAILWAYS EXECUTIVE CORPS • APEX SPEED",
                                "The Lifeline of the Nation: Master India's terrain to command the tracks.",
                                SunstoneGold
                            )
                        }

                        Surface(
                            color = DeepBasalt,
                            shape = RoundedCornerShape(12.dp),
                            border = BorderStroke(1.dp, cadreColor.copy(alpha = 0.5f)),
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(top = 10.dp, bottom = 4.dp)
                        ) {
                            Column(modifier = Modifier.padding(12.dp)) {
                                Text(
                                    text = gloryBadge,
                                    color = cadreColor,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Black,
                                    letterSpacing = 0.6.sp
                                )
                                Spacer(modifier = Modifier.height(3.dp))
                                Text(
                                    text = gloryQuote,
                                    color = AtlasParchment,
                                    fontSize = 11.5.sp,
                                    fontStyle = androidx.compose.ui.text.font.FontStyle.Italic,
                                    lineHeight = 16.sp
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(12.dp))

                    LazyColumn(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.spacedBy(14.dp),
                        contentPadding = PaddingValues(bottom = 24.dp)
                    ) {
                        items(ExamBlueprintRegistry.blueprints.filter { it.isActive }) { blueprint ->
                            val icon = when (blueprint.examId) {
                                "UPSC_CSE_2026" -> Icons.Default.AccountBalance
                                "BPSC_CCE_72ND_2026" -> Icons.AutoMirrored.Filled.MenuBook
                                "SSC_CGL_2025", "SSC_CHSL_2025" -> Icons.Default.Groups
                                "RRB_NTPC_2024", "RRB_GROUP_D_2024" -> Icons.Default.DirectionsRailway
                                else -> Icons.AutoMirrored.Filled.Assignment
                            }
                            val isSelected = selectedExams.contains(blueprint.examId)
                            ExamGoalCard(
                                title = blueprint.displayName,
                                subtitle = "Target Expedition Mode:",
                                features = listOf(blueprint.recommendedPracticeMode),
                                icon = icon,
                                isSelected = isSelected,
                                onClick = {
                                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                    selectedExams = if (isSelected) {
                                        selectedExams - blueprint.examId
                                    } else {
                                        selectedExams + blueprint.examId
                                    }
                                }
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(14.dp))
                    Button(
                        onClick = {
                            val blueprints = selectedExams.mapNotNull { ExamBlueprintRegistry.getBlueprint(it) }
                            if (blueprints.isNotEmpty()) {
                                onProfilesSelected(blueprints)
                            }
                        },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(52.dp),
                        enabled = selectedExams.isNotEmpty(),
                        shape = RoundedCornerShape(14.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = ContourEmerald)
                    ) {
                        Text(
                            text = if (selectedExams.size > 1) "🧭 Embark on Expedition (${selectedExams.size} Selected)" else "🧭 Embark on Geographic Expedition",
                            fontSize = 15.sp,
                            fontWeight = FontWeight.Bold,
                            color = AbyssNavy
                        )
                    }
                    Spacer(modifier = Modifier.height(20.dp))
                }
            }
        }
    }
}

@Composable
fun ExamGoalCard(
    title: String,
    subtitle: String,
    icon: ImageVector,
    features: List<String>,
    isSelected: Boolean,
    onClick: () -> Unit
) {
    com.example.ui.components.AtlasCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        borderColor = if (isSelected) SunstoneGold else SlateBedrock
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = if (isSelected) Icons.Default.CheckCircle else Icons.Default.RadioButtonUnchecked,
                contentDescription = null,
                tint = if (isSelected) SunstoneGold else MeridianMuted,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Box(
                modifier = Modifier
                    .size(52.dp)
                    .background(OceanicDark, RoundedCornerShape(14.dp)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(28.dp),
                    tint = if (isSelected) SummitGold else GlacierAzure
                )
            }
            Spacer(modifier = Modifier.width(14.dp))
            Column {
                Text(
                    text = title,
                    fontSize = 16.sp,
                    fontFamily = CartographicSerif,
                    fontWeight = FontWeight.Bold,
                    color = if (isSelected) SummitGold else AtlasParchment
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = subtitle,
                    fontSize = 11.sp,
                    fontFamily = CoordinatesMonospace,
                    fontWeight = FontWeight.Medium,
                    color = TopoContourMuted
                )
                Spacer(modifier = Modifier.height(6.dp))
                @OptIn(ExperimentalLayoutApi::class)
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    features.forEach { feature ->
                        Surface(
                            color = OceanicDark,
                            shape = RoundedCornerShape(6.dp),
                            border = BorderStroke(1.dp, SlateBedrock)
                        ) {
                            Text(
                                text = "🧭 $feature",
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                color = GlacierAzure,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                            )
                        }
                    }
                }
            }
        }
    }
}
