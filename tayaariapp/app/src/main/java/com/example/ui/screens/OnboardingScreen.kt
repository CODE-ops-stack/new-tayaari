package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AccountBalance
import androidx.compose.material.icons.filled.Assignment
import androidx.compose.material.icons.filled.DirectionsRailway
import androidx.compose.material.icons.filled.Groups
import androidx.compose.material.icons.filled.MenuBook
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.RadioButtonUnchecked
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ExamBlueprint
import com.example.model.ExamBlueprintRegistry

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OnboardingScreen(
    onProfilesSelected: (List<ExamBlueprint>) -> Unit
) {
    var selectedExams by remember { mutableStateOf(setOf<String>()) }
    val deepBlue = MaterialTheme.colorScheme.primary
    val accentGold = MaterialTheme.colorScheme.tertiary
    val surfaceColor = MaterialTheme.colorScheme.surface
    val cardColor = MaterialTheme.colorScheme.background

    com.example.ui.components.AtlasBackground {
      com.example.ui.components.TopographicBackground(lineColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.035f)) {
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
                                color = com.example.ui.theme.SummitGold,
                                fontFamily = com.example.ui.theme.CartographicSerif,
                                fontWeight = FontWeight.Bold,
                                fontSize = 18.sp
                            )
                            Text(
                                "COMMISSION EXPEDITION CALIBRATION",
                                color = com.example.ui.theme.GlacierAzure,
                                fontFamily = com.example.ui.theme.CoordinatesMonospace,
                                fontSize = 10.sp,
                                letterSpacing = 1.sp
                            )
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = com.example.ui.theme.OceanicDark.copy(alpha = 0.9f)
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
                fontFamily = com.example.ui.theme.CartographicSerif,
                fontWeight = FontWeight.Bold,
                color = com.example.ui.theme.AtlasParchment,
                textAlign = TextAlign.Center
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "Calibrate syllabus transects, elevation tiers, and geomorphic distractor traps for your target commission.",
                style = MaterialTheme.typography.bodySmall,
                textAlign = TextAlign.Center,
                color = com.example.ui.theme.TopoContourMuted
            )
            Spacer(modifier = Modifier.height(16.dp))

            LazyColumn(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(14.dp),
                contentPadding = PaddingValues(bottom = 24.dp)
            ) {
                items(ExamBlueprintRegistry.blueprints.filter { it.isActive }) { blueprint ->
                    val icon = when (blueprint.examId) {
                        "UPSC_CSE_2026" -> Icons.Default.AccountBalance
                        "BPSC_CCE_72ND_2026" -> Icons.Default.MenuBook
                        "SSC_CGL_2025", "SSC_CHSL_2025" -> Icons.Default.Groups
                        "RRB_NTPC_2024", "RRB_GROUP_D_2024" -> Icons.Default.DirectionsRailway
                        else -> Icons.Default.Assignment
                    }
                    val isSelected = selectedExams.contains(blueprint.examId)
                    ExamGoalCard(
                        title = blueprint.displayName,
                        subtitle = "Target Expedition Mode:",
                        features = listOf(blueprint.recommendedPracticeMode),
                        icon = icon,
                        isSelected = isSelected,
                        onClick = {
                            selectedExams = if (isSelected) {
                                selectedExams - blueprint.examId
                            } else {
                                selectedExams + blueprint.examId
                            }
                        },
                        deepBlue = deepBlue,
                        accentGold = accentGold,
                        cardColor = cardColor
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
                modifier = Modifier.fillMaxWidth().height(52.dp),
                enabled = selectedExams.isNotEmpty(),
                shape = RoundedCornerShape(14.dp),
                colors = ButtonDefaults.buttonColors(containerColor = com.example.ui.theme.ContourEmerald)
            ) {
                Text(
                    if (selectedExams.size > 1) "🧭 Embark on Expedition (${selectedExams.size} Selected)" else "🧭 Embark on Geographic Expedition", 
                    fontSize = 16.sp, 
                    fontWeight = FontWeight.Bold,
                    color = com.example.ui.theme.AbyssNavy
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
    onClick: () -> Unit,
    deepBlue: Color,
    accentGold: Color,
    cardColor: Color
) {
    com.example.ui.components.AtlasCard(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        borderColor = if (isSelected) com.example.ui.theme.SunstoneGold else com.example.ui.theme.SlateBedrock
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = if (isSelected) androidx.compose.material.icons.Icons.Default.CheckCircle else androidx.compose.material.icons.Icons.Default.RadioButtonUnchecked,
                contentDescription = null,
                tint = if (isSelected) com.example.ui.theme.SunstoneGold else com.example.ui.theme.MeridianMuted,
                modifier = Modifier.size(24.dp)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Box(
                modifier = Modifier
                    .size(52.dp)
                    .background(com.example.ui.theme.OceanicDark, RoundedCornerShape(14.dp)),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    modifier = Modifier.size(28.dp),
                    tint = if (isSelected) com.example.ui.theme.SummitGold else com.example.ui.theme.GlacierAzure
                )
            }
            Spacer(modifier = Modifier.width(14.dp))
            Column {
                Text(
                    text = title,
                    fontSize = 17.sp,
                    fontFamily = com.example.ui.theme.CartographicSerif,
                    fontWeight = FontWeight.Bold,
                    color = if (isSelected) com.example.ui.theme.SummitGold else com.example.ui.theme.AtlasParchment
                )
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = subtitle,
                    fontSize = 11.sp,
                    fontFamily = com.example.ui.theme.CoordinatesMonospace,
                    fontWeight = FontWeight.Medium,
                    color = com.example.ui.theme.TopoContourMuted
                )
                Spacer(modifier = Modifier.height(6.dp))
                @OptIn(ExperimentalLayoutApi::class)
                FlowRow(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    features.forEach { feature ->
                        Surface(
                            color = com.example.ui.theme.OceanicDark,
                            shape = RoundedCornerShape(6.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, com.example.ui.theme.SlateBedrock)
                        ) {
                            Text(
                                text = "🧭 $feature",
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                color = com.example.ui.theme.GlacierAzure,
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                            )
                        }
                    }
                }
            }
        }
    }
}
