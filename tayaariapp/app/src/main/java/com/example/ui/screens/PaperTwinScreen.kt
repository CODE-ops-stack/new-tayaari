package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Fill
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
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
    val scrollState = rememberScrollState()

    com.example.ui.components.AtlasBackground {
        com.example.ui.components.TopographicBackground(lineColor = ContourEmerald.copy(alpha = 0.035f)) {
            Scaffold(
                containerColor = Color.Transparent,
                topBar = {
                    TopAppBar(
                        title = {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("🏛️", fontSize = 22.sp)
                                Spacer(modifier = Modifier.width(10.dp))
                                Column {
                                    Text(
                                        text = "Paper Twin: Examination Hall DNA",
                                        fontFamily = CartographicSerif,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 17.sp,
                                        color = SunstoneGold
                                    )
                                    Text(
                                        text = "OFFICIAL UPSC / STATE PSC BLUEPRINT SYNTHESIS",
                                        fontFamily = CoordinatesMonospace,
                                        fontSize = 9.sp,
                                        letterSpacing = 0.8.sp,
                                        color = HydrosphereCyan
                                    )
                                }
                            }
                        },
                        navigationIcon = {
                            IconButton(onClick = onBack) {
                                Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = MaterialTheme.colorScheme.onSurface)
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
                        .fillMaxSize()
                        .padding(padding)
                        .verticalScroll(scrollState)
                        .padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    // Cadre Header Badge matching active target exam
                    ExaminationCadreSealCanvas(examId = examId)

                    Spacer(modifier = Modifier.height(16.dp))

                    if (uiState.paper == null && !uiState.isGenerating && uiState.error == null) {
                        // Pre-Synthesis State: Blueprint Specifications & Tactile OMR Practice
                        ExaminationBlueprintCard(examId = examId)

                        Spacer(modifier = Modifier.height(16.dp))

                        // Interactive Tactile OMR Bubble Sheet Simulation
                        InteractiveOmrBubblePracticeCard()

                        Spacer(modifier = Modifier.height(16.dp))

                        // Examination Hall Protocol & Mindset Briefing
                        ExaminationHallProtocolCard()

                        Spacer(modifier = Modifier.height(20.dp))

                        Button(
                            onClick = { viewModel.generatePaper(examId, 50) },
                            colors = ButtonDefaults.buttonColors(containerColor = SunstoneGold),
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(52.dp)
                        ) {
                            Icon(Icons.Default.Security, contentDescription = null, tint = Color.Black)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "Synthesize 50-MCQ Geography Mock Paper 🧭",
                                color = Color.Black,
                                fontWeight = FontWeight.Black,
                                fontSize = 14.sp
                            )
                        }
                    } else if (uiState.isGenerating) {
                        // Generating State: High-tech radar synthesis animation
                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(vertical = 32.dp),
                            colors = CardDefaults.cardColors(containerColor = DeepBasalt),
                            shape = RoundedCornerShape(16.dp),
                            border = BorderStroke(1.dp, HydrosphereCyan.copy(alpha = 0.4f))
                        ) {
                            Column(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(32.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                CircularProgressIndicator(
                                    color = SunstoneGold,
                                    strokeWidth = 3.dp,
                                    modifier = Modifier.size(54.dp)
                                )
                                Spacer(modifier = Modifier.height(20.dp))
                                Text(
                                    text = "Synthesizing Examination Transect...",
                                    fontFamily = CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 17.sp,
                                    color = Color.White
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Text(
                                    text = "Querying live cloud slices • Calibrating statement-assertion weightage • Balancing trap ratios against official syllabus DNA for $examId.",
                                    color = TopoContourMuted,
                                    fontSize = 12.sp,
                                    textAlign = TextAlign.Center,
                                    lineHeight = 17.sp
                                )
                            }
                        }
                    } else if (uiState.error != null) {
                        Surface(
                            color = MagmaCrimson.copy(alpha = 0.15f),
                            shape = RoundedCornerShape(12.dp),
                            border = BorderStroke(1.dp, MagmaCrimson),
                            modifier = Modifier.fillMaxWidth().padding(vertical = 16.dp)
                        ) {
                            Column(modifier = Modifier.padding(16.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                                Text("⚠️ SYNTHESIS ERROR", color = MagmaCrimson, fontWeight = FontWeight.Black, fontSize = 14.sp)
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(text = uiState.error ?: "Unknown error", color = MaterialTheme.colorScheme.onSurface, fontSize = 12.sp, textAlign = TextAlign.Center)
                                Spacer(modifier = Modifier.height(12.dp))
                                OutlinedButton(
                                    onClick = { viewModel.generatePaper(examId, 50) },
                                    border = BorderStroke(1.dp, SunstoneGold),
                                    colors = ButtonDefaults.outlinedButtonColors(contentColor = SunstoneGold)
                                ) {
                                    Text("Retry Synthesis 🔄")
                                }
                            }
                        }
                    } else if (uiState.paper != null) {
                        val paper = uiState.paper!!

                        // Paper Generated: Validation Certificate & Hall Seal Ready
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                            shape = RoundedCornerShape(16.dp),
                            border = BorderStroke(1.dp, ContourEmerald.copy(alpha = 0.5f))
                        ) {
                            Column(modifier = Modifier.padding(20.dp)) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Text("✅", fontSize = 20.sp)
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = "Official Blueprint Validation Certificate",
                                        fontFamily = CartographicSerif,
                                        style = MaterialTheme.typography.titleMedium,
                                        fontWeight = FontWeight.Bold,
                                        color = ContourEmerald
                                    )
                                }
                                Spacer(modifier = Modifier.height(10.dp))
                                Text(
                                    text = "STATUS: ${if (paper.report.passedValidation) "PASSED // 100% BLUEPRINT COMPLIANT" else "PROVISIONAL ONLINE TRANSECT"}",
                                    color = if (paper.report.passedValidation) ContourEmerald else SunstoneGold,
                                    fontFamily = CoordinatesMonospace,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 12.sp
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                    Text("Target Question Quota:", color = TopoContourMuted, fontSize = 12.sp)
                                    Text("${paper.report.targetCount} MCQs", color = MaterialTheme.colorScheme.onSurface, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                                }
                                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                                    Text("Synthesized in Paper:", color = TopoContourMuted, fontSize = 12.sp)
                                    Text("${paper.report.actualCount} MCQs", color = SunstoneGold, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                                }

                                if (paper.report.actualCount == 0) {
                                    Spacer(modifier = Modifier.height(12.dp))
                                    Surface(
                                        color = MagmaCrimson.copy(alpha = 0.15f),
                                        shape = RoundedCornerShape(8.dp),
                                        border = BorderStroke(1.dp, MagmaCrimson)
                                    ) {
                                        Text(
                                            text = "📡 Questions are served 100% on-demand from the cloud. Connect to internet and generate again.",
                                            color = MagmaCrimson,
                                            fontSize = 11.sp,
                                            modifier = Modifier.padding(10.dp)
                                        )
                                    }
                                }
                            }
                        }

                        Spacer(modifier = Modifier.height(16.dp))

                        // Examination Transect Specifications
                        Card(
                            modifier = Modifier.fillMaxWidth(),
                            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                            shape = RoundedCornerShape(12.dp),
                            border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.5f))
                        ) {
                            Column(modifier = Modifier.padding(16.dp)) {
                                Text(
                                    text = "📋 Examination Hall Transect Rules:",
                                    color = SunstoneGold,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 13.sp
                                )
                                Spacer(modifier = Modifier.height(6.dp))
                                Text("• Total Time Allotted: 60 Minutes (Strict Speed Training)", color = MaterialTheme.colorScheme.onSurface, fontSize = 11.5.sp)
                                Text("• Marking Scheme: +2.00 for Correct, -0.66 for Wrong", color = MaterialTheme.colorScheme.onSurface, fontSize = 11.5.sp)
                                Text("• Zero-Clue Integrity: Atmospheric instruments active, zero hints", color = MaterialTheme.colorScheme.onSurface, fontSize = 11.5.sp)
                                Text("• Tactile Elimination: Long-press options to strike through distractors", color = MaterialTheme.colorScheme.onSurface, fontSize = 11.5.sp)
                            }
                        }

                        Spacer(modifier = Modifier.height(24.dp))

                        Button(
                            onClick = onStartTest,
                            enabled = paper.report.actualCount > 0,
                            colors = ButtonDefaults.buttonColors(
                                containerColor = ContourEmerald,
                                disabledContainerColor = SlateBedrock
                            ),
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(54.dp)
                        ) {
                            Icon(Icons.Default.PlayArrow, contentDescription = null, tint = Color.Black)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = if (paper.report.actualCount > 0) "BREAK SEAL & BEGIN 50-MCQ EXPEDITION 🧭" else "Connect to Internet to Begin",
                                color = if (paper.report.actualCount > 0) Color.Black else TopoContourMuted,
                                fontWeight = FontWeight.Black,
                                fontSize = 14.sp
                            )
                        }
                    }
                }
            }
        }
    }
}

