package com.example.ui.screens

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.clickable
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Analytics
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.WarningAmber
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.foundation.border
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.drawscope.Stroke
import kotlin.math.cos
import kotlin.math.sin
import com.example.ui.theme.*
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.database.TrapAnalyticsEntity
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TrapDashboardScreen(
    trapAnalytics: List<TrapAnalyticsEntity>,
    onPracticeTrap: (String) -> Unit,
    onBack: () -> Unit
) {
    // Premium color palette
    val surfaceColor = MaterialTheme.colorScheme.surface
    val cardColor = MaterialTheme.colorScheme.background
    val deepBlue = MaterialTheme.colorScheme.primary
    val warningRed = MaterialTheme.colorScheme.error
    val accentGold = MaterialTheme.colorScheme.tertiary

    com.example.ui.components.AtlasBackground {
      com.example.ui.components.TopographicBackground(lineColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.035f)) {
        Scaffold(
            containerColor = Color.Transparent,
            topBar = {
                TopAppBar(
                    title = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("🧭", fontSize = 22.sp)
                            Spacer(modifier = Modifier.width(10.dp))
                            Column {
                                Text(
                                    "Topographic Hazard Radar",
                                    color = deepBlue,
                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 19.sp
                                )
                                Text(
                                    "Examiner Traps & Conceptual Conflation Tracking",
                                    color = deepBlue.copy(alpha = 0.7f),
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Medium
                                )
                            }
                        }
                    },
                    navigationIcon = {
                        IconButton(onClick = onBack) {
                            Icon(
                                imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                contentDescription = "Back",
                                tint = deepBlue
                            )
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = Color.Transparent
                    )
                )
            }
        ) { paddingValues ->
            if (trapAnalytics.isEmpty()) {
                // Premium Empty State
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues)
                        .padding(32.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center
                ) {
                    Box(
                        modifier = Modifier
                            .size(120.dp)
                            .background(deepBlue.copy(alpha = 0.05f), CircleShape),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("🛡️", fontSize = 54.sp)
                    }
                    Spacer(modifier = Modifier.height(24.dp))
                    Text(
                        text = "Zero Geographic Pitfalls Encountered",
                        fontSize = 20.sp,
                        fontFamily = com.example.ui.theme.CartographicSerif,
                        fontWeight = FontWeight.Bold,
                        color = deepBlue
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = "You have navigated through all geographic waypoints without succumbing to examiner traps. Keep your expedition compass calibrated!",
                        fontSize = 15.sp,
                        color = deepBlue.copy(alpha = 0.7f),
                        textAlign = TextAlign.Center
                    )
                }
            } else {
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(paddingValues)
                        .padding(horizontal = 16.dp),
                    contentPadding = PaddingValues(vertical = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    item {
                        SonarTrapRadarCanvas(trapsCount = trapAnalytics.size)
                    }

                    item {
                        Text(
                            text = "Identify cognitive vulnerabilities across Physical, Indian & World Geography. The higher the frequency, the more susceptible you are to that specific trap format.",
                            fontSize = 13.sp,
                            color = deepBlue.copy(alpha = 0.7f),
                            modifier = Modifier.padding(bottom = 8.dp)
                        )
                        HorizontalDivider(
                            color = deepBlue.copy(alpha = 0.1f)
                        )
                    }

                    val maxFreq = trapAnalytics.maxOfOrNull { it.frequency } ?: 1
                    items(trapAnalytics.sortedByDescending { it.frequency }) { trap ->
                        EnhancedTrapStatCard(
                            trap = trap,
                            maxFreq = maxFreq,
                            deepBlue = deepBlue,
                            warningRed = warningRed,
                            accentGold = accentGold,
                            cardColor = cardColor,
                            onPracticeTrap = onPracticeTrap
                        )
                    }
                }
            }
        }
      }
    }
}

