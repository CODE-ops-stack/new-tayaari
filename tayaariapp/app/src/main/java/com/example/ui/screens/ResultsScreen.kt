package com.example.ui.screens

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Cancel
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.RemoveCircleOutline
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.WorkspacePremium
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Fill
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ExamQuestion
import com.example.model.MCQQuestion
import com.example.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ResultsScreen(
    questions: List<ExamQuestion>,
    userAnswers: Map<String, String>,
    score: java.math.BigDecimal,
    onDashboardClick: () -> Unit
) {
    val totalQuestions = questions.size
    val correctCount = questions.count { q ->
        val mcq = q as? MCQQuestion
        mcq != null && userAnswers[mcq.id] == mcq.correctAnswerId
    }
    val wrongCount = questions.count { q ->
        val mcq = q as? MCQQuestion
        val ans = userAnswers[mcq?.id]
        val opt = mcq?.options?.find { it.id == ans }
        val isAbstain = opt?.role == com.example.model.OptionRole.ABSTAIN
        mcq != null && ans != null && !isAbstain && ans != mcq.correctAnswerId
    }
    val percentage = if (totalQuestions > 0) (correctCount * 100 / totalQuestions) else 0

    com.example.ui.components.AtlasBackground {
        com.example.ui.components.TopographicBackground(lineColor = ContourEmerald.copy(alpha = 0.035f)) {
            Scaffold(
                containerColor = Color.Transparent,
                topBar = {
                    TopAppBar(
                        title = {
                            Column {
                                Text(
                                    "Expedition Debrief 🧭",
                                    fontFamily = CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    color = SummitGold,
                                    fontSize = 18.sp
                                )
                                Text(
                                    "SURVEY SUMMARY & ELEVATION REPORT",
                                    fontFamily = CoordinatesMonospace,
                                    fontSize = 10.sp,
                                    color = GlacierAzure,
                                    letterSpacing = 1.sp
                                )
                            }
                        },
                        colors = TopAppBarDefaults.topAppBarColors(
                            containerColor = OceanicDark.copy(alpha = 0.95f)
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

                    // 1. Overall Score Header
                    item {
                        ScoreHeader(score, totalQuestions, percentage)
                    }

                    // 2. Interactive Cadre Peak Elevation Ascent Canvas
                    item {
                        CadrePeakAscentCanvas(percentage = percentage)
                    }

                    // 3. Rank Shield & Negative Marks Defused Summary Card
                    item {
                        RankShieldSummaryCard(
                            correctCount = correctCount,
                            wrongCount = wrongCount,
                            totalCount = totalQuestions
                        )
                    }

                    // 4. Transect Bar Visualization
                    item {
                        ElevationProfileVisualization(questions, userAnswers)
                    }

                    // 5. Question Format Breakdown
                    item {
                        BreakdownSection(questions, userAnswers)
                    }

                    // 6. Surveyed Waypoint Review Section Header
                    item {
                        Text(
                            text = "Surveyed Waypoint Logs 📍",
                            style = MaterialTheme.typography.titleLarge,
                            fontFamily = CartographicSerif,
                            color = SummitGold,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(top = 12.dp, bottom = 4.dp)
                        )
                    }

                    // 7. Question-by-Question Review Cards
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

                    // 8. Certified Expedition Stamp
                    item {
                        CertifiedExpeditionSealStamp()
                    }

                    // 9. Return to Central Dashboard Button
                    item {
                        Button(
                            onClick = onDashboardClick,
                            modifier = Modifier
                                .fillMaxWidth()
                                .height(52.dp)
                                .padding(vertical = 4.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = ContourEmerald),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Text(
                                "🧭 Return to Cadastre Central",
                                color = AbyssNavy,
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

/**
 * Score Summary Header with Field Mastery Gauge
 */
@Composable
fun ScoreHeader(score: java.math.BigDecimal, total: Int, percentage: Int) {
    com.example.ui.components.AtlasCard(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier
                .padding(20.dp)
                .fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                "⛰️ ELEVATION POINTS GAINED",
                style = MaterialTheme.typography.labelSmall,
                fontFamily = CoordinatesMonospace,
                color = GlacierAzure,
                letterSpacing = 1.sp
            )
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = "${score.setScale(2, java.math.RoundingMode.HALF_UP).stripTrailingZeros().toPlainString()} / $total GP",
                style = MaterialTheme.typography.displayMedium,
                fontFamily = CartographicSerif,
                color = SummitGold,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(6.dp))
            Surface(
                color = OceanicDark,
                shape = RoundedCornerShape(6.dp),
                border = BorderStroke(1.dp, SlateBedrock)
            ) {
                Text(
                    text = "🧭 Field Mastery: $percentage% // Summit Transect",
                    color = if (percentage >= 65) ContourEmerald else SunstoneGold,
                    fontSize = 11.sp,
                    fontFamily = CoordinatesMonospace,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp)
                )
            }
        }
    }
}

/**
 * Cadre Peak Elevation Ascent Canvas:
 * Visualizes the aspirant's score as an expedition ascent up the Cadre Peak
 */
@Composable
fun CadrePeakAscentCanvas(percentage: Int) {
    val animatedPercent by animateFloatAsState(
        targetValue = percentage / 100f,
        animationSpec = tween(1200),
        label = "ascentAnim"
    )

    val (campName, altitudeMeters, campColor) = when {
        percentage >= 80 -> Triple("Everest Summit • Cadre Top 100", "8,848m", ContourEmerald)
        percentage >= 65 -> Triple("Hillary Step • Cutoff Secured", "7,800m", HydrosphereCyan)
        percentage >= 45 -> Triple("Ridge Camp 2 • Acclimatization", "5,400m", SunstoneGold)
        else -> Triple("Base Camp • Terrain Scout", "3,200m", TopoContourMuted)
    }

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.dp, SunstoneGold.copy(alpha = 0.4f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("🏔️", fontSize = 16.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "CADRE PEAK EXPEDITION ASCENT",
                        color = SunstoneGold,
                        fontFamily = CoordinatesMonospace,
                        fontWeight = FontWeight.Black,
                        fontSize = 11.sp,
                        letterSpacing = 0.8.sp
                    )
                }
                Surface(color = OceanicDark, shape = RoundedCornerShape(4.dp)) {
                    Text(
                        text = "$altitudeMeters ELEV",
                        color = campColor,
                        fontFamily = CoordinatesMonospace,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Mountain Ascent Canvas
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(130.dp)
                    .background(OceanicDark, RoundedCornerShape(10.dp))
                    .border(0.8.dp, SlateBedrock, RoundedCornerShape(10.dp))
                    .padding(8.dp)
            ) {
                Canvas(modifier = Modifier.fillMaxSize()) {
                    val w = size.width
                    val h = size.height

                    // Background mountain slope contours
                    val slopePath = Path().apply {
                        moveTo(0f, h * 0.9f)
                        cubicTo(
                            w * 0.3f, h * 0.85f,
                            w * 0.5f, h * 0.45f,
                            w * 0.85f, h * 0.15f
                        )
                        lineTo(w, h * 0.1f)
                        lineTo(w, h)
                        lineTo(0f, h)
                        close()
                    }
                    drawPath(path = slopePath, color = DeepBasalt.copy(alpha = 0.8f))

                    // Draw ridge crest line
                    val ridgeLine = Path().apply {
                        moveTo(0f, h * 0.9f)
                        cubicTo(
                            w * 0.3f, h * 0.85f,
                            w * 0.5f, h * 0.45f,
                            w * 0.85f, h * 0.15f
                        )
                        lineTo(w, h * 0.1f)
                    }
                    drawPath(path = ridgeLine, color = SunstoneGold, style = Stroke(width = 2.5f))

                    // 4 Major Expedition Camps along the ridge
                    val campPoints = listOf(
                        Pair(0.15f, 0.88f), // Base Camp
                        Pair(0.42f, 0.65f), // Camp 2
                        Pair(0.68f, 0.35f), // Hillary Step
                        Pair(0.92f, 0.12f)  // Everest Summit
                    )
                    campPoints.forEach { (nx, ny) ->
                        val cx = nx * w
                        val cy = ny * h
                        drawCircle(color = Color.Black, radius = 5f, center = Offset(cx, cy))
                        drawCircle(color = SunstoneGold, radius = 4f, center = Offset(cx, cy))
                    }

                    // Climber Marker pinned at current score
                    val climberNormX = (animatedPercent).coerceIn(0.08f, 0.94f)
                    val climberNormY = 0.9f - (climberNormX * 0.8f) // Linear approximation along the ridge
                    val climberX = climberNormX * w
                    val climberY = climberNormY * h

                    // Draw climber beacon pulse
                    drawCircle(color = campColor.copy(alpha = 0.3f), radius = 14f, center = Offset(climberX, climberY))
                    drawCircle(color = campColor, radius = 7f, center = Offset(climberX, climberY))
                    drawCircle(color = Color.White, radius = 3f, center = Offset(climberX, climberY))
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = "📍 Current Position: $campName",
                color = campColor,
                fontWeight = FontWeight.Bold,
                fontSize = 12.sp
            )
            Spacer(modifier = Modifier.height(2.dp))
            Text(
                text = if (percentage >= 65) {
                    "Outstanding endurance! You cleared the critical geodetic cutoff. Maintain this consistency to cement your top-tier cadre rank."
                } else {
                    "Solid reconnaissance transect. Review the distractor dissections below to convert near-misses into guaranteed summit points."
                },
                color = TopoContourMuted,
                fontSize = 11.sp,
                lineHeight = 15.sp
            )
        }
    }
}

/**
 * Rank Shield & Negative Marks Defused Summary Card
 */
@Composable
fun RankShieldSummaryCard(correctCount: Int, wrongCount: Int, totalCount: Int) {
    val ranksProtected = (correctCount * 320) + (wrongCount * 140)
    val penaltyDefended = String.format("%.2f", wrongCount * 0.66)

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, ContourEmerald.copy(alpha = 0.45f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Default.Shield, contentDescription = null, tint = ContourEmerald, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "RANK SHIELD & EXAM HALL DEFENSE METRICS",
                    color = ContourEmerald,
                    fontFamily = CoordinatesMonospace,
                    fontWeight = FontWeight.Black,
                    fontSize = 11.sp,
                    letterSpacing = 0.6.sp
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Column(modifier = Modifier.weight(1f)) {
                    Text("Ranks Protected", color = TopoContourMuted, fontSize = 10.sp)
                    Text("+$ranksProtected", color = SunstoneGold, fontWeight = FontWeight.Black, fontSize = 16.sp)
                    Text("vs average candidate pool", color = TopoContourMuted, fontSize = 9.5.sp)
                }

                Column(modifier = Modifier.weight(1f)) {
                    Text("Negative Penalties Defused", color = TopoContourMuted, fontSize = 10.sp)
                    Text("-$penaltyDefended Marks", color = ContourEmerald, fontWeight = FontWeight.Black, fontSize = 16.sp)
                    Text("neutralized in training", color = TopoContourMuted, fontSize = 9.5.sp)
                }
            }

            Spacer(modifier = Modifier.height(10.dp))
            HorizontalDivider(color = SlateBedrock, thickness = 0.8.dp)
            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "💡 Topper Wisdom: Mistakes discovered and understood here in practice are 100% immune from tripping you on exam day.",
                color = AtlasParchment,
                fontSize = 11.sp,
                lineHeight = 15.sp,
                fontStyle = androidx.compose.ui.text.font.FontStyle.Italic
            )
        }
    }
}

/**
 * Topographic Elevation Profile visualization of questions
 */
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
                fontFamily = CartographicSerif,
                color = SummitGold,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(14.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(2.dp),
                verticalAlignment = Alignment.Bottom
            ) {
                questions.forEach { q ->
                    val mcq = q as? MCQQuestion
                    val ans = userAnswers[mcq?.id]
                    val isSkipped = mcq != null && ans == null
                    val option = mcq?.options?.find { it.id == ans }
                    val isAbstain = option?.role == com.example.model.OptionRole.ABSTAIN
                    val isCorrect = mcq != null && ans == mcq.correctAnswerId

                    val barColor = when {
                        isSkipped -> MeridianMuted
                        isAbstain -> TopoContourMuted
                        isCorrect -> ContourEmerald
                        else -> MagmaCrimson
                    }
                    val height = if (isCorrect) 44.dp else if (isAbstain) 22.dp else if (isSkipped) 14.dp else 10.dp

                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .height(height)
                            .clip(RoundedCornerShape(topStart = 2.dp, topEnd = 2.dp))
                            .background(barColor)
                    )
                }
            }
        }
    }
}

