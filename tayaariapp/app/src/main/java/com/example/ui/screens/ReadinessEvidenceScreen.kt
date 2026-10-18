package com.example.ui.screens

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.Warning
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.viewmodel.ReadinessPillar
import com.example.viewmodel.ReadinessViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReadinessEvidenceScreen(
    viewModel: ReadinessViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    val fontScale = LocalFontScale.current

    com.example.ui.components.AtlasBackground {
        com.example.ui.components.TopographicBackground(lineColor = ContourEmerald.copy(alpha = 0.035f)) {
            Scaffold(
                containerColor = Color.Transparent,
                topBar = {
                    TopAppBar(
                        title = {
                            Column {
                                Text(
                                    "Field Readiness Radar 🧭",
                                    fontFamily = CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    color = SummitGold,
                                    fontSize = 18.sp
                                )
                                Text(
                                    "GEODETIC READINESS & BEHAVIORAL AUDIT",
                                    fontFamily = CoordinatesMonospace,
                                    fontSize = 10.sp,
                                    color = GlacierAzure,
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
                            containerColor = Color.Transparent,
                            titleContentColor = SummitGold,
                            navigationIconContentColor = MaterialTheme.colorScheme.onSurface
                        )
                    )
                }
            ) { padding ->
                if (uiState.isLoading) {
                    Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                        CircularProgressIndicator(color = GlacierAzure)
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
                                coordinatesText = "📍 BEHAVIORAL FIELD AUDIT // 4-PILLAR CADASTRE"
                            )
                        }

                        // 1. 4-Pillar Behavioral Radar Polygon Canvas
                        item {
                            ReadinessRadarPolygonCanvas(pillars = uiState.pillars)
                        }

                        item {
                            Text(
                                "Empirical Pillar Breakdown ⛰️",
                                style = MaterialTheme.typography.titleLarge,
                                fontFamily = CartographicSerif,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onSurface,
                                fontSize = (18 * fontScale).sp
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                "Forget rank speculation. This radar tracks empirical behavioral evidence of your real geodetic readiness across 4 crucial field pillars.",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                fontSize = (12 * fontScale).sp
                            )
                        }

                        items(uiState.pillars) { pillar ->
                            val statusText = when (pillar.status) {
                                "STRONG" -> "🟢 SUMMIT READY"
                                "WATCH" -> "🟡 TOPOGRAPHIC WATCH"
                                "INSUFFICIENT DATA" -> "⚪ INSUFFICIENT DATA"
                                else -> "🔴 COURSE CORRECTION NEEDED"
                            }
                            val statusColor = when (pillar.status) {
                                "STRONG" -> ContourEmerald
                                "WATCH" -> SunstoneGold
                                "INSUFFICIENT DATA" -> MeridianMuted
                                else -> MagmaCrimson
                            }
                            val icon = when (pillar.status) {
                                "STRONG" -> Icons.Default.CheckCircle
                                "WATCH" -> Icons.Default.Warning
                                "INSUFFICIENT DATA" -> Icons.Default.Warning
                                else -> Icons.Default.Error
                            }

                            com.example.ui.components.AtlasCard(
                                modifier = Modifier.fillMaxWidth(),
                                borderColor = statusColor.copy(alpha = 0.4f)
                            ) {
                                Column(modifier = Modifier.padding(16.dp)) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        horizontalArrangement = Arrangement.SpaceBetween,
                                        verticalAlignment = Alignment.CenterVertically
                                    ) {
                                        Row(
                                            verticalAlignment = Alignment.CenterVertically,
                                            modifier = Modifier.weight(1f)
                                        ) {
                                            Icon(
                                                icon,
                                                contentDescription = pillar.status,
                                                tint = statusColor,
                                                modifier = Modifier.size(20.dp)
                                            )
                                            Spacer(modifier = Modifier.width(8.dp))
                                            Text(
                                                text = pillar.title,
                                                style = MaterialTheme.typography.titleMedium,
                                                fontFamily = CartographicSerif,
                                                fontWeight = FontWeight.Bold,
                                                color = MaterialTheme.colorScheme.onSurface,
                                                fontSize = (15 * fontScale).sp
                                            )
                                        }
                                        Surface(
                                            color = statusColor.copy(alpha = 0.15f),
                                            shape = RoundedCornerShape(6.dp),
                                            border = BorderStroke(1.dp, statusColor.copy(alpha = 0.3f))
                                        ) {
                                            Text(
                                                text = statusText,
                                                color = statusColor,
                                                fontFamily = CoordinatesMonospace,
                                                fontSize = (10 * fontScale).sp,
                                                fontWeight = FontWeight.Bold,
                                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                                            )
                                        }
                                    }
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        pillar.description,
                                        style = MaterialTheme.typography.bodySmall,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                                        fontSize = (12 * fontScale).sp
                                    )
                                    Spacer(modifier = Modifier.height(12.dp))
                                    pillar.evidence.forEach { ev ->
                                        Text(
                                            "🧭 $ev",
                                            style = MaterialTheme.typography.bodySmall,
                                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.9f),
                                            fontSize = (12 * fontScale).sp,
                                            modifier = Modifier.padding(bottom = 4.dp)
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

/**
 * 4-Pillar Behavioral Radar Polygon Canvas
 */
@Composable
fun ReadinessRadarPolygonCanvas(pillars: List<ReadinessPillar>) {
    val animatedProgress by animateFloatAsState(
        targetValue = 1f,
        animationSpec = tween(1200),
        label = "radarAnim"
    )

    // Calculate score for each of 4 main pillars (Coverage, Retention, Mistake Repair, Confidence)
    val pillarScores = pillars.take(4).map { pillar ->
        when (pillar.status) {
            "STRONG" -> 0.90f
            "WATCH" -> 0.65f
            "NEEDS WORK" -> 0.35f
            else -> 0.20f
        }
    }.ifEmpty { listOf(0.5f, 0.5f, 0.5f, 0.5f) }

    val avgScore = (pillarScores.average() * 100).toInt()

    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant,
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.dp, ContourEmerald.copy(alpha = 0.45f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("📡", fontSize = 16.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "4-PILLAR BEHAVIORAL READINESS RADAR",
                        color = SunstoneGold,
                        fontFamily = CoordinatesMonospace,
                        fontWeight = FontWeight.Black,
                        fontSize = 10.5.sp,
                        letterSpacing = 0.6.sp
                    )
                }
                Surface(
                    color = MaterialTheme.colorScheme.surface,
                    shape = RoundedCornerShape(4.dp),
                    border = BorderStroke(0.8.dp, ContourEmerald.copy(alpha = 0.5f))
                ) {
                    Text(
                        text = "$avgScore% READY",
                        color = if (avgScore >= 70) ContourEmerald else SunstoneGold,
                        fontFamily = CoordinatesMonospace,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // 4-Axis Diamond Radar Canvas
            Box(
                modifier = Modifier
                    .size(160.dp)
                    .clip(CircleShape)
                    .background(MaterialTheme.colorScheme.surface),
                contentAlignment = Alignment.Center
            ) {
                Canvas(modifier = Modifier.size(150.dp)) {
                    val radius = size.minDimension / 2f
                    val center = Offset(size.width / 2f, size.height / 2f)

                    // Concentric radar guide rings
                    listOf(0.33f, 0.66f, 1.0f).forEach { fraction ->
                        drawCircle(
                            color = SlateBedrock.copy(alpha = 0.5f),
                            radius = radius * fraction,
                            center = center,
                            style = Stroke(width = 1f)
                        )
                    }

                    // 4 Axes: Top (Coverage), Right (Retention), Bottom (Mistake Repair), Left (Calibration)
                    val axes = listOf(
                        Offset(center.x, center.y - radius),
                        Offset(center.x + radius, center.y),
                        Offset(center.x, center.y + radius),
                        Offset(center.x - radius, center.y)
                    )
                    axes.forEach { endPoint ->
                        drawLine(
                            color = SlateBedrock.copy(alpha = 0.7f),
                            start = center,
                            end = endPoint,
                            strokeWidth = 1.2f
                        )
                    }

                    // Draw Student's Polygon
                    val polyPath = Path()
                    val pScores = pillarScores + List(maxOf(0, 4 - pillarScores.size)) { 0.3f }
                    val polyPoints = listOf(
                        Offset(center.x, center.y - (radius * pScores[0] * animatedProgress)),
                        Offset(center.x + (radius * pScores[1] * animatedProgress), center.y),
                        Offset(center.x, center.y + (radius * pScores[2] * animatedProgress)),
                        Offset(center.x - (radius * pScores[3] * animatedProgress), center.y)
                    )

                    polyPath.moveTo(polyPoints[0].x, polyPoints[0].y)
                    for (i in 1..3) polyPath.lineTo(polyPoints[i].x, polyPoints[i].y)
                    polyPath.close()

                    // Fill polygon with emerald glow
                    drawPath(
                        path = polyPath,
                        color = ContourEmerald.copy(alpha = 0.25f),
                        style = Fill
                    )
                    // Stroke polygon outline
                    drawPath(
                        path = polyPath,
                        color = ContourEmerald,
                        style = Stroke(width = 2.2f)
                    )

                    // Draw points on each apex
                    polyPoints.forEach { pt ->
                        drawCircle(color = Color.White, radius = 3.5f, center = pt)
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // 4 Axis Legend Labels
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceAround
            ) {
                Text("↑ Coverage", color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 9.5.sp, fontFamily = CoordinatesMonospace)
                Text("→ Retention", color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 9.5.sp, fontFamily = CoordinatesMonospace)
                Text("↓ Traps", color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 9.5.sp, fontFamily = CoordinatesMonospace)
                Text("← Confidence", color = MaterialTheme.colorScheme.onSurfaceVariant, fontSize = 9.5.sp, fontFamily = CoordinatesMonospace)
            }
        }
    }
}