/**
 * Authentic Brass Cadre Examination Seal Canvas
 */
@Composable
fun ExaminationCadreSealCanvas(examId: String) {
    val cadreTitle = when {
        examId.contains("UPSC", ignoreCase = true) -> "UNION PUBLIC SERVICE COMMISSION • DHOLPUR HOUSE"
        examId.contains("BPSC", ignoreCase = true) -> "BIHAR PUBLIC SERVICE COMMISSION • 70TH CCE"
        examId.contains("SSC", ignoreCase = true) -> "STAFF SELECTION COMMISSION • CGL MERIT CORPS"
        else -> "INDIAN RAILWAYS RECRUITMENT • APEX TRANSECT"
    }

    val cadreMotto = when {
        examId.contains("UPSC", ignoreCase = true) -> "YOGA KARMASU KAUSHALAM • EXCELLENCE IN ACTION"
        examId.contains("BPSC", ignoreCase = true) -> "SUB-DIVISIONAL MAGISTRATE MERIT TRANSECT"
        examId.contains("SSC", ignoreCase = true) -> "CENTRAL SECRETARIAT SERVICE (ASO) PRESTIGE"
        else -> "LIFELINE OF THE NATION • RAILWAY COMMAND"
    }

    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant,
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.2.dp, SunstoneGold.copy(alpha = 0.5f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Box(
                modifier = Modifier
                    .size(90.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.surface),
                contentAlignment = Alignment.Center
            ) {
                Canvas(modifier = Modifier.size(86.dp)) {
                    val radius = size.minDimension / 2f
                    val center = Offset(size.width / 2f, size.height / 2f)

                    // Outer double brass rings
                    drawCircle(
                        color = SunstoneGold,
                        radius = radius - 2f,
                        style = Stroke(width = 2.5f)
                    )
                    drawCircle(
                        color = SunstoneGold.copy(alpha = 0.5f),
                        radius = radius - 8f,
                        style = Stroke(width = 1.2f)
                    )

                    // 12 Geodetic compass azimuth ticks around seal
                    for (i in 0 until 12) {
                        val angle = (i * 30) * (Math.PI / 180.0)
                        val startX = (center.x + (radius - 8f) * Math.cos(angle)).toFloat()
                        val startY = (center.y + (radius - 8f) * Math.sin(angle)).toFloat()
                        val endX = (center.x + (radius - 14f) * Math.cos(angle)).toFloat()
                        val endY = (center.y + (radius - 14f) * Math.sin(angle)).toFloat()
                        drawLine(
                            color = SunstoneGold,
                            start = Offset(startX, startY),
                            end = Offset(endX, endY),
                            strokeWidth = 1.5f
                        )
                    }

                    // Inner central emblem circle
                    drawCircle(
                        color = ContourEmerald.copy(alpha = 0.15f),
                        radius = radius - 18f,
                        style = Fill
                    )
                    drawCircle(
                        color = HydrosphereCyan.copy(alpha = 0.6f),
                        radius = radius - 18f,
                        style = Stroke(width = 1f)
                    )
                }

                Text(
                    text = if (examId.contains("BPSC", ignoreCase = true)) "🌾" else if (examId.contains("SSC", ignoreCase = true)) "⭐" else "🏛️",
                    fontSize = 32.sp
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            Text(
                text = cadreTitle,
                color = SunstoneGold,
                fontFamily = CartographicSerif,
                fontWeight = FontWeight.Black,
                fontSize = 12.sp,
                textAlign = TextAlign.Center,
                letterSpacing = 0.5.sp
            )

            Spacer(modifier = Modifier.height(4.dp))

            Text(
                text = cadreMotto,
                color = HydrosphereCyan,
                fontFamily = CoordinatesMonospace,
                fontSize = 9.sp,
                textAlign = TextAlign.Center,
                letterSpacing = 0.6.sp
            )
        }
    }
}

/**
 * Examination Blueprint Metrics Specification Card
 */
@Composable
fun ExaminationBlueprintCard(examId: String) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, HydrosphereCyan.copy(alpha = 0.35f))
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("📊", fontSize = 16.sp)
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "50-Question Blueprint Distribution",
                    color = SunstoneGold,
                    fontFamily = CartographicSerif,
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            val syllabusRows = listOf(
                Triple("Physical Geography (Geomorphology, Climate, Ocean)", "18 MCQs", "36%"),
                Triple("Indian Geography (Physiography, Drainage, Monsoon)", "18 MCQs", "36%"),
                Triple("Economic, Agriculture & Resource Geography", "10 MCQs", "20%"),
                Triple("Cartography, Map Projections & Regional Special", "4 MCQs", "8%")
            )

            syllabusRows.forEach { (topic, count, pct) ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(topic, color = MaterialTheme.colorScheme.onSurface, fontSize = 11.5.sp, modifier = Modifier.weight(1f))
                    Text(count, color = SunstoneGold, fontWeight = FontWeight.Bold, fontSize = 11.5.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Surface(
                        color = MaterialTheme.colorScheme.surface,
                        shape = RoundedCornerShape(4.dp),
                        border = BorderStroke(0.6.dp, HydrosphereCyan.copy(alpha = 0.4f))
                    ) {
                        Text(pct, color = HydrosphereCyan, fontSize = 10.sp, fontWeight = FontWeight.Bold, modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp))
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))
            HorizontalDivider(color = SlateBedrock, thickness = 0.8.dp)
            Spacer(modifier = Modifier.height(10.dp))

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("• Statement-Based (Pair Matching / AR): 42%", color = TopoContourMuted, fontSize = 10.5.sp)
                Text("• Strict Anti-Spoiler: 100%", color = ContourEmerald, fontSize = 10.5.sp, fontWeight = FontWeight.Bold)
            }
        }
    }
}

