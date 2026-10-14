package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Cancel
import androidx.compose.material.icons.filled.RemoveCircleOutline
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ExamQuestion
import com.example.model.MCQQuestion

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ResultsScreen(
    questions: List<ExamQuestion>,
    userAnswers: Map<String, String>,
    score: java.math.BigDecimal,
    onDashboardClick: () -> Unit
) {
    com.example.ui.components.AtlasBackground {
        com.example.ui.components.TopographicBackground(lineColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.035f)) {
            Scaffold(
                containerColor = Color.Transparent,
                topBar = {
                    TopAppBar(
                        title = { 
                            Column {
                                Text(
                                    "Expedition Debrief 🧭", 
                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    color = com.example.ui.theme.SummitGold,
                                    fontSize = 18.sp
                                )
                                Text(
                                    "SURVEY SUMMARY & ELEVATION REPORT",
                                    fontFamily = com.example.ui.theme.CoordinatesMonospace,
                                    fontSize = 10.sp,
                                    color = com.example.ui.theme.GlacierAzure,
                                    letterSpacing = 1.sp
                                )
                            }
                        },
                        colors = TopAppBarDefaults.topAppBarColors(
                            containerColor = com.example.ui.theme.OceanicDark.copy(alpha = 0.95f)
                        )
                    )
                }
            ) { paddingValues ->
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues)
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    item {
                        com.example.ui.components.CartographicCoordinatesBanner(
                            coordinatesText = "📍 EXPEDITION TRANSECT COMPLETED // DEBRIEF LOG"
                        )
                    }
                    item {
                        ScoreHeader(score, questions.size)
                    }
                    item {
                        ElevationProfileVisualization(questions, userAnswers)
                    }
                    item {
                        BreakdownSection(questions, userAnswers)
                    }
                    item {
                        Text(
                            text = "Surveyed Waypoint Logs 📍",
                            style = MaterialTheme.typography.titleLarge,
                            fontFamily = com.example.ui.theme.CartographicSerif,
                            color = com.example.ui.theme.SummitGold,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(top = 12.dp, bottom = 4.dp)
                        )
                    }
                    items(questions) { q ->
                        val mcq = q as? MCQQuestion
                        if (mcq != null) {
                            val userAnswerId = userAnswers[mcq.id]
                            val isSkipped = userAnswerId == null
                            val opt = mcq.options.find { it.id == userAnswerId }
                            val isAbstain = opt?.role == com.example.model.OptionRole.ABSTAIN
                            
                            val outcome = when {
                                isSkipped -> com.example.model.AttemptOutcome.UNANSWERED
                                isAbstain -> com.example.model.AttemptOutcome.ABSTAINED
                                userAnswerId == mcq.correctAnswerId -> com.example.model.AttemptOutcome.CORRECT
                                else -> com.example.model.AttemptOutcome.INCORRECT
                            }

                            ReviewCard(
                                question = mcq,
                                userAnswerId = userAnswerId,
                                outcome = outcome
                            )
                        }
                    }
                    
                    item {
                        Button(
                            onClick = onDashboardClick,
                            modifier = Modifier.fillMaxWidth().height(50.dp).padding(vertical = 4.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = com.example.ui.theme.ContourEmerald),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Text(
                                "🧭 Return to Cadastre Central", 
                                color = com.example.ui.theme.AbyssNavy, 
                                fontWeight = FontWeight.Bold,
                                fontSize = 15.sp
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun ScoreHeader(score: java.math.BigDecimal, total: Int) {
    com.example.ui.components.AtlasCard(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(20.dp).fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                "⛰️ ELEVATION POINTS GAINED", 
                style = MaterialTheme.typography.labelSmall, 
                fontFamily = com.example.ui.theme.CoordinatesMonospace,
                color = com.example.ui.theme.GlacierAzure,
                letterSpacing = 1.sp
            )
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = "${score.setScale(2, java.math.RoundingMode.HALF_UP).stripTrailingZeros().toPlainString()} / $total GP",
                style = MaterialTheme.typography.displayMedium,
                fontFamily = com.example.ui.theme.CartographicSerif,
                color = com.example.ui.theme.SummitGold,
                fontWeight = FontWeight.Bold
            )
            val percentage = if (total > 0) (score.toFloat() / total * 100).toInt() else 0
            Spacer(modifier = Modifier.height(4.dp))
            Surface(
                color = com.example.ui.theme.OceanicDark,
                shape = RoundedCornerShape(6.dp),
                border = BorderStroke(1.dp, com.example.ui.theme.SlateBedrock)
            ) {
                Text(
                    text = "🧭 Field Mastery: $percentage% // Summit Transect",
                    color = com.example.ui.theme.ContourEmerald,
                    fontSize = 11.sp,
                    fontFamily = com.example.ui.theme.CoordinatesMonospace,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
                )
            }
        }
    }
}

@Composable
fun ElevationProfileVisualization(
    questions: List<ExamQuestion>,
    userAnswers: Map<String, String>
) {
    com.example.ui.components.AtlasCard(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                "Expedition Topographic Profile 🗺️", 
                style = MaterialTheme.typography.titleMedium, 
                fontFamily = com.example.ui.theme.CartographicSerif,
                color = com.example.ui.theme.SummitGold,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(14.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Bottom
            ) {
                questions.forEachIndexed { index, q ->
                    val mcq = q as? MCQQuestion
                    val ans = userAnswers[mcq?.id]
                    val isSkipped = mcq != null && ans == null
                    val option = mcq?.options?.find { it.id == ans }
                    val isAbstain = option?.role == com.example.model.OptionRole.ABSTAIN
                    val isCorrect = mcq != null && ans == mcq.correctAnswerId
                    
                    val barColor = when {
                        isSkipped -> com.example.ui.theme.MeridianMuted
                        isAbstain -> com.example.ui.theme.TopoContourMuted
                        isCorrect -> com.example.ui.theme.ContourEmerald
                        else -> com.example.ui.theme.MagmaCrimson
                    }
                    val height = if (isCorrect) 56.dp else if (isAbstain) 28.dp else if (isSkipped) 18.dp else 12.dp
                    
                    Box(
                        modifier = Modifier
                            .width(16.dp)
                            .height(height)
                            .clip(RoundedCornerShape(topStart = 4.dp, topEnd = 4.dp))
                            .background(barColor)
                    )
                }
            }
        }
    }
}

@Composable
fun BreakdownSection(
    questions: List<ExamQuestion>,
    userAnswers: Map<String, String>
) {
    val formatStats = mutableMapOf<String, Pair<Int, Int>>()

    questions.forEach { q ->
        val mcq = q as? MCQQuestion
        if (mcq != null) {
            val ans = userAnswers[mcq.id]
            val option = mcq.options.find { it.id == ans }
            val isAbstain = option?.role == com.example.model.OptionRole.ABSTAIN
            val isSkipped = ans == null
            
            if (!isAbstain && !isSkipped) {
                val isCorrect = ans == mcq.correctAnswerId
                val format = mcq.questionFormatType
                
                val current = formatStats.getOrDefault(format, Pair(0, 0))
                formatStats[format] = Pair(
                    current.first + (if (isCorrect) 1 else 0),
                    current.second + 1
                )
            }
        }
    }

    com.example.ui.components.AtlasCard(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                "Field Format Transect Breakdown 🧭", 
                style = MaterialTheme.typography.titleMedium, 
                fontFamily = com.example.ui.theme.CartographicSerif,
                fontWeight = FontWeight.Bold, 
                color = com.example.ui.theme.SummitGold
            )
            Spacer(modifier = Modifier.height(10.dp))
            formatStats.forEach { (format, stats) ->
                Row(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        "📍 $format", 
                        style = MaterialTheme.typography.bodyMedium,
                        color = com.example.ui.theme.AtlasParchment
                    )
                    val percentage = if (stats.second > 0) (stats.first * 100 / stats.second) else 0
                    Text(
                        "${stats.first}/${stats.second} ($percentage%)", 
                        style = MaterialTheme.typography.bodyMedium, 
                        fontFamily = com.example.ui.theme.CoordinatesMonospace,
                        color = if (percentage >= 50) com.example.ui.theme.ContourEmerald else com.example.ui.theme.SunstoneGold
                    )
                }
            }
        }
    }
}

