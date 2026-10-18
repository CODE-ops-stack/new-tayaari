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
import androidx.compose.material.icons.filled.Explore
import androidx.compose.material.icons.filled.Terrain
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
    var learnerProfile by remember { mutableStateOf<com.example.repository.LearnerProfile?>(null) }
    var selectedPlan by remember { mutableStateOf<com.example.repository.StudyPlan?>(null) }
    var isLoading by remember { mutableStateOf(true) }
    
    LaunchedEffect(Unit) {
        coroutineScope.launch {
            blindSpots = localRepository.getBlindSpots()
            confidenceReport = localRepository.getConfidenceCalibrationReport()
            studyPlans = localRepository.getStudyPlans()
            learnerProfile = localRepository.getLearnerProfile()
            isLoading = false
        }
    }
    
    com.example.ui.components.AtlasBackground {
        com.example.ui.components.TopographicBackground(lineColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.035f)) {
            Scaffold(
                containerColor = Color.Transparent,
                topBar = {
                    TopAppBar(
                        title = { 
                            Column {
                                Text(
                                    "Expedition Telemetry & DNA 🧭",
                                    color = com.example.ui.theme.SummitGold,
                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 18.sp
                                )
                                Text(
                                    "GEODETIC MASTERY & SYLLABUS AUDIT",
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
                                    tint = com.example.ui.theme.AtlasParchment
                                )
                            }
                        },
                        colors = TopAppBarDefaults.topAppBarColors(
                            containerColor = com.example.ui.theme.OceanicDark.copy(alpha = 0.95f)
                        )
                    )
                }
            ) { padding ->
                if (isLoading) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(color = com.example.ui.theme.GlacierAzure)
                    }
                } else {
                    LazyColumn(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(padding)
                            .padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        item {
                            com.example.ui.components.CartographicCoordinatesBanner(
                                coordinatesText = "📍 GEODETIC TELEMETRY // SYLLABUS MASTERY CADASTRE"
                            )
                        }

                        // === EXPEDITION TRANSECT PLANS ===
                        if (studyPlans.isNotEmpty()) {
                            item {
                                Text(
                                    text = "Expedition Transect Blocks 🧭",
                                    style = MaterialTheme.typography.titleMedium,
                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    color = com.example.ui.theme.SummitGold
                                )
                                Text(
                                    text = "Structured time-boxed fieldwork sequences to solidify your geographic mastery.",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = com.example.ui.theme.TopoContourMuted,
                                    modifier = Modifier.padding(bottom = 6.dp)
                                )
                            }

                            item {
                                Row(
                                    modifier = Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                                ) {
                                    studyPlans.forEach { (duration, plan) ->
                                        com.example.ui.components.AtlasCard(
                                            modifier = Modifier.width(220.dp).clickable { selectedPlan = plan },
                                            borderColor = com.example.ui.theme.SunstoneGold.copy(alpha = 0.5f)
                                        ) {
                                            Column(modifier = Modifier.padding(14.dp)) {
                                                Row(verticalAlignment = Alignment.CenterVertically) {
                                                    Text("⏱️", fontSize = 16.sp)
                                                    Spacer(modifier = Modifier.width(6.dp))
                                                    Text(
                                                        "${duration}m Transect", 
                                                        fontWeight = FontWeight.Bold, 
                                                        fontFamily = com.example.ui.theme.CartographicSerif,
                                                        color = com.example.ui.theme.SummitGold,
                                                        fontSize = 15.sp
                                                    )
                                                }
                                                Spacer(modifier = Modifier.height(8.dp))
                                                plan.tasks.forEach { task ->
                                                    Text(
                                                        "• ${task.title} (${task.expectedMinutes}m)", 
                                                        style = MaterialTheme.typography.bodySmall,
                                                        color = com.example.ui.theme.AtlasParchment.copy(alpha = 0.85f),
                                                        fontSize = 11.sp
                                                    )
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        
                        // === GEOGRAPHIC SYLLABUS DNA ===
                        if (profile != null && profile.examDna.isNotEmpty()) {
                            item {
                                Text(
                                    text = "Commission Syllabus Blueprint DNA 🗺️",
                                    style = MaterialTheme.typography.titleMedium,
                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    color = com.example.ui.theme.SummitGold
                                )
                                Text(
                                    text = "Historical examination weightage and your real geodetic mastery alignment.",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = com.example.ui.theme.TopoContourMuted,
                                    modifier = Modifier.padding(bottom = 6.dp)
                                )
                            }

                            items(profile.examDna) { theme ->
                                com.example.ui.components.AtlasCard(
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Column(modifier = Modifier.padding(14.dp)) {
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween,
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Row(verticalAlignment = Alignment.CenterVertically) {
                                                Icon(
                                                    Icons.Default.Terrain, 
                                                    contentDescription = "Theme", 
                                                    tint = com.example.ui.theme.GlacierAzure, 
                                                    modifier = Modifier.size(18.dp)
                                                )
                                                Spacer(modifier = Modifier.width(8.dp))
                                                Text(
                                                    theme.themeName, 
                                                    fontWeight = FontWeight.Bold, 
                                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                                    color = com.example.ui.theme.AtlasParchment,
                                                    fontSize = 15.sp
                                                )
                                            }
                                            Text(
                                                "${theme.historicalWeightage}% Weight", 
                                                fontWeight = FontWeight.Bold, 
                                                fontFamily = com.example.ui.theme.CoordinatesMonospace,
                                                color = com.example.ui.theme.SunstoneGold, 
                                                fontSize = 13.sp
                                            )
                                        }
                                        Spacer(modifier = Modifier.height(6.dp))
                                        Text(
                                            theme.description, 
                                            style = MaterialTheme.typography.bodySmall, 
                                            color = com.example.ui.theme.TopoContourMuted
                                        )
                                        Spacer(modifier = Modifier.height(10.dp))
                                        
                                        // Dynamic Telemetry Mastery Progress Bar
                                        val matchedPerf = learnerProfile?.topicPerformances?.values?.firstOrNull {
                                            theme.themeName.contains(it.topicName, ignoreCase = true) || it.topicName.contains(theme.themeName, ignoreCase = true)
                                        }
                                        val masteryPercent = when {
                                            matchedPerf != null && matchedPerf.total > 0 -> matchedPerf.accuracy.toFloat().coerceIn(0.10f, 1.0f)
                                            learnerProfile != null && learnerProfile!!.totalQuestionsAttempted > 0 -> learnerProfile!!.overallAccuracy.toFloat().coerceIn(0.15f, 0.95f)
                                            else -> 0.40f
                                        }
                                        val (tierLabel, barColor) = when {
                                            masteryPercent >= 0.80f -> "Summit Tier (${(masteryPercent * 100).toInt()}%)" to com.example.ui.theme.ContourEmerald
                                            masteryPercent >= 0.60f -> "Mid-Ridge (${(masteryPercent * 100).toInt()}%)" to com.example.ui.theme.SunstoneGold
                                            masteryPercent >= 0.35f -> "Ascent Phase (${(masteryPercent * 100).toInt()}%)" to com.example.ui.theme.GlacierAzure
                                            else -> "Base Camp (${(masteryPercent * 100).toInt()}%)" to com.example.ui.theme.MagmaCrimson
                                        }
                                        
                                        Row(
                                            modifier = Modifier.fillMaxWidth(),
                                            horizontalArrangement = Arrangement.SpaceBetween
                                        ) {
                                            Text(
                                                "Field Proficiency", 
                                                style = MaterialTheme.typography.labelSmall, 
                                                fontFamily = com.example.ui.theme.CoordinatesMonospace,
                                                color = com.example.ui.theme.GlacierAzure
                                            )
                                            Text(
                                                tierLabel, 
                                                style = MaterialTheme.typography.labelSmall, 
                                                fontFamily = com.example.ui.theme.CoordinatesMonospace,
                                                color = barColor
                                            )
                                        }
                                        Spacer(modifier = Modifier.height(4.dp))
                                        Box(
                                            modifier = Modifier
                                                .fillMaxWidth()
                                                .height(6.dp)
                                                .clip(RoundedCornerShape(3.dp))
                                                .background(com.example.ui.theme.OceanicDark)
                                        ) {
                                            Box(
                                                modifier = Modifier
                                                    .fillMaxWidth(masteryPercent)
                                                    .fillMaxHeight()
                                                    .background(barColor)
                                            )
                                        }
                                    }
                                }
                            }
                        }

                        // === COMPASS CALIBRATION ===
                        if (confidenceReport != null) {
                            item {
                                Text(
                                    text = "Compass Calibration (Hazard Analysis) 🧭",
                                    style = MaterialTheme.typography.titleMedium,
                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    color = com.example.ui.theme.SummitGold
                                )
                            }
                            
                            if (confidenceReport!!.overconfidenceDetected) {
                                item {
                                    com.example.ui.components.AtlasCard(
                                        modifier = Modifier.fillMaxWidth(),
                                        borderColor = com.example.ui.theme.MagmaCrimson.copy(alpha = 0.6f)
                                    ) {
                                        Row(
                                            modifier = Modifier.padding(14.dp),
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Icon(
                                                Icons.Default.Warning, 
                                                contentDescription = "Warning", 
                                                tint = com.example.ui.theme.MagmaCrimson,
                                                modifier = Modifier.size(24.dp)
                                            )
                                            Spacer(modifier = Modifier.width(12.dp))
                                            Column {
                                                Text(
                                                    "Overconfidence Hazard Detected ⚠️", 
                                                    style = MaterialTheme.typography.titleSmall,
                                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                                    color = com.example.ui.theme.MagmaCrimson,
                                                    fontWeight = FontWeight.Bold
                                                )
                                                Text(
                                                    confidenceReport!!.overconfidenceMessage, 
                                                    style = MaterialTheme.typography.bodySmall, 
                                                    color = com.example.ui.theme.TopoContourMuted
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                            
                            if (confidenceReport!!.underconfidenceDetected) {
                                item {
                                    com.example.ui.components.AtlasCard(
                                        modifier = Modifier.fillMaxWidth(),
                                        borderColor = com.example.ui.theme.SunstoneGold.copy(alpha = 0.6f)
                                    ) {
                                        Row(
                                            modifier = Modifier.padding(14.dp),
                                            verticalAlignment = Alignment.CenterVertically
                                        ) {
                                            Icon(
                                                Icons.Default.Explore, 
                                                contentDescription = "Warning", 
                                                tint = com.example.ui.theme.SunstoneGold,
                                                modifier = Modifier.size(24.dp)
                                            )
                                            Spacer(modifier = Modifier.width(12.dp))
                                            Column {
                                                Text(
                                                    "Cautious Navigation // Underconfidence", 
                                                    style = MaterialTheme.typography.titleSmall,
                                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                                    color = com.example.ui.theme.SunstoneGold,
                                                    fontWeight = FontWeight.Bold
                                                )
                                                Text(
                                                    confidenceReport!!.underconfidenceMessage, 
                                                    style = MaterialTheme.typography.bodySmall, 
                                                    color = com.example.ui.theme.TopoContourMuted
                                                )
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    
                        // === TOPOGRAPHIC BLIND SPOTS ===
                        item {
                            Text(
                                text = "Topographic Blind Spots & Hazards ⚠️",
                                style = MaterialTheme.typography.titleMedium,
                                fontFamily = com.example.ui.theme.CartographicSerif,
                                fontWeight = FontWeight.Bold,
                                color = com.example.ui.theme.SummitGold
                            )
                            Text(
                                text = "Discrepancy audit between direct recall and multi-statement terrain questions.",
                                style = MaterialTheme.typography.bodySmall,
                                color = com.example.ui.theme.TopoContourMuted,
                                modifier = Modifier.padding(bottom = 6.dp)
                            )
                        }

                        if (blindSpots.isEmpty()) {
                            item {
                                com.example.ui.components.AtlasCard(
                                    modifier = Modifier.fillMaxWidth(),
                                    borderColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.5f)
                                ) {
                                    Row(
                                        modifier = Modifier.padding(14.dp),
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Text("🛡️", fontSize = 24.sp)
                                        Spacer(modifier = Modifier.width(12.dp))
                                        Column {
                                            Text(
                                                "Zero Topographic Blind Spots Detected",
                                                style = MaterialTheme.typography.titleSmall,
                                                fontFamily = com.example.ui.theme.CartographicSerif,
                                                color = com.example.ui.theme.ContourEmerald,
                                                fontWeight = FontWeight.Bold
                                            )
                                            Text(
                                                "No significant divergence between simple fact retrieval and complex statement analysis. Your cartographic intuition is balanced.",
                                                style = MaterialTheme.typography.bodySmall,
                                                color = com.example.ui.theme.TopoContourMuted
                                            )
                                        }
                                    }
                                }
                            }
                        }
                        
                        items(blindSpots) { stat ->
                            com.example.ui.components.AtlasCard(
                                modifier = Modifier.fillMaxWidth(),
                                borderColor = com.example.ui.theme.SunstoneGold.copy(alpha = 0.4f)
                            ) {
                                Row(
                                    modifier = Modifier.padding(14.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        Icons.Default.Warning, 
                                        contentDescription = "Warning", 
                                        tint = com.example.ui.theme.SunstoneGold,
                                        modifier = Modifier.size(24.dp)
                                    )
                                    Spacer(modifier = Modifier.width(12.dp))
                                    Column {
                                        Text(
                                            "📍 ${stat.topicName}", 
                                            style = MaterialTheme.typography.titleSmall,
                                            fontFamily = com.example.ui.theme.CartographicSerif,
                                            color = com.example.ui.theme.AtlasParchment,
                                            fontWeight = FontWeight.Bold
                                        )
                                        
                                        val simplePct = if (stat.simpleTotal > 0) (stat.simpleCorrect.toFloat() / stat.simpleTotal * 100).toInt() else 0
                                        val complexPct = if (stat.complexTotal > 0) (stat.complexCorrect.toFloat() / stat.complexTotal * 100).toInt() else 0
                                        
                                        val confidenceStr = when (stat.confidence) {
                                            LocalRepository.EvidenceConfidence.EARLY_SIGNAL -> "Early Signal"
                                            LocalRepository.EvidenceConfidence.EMERGING -> "Emerging Pattern"
                                            LocalRepository.EvidenceConfidence.CONFIRMED -> "Confirmed Hazard"
                                            else -> ""
                                        }
                                        
                                        Text(
                                            text = "Evidence: $confidenceStr",
                                            style = MaterialTheme.typography.bodySmall,
                                            fontFamily = com.example.ui.theme.CoordinatesMonospace,
                                            color = if (stat.confidence == LocalRepository.EvidenceConfidence.CONFIRMED) com.example.ui.theme.MagmaCrimson else com.example.ui.theme.SunstoneGold,
                                            modifier = Modifier.padding(bottom = 2.dp, top = 2.dp)
                                        )
                                        
                                        Text(
                                            text = "Answered ${stat.simpleTotal} direct questions at $simplePct%, but ${stat.complexTotal} multi-statement questions at $complexPct%.",
                                            style = MaterialTheme.typography.bodySmall,
                                            color = com.example.ui.theme.TopoContourMuted
                                        )
                                        
                                        Spacer(modifier = Modifier.height(6.dp))
                                        Text(
                                            text = "🧭 Recommended Action: Undertake multi-statement transects for this cadastre.",
                                            style = MaterialTheme.typography.labelSmall,
                                            color = com.example.ui.theme.GlacierAzure
                                        )
                                    }
                                }
                            }
                        }
                    }
                    
                    if (selectedPlan != null) {
                        AlertDialog(
                            onDismissRequest = { selectedPlan = null },
                            title = { 
                                Text(
                                    "🧭 ${selectedPlan!!.durationMinutes}m Transect Plan",
                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    color = com.example.ui.theme.SummitGold
                                ) 
                            },
                            text = {
                                Column {
                                    selectedPlan!!.tasks.forEach { task ->
                                        Text("• ${task.title} (${task.expectedMinutes}m)", fontWeight = FontWeight.Bold, color = com.example.ui.theme.AtlasParchment)
                                        Text(task.description, style = MaterialTheme.typography.bodySmall, color = com.example.ui.theme.TopoContourMuted, modifier = Modifier.padding(bottom = 8.dp))
                                        if (task.title.contains("Mistake Replay", ignoreCase = true)) {
                                            Button(
                                                onClick = { 
                                                    selectedPlan = null
                                                    onStartMistakeReplay() 
                                                },
                                                modifier = Modifier.padding(bottom = 8.dp),
                                                colors = ButtonDefaults.buttonColors(containerColor = com.example.ui.theme.ContourEmerald)
                                            ) {
                                                Text("🧭 Launch Course Correction", color = com.example.ui.theme.AbyssNavy, fontWeight = FontWeight.Bold)
                                            }
                                        }
                                    }
                                }
                            },
                            confirmButton = {
                                TextButton(onClick = { selectedPlan = null }) {
                                    Text("Understood", color = com.example.ui.theme.GlacierAzure)
                                }
                            },
                            containerColor = com.example.ui.theme.DeepBasalt
                        )
                    }
                }
            }
        }
    }
}
