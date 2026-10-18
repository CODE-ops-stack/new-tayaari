package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.PlayCircle
import androidx.compose.material.icons.filled.Psychology
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.CartographicSerif
import com.example.ui.theme.DeepBasalt
import com.example.ui.theme.OceanicDark
import com.example.ui.theme.SunstoneGold
import com.example.ui.theme.HydrosphereCyan
import com.example.ui.theme.ContourEmerald
import com.example.ui.theme.AtlasParchment
import com.example.ui.theme.TopoContourMuted
import com.example.ui.theme.AbyssNavy

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RevisionDashboardScreen(
    dueCount: Int,
    onStartRevision: () -> Unit,
    onBack: () -> Unit
) {
    val lightText = Color(0xFFF8FAFC)

    com.example.ui.components.AtlasBackground {
      com.example.ui.components.TopographicBackground(lineColor = ContourEmerald.copy(alpha = 0.035f)) {
        Scaffold(
            topBar = {
                TopAppBar(
                    title = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("🧭", fontSize = 20.sp)
                            Spacer(modifier = Modifier.width(8.dp))
                            Column {
                                Text("Atlas Spaced Cadastre Revision", fontFamily = CartographicSerif, fontWeight = FontWeight.Bold, color = lightText, fontSize = 18.sp)
                                Text("Active Recall & Memory Consolidation Engine", fontSize = 10.sp, color = lightText.copy(alpha = 0.7f))
                            }
                        }
                    },
                    navigationIcon = {
                        IconButton(onClick = onBack) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = lightText)
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.Transparent)
                )
            },
            containerColor = Color.Transparent
        ) { padding ->
            LazyColumn(
                modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // 1. Geodetic Memory Vault Health Dial
                item {
                    MemoryVaultRetentionGauge(dueCount = dueCount, onStartRevision = onStartRevision)
                }

                // 2. Interactive Ebbinghaus Forgetting Curve Canvas
                item {
                    EbbinghausMemoryVaultCanvas()
                }

                // 3. Interactive 60-Second Compass Memory Warmup Drill
                item {
                    CompassMemoryWarmupDrill()
                }

                // 4. Cadastre Review Actions
                item {
                    RevisionCard(
                        title = "Today's Cadastre Review 📍",
                        subtitle = "$dueCount Geographic Waypoints Due for Spaced Recall",
                        reason = "Reinforce vulnerable physical, Indian, and climatic concepts before neural forgetting occurs.",
                        count = dueCount,
                        icon = Icons.Filled.Schedule,
                        cardColor = DeepBasalt,
                        lightText = lightText,
                        accentGold = SunstoneGold,
                        onClick = {
                            if (dueCount > 0) onStartRevision()
                        }
                    )
                }
                item {
                    RevisionCard(
                        title = "High-Priority Hazard Points 🛡️",
                        subtitle = "Repeatedly Conflated Geomorphic & Climatic Traps",
                        reason = "Prioritized because you previously tripped on adjacent concepts or spatial inversion traps.",
                        count = null,
                        icon = Icons.Filled.Warning,
                        cardColor = DeepBasalt,
                        lightText = lightText,
                        accentGold = SunstoneGold,
                        onClick = onStartRevision
                    )
                }
                item {
                    RevisionCard(
                        title = "Expedition Continuity ⛰️",
                        subtitle = "Recently Surveyed Topographic Topics",
                        reason = "Solidify conceptual mastery of recently studied river basins, biomes, and rock strata.",
                        count = null,
                        icon = Icons.Filled.PlayCircle,
                        cardColor = DeepBasalt,
                        lightText = lightText,
                        accentGold = SunstoneGold,
                        onClick = onStartRevision
                    )
                }
            }
        }
      }
    }
}

