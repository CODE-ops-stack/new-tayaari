package com.example.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.CartographicSerif
import com.example.viewmodel.PaperTwinViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PaperTwinScreen(
    viewModel: PaperTwinViewModel,
    examId: String,
    onBack: () -> Unit,
    onStartTest: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    com.example.ui.components.AtlasBackground {
      com.example.ui.components.TopographicBackground(lineColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.035f)) {
        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                TopAppBar(
                    title = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("🧭", fontSize = 20.sp)
                            Spacer(modifier = Modifier.width(8.dp))
                            Column {
                                Text(
                                    "Paper Twin: Geography Simulation",
                                    fontFamily = CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 18.sp,
                                    color = MaterialTheme.colorScheme.primary
                                )
                                Text(
                                    "Official UPSC / State PSC Examination DNA",
                                    fontSize = 10.sp,
                                    color = MaterialTheme.colorScheme.primary.copy(alpha = 0.7f)
                                )
                            }
                        }
                    },
                    navigationIcon = {
                        IconButton(onClick = onBack) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = MaterialTheme.colorScheme.primary)
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = Color.Transparent
                    )
                )
            }
        ) { padding ->
            Column(
                modifier = Modifier.padding(padding).padding(16.dp).fillMaxSize(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                if (uiState.paper == null && !uiState.isGenerating && uiState.error == null) {
                    Card(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp),
                        colors = CardDefaults.cardColors(containerColor = com.example.ui.theme.DeepBasalt),
                        border = androidx.compose.foundation.BorderStroke(1.dp, com.example.ui.theme.HydrosphereCyan.copy(alpha = 0.3f))
                    ) {
                        Column(modifier = Modifier.padding(20.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("🗺️", fontSize = 48.sp)
                            Spacer(modifier = Modifier.height(12.dp))
                            Text(
                                text = "Synthetic Examination Transect",
                                fontFamily = CartographicSerif,
                                fontWeight = FontWeight.Bold,
                                fontSize = 20.sp,
                                color = Color.White
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Generate a highly-accurate 50-question mock exam mirroring the exact syllabus weightage, statement-assertion ratio, and difficulty tiers of $examId.",
                                style = MaterialTheme.typography.bodyMedium,
                                color = com.example.ui.theme.TopoContourMuted,
                                textAlign = androidx.compose.ui.text.style.TextAlign.Center
                            )
                            Spacer(modifier = Modifier.height(24.dp))
                            Button(
                                onClick = { viewModel.generatePaper(examId, 50) },
                                colors = ButtonDefaults.buttonColors(containerColor = com.example.ui.theme.SunstoneGold),
                                shape = androidx.compose.foundation.shape.RoundedCornerShape(12.dp),
                                modifier = Modifier.fillMaxWidth().height(48.dp)
                            ) {
                                Text("Synthesize 50-MCQ Geography Mock Paper 🧭", color = Color.Black, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                } else if (uiState.isGenerating) {
                    CircularProgressIndicator(color = com.example.ui.theme.SunstoneGold)
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("Analyzing geographic syllabus DNA & synthesizing transect questions...", color = Color.White)
                } else if (uiState.error != null) {
                    Text("Error: ${uiState.error}", color = MaterialTheme.colorScheme.error)
                } else if (uiState.paper != null) {
                    val paper = uiState.paper!!
                    Text("Geography Paper Synthesized! 🧭", fontFamily = CartographicSerif, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold, color = Color.White)
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    Card(
                        modifier = Modifier.fillMaxWidth().padding(16.dp),
                        colors = CardDefaults.cardColors(containerColor = com.example.ui.theme.DeepBasalt),
                        border = androidx.compose.foundation.BorderStroke(1.dp, com.example.ui.theme.ContourEmerald.copy(alpha = 0.4f))
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text("Geodetic Blueprint Validation Report", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = com.example.ui.theme.ContourEmerald)
                            Spacer(modifier = Modifier.height(8.dp))
                            Text("Status: ${if (paper.report.passedValidation) "PASSED // 100% BLUEPRINT COMPLIANT" else "OFFLINE / INSUFFICIENT DATA"}", color = if (paper.report.passedValidation) com.example.ui.theme.ContourEmerald else MaterialTheme.colorScheme.error, fontWeight = FontWeight.Bold)
                            Text("Target Count: ${paper.report.targetCount} Questions", color = Color.White)
                            Text("Actual Count: ${paper.report.actualCount} Questions", color = Color.White)
                            
                            if (paper.report.actualCount == 0) {
                                Spacer(modifier = Modifier.height(10.dp))
                                Surface(
                                    color = com.example.ui.theme.MagmaCrimson.copy(alpha = 0.15f),
                                    shape = androidx.compose.foundation.shape.RoundedCornerShape(8.dp),
                                    border = androidx.compose.foundation.BorderStroke(1.dp, com.example.ui.theme.MagmaCrimson)
                                ) {
                                    Text(
                                        text = "📡 Questions are served 100% on-demand from the cloud. Connect to Wi-Fi or mobile data and generate again.",
                                        color = com.example.ui.theme.MagmaCrimson,
                                        fontSize = 12.sp,
                                        modifier = Modifier.padding(10.dp)
                                    )
                                }
                            }
                        }
                    }
                    
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(
                        onClick = onStartTest,
                        enabled = paper.report.actualCount > 0,
                        colors = ButtonDefaults.buttonColors(
                            containerColor = com.example.ui.theme.ContourEmerald,
                            disabledContainerColor = com.example.ui.theme.SlateBedrock
                        ),
                        shape = androidx.compose.foundation.shape.RoundedCornerShape(12.dp),
                        modifier = Modifier.fillMaxWidth().height(48.dp)
                    ) {
                        Text(
                            text = if (paper.report.actualCount > 0) "Begin Examination Expedition Now ⛰️" else "Connect to Internet to Begin", 
                            color = if (paper.report.actualCount > 0) Color.Black else com.example.ui.theme.TopoContourMuted, 
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
            }
        }
      }
    }
}
