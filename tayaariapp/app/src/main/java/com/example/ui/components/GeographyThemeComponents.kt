package com.example.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import kotlin.math.cos
import kotlin.math.sin

// ==========================================
// CARTOGRAPHIC & ATLAS CANVASES
// ==========================================

@Composable
fun AtlasBackground(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    val oceanGradient = Brush.verticalGradient(
        colors = listOf(
            AbyssNavy,
            OceanicDark,
            AbyssNavy
        )
    )

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(brush = oceanGradient)
    ) {
        // 1. Graticule Lat/Long Grid & Intersection Ticks
        Canvas(modifier = Modifier.fillMaxSize()) {
            val gridColor = HydrosphereCyan.copy(alpha = 0.035f)
            val tickColor = HydrosphereCyan.copy(alpha = 0.08f)
            val stepX = 56.dp.toPx()
            val stepY = 56.dp.toPx()

            var x = 0f
            while (x < size.width) {
                drawLine(gridColor, Offset(x, 0f), Offset(x, size.height), strokeWidth = 1f)
                x += stepX
            }

            var y = 0f
            while (y < size.height) {
                drawLine(gridColor, Offset(0f, y), Offset(size.width, y), strokeWidth = 1f)
                y += stepY
            }

            // Draw survey intersection crosses (+) at grid points
            x = stepX
            while (x < size.width) {
                y = stepY
                while (y < size.height) {
                    val crossSize = 4.dp.toPx()
                    drawLine(tickColor, Offset(x - crossSize, y), Offset(x + crossSize, y), strokeWidth = 1.2f)
                    drawLine(tickColor, Offset(x, y - crossSize), Offset(x, y + crossSize), strokeWidth = 1.2f)
                    y += stepY * 2
                }
                x += stepX * 2
            }
        }

        // 2. Faint Compass Rose Watermark in top corner
        CompassRoseWatermark(
            modifier = Modifier
                .align(Alignment.TopEnd)
                .padding(top = 16.dp, end = 16.dp)
                .size(140.dp)
        )

        content()
    }
}

@Composable
fun CyberBackground(
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    AtlasBackground(modifier = modifier, content = content)
}

@Composable
fun TopographicBackground(
    modifier: Modifier = Modifier,
    lineColor: Color = ContourEmerald.copy(alpha = 0.045f),
    content: @Composable () -> Unit
) {
    Box(modifier = modifier.fillMaxSize()) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val width = size.width
            val height = size.height
            val path = Path()

            // Draw 7 flowing topographic elevation contour lines
            for (i in 1..7) {
                path.reset()
                var x = 0f
                val yOffset = height * (i / 9f)
                path.moveTo(x, yOffset)

                while (x <= width) {
                    val y = yOffset +
                            (sin(x * 0.008f + i * 1.2f) * 45f) +
                            (cos(x * 0.015f - i * 0.8f) * 25f)
                    path.lineTo(x, y)
                    x += 24f
                }
                drawPath(path = path, color = lineColor, style = Stroke(width = 1.2f))
            }
        }
        content()
    }
}

// ==========================================
// COMPASS ROSE WATERMARK
// ==========================================

@Composable
fun CompassRoseWatermark(modifier: Modifier = Modifier) {
    Canvas(modifier = modifier) {
        val center = Offset(size.width / 2f, size.height / 2f)
        val radius = size.minDimension / 2f
        val roseColor = HydrosphereCyan.copy(alpha = 0.035f)
        val accentColor = SunstoneGold.copy(alpha = 0.045f)

        // Outer azimuth ring
        drawCircle(roseColor, radius = radius * 0.9f, center = center, style = Stroke(width = 1f))
        drawCircle(roseColor, radius = radius * 0.7f, center = center, style = Stroke(width = 0.8f))

        // 8-point compass star
        val points = 8
        val path = Path()
        for (i in 0 until points) {
            val angle = (i * Math.PI / 4).toFloat()
            val nextAngle = ((i + 1) * Math.PI / 4).toFloat()
            val midAngle = ((angle + nextAngle) / 2f)

            val outerX = center.x + radius * 0.85f * cos(angle)
            val outerY = center.y + radius * 0.85f * sin(angle)

            val innerX = center.x + radius * 0.25f * cos(midAngle)
            val innerY = center.y + radius * 0.25f * sin(midAngle)

            path.reset()
            path.moveTo(center.x, center.y)
            path.lineTo(outerX, outerY)
            path.lineTo(innerX, innerY)
            path.close()

            drawPath(path, if (i % 2 == 0) accentColor else roseColor)
        }
    }
}