@Composable
fun ReviewCard(
    question: MCQQuestion,
    userAnswerId: String?,
    outcome: com.example.model.AttemptOutcome
) {
    val borderColor = when (outcome) {
        com.example.model.AttemptOutcome.CORRECT -> com.example.ui.theme.ContourEmerald
        com.example.model.AttemptOutcome.INCORRECT -> com.example.ui.theme.MagmaCrimson
        com.example.model.AttemptOutcome.ABSTAINED -> com.example.ui.theme.TopoContourMuted
        com.example.model.AttemptOutcome.UNANSWERED -> com.example.ui.theme.MeridianMuted
    }
    val icon = when (outcome) {
        com.example.model.AttemptOutcome.CORRECT -> Icons.Filled.CheckCircle
        com.example.model.AttemptOutcome.ABSTAINED -> Icons.Filled.RemoveCircleOutline
        else -> Icons.Filled.Cancel
    }

    com.example.ui.components.AtlasCard(
        modifier = Modifier.fillMaxWidth(),
        borderColor = borderColor.copy(alpha = 0.5f)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = icon,
                    contentDescription = outcome.name,
                    tint = borderColor,
                    modifier = Modifier.size(18.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "🧭 ${question.questionFormatType.uppercase()} // ${question.chapterCode}",
                    style = MaterialTheme.typography.labelSmall,
                    fontFamily = com.example.ui.theme.CoordinatesMonospace,
                    color = com.example.ui.theme.GlacierAzure
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            
            Text(
                text = question.questionText,
                style = MaterialTheme.typography.bodyMedium,
                fontFamily = com.example.ui.theme.CartographicSerif,
                fontWeight = FontWeight.Medium,
                color = com.example.ui.theme.AtlasParchment,
                lineHeight = 22.sp
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            val userOption = question.options.find { it.id == userAnswerId }
            val correctOption = question.options.find { it.id == question.correctAnswerId }
            
            if (userAnswerId != null) {
                Text(
                    text = "Your Recorded Bearing: ${userOption?.text ?: "Unknown"}",
                    style = MaterialTheme.typography.bodySmall,
                    color = borderColor,
                    fontWeight = FontWeight.Bold
                )
            } else {
                Text(
                    text = "Your Bearing: Skipped Waypoint",
                    style = MaterialTheme.typography.bodySmall,
                    color = com.example.ui.theme.TopoContourMuted,
                    fontWeight = FontWeight.Bold
                )
            }
            
            if (outcome != com.example.model.AttemptOutcome.CORRECT) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Verified Atlas Key: ${correctOption?.text ?: "Unknown"}",
                    style = MaterialTheme.typography.bodySmall,
                    color = com.example.ui.theme.ContourEmerald,
                    fontWeight = FontWeight.Bold
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Surface(
                color = com.example.ui.theme.OceanicDark,
                shape = RoundedCornerShape(8.dp),
                border = BorderStroke(1.dp, com.example.ui.theme.SlateBedrock)
            ) {
                Text(
                    text = "🗺️ Cadastre Key: ${question.correctExplanation}",
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(10.dp),
                    color = com.example.ui.theme.TopoContourMuted,
                    lineHeight = 16.sp
                )
            }
        }
    }
}
