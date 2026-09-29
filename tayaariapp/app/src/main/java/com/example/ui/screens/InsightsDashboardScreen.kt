package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.filled.Biotech
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.repository.LocalRepository
import com.example.model.ExamBlueprint
import kotlinx.coroutines.launch

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun InsightsDashboardScreen(
    localRepository: LocalRepository,
    profile: ExamBlueprint?,
    onStartMistakeReplay: () -> Unit = {},
    onBack: () -> Unit
) {
    val coroutineScope = rememberCoroutineScope()
    var blindSpots by remember { mutableStateOf<List<LocalRepository.BlindSpotDetail>>(emptyList()) }
    var confidenceReport by remember { mutableStateOf<LocalRepository.ConfidenceCalibrationReport?>(null) }
    var studyPlans by remember { mutableStateOf<Map<Int, com.example.repository.StudyPlan>>(emptyMap()) }
    var selectedPlan by remember { mutableStateOf<com.example.repository.StudyPlan?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    
    LaunchedEffect(Unit) {
        coroutineScope.launch {
            blindSpots = localRepository.getBlindSpots()
            confidenceReport = localRepository.getConfidenceCalibrationReport()
            studyPlans = localRepository.getStudyPlans()
            isLoading = false
        }
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Performance Insights") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = Color.White,
                    navigationIconContentColor = Color.White
                )
            )
        },
        containerColor = MaterialTheme.colorScheme.background
    ) { padding ->
        if (isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // === STUDY PLANS ===
                if (studyPlans.isNotEmpty()) {
                    item {
                        Text(
                            text = "Time-Based Study Plans",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Text(
                            text = "Choose a block length to get a customized, evidence-based learning sequence.",
                            style = MaterialTheme.typography.bodySmall,
                            color = Color.Gray,
                            modifier = Modifier.padding(bottom = 8.dp)
                        )
                    }

                    item {
                        Row(
                            modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            studyPlans.forEach { (duration, plan) ->
                                Card(
                                    modifier = Modifier.width(200.dp).clickable { selectedPlan = plan },
                                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer),
                                ) {
                                    Column(modifier = Modifier.padding(16.dp)) {
                                        Text("${duration}m Block", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSecondaryContainer)
                                        Spacer(modifier = Modifier.height(8.dp))
                                        plan.tasks.forEach { task ->
                                            Text("• ${task.title} (${task.expectedMinutes}m)", style = MaterialTheme.typography.bodySmall)
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                

                
                // === PAPER DNA ===
                if (profile != null && profile.examDna.isNotEmpty()) {
                    item {
                        Text(
                            text = "Exam DNA: ",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Text(
                            text = "Historical theme weightage and your alignment.",
                            style = MaterialTheme.typography.bodySmall,
                            color = Color.Gray,
                            modifier = Modifier.padding(bottom = 8.dp)
                        )
                    }

                    items(profile.examDna) { theme ->
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(containerColor = Color.White),
                            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Icon(Icons.Default.Biotech, contentDescription = "Theme", tint = MaterialTheme.colorScheme.primary, modifier = Modifier.size(20.dp))
                                        Spacer(modifier = Modifier.width(8.dp))
                                        Text(theme.themeName, fontWeight = FontWeight.Bold, fontSize = 16.sp)
                                    }
                                    Text("$(${theme.historicalWeightage}%)", fontWeight = FontWeight.ExtraBold, color = MaterialTheme.colorScheme.secondary, fontSize = 18.sp)
                                }
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(theme.description, style = MaterialTheme.typography.bodySmall, color = Color.DarkGray)
                                Spacer(modifier = Modifier.height(12.dp))
                                
                                // Mock User Mastery Bar
                                val masteryPercent = (40..90).random() / 100f // In a real system, we compute this based on questions grouped by this theme
                                val barColor = when {
                                    masteryPercent > 0.7f -> Color(0xFF4CAF50) // Green
                                    masteryPercent > 0.4f -> Color(0xFFFFC107) // Yellow
                                    else -> Color(0xFFF44336) // Red
                                }
                                
                                Text("Your Mastery", style = MaterialTheme.typography.labelSmall, color = Color.Gray)
                                Spacer(modifier = Modifier.height(4.dp))
                                Box(modifier = Modifier.fillMaxWidth().height(8.dp).clip(RoundedCornerShape(4.dp)).background(Color.LightGray.copy(alpha = 0.5f))) {
                                    Box(modifier = Modifier.fillMaxWidth(masteryPercent).fillMaxHeight().background(barColor))
                                }
                            }
                        }
                    }
                }

                // === CONFIDENCE CALIBRATION ===
                if (confidenceReport != null) {
                    item {
                        Text(
                            text = "Confidence Calibration",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                    }
                    
                    if (confidenceReport!!.overconfidenceDetected) {
                        item {
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                colors = CardDefaults.cardColors(containerColor = Color.White),
                                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                            ) {
                                Row(
                                    modifier = Modifier.padding(16.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(Icons.Default.Warning, contentDescription = "Warning", tint = Color.Red)
                                    Spacer(modifier = Modifier.width(16.dp))
                                    Column {
                                        Text("Overconfidence", style = MaterialTheme.typography.titleSmall)
                                        Text(confidenceReport!!.overconfidenceMessage, style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                                    }
                                }
                            }
                        }
                    }
                    
                    if (confidenceReport!!.underconfidenceDetected) {
                        item {
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                colors = CardDefaults.cardColors(containerColor = Color.White),
                                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                            ) {
                                Row(
                                    modifier = Modifier.padding(16.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(Icons.Default.Warning, contentDescription = "Warning", tint = Color(0xFFE65100))
                                    Spacer(modifier = Modifier.width(16.dp))
                                    Column {
                                        Text("Underconfidence", style = MaterialTheme.typography.titleSmall)
                                        Text(confidenceReport!!.underconfidenceMessage, style = MaterialTheme.typography.bodySmall, color = Color.Gray)
                                    }
                                }
                            }
                        }
                    }
                }
            
                // === BLIND SPOTS ===
                if (blindSpots.isNotEmpty()) {
                    item {
                        Text(
                            text = "Your Blind Spots",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Text(
                            text = "You are strong on direct facts, but statement-based questions are still causing mistakes.",
                            style = MaterialTheme.typography.bodySmall,
                            color = Color.Gray,
                            modifier = Modifier.padding(bottom = 8.dp)
                        )
                    }
                }
                
                items(blindSpots) { stat ->
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(containerColor = Color.White),
                        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                    ) {
                        Row(
                            modifier = Modifier.padding(16.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Icon(Icons.Default.Warning, contentDescription = "Warning", tint = Color(0xFFE65100))
                            Spacer(modifier = Modifier.width(16.dp))
                            Column {
                                Text(stat.topicName, style = MaterialTheme.typography.titleSmall)
                                
                                val simplePct = (stat.simpleCorrect.toFloat() / stat.simpleTotal * 100).toInt()
                                val complexPct = (stat.complexCorrect.toFloat() / stat.complexTotal * 100).toInt()
                                
                                val confidenceStr = when (stat.confidence) {
                                    LocalRepository.EvidenceConfidence.EARLY_SIGNAL -> "Early Signal"
                                    LocalRepository.EvidenceConfidence.EMERGING -> "Emerging Pattern"
                                    LocalRepository.EvidenceConfidence.CONFIRMED -> "Confirmed Weakness"
                                    else -> ""
                                }
                                
                                Text(
                                    text = "Confidence: $({confidenceStr})",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = if (stat.confidence == LocalRepository.EvidenceConfidence.CONFIRMED) Color.Red else Color.DarkGray,
                                    modifier = Modifier.padding(bottom = 4.dp, top = 2.dp)
                                )
                                
                                Text(
                                    text = "Why: You've answered $({stat.simpleTotal}) direct questions at $({simplePct})%, but only $({stat.complexTotal}) complex questions at $({complexPct})%.",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = Color.Gray
                                )
                                
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    text = "What to do: Practice more complex format questions from this topic.",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.primary
                                )
                            }
                        }
                    }
                }
            }
            
            if (selectedPlan != null) {
                AlertDialog(
                    onDismissRequest = { selectedPlan = null },
                    title = { Text("${selectedPlan!!.durationMinutes}m Study Plan") },
                    text = {
                        Column {
                            selectedPlan!!.tasks.forEach { task ->
                                Text("• ${task.title} (${task.expectedMinutes}m)", fontWeight = FontWeight.Bold)
                                Text(task.description, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(bottom = 8.dp))
                                if (task.title.contains("Mistake Replay", ignoreCase = true)) {
                                    Button(
                                        onClick = { 
                                            selectedPlan = null
                                            onStartMistakeReplay() 
                                        },
                                        modifier = Modifier.padding(bottom = 8.dp)
                                    ) {
                                        Text("Launch Mistake Replay")
                                    }
                                }
                            }
                        }
                    },
                    confirmButton = {
                        TextButton(onClick = { selectedPlan = null }) {
                            Text("Got it")
                        }
                    }
                )
            }
        }
    }
}