@Composable
fun EnhancedTrapStatCard(
    trap: TrapAnalyticsEntity,
    maxFreq: Int,
    deepBlue: Color,
    warningRed: Color,
    accentGold: Color,
    cardColor: Color,
    onPracticeTrap: (String) -> Unit
) {
    val targetFraction = if (maxFreq > 0) trap.frequency.toFloat() / maxFreq else 0f
    var animationPlayed by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        delay(100) // Slight delay for stagger effect
        animationPlayed = true
    }

    val animatedProgress by animateFloatAsState(
        targetValue = if (animationPlayed) targetFraction else 0f,
        animationSpec = tween(durationMillis = 1000, easing = FastOutSlowInEasing),
        label = "progressAnimation"
    )

    // Color code based on severity
    val barColor = when {
        targetFraction > 0.7f -> warningRed
        targetFraction > 0.4f -> accentGold
        else -> deepBlue.copy(alpha = 0.6f)
    }

    var expanded by remember { mutableStateOf(false) }
    
    val failedQuestions = remember(trap.failedQuestionsJson) {
        try {
            val arr = org.json.JSONArray(trap.failedQuestionsJson)
            val list = mutableListOf<org.json.JSONObject>()
            for (i in 0 until arr.length()) list.add(arr.getJSONObject(i))
            list
        } catch (e: Exception) { emptyList() }
    }

    Card(
        modifier = Modifier.fillMaxWidth().clickable { expanded = !expanded },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = cardColor),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = trap.trapType.uppercase(),
                    color = deepBlue,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.2.sp
                )
                Surface(
                    shape = RoundedCornerShape(24.dp),
                    color = barColor.copy(alpha = 0.1f)
                ) {
                    Text(
                        text = "${trap.frequency} TRIPPED",
                        color = barColor,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Black,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
                    )
                }
            }

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(10.dp)
                    .clip(RoundedCornerShape(5.dp))
                    .background(Color.LightGray.copy(alpha = 0.3f))
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth(animatedProgress)
                        .height(10.dp)
                        .clip(RoundedCornerShape(5.dp))
                        .background(barColor)
                )
            }
            
            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically(),
                exit = shrinkVertically()
            ) {
                Column(modifier = Modifier.padding(top = 16.dp)) {
                    Divider(color = Color.LightGray.copy(alpha = 0.5f), thickness = 1.dp)
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    if (failedQuestions.isEmpty()) {
                        Text(
                            text = "No detailed history available for this trap.",
                            color = deepBlue.copy(alpha = 0.6f),
                            fontSize = 14.sp
                        )
                    } else {
                        failedQuestions.forEachIndexed { index, q ->
                            Column(modifier = Modifier.padding(bottom = 16.dp)) {
                                Text(
                                    text = "Question ${index + 1}:",
                                    color = accentGold,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 12.sp
                                )
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = q.optString("questionText", "Unknown"),
                                    color = deepBlue,
                                    fontSize = 14.sp,
                                    lineHeight = 20.sp
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Surface(
                                    color = warningRed.copy(alpha = 0.05f),
                                    shape = RoundedCornerShape(8.dp),
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Column(modifier = Modifier.padding(12.dp)) {
                                        Text(
                                            text = "Why you fell for it:",
                                            color = warningRed,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 12.sp
                                        )
                                        Text(
                                            text = q.optString("dissection", ""),
                                            color = deepBlue.copy(alpha = 0.8f),
                                            fontSize = 14.sp
                                        )
                                    }
                                }
                            }
                        }
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(
                            onClick = { onPracticeTrap(trap.trapType) },
                            colors = ButtonDefaults.buttonColors(containerColor = accentGold),
                            modifier = Modifier.fillMaxWidth().height(48.dp),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Text("Practice This Trap", fontWeight = FontWeight.Bold, color = Color.White)
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun SonarTrapRadarCanvas(
    trapsCount: Int,
    modifier: Modifier = Modifier
) {
    val infiniteTransition = rememberInfiniteTransition(label = "radarSweep")
    val sweepAngle by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 360f,
        animationSpec = infiniteRepeatable(
            animation = tween(4000, easing = LinearEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "sweep"
    )

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.2.dp, ContourEmerald.copy(alpha = 0.5f)),
        modifier = modifier.fillMaxWidth().padding(bottom = 8.dp)
    ) {
        Column(
            modifier = Modifier.padding(14.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(10.dp)
                            .clip(CircleShape)
                            .background(Color(0xFFEF4444))
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "SONAR TRAP RADAR // 360° SWEEP",
                        color = ContourEmerald,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.8.sp
                    )
                }
                Surface(
                    color = ContourEmerald.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(4.dp)
                ) {
                    Text(
                        text = "$trapsCount DETECTED",
                        color = ContourEmerald,
                        fontSize = 9.5.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Box(
                modifier = Modifier
                    .size(160.dp)
                    .clip(CircleShape)
                    .background(OceanicDark)
                    .border(1.5.dp, ContourEmerald.copy(alpha = 0.4f), CircleShape),
                contentAlignment = Alignment.Center
            ) {
                Canvas(modifier = Modifier.fillMaxSize()) {
                    val center = Offset(size.width / 2f, size.height / 2f)
                    val radius = size.width / 2f

                    // Concentric Range Rings
                    drawCircle(color = ContourEmerald.copy(alpha = 0.15f), radius = radius * 0.33f, center = center, style = Stroke(1.2f))
                    drawCircle(color = ContourEmerald.copy(alpha = 0.2f), radius = radius * 0.66f, center = center, style = Stroke(1.2f))
                    drawCircle(color = ContourEmerald.copy(alpha = 0.3f), radius = radius * 0.95f, center = center, style = Stroke(1.5f))

                    // Crosshair grid lines
                    drawLine(color = ContourEmerald.copy(alpha = 0.2f), start = Offset(0f, center.y), end = Offset(size.width, center.y), strokeWidth = 1f)
                    drawLine(color = ContourEmerald.copy(alpha = 0.2f), start = Offset(center.x, 0f), end = Offset(center.x, size.height), strokeWidth = 1f)

                    // Sweeping Sonar Beam
                    val rad = sweepAngle * (Math.PI / 180f)
                    val endX = center.x + radius * cos(rad).toFloat()
                    val endY = center.y + radius * sin(rad).toFloat()
                    drawLine(
                        color = ContourEmerald,
                        start = center,
                        end = Offset(endX, endY),
                        strokeWidth = 2.5f
                    )

                    // Draw trap blips
                    val blipAngles = listOf(45f, 130f, 210f, 315f)
                    val blipDists = listOf(0.45f, 0.72f, 0.58f, 0.85f)
                    for (i in 0 until minOf(trapsCount, 4)) {
                        val bAngle = blipAngles[i] * (Math.PI / 180f)
                        val bx = center.x + radius * blipDists[i] * cos(bAngle).toFloat()
                        val by = center.y + radius * blipDists[i] * sin(bAngle).toFloat()
                        drawCircle(color = Color(0xFFEF4444), radius = 5f, center = Offset(bx, by))
                        drawCircle(color = Color(0xFFEF4444).copy(alpha = 0.3f), radius = 9f, center = Offset(bx, by))
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))
            Text(
                text = "Sonar Pulse: Factual Inversion, Extreme Qualifiers & Causality Traps Mapped",
                color = TopoContourMuted,
                fontSize = 10.5.sp,
                textAlign = TextAlign.Center
            )
        }
    }
}