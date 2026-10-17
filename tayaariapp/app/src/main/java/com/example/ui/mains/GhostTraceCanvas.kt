package com.example.ui.mains

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.MicroDiagramBlueprint
import kotlinx.coroutines.delay

@Composable
fun GhostTraceCanvas(
    blueprint: MicroDiagramBlueprint,
    modifier: Modifier = Modifier,
    onCompleted: (timeTakenSec: Int, accuracy: Float) -> Unit = { _, _ -> },
    onDismiss: () -> Unit = {}
) {
    var drawnPaths by remember { mutableStateOf(listOf<List<Offset>>()) }
    var currentPath by remember { mutableStateOf(listOf<Offset>()) }
    var timeRemainingSeconds by remember { mutableIntStateOf(blueprint.targetSeconds) }
    var isTimerRunning by remember { mutableStateOf(false) }
    var isCompleted by remember { mutableStateOf(false) }

    // Countdown Timer Coroutine
    LaunchedEffect(isTimerRunning) {
        if (isTimerRunning && timeRemainingSeconds > 0) {
            while (timeRemainingSeconds > 0 && isTimerRunning) {
                delay(1000L)
                timeRemainingSeconds--
            }
            if (timeRemainingSeconds == 0) {
                isCompleted = true
                isTimerRunning = false
                val accuracy = (drawnPaths.size.coerceAtLeast(1) * 0.25f).coerceIn(0.6f, 0.95f)
                onCompleted(blueprint.targetSeconds, accuracy)
            }
        }
    }

    Card(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(16.dp)),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.95f)),
        elevation = CardDefaults.cardElevation(defaultElevation = 8.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            // Header Bar: Diagram Title & 20-Second Stopwatch Ring
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(
                        text = "📐 20s Micro-Diagram Canvas",
                        style = MaterialTheme.typography.labelMedium,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    Text(
                        text = blueprint.name,
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.ExtraBold,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                }

                // 20s Timer Ring
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier
                        .size(48.dp)
                        .clip(CircleShape)
                        .background(if (timeRemainingSeconds <= 5) MaterialTheme.colorScheme.errorContainer else MaterialTheme.colorScheme.primaryContainer)
                ) {
                    Text(
                        text = "${timeRemainingSeconds}s",
                        style = MaterialTheme.typography.labelLarge,
                        fontWeight = FontWeight.Bold,
                        color = if (timeRemainingSeconds <= 5) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
                    )
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Mandatory Physical Paper Guardrail Banner
            Surface(
                color = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.5f),
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Icon(
                        imageVector = Icons.Default.EditNote,
                        contentDescription = "Paper Note",
                        tint = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "Examiner Mandate: Replicate this on real paper with pen within 20s!",
                        style = MaterialTheme.typography.labelSmall,
                        fontWeight = FontWeight.SemiBold,
                        color = MaterialTheme.colorScheme.onSecondaryContainer
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Interactive Drawing Canvas (With Translucent Ghost Vector Outline)
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(220.dp)
                    .clip(RoundedCornerShape(12.dp))
                    .background(Color(0xFF0F172A)) // Slate Dark Canvas
                    .border(BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)), RoundedCornerShape(12.dp))
                    .pointerInput(Unit) {
                        detectDragGestures(
                            onDragStart = { offset ->
                                if (!isTimerRunning && timeRemainingSeconds > 0) {
                                    isTimerRunning = true
                                }
                                currentPath = listOf(offset)
                            },
                            onDrag = { change, _ ->
                                currentPath = currentPath + change.position
                            },
                            onDragEnd = {
                                if (currentPath.isNotEmpty()) {
                                    drawnPaths = drawnPaths + listOf(currentPath)
                                    currentPath = emptyList()
                                }
                            }
                        )
                    }
            ) {
                // Background Ghost Guide (ASCII Rendering / Grid)
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(12.dp)
                ) {
                    Text(
                        text = blueprint.asciiRendering,
                        fontFamily = FontFamily.Monospace,
                        fontSize = 10.sp,
                        color = Color.White.copy(alpha = 0.22f), // Faint Ghost Vector Outline
                        lineHeight = 13.sp
                    )
                }

                // Foreground Canvas Rendering User's Finger Strokes
                Canvas(modifier = Modifier.fillMaxSize()) {
                    // Draw completed paths
                    drawnPaths.forEach { points ->
                        if (points.size > 1) {
                            val path = Path().apply {
                                moveTo(points.first().x, points.first().y)
                                for (i in 1 until points.size) {
                                    lineTo(points[i].x, points[i].y)
                                }
                            }
                            drawPath(
                                path = path,
                                color = Color(0xFF10B981), // Emerald Stroke
                                style = Stroke(width = 4.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
                            )
                        }
                    }

                    // Draw currently active stroke
                    if (currentPath.size > 1) {
                        val path = Path().apply {
                            moveTo(currentPath.first().x, currentPath.first().y)
                            for (i in 1 until currentPath.size) {
                                lineTo(currentPath[i].x, currentPath[i].y)
                            }
                        }
                        drawPath(
                            path = path,
                            color = Color(0xFF38BDF8), // Cyan Active Stroke
                            style = Stroke(width = 4.dp.toPx(), cap = StrokeCap.Round, join = StrokeJoin.Round)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Step-by-Step Stroke Guidance
            Text(
                text = "⚡ Stroke Instructions (${blueprint.strokeInstructions.size} Steps):",
                style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            blueprint.strokeInstructions.forEach { instruction ->
                Text(
                    text = "• $instruction",
                    style = MaterialTheme.typography.bodySmall,
                    fontSize = 11.sp,
                    color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.85f),
                    modifier = Modifier.padding(start = 4.dp, top = 2.dp)
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Action Buttons (Clear, Start/Pause, Done)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextButton(
                    onClick = {
                        drawnPaths = emptyList()
                        currentPath = emptyList()
                        timeRemainingSeconds = blueprint.targetSeconds
                        isTimerRunning = false
                        isCompleted = false
                    }
                ) {
                    Icon(Icons.Default.Refresh, contentDescription = "Clear", modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Clear Canvas", style = MaterialTheme.typography.labelMedium)
                }

                Row {
                    FilledTonalButton(
                        onClick = onDismiss
                    ) {
                        Text("Close")
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Button(
                        onClick = {
                            isTimerRunning = false
                            isCompleted = true
                            val accuracy = (drawnPaths.size.coerceAtLeast(1) * 0.25f).coerceIn(0.7f, 0.95f)
                            onCompleted(blueprint.targetSeconds - timeRemainingSeconds, accuracy)
                            onDismiss()
                        }
                    ) {
                        Icon(Icons.Default.Check, contentDescription = "Done", modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(4.dp))
                        Text("Done")
                    }
                }
            }
        }
    }
}
