package com.example.ui.mains

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.MenuBook
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.example.model.MainsEvaluationResult

@Composable
fun MainsEvaluationResultDialog(
    result: MainsEvaluationResult,
    onDismiss: () -> Unit,
    onReattempt: () -> Unit,
    onRevealModelAnswer: () -> Unit
) {
    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false)
    ) {
        Surface(
            modifier = Modifier
                .fillMaxWidth(0.95f)
                .fillMaxHeight(0.90f)
                .clip(RoundedCornerShape(24.dp)),
            color = MaterialTheme.colorScheme.surface,
            tonalElevation = 6.dp
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(20.dp)
                    .verticalScroll(rememberScrollState())
            ) {
                // Header: Examiner Seal & Close Button
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(40.dp)
                                .clip(CircleShape)
                                .background(MaterialTheme.colorScheme.primaryContainer),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                imageVector = Icons.Default.Verified,
                                contentDescription = "Seal",
                                tint = MaterialTheme.colorScheme.primary,
                                modifier = Modifier.size(24.dp)
                            )
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Column {
                            Text(
                                text = "Chief Evaluator Report",
                                style = MaterialTheme.typography.titleMedium,
                                fontWeight = FontWeight.ExtraBold
                            )
                            Text(
                                text = "Attempt #${result.attemptNumber} • Infinite Deliberate Practice",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }

                    IconButton(onClick = onDismiss) {
                        Icon(Icons.Default.Close, contentDescription = "Close")
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Score Banner Card
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = if (result.totalScore >= result.maxMarks * 0.7f) Color(0xFF064E3B) else Color(0xFF1E293B)
                    ),
                    shape = RoundedCornerShape(16.dp)
                ) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = result.percentileBand,
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.Bold,
                            color = Color(0xFF34D399) // Emerald
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Row(verticalAlignment = Alignment.Bottom) {
                            Text(
                                text = "${result.totalScore}",
                                style = MaterialTheme.typography.displayMedium,
                                fontWeight = FontWeight.Black,
                                color = Color.White
                            )
                            Text(
                                text = " / ${result.maxMarks.toInt()} Marks",
                                style = MaterialTheme.typography.titleLarge,
                                fontWeight = FontWeight.Bold,
                                color = Color.White.copy(alpha = 0.7f),
                                modifier = Modifier.padding(bottom = 6.dp, start = 4.dp)
                            )
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(
                            text = "\"${result.examinerVerdict}\"",
                            style = MaterialTheme.typography.bodySmall,
                            color = Color.White.copy(alpha = 0.9f),
                            lineHeight = 16.sp
                        )
                    }
                }

                // Word Economy & Information Density Card
                if (result.wordCount > 0) {
                    Spacer(modifier = Modifier.height(12.dp))
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
                        ),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Column(modifier = Modifier.padding(12.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "✍️ Word Economy: ${result.wordCount} Words",
                                    style = MaterialTheme.typography.labelMedium,
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    text = "Concept Density: ${result.conceptualDensityScore.toInt()}%",
                                    style = MaterialTheme.typography.labelSmall,
                                    fontWeight = FontWeight.ExtraBold,
                                    color = if (result.conceptualDensityScore >= 75f) Color(0xFF059669) else Color(0xFFD97706)
                                )
                            }
                            if (result.wordCountEnvelopeFeedback.isNotBlank()) {
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = result.wordCountEnvelopeFeedback,
                                    style = MaterialTheme.typography.bodySmall,
                                    fontSize = 12.sp,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // 5-Component Scoring Rubric Bars
                Text(
                    text = "📊 5-Component Evaluator Rubric",
                    style = MaterialTheme.typography.labelLarge,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))

                val maxComponent = result.maxMarks * 0.20f
                ComponentScoreBar(title = "1. Theoretical Precision & Thinkers", score = result.scoreTheory, max = maxComponent)
                ComponentScoreBar(title = "2. Empirical Case & Indian Proof", score = result.scoreEmpirical, max = maxComponent)
                ComponentScoreBar(title = "3. Micro-Diagram & Visual Schematics", score = result.scoreDiagram, max = maxComponent)
                ComponentScoreBar(title = "4. P-H-E-S-G Dimensional Depth", score = result.scorePhesg, max = maxComponent)
                ComponentScoreBar(title = "5. Presentation & Directive Compliance", score = result.scorePresentation, max = maxComponent)

                Spacer(modifier = Modifier.height(16.dp))

                // Green Highlights (Earned Marks)
                if (result.greenHighlights.isNotEmpty()) {
                    Text(
                        text = "🟢 Topper Strengths (Earned Marks):",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFF059669)
                    )
                    result.greenHighlights.forEach { item ->
                        Text(
                            text = "• $item",
                            style = MaterialTheme.typography.bodySmall,
                            fontSize = 12.sp,
                            modifier = Modifier.padding(start = 6.dp, top = 2.dp)
                        )
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                }

                // Yellow Warnings (Generic GS Prose)
                if (result.yellowWarnings.isNotEmpty()) {
                    Text(
                        text = "🟡 GS-1 Prose Warnings (Elevate to Optional):",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = Color(0xFFD97706)
                    )
                    result.yellowWarnings.forEach { item ->
                        Text(
                            text = "• $item",
                            style = MaterialTheme.typography.bodySmall,
                            fontSize = 12.sp,
                            modifier = Modifier.padding(start = 6.dp, top = 2.dp)
                        )
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                }

                // Red Omissions (Missing Critical Elements)
                if (result.redOmissions.isNotEmpty()) {
                    Text(
                        text = "🔴 Critical Omissions (Examiner Penalties):",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.error
                    )
                    result.redOmissions.forEach { item ->
                        Text(
                            text = "• $item",
                            style = MaterialTheme.typography.bodySmall,
                            fontSize = 12.sp,
                            modifier = Modifier.padding(start = 6.dp, top = 2.dp)
                        )
                    }
                    Spacer(modifier = Modifier.height(16.dp))
                }

                // Footer Actions: Re-attempt Infinite Loop & Reveal Model Answer
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    OutlinedButton(
                        onClick = onReattempt,
                        modifier = Modifier.weight(1f)
                    ) {
                        Icon(Icons.Default.Refresh, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Re-attempt")
                    }

                    Button(
                        onClick = onRevealModelAnswer,
                        modifier = Modifier.weight(1.3f)
                    ) {
                        Icon(Icons.AutoMirrored.Filled.MenuBook, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(modifier = Modifier.width(6.dp))
                        Text("Model Solution")
                    }
                }
            }
        }
    }
}

@Composable
private fun ComponentScoreBar(title: String, score: Float, max: Float) {
    val progress = (score / max).coerceIn(0f, 1f)
    Column(modifier = Modifier.padding(vertical = 4.dp)) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(text = title, style = MaterialTheme.typography.bodySmall, fontSize = 11.sp)
            Text(
                text = "${score}/${String.format("%.1f", max)}",
                style = MaterialTheme.typography.labelSmall,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
        }
        Spacer(modifier = Modifier.height(2.dp))
        LinearProgressIndicator(
            progress = { progress },
            modifier = Modifier
                .fillMaxWidth()
                .height(6.dp)
                .clip(RoundedCornerShape(3.dp)),
            color = if (progress >= 0.75f) Color(0xFF10B981) else if (progress >= 0.5f) Color(0xFFF59E0B) else MaterialTheme.colorScheme.error,
            trackColor = MaterialTheme.colorScheme.surfaceVariant
        )
    }
}