@Composable
fun MemoryVaultRetentionGauge(
    dueCount: Int,
    onStartRevision: () -> Unit
) {
    val retentionScore = remember(dueCount) {
        if (dueCount == 0) 96 else (96 - (dueCount * 3)).coerceIn(55, 96)
    }

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.2.dp, SunstoneGold.copy(alpha = 0.5f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(36.dp)
                            .clip(CircleShape)
                            .background(SunstoneGold.copy(alpha = 0.15f)),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("🧠", fontSize = 18.sp)
                    }
                    Spacer(modifier = Modifier.width(10.dp))
                    Column {
                        Text(
                            text = "GEODETIC RETENTION VAULT",
                            color = SunstoneGold,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Black,
                            letterSpacing = 0.8.sp
                        )
                        Text(
                            text = "Long-Term Synaptic Memory Index",
                            color = TopoContourMuted,
                            fontSize = 10.sp
                        )
                    }
                }
                Surface(
                    color = if (retentionScore >= 80) ContourEmerald.copy(alpha = 0.15f) else Color(0xFFEF4444).copy(alpha = 0.15f),
                    shape = RoundedCornerShape(6.dp),
                    border = BorderStroke(0.8.dp, if (retentionScore >= 80) ContourEmerald.copy(alpha = 0.4f) else Color(0xFFEF4444).copy(alpha = 0.4f))
                ) {
                    Text(
                        text = if (retentionScore >= 80) "CADASTRE STABLE" else "DECAY DETECTED",
                        color = if (retentionScore >= 80) ContourEmerald else Color(0xFFEF4444),
                        fontSize = 9.sp,
                        fontWeight = FontWeight.ExtraBold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Column {
                    Row(verticalAlignment = Alignment.Bottom) {
                        Text(
                            text = "$retentionScore%",
                            color = SunstoneGold,
                            fontSize = 32.sp,
                            fontWeight = FontWeight.Black,
                            fontFamily = CartographicSerif
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Recall Health",
                            color = TopoContourMuted,
                            fontSize = 12.sp,
                            modifier = Modifier.padding(bottom = 6.dp)
                        )
                    }
                    Text(
                        text = if (dueCount > 0) "$dueCount waypoints require review before memory decay." else "All geographic waypoints fortified in crystalline memory.",
                        color = AtlasParchment,
                        fontSize = 11.sp
                    )
                }

                if (dueCount > 0) {
                    Button(
                        onClick = onStartRevision,
                        colors = ButtonDefaults.buttonColors(containerColor = SunstoneGold),
                        shape = RoundedCornerShape(10.dp),
                        contentPadding = PaddingValues(horizontal = 14.dp, vertical = 8.dp)
                    ) {
                        Text(
                            text = "Review Now ⚡",
                            color = AbyssNavy,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Black
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun EbbinghausMemoryVaultCanvas() {
    var selectedDay by remember { mutableIntStateOf(1) } // 0=Day 1, 1=Day 3, 2=Day 7, 3=Day 30
    val days = listOf("Day 1", "Day 3", "Day 7", "Day 30")
    val retentionWithoutReview = listOf("58%", "42%", "28%", "18%")
    val retentionWithReview = listOf("95%", "96%", "98%", "99%")
    val scientificInsights = listOf(
        "Day 1: Without review, 42% of newly learned facts (e.g. Koppen climate codes Amw, As) fade within 24 hours. A 3-minute quiz today resets retention to 95%.",
        "Day 3: Synaptic pruning accelerates. Actively testing difficult river origins (e.g. Narmada at Amarkantak, Krishna at Mahabaleshwar) locks them into the hippocampus.",
        "Day 7: The transition from working memory to long-term memory occurs here. Reviewing at Day 7 doubles subsequent retention duration to 30 days.",
        "Day 30: Crystalline memory achieved! Concepts reviewed 4 times across spaced intervals resist exam-hall anxiety and spatial inversion traps permanently."
    )

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.2.dp, HydrosphereCyan.copy(alpha = 0.4f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("📉", fontSize = 16.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Column {
                        Text(
                            text = "EBBINGHAUS RETENTION FORGETTING CURVE",
                            color = HydrosphereCyan,
                            fontSize = 10.5.sp,
                            fontWeight = FontWeight.Black,
                            letterSpacing = 0.8.sp
                        )
                        Text(
                            text = "Scientific evidence for Cadastre Spaced Active Recall",
                            color = TopoContourMuted,
                            fontSize = 10.sp
                        )
                    }
                }
                Text("Tap Days ➔", color = TopoContourMuted, fontSize = 9.sp)
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Interactive Forgetting Curve Canvas
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(115.dp)
                    .background(OceanicDark, RoundedCornerShape(10.dp))
                    .border(0.8.dp, HydrosphereCyan.copy(alpha = 0.25f), RoundedCornerShape(10.dp))
            ) {
                Canvas(modifier = Modifier.fillMaxSize().padding(12.dp)) {
                    val w = size.width
                    val h = size.height

                    // Grid baselines (100%, 50%, 0%)
                    drawLine(color = Color.White.copy(alpha = 0.08f), start = Offset(0f, 0f), end = Offset(w, 0f), strokeWidth = 1f)
                    drawLine(color = Color.White.copy(alpha = 0.08f), start = Offset(0f, h * 0.5f), end = Offset(w, h * 0.5f), strokeWidth = 1f)
                    drawLine(color = Color.White.copy(alpha = 0.15f), start = Offset(0f, h), end = Offset(w, h), strokeWidth = 1.2f)

                    // 1. Natural Decay Curve (Red Dashed Path)
                    val decayPath = Path().apply {
                        moveTo(0f, 0f) // 100%
                        quadraticTo(w * 0.25f, h * 0.58f, w * 0.5f, h * 0.72f)
                        quadraticTo(w * 0.75f, h * 0.82f, w, h * 0.86f) // 14%
                    }
                    drawPath(
                        path = decayPath,
                        color = Color(0xFFEF4444).copy(alpha = 0.65f),
                        style = Stroke(width = 2.dp.toPx())
                    )

                    // 2. Spaced Cadastre Active Review Curve (Golden Emerald Path)
                    val reviewPath = Path().apply {
                        moveTo(0f, 0f)
                        // Review at Day 1: drops to 55%, jumps to 95%
                        lineTo(w * 0.25f, h * 0.45f)
                        lineTo(w * 0.25f, h * 0.05f)
                        // Review at Day 3: drops to 60%, jumps to 96%
                        lineTo(w * 0.50f, h * 0.40f)
                        lineTo(w * 0.50f, h * 0.04f)
                        // Review at Day 7: drops to 70%, jumps to 98%
                        lineTo(w * 0.75f, h * 0.30f)
                        lineTo(w * 0.75f, h * 0.02f)
                        // Day 30 crystalline plateau
                        lineTo(w, h * 0.08f)
                    }
                    drawPath(
                        path = reviewPath,
                        color = Color(0xFF10B981),
                        style = Stroke(width = 2.5.dp.toPx())
                    )

                    // Highlight active selected day vertical indicator
                    val selectedX = when (selectedDay) {
                        0 -> w * 0.25f
                        1 -> w * 0.50f
                        2 -> w * 0.75f
                        else -> w
                    }
                    drawLine(
                        color = SunstoneGold.copy(alpha = 0.85f),
                        start = Offset(selectedX, 0f),
                        end = Offset(selectedX, h),
                        strokeWidth = 1.5.dp.toPx()
                    )
                    drawCircle(
                        color = SunstoneGold,
                        radius = 4.dp.toPx(),
                        center = Offset(selectedX, h * 0.05f)
                    )
                }

                Row(
                    modifier = Modifier.fillMaxSize().padding(horizontal = 10.dp, vertical = 6.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.Bottom
                ) {
                    Text("🔴 No Review (18% Retention)", fontSize = 8.sp, color = Color(0xFFEF4444))
                    Text("🟢 Spaced Active Recall (99% Retention)", fontSize = 8.sp, color = ContourEmerald, fontWeight = FontWeight.Bold)
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Day Selector Chips
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                days.forEachIndexed { idx, name ->
                    val isTabSelected = selectedDay == idx
                    Surface(
                        color = if (isTabSelected) HydrosphereCyan else OceanicDark,
                        shape = RoundedCornerShape(8.dp),
                        border = BorderStroke(0.8.dp, if (isTabSelected) HydrosphereCyan else HydrosphereCyan.copy(alpha = 0.3f)),
                        modifier = Modifier
                            .weight(1f)
                            .clickable { selectedDay = idx }
                    ) {
                        Text(
                            text = name,
                            color = if (isTabSelected) AbyssNavy else AtlasParchment,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.padding(vertical = 6.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Scientific Insight Box
            Surface(
                color = OceanicDark,
                shape = RoundedCornerShape(8.dp),
                border = BorderStroke(0.8.dp, HydrosphereCyan.copy(alpha = 0.25f)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(10.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "Recall: ${retentionWithoutReview[selectedDay]} (Passive) ➔ ${retentionWithReview[selectedDay]} (Cadastre Review)",
                            color = SunstoneGold,
                            fontSize = 10.5.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = scientificInsights[selectedDay],
                        color = AtlasParchment,
                        fontSize = 11.sp,
                        lineHeight = 15.sp
                    )
                }
            }
        }
    }
}

@Composable
fun CompassMemoryWarmupDrill() {
    var drillIndex by remember { mutableIntStateOf(0) }
    var selectedOption by remember { mutableStateOf<Int?>(null) }

    data class WarmupQuestion(
        val prompt: String,
        val options: List<String>,
        val correctIndex: Int,
        val rationale: String
    )

    val drills = listOf(
        WarmupQuestion(
            prompt = "Which ocean current is responsible for the arid Namib Desert?",
            options = listOf("Benguela Current (Cold)", "Agulhas Current (Warm)", "Mozambique Current (Warm)"),
            correctIndex = 0,
            rationale = "The cold Benguela Current chills surface air, creating atmospheric stability/inversion that prevents cloud formation along the southwest African coast."
        ),
        WarmupQuestion(
            prompt = "Which soil order characterizes the black cotton soils of the Deccan Trap?",
            options = listOf("Vertisols (High Swell-Shrink Clay)", "Inceptisols (Young Embryonic)", "Oxisols (Highly Leached Lateritic)"),
            correctIndex = 0,
            rationale = "Vertisols are montmorillonite-rich expansive clay soils that self-plough with deep summer fissures, typical of the Cretaceous Deccan basalt."
        ),
        WarmupQuestion(
            prompt = "What drainage pattern develops when streams radiate outward from a central dome?",
            options = listOf("Radial Pattern (e.g. Amarkantak)", "Trellis Pattern (Folded Strata)", "Dendritic Pattern (Homogeneous)"),
            correctIndex = 0,
            rationale = "Radial drainage radiates outward from a central peak, as seen at Amarkantak plateau where Narmada, Son, and Johilla originate in different directions."
        )
    )

    val currentDrill = drills[drillIndex % drills.size]

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.2.dp, ContourEmerald.copy(alpha = 0.45f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("⚡", fontSize = 16.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Column {
                        Text(
                            text = "60-SECOND COMPASS MEMORY CHECK",
                            color = ContourEmerald,
                            fontSize = 10.5.sp,
                            fontWeight = FontWeight.Black,
                            letterSpacing = 0.8.sp
                        )
                        Text(
                            text = "Rapid synaptic warmup drill before full revision",
                            color = TopoContourMuted,
                            fontSize = 10.sp
                        )
                    }
                }
                TextButton(
                    onClick = {
                        selectedOption = null
                        drillIndex++
                    },
                    contentPadding = PaddingValues(0.dp)
                ) {
                    Text("Next Drill ➔", color = SunstoneGold, fontSize = 10.sp, fontWeight = FontWeight.Bold)
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = currentDrill.prompt,
                color = AtlasParchment,
                fontSize = 13.sp,
                fontWeight = FontWeight.Bold,
                lineHeight = 18.sp
            )

            Spacer(modifier = Modifier.height(10.dp))

            Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                currentDrill.options.forEachIndexed { optIdx, optText ->
                    val isChosen = selectedOption == optIdx
                    val isCorrect = optIdx == currentDrill.correctIndex
                    val hasAnswered = selectedOption != null

                    val bgColor = when {
                        !hasAnswered -> OceanicDark
                        isChosen && isCorrect -> ContourEmerald.copy(alpha = 0.15f)
                        isChosen && !isCorrect -> Color(0xFFEF4444).copy(alpha = 0.15f)
                        isCorrect -> ContourEmerald.copy(alpha = 0.15f)
                        else -> OceanicDark
                    }
                    val borderColor = when {
                        !hasAnswered -> HydrosphereCyan.copy(alpha = 0.3f)
                        isChosen && isCorrect -> ContourEmerald
                        isChosen && !isCorrect -> Color(0xFFEF4444)
                        isCorrect -> ContourEmerald.copy(alpha = 0.6f)
                        else -> Color.Transparent
                    }

                    Surface(
                        color = bgColor,
                        shape = RoundedCornerShape(8.dp),
                        border = BorderStroke(0.8.dp, borderColor),
                        modifier = Modifier
                            .fillMaxWidth()
                            .clickable(enabled = !hasAnswered) { selectedOption = optIdx }
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Text(
                                text = listOf("A", "B", "C")[optIdx],
                                color = SunstoneGold,
                                fontWeight = FontWeight.Bold,
                                fontSize = 11.sp
                            )
                            Spacer(modifier = Modifier.width(10.dp))
                            Text(
                                text = optText,
                                color = AtlasParchment,
                                fontSize = 12.sp,
                                modifier = Modifier.weight(1f)
                            )
                            if (hasAnswered) {
                                if (isCorrect) {
                                    Icon(Icons.Default.CheckCircle, contentDescription = null, tint = ContourEmerald, modifier = Modifier.size(16.dp))
                                } else if (isChosen) {
                                    Icon(Icons.Default.Close, contentDescription = null, tint = Color(0xFFEF4444), modifier = Modifier.size(16.dp))
                                }
                            }
                        }
                    }
                }
            }

            if (selectedOption != null) {
                Spacer(modifier = Modifier.height(8.dp))
                Surface(
                    color = OceanicDark,
                    shape = RoundedCornerShape(8.dp),
                    border = BorderStroke(0.8.dp, SunstoneGold.copy(alpha = 0.35f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(10.dp)) {
                        Text(
                            text = if (selectedOption == currentDrill.correctIndex) "✅ SYNAPSE VERIFIED" else "⚠️ RETRIEVAL REFRESH",
                            color = if (selectedOption == currentDrill.correctIndex) ContourEmerald else SunstoneGold,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Black
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = currentDrill.rationale,
                            color = AtlasParchment,
                            fontSize = 11.sp,
                            lineHeight = 15.sp
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun RevisionCard(
    title: String,
    subtitle: String,
    reason: String,
    count: Int?,
    icon: ImageVector,
    cardColor: Color,
    lightText: Color,
    accentGold: Color,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth().clickable { onClick() },
        colors = CardDefaults.cardColors(containerColor = cardColor),
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.dp, HydrosphereCyan.copy(alpha = 0.25f)),
        elevation = CardDefaults.cardElevation(defaultElevation = 3.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .background(accentGold.copy(alpha = 0.15f), RoundedCornerShape(8.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(icon, contentDescription = null, tint = accentGold, modifier = Modifier.size(24.dp))
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(title, fontWeight = FontWeight.Bold, color = lightText, fontSize = 16.sp, fontFamily = CartographicSerif)
                        Text(subtitle, fontSize = 12.sp, color = lightText.copy(alpha = 0.7f))
                    }
                }
                if (count != null) {
                    Surface(
                        color = if (count > 0) accentGold else Color.Gray.copy(alpha = 0.2f),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text(
                            text = "$count DUE",
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (count > 0) Color.Black else lightText
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(12.dp))
            Text(reason, fontSize = 13.sp, color = lightText.copy(alpha = 0.8f), lineHeight = 18.sp)
        }
    }
}
