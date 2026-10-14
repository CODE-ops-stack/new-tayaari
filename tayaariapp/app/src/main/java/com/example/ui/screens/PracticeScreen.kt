package com.example.ui.screens

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.runtime.getValue


import androidx.compose.animation.AnimatedContent
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.ExperimentalAnimationApi
import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.animation.togetherWith
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Assessment
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.BookmarkBorder
import androidx.compose.material.icons.filled.CheckCircleOutline
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.EmojiEvents
import androidx.compose.material.icons.filled.HighlightOff
import androidx.compose.material.icons.filled.SearchOff
import androidx.compose.material.icons.filled.WarningAmber
import androidx.compose.material.icons.filled.Lightbulb
import androidx.compose.material.icons.filled.CompareArrows
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.Modifier
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.DistractorDissection
import com.example.model.ExamQuestion
import com.example.model.MCQQuestion
import com.example.model.Option
import com.example.model.TestUiState

@OptIn(ExperimentalMaterial3Api::class, ExperimentalAnimationApi::class)
@Composable
fun PracticeScreen(
    topicName: String,
    tier: String,
    format: String,
    uiState: TestUiState,
    onOptionSelected: (String) -> Unit,
    onOptionCrossOut: (String) -> Unit = {},
    onSubmitAnswer: () -> Unit = {},
    onBookmarkToggle: () -> Unit,
    onPrevious: () -> Unit,
    onSkip: () -> Unit,
    onNext: () -> Unit,
    onDashboardClick: () -> Unit,
    onRestart: () -> Unit,
    onJumpToQuestion: (Int) -> Unit,
    onToggleGameMode: () -> Unit = {},
    onBack: () -> Unit
) {
    var showSummitModal by remember { mutableStateOf(false) }
    LaunchedEffect(uiState.summitReached) {
        if (uiState.summitReached) {
            showSummitModal = true
        }
    }

    if (showSummitModal) {
        com.example.ui.game.SummitTriumphDialog(
            uiState = uiState,
            onDismiss = { showSummitModal = false },
            onRestart = {
                showSummitModal = false
                onRestart()
            }
        )
    }

    // Premium color palette mapping to MaterialTheme
    val surfaceColor = MaterialTheme.colorScheme.surface
    val deepBlue = MaterialTheme.colorScheme.primary
    val accentGold = MaterialTheme.colorScheme.tertiary
    val cardColor = MaterialTheme.colorScheme.background
    val errorRed = MaterialTheme.colorScheme.error
    val successGreen = MaterialTheme.colorScheme.secondary
    val trapBackground = MaterialTheme.colorScheme.errorContainer

    com.example.ui.components.AtlasBackground {
      com.example.ui.components.TopographicBackground(lineColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.035f)) {
        Scaffold(
            containerColor = androidx.compose.ui.graphics.Color.Transparent,
            topBar = {
            Column {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(start = 4.dp, end = 20.dp, top = 16.dp, bottom = 16.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back to Topics",
                            tint = deepBlue
                        )
                    }
                    Column(modifier = Modifier.weight(1f)) {
                        val cleanTopicName = remember(topicName) {
                            topicName.substringAfter(". ")
                                .replace(Regex("^[\\p{So}\\p{Sk}\\p{Sm}\\p{Sc}\\s]+"), "")
                                .trim()
                        }
                        Text(
                            text = if (cleanTopicName.isNotEmpty()) cleanTopicName else topicName,
                            color = deepBlue,
                            fontFamily = com.example.ui.theme.CartographicSerif,
                            fontWeight = FontWeight.Bold,
                            fontSize = 20.sp,
                            maxLines = 1
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                            com.example.ui.components.ElevationTierPill(tier = tier)
                            BadgeChip(text = "🗺️ $format", color = deepBlue.copy(alpha = 0.1f), textColor = deepBlue)
                            if (uiState.currentStreak >= 2) {
                                BadgeChip(text = "🧭 ${uiState.currentStreak} COMBO", color = com.example.ui.theme.SunstoneGold, textColor = Color.Black)
                            }
                            BadgeChip(text = "📍 ${uiState.mindPowerPoints} GP", color = com.example.ui.theme.HydrosphereCyan.copy(alpha = 0.15f), textColor = com.example.ui.theme.HydrosphereCyan)
                        }
                    }
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        if (!uiState.isTestFinished && !uiState.isLoading && uiState.timeRemaining > 0) {
                            Text(
                                text = String.format("%02d:%02d", uiState.timeRemaining / 60, uiState.timeRemaining % 60),
                                color = deepBlue,
                                fontWeight = FontWeight.Bold,
                                fontSize = 16.sp
                            )
                            Spacer(modifier = Modifier.width(16.dp))
                        }
                        IconButton(onClick = onDashboardClick) {
                            Icon(Icons.Filled.Assessment, contentDescription = "Dashboard", tint = deepBlue)
                        }
                    }
                }

                // ==========================================
                // HIMALAYAN SUMMIT RUSH (VISUAL GAME ENGINE)
                // ==========================================
                if (!uiState.isTestFinished && uiState.totalQuestionsInSet > 0) {
                    com.example.ui.game.SummitRushCanvas(
                        uiState = uiState,
                        onToggleGameMode = onToggleGameMode
                    )
                }
                
                // --- Navigation Grid ---
                if (!uiState.isTestFinished && uiState.totalQuestionsInSet > 0) {
                    androidx.compose.foundation.lazy.LazyRow(
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 8.dp, vertical = 8.dp),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        items(uiState.totalQuestionsInSet) { index ->
                            val isCurrent = index == uiState.questionNumber - 1
                            val qId = uiState.allQuestions.getOrNull(index)?.id
                            val isAnswered = qId != null && uiState.userAnswers.containsKey(qId)
                            val isCorrect = if (isAnswered) {
                                val uq = uiState.allQuestions[index] as? com.example.model.MCQQuestion
                                uq?.correctAnswerId == uiState.userAnswers[qId]
                            } else false
                            
                            val bgColor = when {
                                isCurrent -> accentGold
                                isAnswered && isCorrect -> successGreen
                                isAnswered && !isCorrect -> errorRed
                                else -> deepBlue.copy(alpha = 0.1f)
                            }
                            val textColor = if (isCurrent || isAnswered) Color.White else deepBlue
                            
                            Box(
                                modifier = Modifier
                                    .size(36.dp)
                                    .clip(CircleShape)
                                    .background(bgColor)
                                    .clickable { onJumpToQuestion(index) },
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = (index + 1).toString(),
                                    color = textColor,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 14.sp
                                )
                            }
                        }
                    }
                }

            }
        },
        bottomBar = {
            // Only show bottom bar when there's an active question (not finished, not loading, not empty)
            if (!uiState.isTestFinished && !uiState.isLoading && uiState.currentQuestion != null) {
                Surface(
                    color = cardColor,
                    shadowElevation = 8.dp,
                    shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp)
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 24.dp, vertical = 16.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        if (uiState.questionNumber > 1) {
                            OutlinedButton(
                                onClick = onPrevious,
                                colors = ButtonDefaults.outlinedButtonColors(contentColor = deepBlue),
                                border = BorderStroke(1.dp, deepBlue.copy(alpha = 0.3f)),
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.weight(1f).height(50.dp)
                            ) {
                                Text("< Prev", fontWeight = FontWeight.Bold)
                            }
                            Spacer(modifier = Modifier.width(8.dp))
                        }

                        OutlinedButton(
                            onClick = onSkip,
                            enabled = uiState.selectedOptionId == null,
                            colors = ButtonDefaults.outlinedButtonColors(contentColor = deepBlue),
                            border = BorderStroke(1.dp, deepBlue.copy(alpha = 0.3f)),
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier.weight(1f).height(50.dp)
                        ) {
                            Text("Skip", fontWeight = FontWeight.Bold)
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        Button(
                            onClick = onNext,
                            enabled = uiState.selectedOptionId != null,
                            colors = ButtonDefaults.buttonColors(containerColor = deepBlue, contentColor = MaterialTheme.colorScheme.onPrimary),
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier.weight(1.5f).height(50.dp)
                        ) {
                            Text("Next", fontWeight = FontWeight.Bold, fontSize = 16.sp)
                        }
                    }
                }
            }
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when {
                // 1. Loading state
                uiState.isLoading -> {
                    Column(
                        modifier = Modifier.fillMaxSize(),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        CircularProgressIndicator(color = accentGold)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            "Fetching Next Challenge...",
                            color = deepBlue.copy(alpha = 0.7f),
                            fontWeight = FontWeight.Medium
                        )
                    }
                }

                // 2. Error state
                uiState.error != null -> {
                    Column(
                        modifier = Modifier.fillMaxSize().padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Icon(
                            Icons.Default.WarningAmber,
                            contentDescription = null,
                            tint = errorRed,
                            modifier = Modifier.size(64.dp)
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            "Something went wrong",
                            color = deepBlue,
                            fontWeight = FontWeight.Bold,
                            fontSize = 20.sp
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            uiState.error ?: "",
                            color = deepBlue.copy(alpha = 0.6f),
                            textAlign = TextAlign.Center
                        )
                        Spacer(modifier = Modifier.height(24.dp))
                        Row(
                            horizontalArrangement = Arrangement.spacedBy(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            OutlinedButton(
                                onClick = onBack,
                                colors = ButtonDefaults.outlinedButtonColors(contentColor = deepBlue),
                                border = BorderStroke(1.dp, deepBlue.copy(alpha = 0.5f))
                            ) {
                                Text("Back to Topics")
                            }
                            Button(
                                onClick = onRestart,
                                colors = ButtonDefaults.buttonColors(containerColor = accentGold)
                            ) {
                                Text("Retry Connection", color = Color.Black, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }

                // 3. No questions available (empty DB for this topic/tier/format)
                !uiState.isLoading && uiState.currentQuestion == null && !uiState.isTestFinished -> {
                    Column(
                        modifier = Modifier.fillMaxSize().padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Box(
                            modifier = Modifier
                                .size(120.dp)
                                .background(deepBlue.copy(alpha = 0.05f), CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                Icons.Default.SearchOff,
                                contentDescription = null,
                                tint = deepBlue.copy(alpha = 0.5f),
                                modifier = Modifier.size(64.dp)
                            )
                        }
                        Spacer(modifier = Modifier.height(24.dp))
                        Text(
                            "No Questions Available",
                            color = deepBlue,
                            fontWeight = FontWeight.Bold,
                            fontSize = 20.sp
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            "No questions matched your selected topic, tier, and format. Try a different combination.",
                            color = deepBlue.copy(alpha = 0.6f),
                            textAlign = TextAlign.Center,
                            fontSize = 16.sp
                        )
                        Spacer(modifier = Modifier.height(24.dp))
                        Button(
                            onClick = onBack,
                            colors = ButtonDefaults.buttonColors(containerColor = accentGold)
                        ) {
                            Text("Choose Another Topic", fontWeight = FontWeight.Bold)
                        }
                    }
                }

                // 4. Test finished state
                uiState.isTestFinished -> {
                    Column(
                        modifier = Modifier.fillMaxSize().padding(32.dp),
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        Box(
                            modifier = Modifier
                                .size(120.dp)
                                .background(accentGold.copy(alpha = 0.1f), CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Icon(
                                Icons.Default.EmojiEvents,
                                contentDescription = null,
                                tint = accentGold,
                                modifier = Modifier.size(64.dp)
                            )
                        }
                        Spacer(modifier = Modifier.height(24.dp))
                        Text(
                            "Expedition Successful!",
                            color = deepBlue,
                            fontWeight = FontWeight.ExtraBold,
                            fontSize = 24.sp
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        
                        Text(
                            "You scored ${uiState.currentScore.toDisplayString()} out of ${uiState.totalQuestionsInSet}",
                            color = deepBlue.copy(alpha = 0.7f),
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Spacer(modifier = Modifier.height(24.dp))
                        
                        if (uiState.marksLostReport.isNotEmpty()) {
                            Card(
                                modifier = Modifier.fillMaxWidth(),
                                colors = CardDefaults.cardColors(containerColor = Color.White),
                                elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
                            ) {
                                Column(modifier = Modifier.padding(16.dp)) {
                                    Text("Marks-Lost Analysis", style = MaterialTheme.typography.titleMedium, color = deepBlue)
                                    Spacer(modifier = Modifier.height(8.dp))
                                    uiState.marksLostReport.forEach { report ->
                                        Text("- $report", style = MaterialTheme.typography.bodySmall, color = Color.DarkGray)
                                        Spacer(modifier = Modifier.height(4.dp))
                                    }
                                }
                            }
                            Spacer(modifier = Modifier.height(24.dp))
                        }

                        Spacer(modifier = Modifier.height(32.dp))
                        
                        Button(
                            onClick = onRestart,
                            colors = ButtonDefaults.buttonColors(containerColor = accentGold),
                            shape = RoundedCornerShape(12.dp),
                            modifier = Modifier.fillMaxWidth().height(50.dp)
                        ) {
                            Text("Restart Topic", fontWeight = FontWeight.Bold, color = Color.White)
                        }
                        Spacer(modifier = Modifier.height(12.dp))

                        Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                            OutlinedButton(
                                onClick = onDashboardClick,
                                colors = ButtonDefaults.outlinedButtonColors(contentColor = deepBlue),
                                border = BorderStroke(1.dp, deepBlue.copy(alpha = 0.3f)),
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.weight(1f)
                            ) {
                                Text("View Traps", fontWeight = FontWeight.Bold)
                            }
                            Button(
                                onClick = onBack,
                                colors = ButtonDefaults.buttonColors(containerColor = deepBlue),
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.weight(1f)
                            ) {
                                Text("Back to Topics", fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                }

                // 5. Active question
                else -> {
                    val question = uiState.currentQuestion!!
                    AnimatedContent(
                        targetState = question,
                        transitionSpec = {
                            fadeIn(animationSpec = tween(400)).togetherWith(fadeOut(animationSpec = tween(400)))
                        },
                        label = "QuestionAnimation"
                    ) { targetQuestion ->
                        LazyColumn(
                            modifier = Modifier.fillMaxSize(),
                            contentPadding = PaddingValues(horizontal = 20.dp, vertical = 24.dp),
                            verticalArrangement = Arrangement.spacedBy(24.dp)
                        ) {
                            item {
                                PremiumQuestionCard(
                                    question = targetQuestion,
                                    isBookmarked = uiState.isBookmarked,
                                    onBookmarkClick = onBookmarkToggle,
                                    deepBlue = deepBlue,
                                    accentGold = accentGold,
                                    cardColor = cardColor
                                )
                            }

                            if (targetQuestion is MCQQuestion) {
                                item {
                                    PremiumOptionsList(
                                        options = targetQuestion.options,
                                        selectedOptionId = uiState.selectedOptionId,
                                        pendingOptionId = uiState.pendingOptionId,
                                        crossedOutOptionIds = uiState.crossedOutOptionIds,
                                        correctAnswerId = targetQuestion.correctAnswerId,
                                        correctExplanation = targetQuestion.correctExplanation,
                                        distractorDissections = targetQuestion.distractorDissections,
                                        detectedConfusionPair = uiState.detectedConfusionPair,
                                        onOptionSelected = onOptionSelected,
                                        onOptionCrossOut = onOptionCrossOut,
                                        onSubmitAnswer = onSubmitAnswer,
                                        deepBlue = deepBlue,
                                        successGreen = successGreen,
                                        errorRed = errorRed,
                                        cardColor = cardColor,
                                        trapBackground = trapBackground
                                    )
                                }

                                // Always show correct explanation after any answer is submitted
                                if (uiState.selectedOptionId != null) {
                                    val isUserCorrect = uiState.selectedOptionId == targetQuestion.correctAnswerId
                                    item {
                                        DopamineCognitiveFeedbackBanner(
                                            isCorrect = isUserCorrect,
                                            streak = uiState.currentStreak,
                                            points = if (isUserCorrect) 15 else 5
                                        )
                                    }
                                    item {
                                        CorrectExplanationCard(
                                            explanation = targetQuestion.correctExplanation,
                                            correctOption = targetQuestion.options.find { it.id == targetQuestion.correctAnswerId },
                                            deepBlue = deepBlue,
                                            successGreen = successGreen
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
      }
    }

@Composable
fun BadgeChip(text: String, color: Color, textColor: Color) {
    Box(
        modifier = Modifier
            .background(color, RoundedCornerShape(6.dp))
            .padding(horizontal = 8.dp, vertical = 4.dp)
    ) {
        Text(
            text = text,
            color = textColor,
            fontSize = 11.sp,
            fontWeight = FontWeight.Bold,
            letterSpacing = 0.5.sp
        )
    }
}

@Composable
fun CorrectExplanationCard(
    explanation: String,
    correctOption: Option?,
    deepBlue: Color,
    successGreen: Color
) {
    Surface(
        color = Color(0xFF0F172A),
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.dp, Color(0xFF10B981).copy(alpha = 0.35f)),
        modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp)
    ) {
        Column(modifier = Modifier.padding(18.dp)) {
            // Header Row
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(28.dp)
                        .clip(CircleShape)
                        .background(Color(0xFF10B981).copy(alpha = 0.15f)),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        Icons.Default.CheckCircleOutline,
                        contentDescription = null,
                        tint = Color(0xFF10B981),
                        modifier = Modifier.size(18.dp)
                    )
                }
                Spacer(modifier = Modifier.width(10.dp))
                Text(
                    text = "SURVEYOR GENERAL DISSECTION // VERIFIED ATLAS KEY",
                    color = Color(0xFF10B981),
                    fontWeight = FontWeight.Black,
                    fontSize = 11.sp,
                    letterSpacing = 1.sp
                )
            }

            if (correctOption != null) {
                Spacer(modifier = Modifier.height(10.dp))
                Surface(
                    color = Color(0xFF10B981).copy(alpha = 0.1f),
                    shape = RoundedCornerShape(8.dp),
                    border = BorderStroke(1.dp, Color(0xFF10B981).copy(alpha = 0.25f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = "📍 Verified Cartographic Key: ${correctOption.text}",
                        color = Color(0xFF34D399),
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp,
                        lineHeight = 20.sp,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Parse Takeaway / Mnemonic
            val hasTakeaway = explanation.contains("🎯 Ranker's Takeaway:") || explanation.contains("💡")
            val baseText = if (hasTakeaway) {
                explanation.substringBefore("🎯 Ranker's Takeaway:").substringBefore("💡").trim()
            } else {
                explanation.trim()
            }
            val rawTakeaway = if (hasTakeaway) {
                if (explanation.contains("🎯 Ranker's Takeaway:")) {
                    explanation.substringAfter("🎯 Ranker's Takeaway:").trim()
                } else {
                    explanation.substringAfter("💡").trim()
                }
            } else ""
            val takeawayText = rawTakeaway
                .replace(Regex("^(RANKER'S MEMORY LOCK|MEMORY LOCK)[:\\s-]*", RegexOption.IGNORE_CASE), "")
                .trim()

            // Bullet-point or structured breakdown rendering
            val lines = baseText.split("\n").filter { it.isNotBlank() }
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                lines.forEach { line ->
                    val isBullet = line.trimStart().startsWith("•") || line.trimStart().startsWith("-")
                    val cleanLine = if (isBullet) line.trimStart().removePrefix("•").removePrefix("-").trim() else line.trim()
                    
                    Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.Top) {
                        if (isBullet) {
                            Text(
                                text = "◆",
                                color = Color(0xFF00F0FF),
                                fontSize = 11.sp,
                                modifier = Modifier.padding(top = 4.dp, end = 8.dp)
                            )
                        }
                        Text(
                            text = cleanLine,
                            color = Color(0xFFE2E8F0),
                            fontSize = 14.sp,
                            lineHeight = 21.sp,
                            fontWeight = if (cleanLine.contains("CORRECT") || cleanLine.contains("INCORRECT")) FontWeight.SemiBold else FontWeight.Normal
                        )
                    }
                }
            }

            // High-Yield Ranker's Takeaway Banner
            if (takeawayText.isNotBlank()) {
                Spacer(modifier = Modifier.height(14.dp))
                Surface(
                    color = Color(0xFFF59E0B).copy(alpha = 0.12f),
                    shape = RoundedCornerShape(10.dp),
                    border = BorderStroke(1.dp, Color(0xFFF59E0B).copy(alpha = 0.35f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.Top
                    ) {
                        Text(text = "🗺️", fontSize = 16.sp, modifier = Modifier.padding(end = 8.dp))
                        Column {
                            Text(
                                text = "GEOGRAPHER'S MEMORY LOCK / ATLAS MNEMONIC",
                                color = Color(0xFFF59E0B),
                                fontWeight = FontWeight.Black,
                                fontSize = 10.sp,
                                letterSpacing = 0.8.sp
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = takeawayText,
                                color = Color(0xFFFDE68A),
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Medium,
                                lineHeight = 19.sp
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun PremiumQuestionCard(
    question: ExamQuestion,
    isBookmarked: Boolean,
    onBookmarkClick: () -> Unit,
    deepBlue: Color,
    accentGold: Color,
    cardColor: Color
) {
    Surface(
        color = cardColor,
        shape = RoundedCornerShape(16.dp),
        shadowElevation = 2.dp,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(24.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "🧭 EXPEDITION TRANSECT // FIELD QUESTION",
                    color = accentGold,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 1.2.sp
                )
                Icon(
                    imageVector = if (isBookmarked) Icons.Filled.Bookmark else Icons.Filled.BookmarkBorder,
                    contentDescription = "Bookmark",
                    tint = if (isBookmarked) accentGold else deepBlue.copy(alpha = 0.3f),
                    modifier = Modifier.clickable { onBookmarkClick() }.size(28.dp)
                )
            }
            Spacer(modifier = Modifier.height(16.dp))
            var showImageDialog by remember { mutableStateOf(false) }
            
            if (!question.imageUrl.isNullOrEmpty()) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(12.dp))
                        .clickable { showImageDialog = true }
                ) {
                    coil.compose.AsyncImage(
                        model = question.imageUrl,
                        contentDescription = "Question Image",
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(200.dp),
                        contentScale = androidx.compose.ui.layout.ContentScale.Fit
                    )
                    Surface(
                        color = Color.Black.copy(alpha = 0.65f),
                        shape = RoundedCornerShape(6.dp),
                        modifier = Modifier
                            .align(Alignment.BottomEnd)
                            .padding(8.dp)
                    ) {
                        Text(
                            text = "🔍 Tap to Inspect Topographic Map & Coordinates",
                            color = Color(0xFF00F0FF),
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                }
                Spacer(modifier = Modifier.height(16.dp))
                
                if (showImageDialog) {
                    ZoomableImageDialog(
                        imageUrl = question.imageUrl!!,
                        onDismiss = { showImageDialog = false }
                    )
                }
            }
            StructuredQuestionContent(
                questionText = question.questionText.trim(),
                textColor = deepBlue
            )
        }
    }
}

@Composable
fun DopamineCognitiveFeedbackBanner(
    isCorrect: Boolean,
    streak: Int,
    points: Int
) {
    val borderColor = if (isCorrect) Color(0xFF10B981) else Color(0xFFF59E0B)
    val bgColor = if (isCorrect) Color(0xFF10B981).copy(alpha = 0.12f) else Color(0xFFF59E0B).copy(alpha = 0.12f)
    val titleColor = if (isCorrect) Color(0xFF10B981) else Color(0xFFF59E0B)

    Surface(
        color = bgColor,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.5.dp, borderColor),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(44.dp)
                    .clip(CircleShape)
                    .background(borderColor.copy(alpha = 0.2f)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = if (isCorrect) "🧭" else "🛡️",
                    fontSize = 22.sp
                )
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = if (isCorrect) "TRUE NORTH CONFIRMED // KNOWLEDGE LOCKED" else "GEOGRAPHY TRAP NEUTRALIZED // COURSE CORRECTION",
                        color = titleColor,
                        fontWeight = FontWeight.ExtraBold,
                        fontSize = 12.sp,
                        letterSpacing = 0.8.sp
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "+$points GP",
                        color = titleColor,
                        fontWeight = FontWeight.Black,
                        fontSize = 12.sp
                    )
                }
                Spacer(modifier = Modifier.height(2.dp))
                Text(
                    text = if (isCorrect) {
                        if (streak >= 2) "🔥 $streak Waypoint Streak! Topographic memory locked."
                        else "Geographic concept firmly anchored in active memory."
                    } else {
                        "Cognitive immunity acquired. Review the cartographic trap dissection below!"
                    },
                    color = Color.White.copy(alpha = 0.85f),
                    fontSize = 12.sp,
                    lineHeight = 16.sp
                )
            }
        }
    }
}

@Composable
fun StructuredQuestionContent(
    questionText: String,
    textColor: Color
) {
    val lines = remember(questionText) {
        questionText.trim().split("\n").map { it.trim() }.filter { it.isNotEmpty() }
    }

    val isMultiStatement = remember(lines) {
        lines.any { it.matches(Regex("^[0-9]+\\..*")) || it.startsWith("Statement-I:", ignoreCase = true) || it.startsWith("Assertion (A):", ignoreCase = true) }
    }

    if (!isMultiStatement || lines.size <= 1) {
        Text(
            text = questionText.trim(),
            color = textColor,
            fontSize = 17.sp,
            fontWeight = FontWeight.SemiBold,
            lineHeight = 25.sp,
            letterSpacing = 0.2.sp
        )
    } else {
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            lines.forEach { line ->
                val isStatement = line.matches(Regex("^[0-9]+\\..*"))
                val isPrompt = line.startsWith("Which of the", ignoreCase = true) || 
                               line.startsWith("How many", ignoreCase = true) ||
                               line.startsWith("Select the correct", ignoreCase = true) ||
                               line.startsWith("Arrange the following", ignoreCase = true)
                val isAssertionReason = line.startsWith("Assertion (A):", ignoreCase = true) || 
                                        line.startsWith("Reason (R):", ignoreCase = true) ||
                                        line.startsWith("Statement-I:", ignoreCase = true) ||
                                        line.startsWith("Statement-II:", ignoreCase = true)

                when {
                    isStatement -> {
                        val num = line.substringBefore(".").trim()
                        val content = line.substringAfter(".").trim()
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(10.dp))
                                .background(Color(0xFF1E293B).copy(alpha = 0.6f))
                                .padding(horizontal = 12.dp, vertical = 8.dp),
                            verticalAlignment = Alignment.Top
                        ) {
                            Box(
                                modifier = Modifier
                                    .size(24.dp)
                                    .clip(CircleShape)
                                    .background(Color(0xFF00F0FF).copy(alpha = 0.2f)),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = num,
                                    color = Color(0xFF00F0FF),
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.ExtraBold
                                )
                            }
                            Spacer(modifier = Modifier.width(10.dp))
                            Text(
                                text = content,
                                color = textColor,
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Medium,
                                lineHeight = 22.sp,
                                modifier = Modifier.weight(1f)
                            )
                        }
                    }
                    isAssertionReason -> {
                        val label = line.substringBefore(":").trim()
                        val content = line.substringAfter(":").trim()
                        Column(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(10.dp))
                                .background(Color(0xFF1E293B).copy(alpha = 0.6f))
                                .padding(horizontal = 12.dp, vertical = 8.dp)
                        ) {
                            Text(
                                text = label.uppercase(),
                                color = Color(0xFFF59E0B),
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 0.8.sp
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = content,
                                color = textColor,
                                fontSize = 15.sp,
                                fontWeight = FontWeight.Medium,
                                lineHeight = 22.sp
                            )
                        }
                    }
                    isPrompt -> {
                        Box(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(10.dp))
                                .background(Color(0xFF00F0FF).copy(alpha = 0.1f))
                                .border(1.dp, Color(0xFF00F0FF).copy(alpha = 0.3f), RoundedCornerShape(10.dp))
                                .padding(horizontal = 12.dp, vertical = 10.dp)
                        ) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("🎯", fontSize = 14.sp)
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = line,
                                    color = Color(0xFF00F0FF),
                                    fontSize = 15.sp,
                                    fontWeight = FontWeight.Bold,
                                    lineHeight = 22.sp
                                )
                            }
                        }
                    }
                    else -> {
                        Text(
                            text = line,
                            color = textColor.copy(alpha = 0.95f),
                            fontSize = 16.sp,
                            fontWeight = FontWeight.SemiBold,
                            lineHeight = 24.sp
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun PremiumOptionsList(
    options: List<Option>,
    selectedOptionId: String?,
    pendingOptionId: String?,
    crossedOutOptionIds: Set<String>,
    correctAnswerId: String,
    correctExplanation: String,
    distractorDissections: List<DistractorDissection>,
    detectedConfusionPair: com.example.repository.ConfusionDetectionResult? = null,
    onOptionSelected: (String) -> Unit,
    onOptionCrossOut: (String) -> Unit = {},
    onSubmitAnswer: () -> Unit = {},
    deepBlue: Color,
    successGreen: Color,
    errorRed: Color,
    cardColor: Color,
    trapBackground: Color
) {
    val labels = listOf("A", "B", "C", "D", "E")

    Column(verticalArrangement = Arrangement.spacedBy(16.dp)) {
        options.forEachIndexed { index, option ->
            val isSelected = selectedOptionId == option.id
              val isPending = pendingOptionId == option.id
            val isCorrect = option.id == correctAnswerId
            val isCrossedOut = crossedOutOptionIds.contains(option.id)
            val isAnswerSubmitted = selectedOptionId != null
            val isAbstain = option.role == com.example.model.OptionRole.ABSTAIN
            val showTrapFeedback = isAnswerSubmitted && isSelected && !isCorrect && !isAbstain

            val targetBorderColor = when {
                isAnswerSubmitted && isSelected && isCorrect -> successGreen
                isAnswerSubmitted && isSelected && !isCorrect && !isAbstain -> errorRed.copy(alpha = 0.05f)
                isAnswerSubmitted && isSelected && isAbstain -> Color.Gray
                isAnswerSubmitted && isCorrect -> successGreen.copy(alpha = 0.5f)
                  isPending -> deepBlue
                else -> Color.Transparent
            }

            val targetBgColor = when {
                isAnswerSubmitted && isSelected && isCorrect -> successGreen.copy(alpha = 0.05f)
                isAnswerSubmitted && isSelected && !isCorrect && !isAbstain -> errorRed.copy(alpha = 0.05f)
                isAnswerSubmitted && isSelected && isAbstain -> Color.Gray.copy(alpha = 0.05f)
                  isPending -> deepBlue.copy(alpha = 0.1f)
                else -> cardColor
            }

            val animatedBorderColor by animateColorAsState(targetValue = targetBorderColor, label = "borderColor")
            val animatedBgColor by animateColorAsState(targetValue = targetBgColor, label = "bgColor")

            Column {
                Surface(
                    color = animatedBgColor,
                    shape = RoundedCornerShape(12.dp),
                    border = if ((isAnswerSubmitted && (isSelected || isCorrect)) || isPending) BorderStroke(2.dp, animatedBorderColor) else null,
                    shadowElevation = if (isAnswerSubmitted) 0.dp else 2.dp,
                    modifier = Modifier.alpha(if (isCrossedOut) 0.5f else 1f)
                        .fillMaxWidth()
                        .clickable(enabled = !isAnswerSubmitted && !isCrossedOut) { onOptionSelected(option.id) }
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .background(deepBlue.copy(alpha = 0.05f), CircleShape)
                                .border(1.dp, deepBlue.copy(alpha = 0.1f), CircleShape),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = labels.getOrElse(index) { "" },
                                color = deepBlue,
                                fontWeight = FontWeight.Bold,
                                fontSize = 14.sp
                            )
                        }
                        Spacer(modifier = Modifier.width(16.dp))
                        Text(
                            text = option.text,
                            textDecoration = if (isCrossedOut) androidx.compose.ui.text.style.TextDecoration.LineThrough else null,
                            modifier = Modifier.weight(1f),
                            color = deepBlue.copy(alpha = 0.9f),
                            fontSize = 16.sp,
                            lineHeight = 22.sp
                        )
                        if (!isAnswerSubmitted) {
                            IconButton(
                                onClick = { onOptionCrossOut(option.id) },
                                modifier = Modifier.size(36.dp)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Close,
                                    contentDescription = "Cross out",
                                    tint = if (isCrossedOut) errorRed else deepBlue.copy(alpha = 0.3f)
                                )
                            }
                        }
                        if (isAnswerSubmitted) {
                            Spacer(modifier = Modifier.width(8.dp))
                            if (isSelected && isCorrect) {
                                Icon(Icons.Filled.CheckCircleOutline, tint = successGreen, contentDescription = "Correct")
                            } else if (isSelected && !isCorrect && !isAbstain) {
                                Icon(Icons.Filled.HighlightOff, tint = errorRed, contentDescription = "Incorrect")
                            } else if (isSelected && isAbstain) {
                                // no icon for abstain
                            } else if (isCorrect) {
                                Icon(Icons.Filled.CheckCircleOutline, tint = successGreen.copy(alpha = 0.5f), contentDescription = "Correct answer")
                            }
                        }
                    }
                }

                // Trap Dissection — only for the incorrectly selected option
                AnimatedVisibility(visible = showTrapFeedback) {
                    val dissection = distractorDissections.find { it.optionId == option.id }
                    Spacer(modifier = Modifier.height(12.dp))
                    FeedbackBox(
                        title = "⚠️ GEOGRAPHIC TRAP: ${dissection?.trapType?.uppercase() ?: "DISTRACTOR"}",
                        message = dissection?.dissection ?: "That is not the correct answer.",
                        color = errorRed,
                        bgColor = trapBackground
                    )
                }
            }
        }

        // CONFUSION PAIR DISAMBIGUATION
        detectedConfusionPair?.let { result ->
            val pair = result.pair
            val evidenceLevel = result.evidenceLevel
            
            val (titleText, color) = when (evidenceLevel) {
                com.example.repository.ConfusionEvidenceLevel.CONFIRMED_CONFUSION -> "Recurring geographic confusion" to Color(0xFFD32F2F)
                com.example.repository.ConfusionEvidenceLevel.CONFIRMED_CONTEXT -> "Recurring geographic confusion" to Color(0xFFD32F2F)
                com.example.repository.ConfusionEvidenceLevel.EMERGING_CONFUSION -> "Geographic pattern emerging" to Color(0xFFF57C00)
                com.example.repository.ConfusionEvidenceLevel.POSSIBLE_CONFUSION -> "Possible conceptual confusion" to Color(0xFFFBC02D)
                else -> "None" to Color.Transparent
            }

            if (evidenceLevel != com.example.repository.ConfusionEvidenceLevel.NONE) {
                AnimatedVisibility(visible = true) {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(top = 16.dp)
                            .background(Color(0xFFFFF8E1), RoundedCornerShape(12.dp))
                            .border(1.dp, color, RoundedCornerShape(12.dp))
                            .padding(16.dp)
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Filled.CompareArrows, contentDescription = "Confusion Pair", tint = color)
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(titleText, fontWeight = FontWeight.Bold, color = color)
                        }
                        Spacer(modifier = Modifier.height(12.dp))
                        Text("Geographic Disambiguation: You may be conflating two adjacent concepts. Let's delineate:", fontSize = 14.sp, color = Color.DarkGray)
                        Spacer(modifier = Modifier.height(16.dp))
                        
                        Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(pair.displayNameA, fontWeight = FontWeight.Bold, color = deepBlue)
                                Text(pair.descriptionA, fontSize = 13.sp, color = Color.Gray)
                            }
                            Spacer(modifier = Modifier.width(16.dp))
                            Column(modifier = Modifier.weight(1f)) {
                                Text(pair.displayNameB, fontWeight = FontWeight.Bold, color = deepBlue)
                                Text(pair.descriptionB, fontSize = 13.sp, color = Color.Gray)
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun FeedbackBox(title: String, message: String, color: Color, bgColor: Color) {
    Surface(
        color = bgColor,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, color.copy(alpha = 0.3f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.Top
        ) {
            Icon(
                Icons.Default.Lightbulb,
                contentDescription = null,
                tint = color,
                modifier = Modifier.size(20.dp).padding(top = 2.dp)
            )
            Spacer(modifier = Modifier.width(12.dp))
            Column {
                Text(
                    text = title,
                    color = color,
                    fontWeight = FontWeight.Black,
                    fontSize = 12.sp,
                    letterSpacing = 1.sp
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = message,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f),
                    fontSize = 14.sp,
                    lineHeight = 20.sp
                )
            }
        }
    }
}





@Composable
fun ZoomableImageDialog(imageUrl: String, onDismiss: () -> Unit) {
    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(usePlatformDefaultWidth = false)
    ) {
        var scale by remember { mutableFloatStateOf(1f) }
        var offsetX by remember { mutableFloatStateOf(0f) }
        var offsetY by remember { mutableFloatStateOf(0f) }

        Surface(
            modifier = Modifier.fillMaxSize(),
            color = Color.Black.copy(alpha = 0.9f)
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .pointerInput(Unit) {
                        detectTransformGestures { _, pan, zoom, _ ->
                            scale = (scale * zoom).coerceIn(1f, 5f)
                            if (scale > 1f) {
                                offsetX += pan.x
                                offsetY += pan.y
                            } else {
                                offsetX = 0f
                                offsetY = 0f
                            }
                        }
                    }
            ) {
                coil.compose.AsyncImage(
                    model = imageUrl,
                    contentDescription = "Zoomed Image",
                    modifier = Modifier
                        .fillMaxSize()
                        .graphicsLayer(
                            scaleX = scale,
                            scaleY = scale,
                            translationX = offsetX,
                            translationY = offsetY
                        ),
                    contentScale = androidx.compose.ui.layout.ContentScale.Fit
                )
                
                IconButton(
                    onClick = onDismiss,
                    modifier = Modifier
                        .align(Alignment.TopEnd)
                        .padding(16.dp)
                ) {
                    Icon(
                        Icons.Default.Close,
                        contentDescription = "Close",
                        tint = Color.White
                    )
                }
            }
        }
    }
}
