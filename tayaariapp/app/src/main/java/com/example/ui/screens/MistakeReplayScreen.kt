package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Error
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.viewmodel.MistakeReplayViewModel
import com.example.viewmodel.ReplayState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MistakeReplayScreen(
    viewModel: MistakeReplayViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    val fontScale = com.example.ui.theme.LocalFontScale.current

    com.example.ui.components.AtlasBackground {
        com.example.ui.components.TopographicBackground(lineColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.035f)) {
            Scaffold(
                containerColor = Color.Transparent,
                topBar = {
                    TopAppBar(
                        title = { 
                            Column {
                                Text(
                                    "Course Correction Transect 🧭",
                                    color = com.example.ui.theme.SummitGold,
                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 18.sp
                                )
                                Text(
                                    "GEODETIC ERROR RECOVERY ENGINE",
                                    color = com.example.ui.theme.GlacierAzure,
                                    fontFamily = com.example.ui.theme.CoordinatesMonospace,
                                    fontSize = 10.sp,
                                    letterSpacing = 1.sp
                                )
                            }
                        },
                        navigationIcon = {
                            IconButton(onClick = onBack) {
                                Icon(
                                    Icons.AutoMirrored.Filled.ArrowBack, 
                                    contentDescription = "Back",
                                    tint = MaterialTheme.colorScheme.onSurface
                                )
                            }
                        },
                        colors = TopAppBarDefaults.topAppBarColors(
                            containerColor = Color.Transparent
                        )
                    )
                }
            ) { padding ->
                Column(
                    modifier = Modifier
                        .padding(padding)
                        .padding(16.dp)
                        .fillMaxSize(),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    when (uiState.currentState) {
                        ReplayState.LOADING -> {
                            CircularProgressIndicator(color = com.example.ui.theme.GlacierAzure)
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                "Scanning geodetic field logs for course deviations...",
                                color = MaterialTheme.colorScheme.onSurface,
                                fontFamily = com.example.ui.theme.CartographicSerif,
                                fontSize = (15 * fontScale).sp
                            )
                        }
                        ReplayState.NO_CANDIDATES -> {
                            Text("🧭", fontSize = 54.sp)
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                "Bearing: True North 🧭", 
                                style = MaterialTheme.typography.headlineMedium,
                                fontFamily = com.example.ui.theme.CartographicSerif,
                                fontWeight = FontWeight.Bold,
                                color = com.example.ui.theme.SummitGold
                            )
                            Spacer(modifier = Modifier.height(6.dp))
                            Text(
                                "Zero topographic deviations detected. All surveyed waypoints are locked and accurate.", 
                                color = com.example.ui.theme.TopoContourMuted,
                                textAlign = androidx.compose.ui.text.style.TextAlign.Center,
                                fontSize = 14.sp
                            )
                        }
                        ReplayState.REVIEW_MISTAKE -> {
                            val candidate = uiState.candidate!!
                            com.example.ui.components.CartographicCoordinatesBanner(
                                coordinatesText = "📍 COURSE DEVIATION // FIELD ANALYSIS"
                            )
                            Spacer(modifier = Modifier.height(12.dp))
                            Text(
                                "Topographic Hazard Encountered ⚠️", 
                                style = MaterialTheme.typography.titleLarge, 
                                fontFamily = com.example.ui.theme.CartographicSerif,
                                fontWeight = FontWeight.Bold,
                                color = com.example.ui.theme.MagmaCrimson
                            )
                            Spacer(modifier = Modifier.height(12.dp))
                            com.example.ui.components.AtlasCard(
                                modifier = Modifier.fillMaxWidth(),
                                borderColor = com.example.ui.theme.MagmaCrimson.copy(alpha = 0.5f)
                            ) {
                                Column(modifier = Modifier.padding(16.dp)) {
                                    Surface(
                                        color = MaterialTheme.colorScheme.surfaceVariant,
                                        shape = RoundedCornerShape(6.dp),
                                        border = androidx.compose.foundation.BorderStroke(1.dp, com.example.ui.theme.MagmaCrimson)
                                    ) {
                                        Text(
                                            "TRAP TYPE: ${candidate.evidenceType}", 
                                            fontWeight = FontWeight.Bold,
                                            fontFamily = com.example.ui.theme.CoordinatesMonospace,
                                            fontSize = (11 * fontScale).sp,
                                            color = com.example.ui.theme.MagmaCrimson,
                                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                        )
                                    }
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        "Context: ${candidate.context}",
                                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                                        fontSize = (12 * fontScale).sp
                                    )
                                    Spacer(modifier = Modifier.height(14.dp))
                                    Text(
                                        "Original Waypoint Question:", 
                                        fontWeight = FontWeight.Bold,
                                        color = com.example.ui.theme.SunstoneGold,
                                        fontSize = (13 * fontScale).sp
                                    )
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Text(
                                        candidate.originalQuestion.questionText,
                                        color = MaterialTheme.colorScheme.onSurface,
                                        fontFamily = com.example.ui.theme.CartographicSerif,
                                        fontSize = (15 * fontScale).sp,
                                        lineHeight = (22 * fontScale).sp
                                    )
                                }
                            }
                            Spacer(modifier = Modifier.height(20.dp))
                            Button(
                                onClick = { viewModel.commitToRepair() },
                                colors = ButtonDefaults.buttonColors(containerColor = com.example.ui.theme.ContourEmerald),
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.fillMaxWidth().height(48.dp)
                            ) {
                                Text(
                                    "🧭 Begin Concept Recalibration (${candidate.repairRoute})",
                                    color = com.example.ui.theme.AbyssNavy,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                        ReplayState.REPAIR -> {
                            val candidate = uiState.candidate!!
                            com.example.ui.components.CartographicCoordinatesBanner(
                                coordinatesText = "📍 SURVEYOR GENERAL CONCEPT RECALIBRATION"
                            )
                            Spacer(modifier = Modifier.height(12.dp))
                            Text(
                                "Core Geographic Concept Repair 🗺️", 
                                style = MaterialTheme.typography.titleLarge,
                                fontFamily = com.example.ui.theme.CartographicSerif,
                                fontWeight = FontWeight.Bold,
                                color = com.example.ui.theme.SummitGold
                            )
                            Spacer(modifier = Modifier.height(12.dp))
                            com.example.ui.components.AtlasCard(
                                modifier = Modifier.fillMaxWidth(),
                                borderColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.5f)
                            ) {
                                Column(modifier = Modifier.padding(16.dp)) {
                                    Text(
                                        "Verified Atlas Cadastre Principle:", 
                                        fontWeight = FontWeight.Bold,
                                        color = com.example.ui.theme.ContourEmerald,
                                        fontSize = (13 * fontScale).sp
                                    )
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        candidate.originalQuestion.explanation ?: "Review the standard cartographic dissection for this topic.",
                                        color = MaterialTheme.colorScheme.onSurface,
                                        fontFamily = com.example.ui.theme.CartographicSerif,
                                        fontSize = (15 * fontScale).sp,
                                        lineHeight = (22 * fontScale).sp
                                    )
                                }
                            }
                            Spacer(modifier = Modifier.height(20.dp))
                            Button(
                                onClick = { viewModel.proceedToAlternate() },
                                colors = ButtonDefaults.buttonColors(containerColor = com.example.ui.theme.GlacierAzure),
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.fillMaxWidth().height(48.dp)
                            ) {
                                Text(
                                    "📍 Test Field Transfer Transect",
                                    color = com.example.ui.theme.AbyssNavy,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                        ReplayState.ALTERNATE_QUESTION -> {
                            val altQuestion = uiState.alternateQuestion!!
                            com.example.ui.components.CartographicCoordinatesBanner(
                                coordinatesText = "📍 TRANSFER TEST // INDEPENDENT WAYPOINT"
                            )
                            Spacer(modifier = Modifier.height(12.dp))
                            Text(
                                "Field Transfer Challenge 🧭", 
                                style = MaterialTheme.typography.titleLarge, 
                                fontFamily = com.example.ui.theme.CartographicSerif,
                                fontWeight = FontWeight.Bold,
                                color = com.example.ui.theme.GlacierAzure
                            )
                            Spacer(modifier = Modifier.height(12.dp))
                            com.example.ui.components.AtlasCard(
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Column(modifier = Modifier.padding(16.dp)) {
                                    Text(
                                        altQuestion.questionText,
                                        color = MaterialTheme.colorScheme.onSurface,
                                        fontFamily = com.example.ui.theme.CartographicSerif,
                                        fontSize = (15 * fontScale).sp,
                                        lineHeight = (22 * fontScale).sp
                                    )
                                    Spacer(modifier = Modifier.height(16.dp))
                                    val options = uiState.altOptions
                                    options.forEachIndexed { index, opt ->
                                        Surface(
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .padding(vertical = 4.dp)
                                                .clickable { viewModel.selectOption(index) },
                                            color = if (uiState.selectedOptionIndex == index) MaterialTheme.colorScheme.surfaceVariant else Color.Transparent,
                                            shape = RoundedCornerShape(8.dp),
                                            border = androidx.compose.foundation.BorderStroke(
                                                1.dp, 
                                                if (uiState.selectedOptionIndex == index) com.example.ui.theme.SunstoneGold else MaterialTheme.colorScheme.outline.copy(alpha = 0.4f)
                                            )
                                        ) {
                                            Row(
                                                modifier = Modifier.padding(10.dp),
                                                verticalAlignment = Alignment.CenterVertically
                                            ) {
                                                RadioButton(
                                                    selected = uiState.selectedOptionIndex == index,
                                                    onClick = { viewModel.selectOption(index) },
                                                    colors = RadioButtonDefaults.colors(selectedColor = com.example.ui.theme.SunstoneGold)
                                                )
                                                Spacer(modifier = Modifier.width(8.dp))
                                                Text(
                                                    opt,
                                                    color = if (uiState.selectedOptionIndex == index) com.example.ui.theme.SummitGold else MaterialTheme.colorScheme.onSurface,
                                                    fontSize = (14 * fontScale).sp
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                            Spacer(modifier = Modifier.height(20.dp))
                            Button(
                                onClick = { 
                                    val isCorrect = (uiState.selectedOptionIndex == uiState.altCorrectIndex)
                                    viewModel.submitAlternateAnswer(isCorrect)
                                },
                                enabled = uiState.selectedOptionIndex != null,
                                colors = ButtonDefaults.buttonColors(containerColor = com.example.ui.theme.ContourEmerald),
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.fillMaxWidth().height(48.dp)
                            ) {
                                Text(
                                    "⛰️ Confirm Waypoint Answer",
                                    color = com.example.ui.theme.AbyssNavy,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                        ReplayState.RESULT -> {
                            val improved = uiState.outcomeState == "IMPROVED"
                            Text(
                                text = if (improved) "🧭" else "⚠️",
                                fontSize = 54.sp
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = if (improved) "True North Confirmed! (+15 GP)" else "Course Deviation Persists",
                                style = MaterialTheme.typography.headlineSmall,
                                fontFamily = com.example.ui.theme.CartographicSerif,
                                fontWeight = FontWeight.Bold,
                                color = if (improved) com.example.ui.theme.ContourEmerald else com.example.ui.theme.MagmaCrimson
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                "Next Action: ${uiState.nextBestAction}",
                                color = com.example.ui.theme.TopoContourMuted,
                                fontSize = 13.sp
                            )
                            Spacer(modifier = Modifier.height(24.dp))
                            Button(
                                onClick = { viewModel.loadCandidate() },
                                colors = ButtonDefaults.buttonColors(containerColor = com.example.ui.theme.GlacierAzure),
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.fillMaxWidth().height(48.dp)
                            ) {
                                Text(
                                    "🧭 Next Field Deviation",
                                    color = com.example.ui.theme.AbyssNavy,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