/**
 * Format Breakdown Section
 */
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
                fontFamily = CartographicSerif,
                fontWeight = FontWeight.Bold,
                color = SummitGold
            )
            Spacer(modifier = Modifier.height(10.dp))
            formatStats.forEach { (format, stats) ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        "📍 $format",
                        style = MaterialTheme.typography.bodyMedium,
                        color = AtlasParchment
                    )
                    val percentage = if (stats.second > 0) (stats.first * 100 / stats.second) else 0
                    Text(
                        "${stats.first}/${stats.second} ($percentage%)",
                        style = MaterialTheme.typography.bodyMedium,
                        fontFamily = CoordinatesMonospace,
                        color = if (percentage >= 50) ContourEmerald else SunstoneGold
                    )
                }
            }
        }
    }
}

/**
 * Individual Question Review Card
 */
@Composable
fun ReviewCard(
    question: MCQQuestion,
    userAnswerId: String?,
    outcome: com.example.model.AttemptOutcome
) {
    val borderColor = when (outcome) {
        com.example.model.AttemptOutcome.CORRECT -> ContourEmerald
        com.example.model.AttemptOutcome.INCORRECT -> MagmaCrimson
        com.example.model.AttemptOutcome.ABSTAINED -> TopoContourMuted
        com.example.model.AttemptOutcome.UNANSWERED -> MeridianMuted
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
                    fontFamily = CoordinatesMonospace,
                    color = GlacierAzure
                )
            }
            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = question.questionText,
                style = MaterialTheme.typography.bodyMedium,
                fontFamily = CartographicSerif,
                fontWeight = FontWeight.Medium,
                color = AtlasParchment,
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
                    color = TopoContourMuted,
                    fontWeight = FontWeight.Bold
                )
            }

            if (outcome != com.example.model.AttemptOutcome.CORRECT) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Verified Atlas Key: ${correctOption?.text ?: "Unknown"}",
                    style = MaterialTheme.typography.bodySmall,
                    color = ContourEmerald,
                    fontWeight = FontWeight.Bold
                )
            }

            Spacer(modifier = Modifier.height(8.dp))

            Surface(
                color = OceanicDark,
                shape = RoundedCornerShape(8.dp),
                border = BorderStroke(1.dp, SlateBedrock)
            ) {
                Text(
                    text = "🗺️ Cadastre Key: ${question.correctExplanation}",
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(10.dp),
                    color = TopoContourMuted,
                    lineHeight = 16.sp
                )
            }
        }
    }
}

/**
 * Official Expedition Survey Seal Stamp
 */
@Composable
fun CertifiedExpeditionSealStamp() {
    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, SunstoneGold.copy(alpha = 0.35f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(14.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .clip(CircleShape)
                    .background(OceanicDark)
                    .border(1.2.dp, SunstoneGold, CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.WorkspacePremium,
                    contentDescription = null,
                    tint = SunstoneGold,
                    modifier = Modifier.size(24.dp)
                )
            }

            Spacer(modifier = Modifier.width(12.dp))

            Column {
                Text(
                    text = "TAYAARI GEODETIC SURVEY CORPS",
                    color = SunstoneGold,
                    fontFamily = CoordinatesMonospace,
                    fontWeight = FontWeight.Black,
                    fontSize = 10.5.sp,
                    letterSpacing = 0.6.sp
                )
                Text(
                    text = "Expedition Verified • Transect Logged in Memory Vault",
                    color = TopoContourMuted,
                    fontSize = 10.sp
                )
            }
        }
    }
}