// ==========================================
// CARTOGRAPHIC CARDS & HUD CONTAINERS
// ==========================================

@Composable
fun AtlasCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    borderColor: Color = CartographicBorder,
    content: @Composable () -> Unit
) {
    val cardShape = RoundedCornerShape(16.dp)
    val cardColors = CardDefaults.cardColors(
        containerColor = DeepBasalt.copy(alpha = 0.94f),
        contentColor = AtlasParchment
    )
    val borderStroke = BorderStroke(1.dp, borderColor)

    if (onClick != null) {
        Card(
            onClick = onClick,
            modifier = modifier,
            shape = cardShape,
            colors = cardColors,
            border = borderStroke,
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Box(modifier = Modifier.padding(16.dp)) {
                content()
            }
        }
    } else {
        Card(
            modifier = modifier,
            shape = cardShape,
            colors = cardColors,
            border = borderStroke,
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
        ) {
            Box(modifier = Modifier.padding(16.dp)) {
                content()
            }
        }
    }
}

// ==========================================
// GEOGRAPHY HUD BADGES & COORDINATE PILLS
// ==========================================

@Composable
fun CyberHudBadge(
    text: String,
    icon: ImageVector? = null,
    accentColor: Color = HydrosphereCyan,
    modifier: Modifier = Modifier
) {
    CartographicBadge(text = text, icon = icon, accentColor = accentColor, modifier = modifier)
}

@Composable
fun CartographicBadge(
    text: String,
    icon: ImageVector? = null,
    accentColor: Color = HydrosphereCyan,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .clip(RoundedCornerShape(8.dp))
            .background(accentColor.copy(alpha = 0.14f))
            .padding(horizontal = 10.dp, vertical = 5.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            if (icon != null) {
                Icon(
                    imageVector = icon,
                    contentDescription = null,
                    tint = accentColor,
                    modifier = Modifier.size(13.dp)
                )
                Spacer(modifier = Modifier.width(4.dp))
            }
            Text(
                text = text,
                color = accentColor,
                fontWeight = FontWeight.Bold,
                fontSize = 11.sp,
                letterSpacing = 0.6.sp
            )
        }
    }
}

@Composable
fun StreakFirePill(
    streakDays: Int,
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .clip(CircleShape)
            .background(SunstoneGold.copy(alpha = 0.16f))
            .padding(horizontal = 12.dp, vertical = 6.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text("🧭", fontSize = 14.sp)
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = "Day $streakDays Expedition",
                color = SunstoneGold,
                fontWeight = FontWeight.ExtraBold,
                fontSize = 12.sp
            )
        }
    }
}

@Composable
fun CartographicCoordinatesBanner(
    coordinates: String = "82°30′E IST // 23°30′N CANCER",
    modifier: Modifier = Modifier,
    coordinatesText: String = coordinates
) {
    val displayCoordinates = if (coordinatesText != "82°30′E IST // 23°30′N CANCER" && coordinates == "82°30′E IST // 23°30′N CANCER") {
        coordinatesText
    } else {
        coordinates
    }
    Surface(
        color = OceanicDark.copy(alpha = 0.65f),
        shape = RoundedCornerShape(6.dp),
        border = BorderStroke(1.dp, HydrosphereCyan.copy(alpha = 0.2f)),
        modifier = modifier
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = if (displayCoordinates.startsWith("📍")) displayCoordinates else "📍 $displayCoordinates",
                color = MeridianMuted,
                fontSize = 10.sp,
                fontFamily = CoordinatesMonospace,
                fontWeight = FontWeight.Medium,
                letterSpacing = 0.5.sp
            )
        }
    }
}

@Composable
fun ElevationTierPill(
    tier: String,
    modifier: Modifier = Modifier
) {
    val (label, color, icon) = when (tier.lowercase()) {
        "basic" -> Triple("NCERT Base (0m)", ContourEmerald, "🟢")
        "medium" -> Triple("Montane Ridge (800m)", SunstoneGold, "🟡")
        "hard" -> Triple("Alpine Peak (8,848m)", MagmaCrimson, "🔴")
        else -> Triple(tier.uppercase(), HydrosphereCyan, "📍")
    }

    Box(
        modifier = modifier
            .clip(RoundedCornerShape(6.dp))
            .background(color.copy(alpha = 0.15f))
            .padding(horizontal = 8.dp, vertical = 4.dp)
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(icon, fontSize = 10.sp)
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = label,
                color = color,
                fontSize = 11.sp,
                fontWeight = FontWeight.Bold,
                letterSpacing = 0.4.sp
            )
        }
    }
}