/**
 * Interactive Tactile OMR Bubble Sheet Practice Card
 * Zero spoilers: Candidates practice tactile bubble darkening and understand real-exam OMR rules!
 */
@Composable
fun InteractiveOmrBubblePracticeCard() {
    val haptic = LocalHapticFeedback.current
    val markedBubbles = remember { mutableStateMapOf<Int, String>() }
    var omrWarningMessage by remember { mutableStateOf<String?>(null) }

    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant,
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, ContourEmerald.copy(alpha = 0.45f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("✏️", fontSize = 16.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "TACTILE OMR PRACTICE SHEET",
                        color = ContourEmerald,
                        fontFamily = CoordinatesMonospace,
                        fontWeight = FontWeight.Black,
                        fontSize = 11.sp,
                        letterSpacing = 0.8.sp
                    )
                }
                if (markedBubbles.isNotEmpty()) {
                    Text(
                        text = "Clear Grid ↺",
                        color = TopoContourMuted,
                        fontSize = 10.sp,
                        modifier = Modifier.clickable {
                            markedBubbles.clear()
                            omrWarningMessage = null
                        }
                    )
                }
            }

            Spacer(modifier = Modifier.height(6.dp))

            Text(
                text = "Train muscle memory for authentic 2B pencil / black ballpoint darkening. Tap bubbles below to simulate official hall bubbling:",
                color = MaterialTheme.colorScheme.onSurface,
                fontSize = 11.sp,
                lineHeight = 15.sp
            )

            Spacer(modifier = Modifier.height(12.dp))

            // 5 Sample Practice OMR Rows (Q1 to Q5)
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                for (row in 1..5) {
                    val selectedCol = markedBubbles[row]
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .background(MaterialTheme.colorScheme.surface, RoundedCornerShape(8.dp))
                            .padding(horizontal = 12.dp, vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "Q0$row",
                            color = TopoContourMuted,
                            fontFamily = CoordinatesMonospace,
                            fontWeight = FontWeight.Bold,
                            fontSize = 12.sp,
                            modifier = Modifier.width(36.dp)
                        )

                        listOf("A", "B", "C", "D").forEach { optLetter ->
                            val isDarkened = selectedCol == optLetter

                            Box(
                                modifier = Modifier
                                    .size(32.dp)
                                    .clip(CircleShape)
                                    .background(if (isDarkened) Color(0xFF1E293B) else MaterialTheme.colorScheme.surfaceVariant)
                                    .border(
                                        width = if (isDarkened) 2.dp else 1.2.dp,
                                        color = if (isDarkened) SunstoneGold else TopoContourMuted.copy(alpha = 0.6f),
                                        shape = CircleShape
                                    )
                                    .clickable {
                                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                        if (selectedCol != null && selectedCol != optLetter) {
                                            omrWarningMessage = "⚠️ WARNING: Changing answers on real OMR leaves graphite residue or requires double-bubbling, which marks the question as invalid (-0.00 / rejected by optical scanner)!"
                                        }
                                        markedBubbles[row] = optLetter
                                    },
                                contentAlignment = Alignment.Center
                            ) {
                                if (isDarkened) {
                                    Canvas(modifier = Modifier.size(24.dp)) {
                                        drawCircle(
                                            color = Color.Black,
                                            radius = size.minDimension / 2f,
                                            style = Fill
                                        )
                                        drawCircle(
                                            color = SunstoneGold,
                                            radius = size.minDimension / 2f - 2f,
                                            style = Stroke(width = 1.2f)
                                        )
                                    }
                                }
                                Text(
                                    text = optLetter,
                                    color = if (isDarkened) SunstoneGold else MaterialTheme.colorScheme.onSurface,
                                    fontWeight = if (isDarkened) FontWeight.Black else FontWeight.Bold,
                                    fontSize = 11.sp
                                )
                            }
                        }
                    }
                }
            }

            if (omrWarningMessage != null) {
                Spacer(modifier = Modifier.height(10.dp))
                Surface(
                    color = MagmaCrimson.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(6.dp),
                    border = BorderStroke(0.8.dp, MagmaCrimson)
                ) {
                    Text(
                        text = omrWarningMessage!!,
                        color = MagmaCrimson,
                        fontSize = 10.5.sp,
                        lineHeight = 14.sp,
                        modifier = Modifier.padding(8.dp)
                    )
                }
            }
        }
    }
}

