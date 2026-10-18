package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ExamQuestion
import com.example.model.MCQQuestion
import com.example.ui.theme.*
import com.example.viewmodel.BookmarksViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BookmarksScreen(
    viewModel: BookmarksViewModel,
    onBack: () -> Unit
) {
    val questions by viewModel.bookmarkedQuestions.collectAsState()
    val availableTopics by viewModel.availableTopics.collectAsState()
    val selectedTopic by viewModel.selectedTopic.collectAsState()

    com.example.ui.components.AtlasBackground {
        com.example.ui.components.TopographicBackground(lineColor = ContourEmerald.copy(alpha = 0.035f)) {
            Scaffold(
                containerColor = Color.Transparent,
                topBar = {
                    TopAppBar(
                        title = {
                            Column {
                                Text(
                                    "Saved Folios & Waypoints 📍",
                                    color = SummitGold,
                                    fontFamily = CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 18.sp
                                )
                                Text(
                                    "FIELD CADASTRE & ACTIVE RECALL DECK",
                                    color = GlacierAzure,
                                    fontFamily = CoordinatesMonospace,
                                    fontSize = 10.sp,
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
                            containerColor = Color.Transparent
                        )
                    )
                }
            ) { paddingValues ->
                Column(
                    modifier = Modifier
                        .padding(paddingValues)
                        .fillMaxSize()
                ) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Box(modifier = Modifier.padding(horizontal = 16.dp)) {
                        com.example.ui.components.CartographicCoordinatesBanner(
                            coordinatesText = "📍 GEOGRAPHIC FIELD FOLIO // ${questions.size} RECORDED WAYPOINTS"
                        )
                    }

                    if (availableTopics.size > 1) {
                        LazyRow(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(horizontal = 16.dp, vertical = 10.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            items(availableTopics) { topic ->
                                val isSelected = topic == selectedTopic
                                Surface(
                                    color = if (isSelected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceVariant,
                                    shape = RoundedCornerShape(8.dp),
                                    border = BorderStroke(
                                        1.dp,
                                        if (isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline.copy(alpha = 0.5f)
                                    ),
                                    modifier = Modifier.clickable { viewModel.filterByTopic(topic) }
                                ) {
                                    Text(
                                        text = "🗺️ $topic",
                                        color = if (isSelected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant,
                                        fontSize = 12.sp,
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                                    )
                                }
                            }
                        }
                    }

                    if (questions.isEmpty()) {
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(32.dp),
                            contentAlignment = Alignment.Center
                        ) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text(
                                    text = "🧭",
                                    fontSize = 48.sp
                                )
                                Spacer(modifier = Modifier.height(12.dp))
                                Text(
                                    text = "No Field Waypoints Recorded",
                                    fontFamily = CartographicSerif,
                                    color = MaterialTheme.colorScheme.onBackground,
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold
                                )
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(
                                    text = "Tap the bookmark ribbon (🔖) during any expedition transect to save crucial map questions, diagrams, and memory keys to your folio.",
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    fontSize = 13.sp,
                                    lineHeight = 18.sp,
                                    textAlign = TextAlign.Center
                                )
                            }
                        }
                    } else {
                        LazyColumn(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(horizontal = 16.dp),
                            contentPadding = PaddingValues(top = 8.dp, bottom = 24.dp),
                            verticalArrangement = Arrangement.spacedBy(14.dp)
                        ) {
                            items(questions, key = { it.id }) { q ->
                                PremiumBookmarkCard(
                                    question = q,
                                    onRemove = { viewModel.removeBookmark(q.id) }
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

/**
 * Interactive Bookmark Card with Active Recall Flashcard Test Mode
 */
@Composable
fun PremiumBookmarkCard(
    question: ExamQuestion,
    onRemove: () -> Unit
) {
    val haptic = LocalHapticFeedback.current
    val fontScale = LocalFontScale.current
    var isTestRecallMode by remember { mutableStateOf(false) }
    var selectedOptionId by remember { mutableStateOf<String?>(null) }
    val mcq = question as? MCQQuestion
    val formatText = mcq?.questionFormatType ?: "Direct Cartography"

    com.example.ui.components.AtlasCard(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            // Header Row: Format Tag, Chapter Code, and Actions
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Surface(
                        color = MaterialTheme.colorScheme.surfaceVariant,
                        shape = RoundedCornerShape(4.dp),
                        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.5f))
                    ) {
                        Text(
                            text = "🧭 ${formatText.uppercase()}",
                            color = GlacierAzure,
                            fontSize = 10.sp,
                            fontFamily = CoordinatesMonospace,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                    Text(
                        text = "📍 ${question.chapterCode}",
                        color = SunstoneGold,
                        fontSize = 11.sp,
                        fontFamily = CoordinatesMonospace,
                        fontWeight = FontWeight.Bold
                    )
                }

                Row(verticalAlignment = Alignment.CenterVertically) {
                    // Active Recall Drill Toggle
                    Surface(
                        color = if (isTestRecallMode) SunstoneGold else MaterialTheme.colorScheme.surfaceVariant,
                        shape = RoundedCornerShape(6.dp),
                        border = BorderStroke(0.8.dp, SunstoneGold.copy(alpha = 0.5f)),
                        modifier = Modifier
                            .clickable {
                                isTestRecallMode = !isTestRecallMode
                                selectedOptionId = null
                            }
                    ) {
                        Text(
                            text = if (isTestRecallMode) "📖 Show Key" else "🧠 Test Recall",
                            color = if (isTestRecallMode) Color.Black else SunstoneGold,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }

                    Spacer(modifier = Modifier.width(6.dp))

                    IconButton(onClick = onRemove, modifier = Modifier.size(28.dp)) {
                        Icon(
                            Icons.Default.DeleteOutline,
                            contentDescription = "Remove Bookmark",
                            tint = MagmaCrimson,
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Question Stem
            Text(
                text = question.questionText.trim(),
                color = MaterialTheme.colorScheme.onSurface,
                fontFamily = CartographicSerif,
                fontSize = (15 * fontScale).sp,
                fontWeight = FontWeight.SemiBold,
                lineHeight = (22 * fontScale).sp
            )

            if (mcq != null) {
                Spacer(modifier = Modifier.height(14.dp))
                val correctOption = mcq.options.find { it.id == mcq.correctAnswerId }

                if (isTestRecallMode) {
                    // Active Recall Test Mode: Interactive Options (Zero spoilers until tapped!)
                    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(
                            text = "⚡ Tap an option to test your retrieval memory:",
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            fontSize = (11 * fontScale).sp,
                            fontWeight = FontWeight.Bold
                        )

                        mcq.options.forEachIndexed { idx, opt ->
                            val isSelected = selectedOptionId == opt.id
                            val isCorrect = opt.id == mcq.correctAnswerId
                            val hasTested = selectedOptionId != null

                            val optionBorderColor = when {
                                !hasTested -> MaterialTheme.colorScheme.outline.copy(alpha = 0.5f)
                                isSelected && isCorrect -> ContourEmerald
                                isSelected && !isCorrect -> MagmaCrimson
                                isCorrect -> ContourEmerald.copy(alpha = 0.6f)
                                else -> MaterialTheme.colorScheme.outline.copy(alpha = 0.2f)
                            }

                            val optionBgColor = when {
                                !hasTested -> MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
                                isSelected && isCorrect -> ContourEmerald.copy(alpha = 0.15f)
                                isSelected && !isCorrect -> MagmaCrimson.copy(alpha = 0.15f)
                                isCorrect -> ContourEmerald.copy(alpha = 0.1f)
                                else -> MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.25f)
                            }

                            Surface(
                                color = optionBgColor,
                                shape = RoundedCornerShape(8.dp),
                                border = BorderStroke(1.dp, optionBorderColor),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable(enabled = !hasTested) {
                                        haptic.performHapticFeedback(
                                            if (opt.id == mcq.correctAnswerId) HapticFeedbackType.LongPress
                                            else HapticFeedbackType.TextHandleMove
                                        )
                                        selectedOptionId = opt.id
                                    }
                            ) {
                                Row(
                                    modifier = Modifier.padding(10.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Box(
                                        modifier = Modifier
                                            .size(24.dp)
                                            .clip(CircleShape)
                                            .background(MaterialTheme.colorScheme.surfaceVariant),
                                        contentAlignment = Alignment.Center
                                    ) {
                                        Text(
                                            text = listOf("A", "B", "C", "D").getOrElse(idx) { "" },
                                            color = if (isSelected && isCorrect) ContourEmerald else MaterialTheme.colorScheme.onSurface,
                                            fontSize = (11 * fontScale).sp,
                                            fontWeight = FontWeight.Bold
                                        )
                                    }
                                    Spacer(modifier = Modifier.width(10.dp))
                                    Text(
                                        text = opt.text,
                                        color = MaterialTheme.colorScheme.onSurface,
                                        fontSize = (12.5 * fontScale).sp,
                                        modifier = Modifier.weight(1f)
                                    )
                                    if (hasTested && isCorrect) {
                                        Icon(
                                            Icons.Default.CheckCircle,
                                            contentDescription = null,
                                            tint = ContourEmerald,
                                            modifier = Modifier.size(16.dp)
                                        )
                                    }
                                }
                            }
                        }

                        if (selectedOptionId != null) {
                            Spacer(modifier = Modifier.height(6.dp))
                            val recallSuccess = selectedOptionId == mcq.correctAnswerId
                            Surface(
                                color = if (recallSuccess) ContourEmerald.copy(alpha = 0.15f) else MagmaCrimson.copy(alpha = 0.15f),
                                shape = RoundedCornerShape(8.dp),
                                border = BorderStroke(0.8.dp, if (recallSuccess) ContourEmerald else MagmaCrimson)
                            ) {
                                Column(modifier = Modifier.padding(10.dp)) {
                                    Text(
                                        text = if (recallSuccess) "🎯 RETRIEVAL MASTERED: Correct!" else "⚠️ REVIEW TRIGGER: Misaligned bearing",
                                        color = if (recallSuccess) ContourEmerald else MagmaCrimson,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = (11.5 * fontScale).sp
                                    )
                                    if (mcq.correctExplanation.isNotBlank()) {
                                        Spacer(modifier = Modifier.height(4.dp))
                                        Text(
                                            text = "🗺️ Cadastre Key: ${mcq.correctExplanation}",
                                            color = MaterialTheme.colorScheme.onSurface,
                                            fontSize = (11.5 * fontScale).sp,
                                            lineHeight = (16 * fontScale).sp
                                        )
                                    }
                                }
                            }
                        }
                    }
                } else {
                    // Default Folio View: Surveyor General Key & Deep Explanation
                    Surface(
                        color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f),
                        shape = RoundedCornerShape(10.dp),
                        border = BorderStroke(1.dp, ContourEmerald.copy(alpha = 0.5f)),
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Column(modifier = Modifier.padding(12.dp)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(
                                    Icons.Default.CheckCircleOutline,
                                    contentDescription = null,
                                    tint = ContourEmerald,
                                    modifier = Modifier.size(16.dp)
                                )
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = "SURVEYOR GENERAL KEY: ${correctOption?.text ?: "Unknown"}",
                                    color = ContourEmerald,
                                    fontSize = (13 * fontScale).sp,
                                    fontWeight = FontWeight.Bold,
                                    lineHeight = (18 * fontScale).sp
                                )
                            }
                            if (mcq.correctExplanation.isNotBlank()) {
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(
                                    text = "🗺️ ${mcq.correctExplanation}",
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    fontSize = (12 * fontScale).sp,
                                    lineHeight = (17 * fontScale).sp
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}
