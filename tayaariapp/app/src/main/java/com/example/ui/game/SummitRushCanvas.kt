package com.example.ui.game

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.*
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ElectricBolt
import androidx.compose.material.icons.filled.Flag
import androidx.compose.material.icons.filled.Terrain
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.TestUiState
import com.example.ui.theme.*
import kotlin.math.sin

/**
 * SummitRushCanvas
 *
 * Visual Gamified Practice Engine for UPSC Geography.
 * Renders an animated mountain altitude ascent where correct answers under time pressure
 * propel the expedition explorer up the Himalayan transect in real time.
 */
@Composable
fun SummitRushCanvas(
    uiState: TestUiState,
    onToggleGameMode: () -> Unit,
    modifier: Modifier = Modifier
) {
    if (!uiState.isGameModeEnabled) {
        // Calm Minimalist Mode Toggle Bar
        Surface(
            color = DeepBasalt.copy(alpha = 0.95f),
            shape = RoundedCornerShape(10.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, TopoContourMuted.copy(alpha = 0.3f)),
            modifier = modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp, vertical = 4.dp)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 12.dp, vertical = 6.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.Terrain,
                        contentDescription = "Calm Transect Mode",
                        tint = TopoContourMuted,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "TRANSECT MODE: CALM STUDY",
                        color = TopoContourMuted,
                        fontSize = 11.sp,
                        fontFamily = CoordinatesMonospace,
                        fontWeight = FontWeight.Bold
                    )
                }
                TextButton(
                    onClick = onToggleGameMode,
                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp)
                ) {
                    Text(
                        text = "⚡ ACTIVATE SUMMIT RUSH",
                        color = SunstoneGold,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = CoordinatesMonospace
                    )
                }
            }
        }
        return
    }

    // Active Gamified Mode
    val targetFraction = (uiState.currentAltitudeMeters - 500).toFloat() / maxOf(1f, (uiState.targetAltitudeMeters - 500).toFloat())
    val animatedClimbProgress by animateFloatAsState(
        targetValue = targetFraction.coerceIn(0f, 1f),
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioLowBouncy,
            stiffness = Spring.StiffnessLow
        ),
        label = "climber_elevation_progress"
    )

    // Infinite breathing animation for mountain wind & trail particles
    val infiniteTransition = rememberInfiniteTransition(label = "mountain_ambience")
    val windSway by infiniteTransition.animateFloat(
        initialValue = -3f,
        targetValue = 3f,
        animationSpec = infiniteRepeatable(
            animation = tween(2000, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse
        ),
        label = "wind_sway"
    )

    // Elevation Zone Classification
    val elevationZoneName = when {
        uiState.currentAltitudeMeters >= 8000 -> "EVEREST SUMMIT CREST"
        uiState.currentAltitudeMeters >= 6000 -> "HIMADRI GLACIAL COL"
        uiState.currentAltitudeMeters >= 4000 -> "PIR PANJAL BUGYALS"
        uiState.currentAltitudeMeters >= 2000 -> "SHIWALIK PINE RIDGE"
        else -> "TERAI VALLEY FOOTHILLS"
    }

    val timerProgress = (uiState.questionTimerSeconds.toFloat() / 35f).coerceIn(0f, 1f)
    val timerColor = when {
        uiState.questionTimerSeconds > 15 -> ContourEmerald
        uiState.questionTimerSeconds > 7 -> SunstoneGold
        else -> MagmaCrimson
    }

    Surface(
        color = DeepBasalt.copy(alpha = 0.98f),
        shape = RoundedCornerShape(14.dp),
        border = androidx.compose.foundation.BorderStroke(1.5.dp, if (uiState.isOxygenBoostActive) SunstoneGold else HydrosphereCyan.copy(alpha = 0.4f)),
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 4.dp)
    ) {
        Column(modifier = Modifier.padding(10.dp)) {
            // HUD Top Stat Bar
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(8.dp)
                            .clip(CircleShape)
                            .background(if (uiState.isOxygenBoostActive) SunstoneGold else ContourEmerald)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "ALT: %,dm".format(uiState.currentAltitudeMeters),
                        color = if (uiState.isOxygenBoostActive) SunstoneGold else AtlasParchment,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Black,
                        fontFamily = CoordinatesMonospace
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "• $elevationZoneName",
                        color = TopoContourMuted,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Medium
                    )
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (uiState.comboMultiplier > 1) {
                        Surface(
                            color = SunstoneGold.copy(alpha = 0.2f),
                            shape = RoundedCornerShape(6.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, SunstoneGold)
                        ) {
                            Text(
                                text = "🔥 ${uiState.comboMultiplier}x COMBO",
                                color = SunstoneGold,
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(6.dp))
                    }

                    // Mode switch toggle
                    Text(
                        text = "🏔️ RUSH ON",
                        color = GlacierAzure,
                        fontSize = 9.sp,
                        fontFamily = CoordinatesMonospace,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier
                            .clip(RoundedCornerShape(4.dp))
                            .background(OceanicDark)
                            .clickable { onToggleGameMode() }
                            .padding(horizontal = 6.dp, vertical = 3.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(6.dp))

            // Mountain Ascent Canvas with Parallax Contours & Explorer
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(58.dp)
                    .clip(RoundedCornerShape(8.dp))
                    .background(OceanicDark)
            ) {
                Canvas(modifier = Modifier.fillMaxSize()) {
                    drawMountainBackdrop(size, windSway)
                    drawAscentTrail(size, animatedClimbProgress)
                    drawClimberAvatar(size, animatedClimbProgress, uiState.isOxygenBoostActive, windSway)
                    drawMilestoneFlags(size)
                }

                // Elevation Gain Badge Popup
                if (uiState.elevationGainLastAnswer > 0) {
                    Box(
                        modifier = Modifier
                            .align(Alignment.TopEnd)
                            .padding(end = 8.dp, top = 4.dp)
                    ) {
                        Surface(
                            color = ContourEmerald.copy(alpha = 0.9f),
                            shape = RoundedCornerShape(4.dp)
                        ) {
                            Text(
                                text = "+${uiState.elevationGainLastAnswer}m ▲",
                                color = AbyssNavy,
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Black,
                                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(6.dp))

            // Time Pressure Gauge (35s Oxygen Gauge)
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.ElectricBolt,
                        contentDescription = "Oxygen Speed Timer",
                        tint = timerColor,
                        modifier = Modifier.size(12.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "OXYGEN GAUGE: ${uiState.questionTimerSeconds}s",
                        color = timerColor,
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Bold,
                        fontFamily = CoordinatesMonospace
                    )
                    if (uiState.questionTimerSeconds >= 23) {
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "(⚡ BOOST ACTIVE)",
                            color = SunstoneGold,
                            fontSize = 8.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }

                Text(
                    text = "${(animatedClimbProgress * 100).toInt()}% TO SUMMIT",
                    color = TopoContourMuted,
                    fontSize = 9.sp,
                    fontFamily = CoordinatesMonospace
                )
            }

            Spacer(modifier = Modifier.height(3.dp))

            // Slim Countdown Bar
            LinearProgressIndicator(
                progress = { timerProgress },
                color = timerColor,
                trackColor = DeepBasalt,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(3.dp)
                    .clip(RoundedCornerShape(1.5.dp))
            )
        }
    }
}

private fun DrawScope.drawMountainBackdrop(size: androidx.compose.ui.geometry.Size, windSway: Float) {
    val w = size.width
    val h = size.height

    // Background Mountain Silhouette
    val bgPath = Path().apply {
        moveTo(0f, h)
        lineTo(0f, h * 0.65f)
        cubicTo(w * 0.25f, h * 0.45f + windSway, w * 0.45f, h * 0.55f, w * 0.7f, h * 0.25f)
        lineTo(w, h * 0.15f)
        lineTo(w, h)
        close()
    }
    drawPath(bgPath, color = GlacierAzure.copy(alpha = 0.12f))

    // Midground Ridge
    val midPath = Path().apply {
        moveTo(0f, h)
        lineTo(0f, h * 0.85f)
        cubicTo(w * 0.3f, h * 0.7f, w * 0.6f, h * 0.45f, w * 0.85f, h * 0.35f)
        lineTo(w, h * 0.2f)
        lineTo(w, h)
        close()
    }
    drawPath(midPath, color = OceanicDark.copy(alpha = 0.5f))
}

private fun DrawScope.drawAscentTrail(size: androidx.compose.ui.geometry.Size, progress: Float) {
    val w = size.width
    val h = size.height

    // The Ascent Slope line from bottom-left (500m) to top-right (8848m)
    val startX = 20f
    val startY = h - 14f
    val endX = w - 24f
    val endY = 14f

    // Inactive trail
    drawLine(
        color = TopoContourMuted.copy(alpha = 0.3f),
        start = Offset(startX, startY),
        end = Offset(endX, endY),
        strokeWidth = 3f,
        pathEffect = PathEffect.dashPathEffect(floatArrayOf(8f, 6f), 0f)
    )

    // Active Conquered Trail
    val currentX = startX + (endX - startX) * progress
    val currentY = startY + (endY - startY) * progress
    drawLine(
        color = ContourEmerald,
        start = Offset(startX, startY),
        end = Offset(currentX, currentY),
        strokeWidth = 4f
    )
}

private fun DrawScope.drawClimberAvatar(
    size: androidx.compose.ui.geometry.Size,
    progress: Float,
    isBoostActive: Boolean,
    windSway: Float
) {
    val w = size.width
    val h = size.height

    val startX = 20f
    val startY = h - 14f
    val endX = w - 24f
    val endY = 14f

    val cx = startX + (endX - startX) * progress
    val cy = startY + (endY - startY) * progress

    // Speed Boost Golden Aura
    if (isBoostActive) {
        drawCircle(
            brush = Brush.radialGradient(
                colors = listOf(SunstoneGold.copy(alpha = 0.6f), Color.Transparent),
                center = Offset(cx, cy),
                radius = 18f
            ),
            radius = 18f,
            center = Offset(cx, cy)
        )
    }

    // Climber Body: Head & Torso with trekking backpack
    val climberColor = if (isBoostActive) SunstoneGold else AtlasParchment

    // Head
    drawCircle(
        color = climberColor,
        radius = 4.5f,
        center = Offset(cx, cy - 10f)
    )

    // Torso (leaning into mountain slope)
    drawLine(
        color = climberColor,
        start = Offset(cx, cy - 6f),
        end = Offset(cx + 2f, cy),
        strokeWidth = 3.5f
    )

    // Backpack
    drawCircle(
        color = OceanicDark,
        radius = 3.5f,
        center = Offset(cx - 3.5f, cy - 4f)
    )
    drawCircle(
        color = if (isBoostActive) SunstoneGold else GlacierAzure,
        radius = 2.5f,
        center = Offset(cx - 3.5f, cy - 4f)
    )

    // Trekking Pole (planted ahead on slope)
    drawLine(
        color = SunstoneGold,
        start = Offset(cx + 1f, cy - 4f),
        end = Offset(cx + 7f, cy + 2f),
        strokeWidth = 1.8f
    )

    // Ground shadow
    drawOval(
        color = Color.Black.copy(alpha = 0.4f),
        topLeft = Offset(cx - 5f, cy + 1f),
        size = androidx.compose.ui.geometry.Size(12f, 4f)
    )
}

private fun DrawScope.drawMilestoneFlags(size: androidx.compose.ui.geometry.Size) {
    val w = size.width
    val h = size.height
    val endX = w - 24f
    val endY = 14f

    // Summit Flagpole at the peak
    drawLine(
        color = SunstoneGold,
        start = Offset(endX, endY + 4f),
        end = Offset(endX, endY - 12f),
        strokeWidth = 2f
    )
    // Pennant Flag
    val flagPath = Path().apply {
        moveTo(endX, endY - 12f)
        lineTo(endX + 10f, endY - 8f)
        lineTo(endX, endY - 4f)
        close()
    }
    drawPath(flagPath, color = SunstoneGold)
}