/**
 * Examination Hall Protocol & Mindset Briefing
 */
@Composable
fun ExaminationHallProtocolCard() {
    var isExpanded by remember { mutableStateOf(false) }

    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant,
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, SunstoneGold.copy(alpha = 0.35f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .clickable { isExpanded = !isExpanded },
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("🛡️", fontSize = 16.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "EXAMINATION HALL PROTOCOL // TOPPER STRATEGY",
                        color = SunstoneGold,
                        fontFamily = CoordinatesMonospace,
                        fontWeight = FontWeight.Black,
                        fontSize = 11.sp,
                        letterSpacing = 0.6.sp
                    )
                }
                Icon(
                    imageVector = if (isExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                    contentDescription = null,
                    tint = SunstoneGold
                )
            }

            AnimatedVisibility(visible = isExpanded) {
                Column(modifier = Modifier.padding(top = 12.dp)) {
                    Text(
                        text = "1. The 3-Pass Strategy:",
                        color = ContourEmerald,
                        fontWeight = FontWeight.Bold,
                        fontSize = 12.sp
                    )
                    Text(
                        text = "• Pass 1 (0-35 mins): Solve only 100% sure-shot questions (approx 25-30). Bubble immediately.\n• Pass 2 (35-50 mins): 50-50 eliminated questions. Statistically guaranteed net positive marks!\n• Pass 3 (50-60 mins): Guard against negative penalty traps. Never blind guess on 4 unknowns.",
                        color = MaterialTheme.colorScheme.onSurface,
                        fontSize = 11.sp,
                        lineHeight = 16.sp,
                        modifier = Modifier.padding(top = 2.dp, bottom = 8.dp)
                    )

                    Text(
                        text = "2. Anti-Panic Micro-Reset:",
                        color = HydrosphereCyan,
                        fontWeight = FontWeight.Bold,
                        fontSize = 12.sp
                    )
                    Text(
                        text = "If you encounter 2 tough questions in a row, take a 5-second breath. The cut-off for Prelims is typically 45-50%—you do NOT need to score 100% to qualify!",
                        color = MaterialTheme.colorScheme.onSurface,
                        fontSize = 11.sp,
                        lineHeight = 16.sp,
                        modifier = Modifier.padding(top = 2.dp)
                    )
                }
            }
        }
    }
}
