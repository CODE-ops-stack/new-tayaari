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
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.rememberScrollState
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import kotlin.math.cos
import kotlin.math.sin
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
import androidx.compose.material.icons.filled.Explore
import androidx.compose.material.icons.filled.Tune
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material.icons.filled.VolumeOff
import androidx.compose.material.icons.automirrored.filled.CompareArrows
import androidx.compose.material3.*
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
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
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
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
    profile: com.example.model.ExamBlueprint? = null,
    uiState: TestUiState,
    themeMode: com.example.repository.AppThemeMode = com.example.repository.AppThemeMode.DARK,
    onThemeModeChange: (com.example.repository.AppThemeMode) -> Unit = {},
    fontScaleOption: com.example.repository.FontScaleOption = com.example.repository.FontScaleOption.NORMAL,
    onFontScaleOptionChange: (com.example.repository.FontScaleOption) -> Unit = {},
    isZenMode: Boolean = false,
    onZenModeChange: (Boolean) -> Unit = {},
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
    var dismissedChillForQuestion by remember { mutableIntStateOf(-1) }
    var showAtlasDialog by remember { mutableStateOf(false) }
    var showSettingsDialog by remember { mutableStateOf(false) }

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

    if (showAtlasDialog) {
        com.example.ui.components.CartographicAtlasSheetDialog(
            onDismissRequest = { showAtlasDialog = false }
        )
    }

    if (showSettingsDialog) {
        com.example.ui.components.AspirantSettingsDialog(
            themeMode = themeMode,
            onThemeModeChange = onThemeModeChange,
            fontScaleOption = fontScaleOption,
            onFontScaleOptionChange = onFontScaleOptionChange,
            isZenMode = isZenMode,
            onZenModeChange = onZenModeChange,
            showQuotaSection = false,
            onDismiss = { showSettingsDialog = false }
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
            Column(modifier = Modifier.statusBarsPadding()) {
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
                            if (profile != null) {
                                val shortExamName = profile.displayName.substringBefore(" (").trim()
                                BadgeChip(text = "🏛️ $shortExamName", color = com.example.ui.theme.SunstoneGold.copy(alpha = 0.2f), textColor = com.example.ui.theme.SunstoneGold)
                            }
                            com.example.ui.components.ElevationTierPill(tier = tier)
                            BadgeChip(text = "🗺️ $format", color = deepBlue.copy(alpha = 0.1f), textColor = deepBlue)
                            val isZen = LocalZenMode.current
                            if (uiState.currentStreak >= 2 && !isZen) {
                                BadgeChip(text = "🧭 ${uiState.currentStreak} COMBO", color = com.example.ui.theme.SunstoneGold, textColor = Color.Black)
                            }
                            BadgeChip(text = "📍 ${uiState.mindPowerPoints} GP", color = com.example.ui.theme.HydrosphereCyan.copy(alpha = 0.15f), textColor = com.example.ui.theme.HydrosphereCyan)
                        }
                    }
                    val isZen = LocalZenMode.current
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        if (!uiState.isTestFinished && !uiState.isLoading) {
                            if (isZen) {
                                Surface(
                                    color = Color(0xFF10B981).copy(alpha = 0.15f),
                                    shape = RoundedCornerShape(12.dp)
                                ) {
                                    Text(
                                        text = "🧘 Zen Focus",
                                        color = Color(0xFF10B981),
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 12.sp,
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                    )
                                }
                                Spacer(modifier = Modifier.width(12.dp))
                            } else if (uiState.timeRemaining > 0) {
                                Text(
                                    text = String.format("%02d:%02d", uiState.timeRemaining / 60, uiState.timeRemaining % 60),
                                    color = deepBlue,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 16.sp
                                )
                                Spacer(modifier = Modifier.width(16.dp))
                            }
                        }
                        IconButton(onClick = { showAtlasDialog = true }) {
                            Icon(Icons.Filled.Explore, contentDescription = "Cartographic Atlas", tint = deepBlue)
                        }
                        IconButton(onClick = { showSettingsDialog = true }) {
                            Icon(Icons.Filled.Tune, contentDescription = "Ergonomics & Themes", tint = deepBlue)
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
                    shape = RoundedCornerShape(topStart = 24.dp, topEnd = 24.dp),
                    modifier = Modifier.navigationBarsPadding()
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
                        
                        val maxMarks = (profile?.positiveMarks?.toDouble() ?: 1.0) * uiState.totalQuestionsInSet
                        val maxMarksFormatted = if (maxMarks % 1.0 == 0.0) maxMarks.toInt().toString() else String.format("%.1f", maxMarks)
                        Text(
                            "Score: ${uiState.currentScore.toDisplayString()} / $maxMarksFormatted Marks (${uiState.totalCorrectCount}/${uiState.totalQuestionsInSet} Correct)",
                            color = deepBlue,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        val penaltyRule = profile?.negativePenaltyRule
                        val penaltyText = if (penaltyRule != null && penaltyRule != com.example.model.PenaltyRule.NONE) {
                            "Official Negative Marking: -${penaltyRule.numerator}/${penaltyRule.denominator} marks per wrong attempt"
                        } else {
                            "Official Commission Scoring Scheme Applied"
                        }
                        Text(
                            penaltyText,
                            color = com.example.ui.theme.TopoContourMuted,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Medium
                        )
                        Spacer(modifier = Modifier.height(20.dp))
                        
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
                            val effectiveExam = profile?.examId ?: targetQuestion.chapterCode
                            item {
                                GeodeticSurveyHudStrip(
                                    questionNumber = uiState.questionNumber,
                                    totalQuestions = uiState.totalQuestionsInSet,
                                    tier = tier,
                                    altitudeMeters = uiState.currentAltitudeMeters
                                )
                            }
                            item {
                                ExamGloryHeader(examTarget = effectiveExam, tier = tier)
                            }

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
                                            points = if (isUserCorrect) 15 else 5,
                                            examTarget = effectiveExam
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
                                    if (uiState.questionNumber > 0 && uiState.questionNumber % 5 == 0 && dismissedChillForQuestion != uiState.questionNumber) {
                                        item {
                                            BrainChillCard(onDismiss = { dismissedChillForQuestion = uiState.questionNumber })
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

            // High-Yield Ranker's Takeaway Banner (Interactive Tap-to-Unlock)
            if (takeawayText.isNotBlank()) {
                Spacer(modifier = Modifier.height(14.dp))
                InteractiveMnemonicCard(takeawayText = takeawayText)
            }

            // Interactive Geographic Science Sandbox
            InteractiveGeographicModelSandbox(explanation = explanation)
        }
    }
}

@Composable
fun InteractiveMnemonicCard(takeawayText: String) {
    var isRevealed by remember { mutableStateOf(false) }

    Surface(
        color = if (isRevealed) Color(0xFFF59E0B).copy(alpha = 0.12f) else DeepBasalt,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.2.dp, if (isRevealed) SunstoneGold.copy(alpha = 0.6f) else SunstoneGold.copy(alpha = 0.3f)),
        modifier = Modifier
            .fillMaxWidth()
            .clickable { isRevealed = !isRevealed }
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = if (isRevealed) "🔓" else "🔒", fontSize = 16.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = if (isRevealed) "ACTIVE RECALL UNLOCKED // TOPPER MNEMONIC" else "TAP TO UNLOCK // ACTIVE RECALL DRILL",
                        color = SunstoneGold,
                        fontWeight = FontWeight.Black,
                        fontSize = 10.5.sp,
                        letterSpacing = 0.8.sp
                    )
                }
                Surface(
                    color = SunstoneGold.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(4.dp)
                ) {
                    Text(
                        text = if (isRevealed) "REVEALED" else "TAP TO REVEAL 👁️",
                        color = SunstoneGold,
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.height(6.dp))
            if (isRevealed) {
                Text(
                    text = takeawayText,
                    color = Color(0xFFFDE68A),
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Medium,
                    lineHeight = 19.sp
                )
            } else {
                Text(
                    text = "Test your memory first! Can you recall the key exam formula before tapping?",
                    color = TopoContourMuted,
                    fontSize = 11.sp,
                    fontStyle = FontStyle.Italic
                )
            }
        }
    }
}

@Composable
fun InteractiveGeographicModelSandbox(explanation: String) {
    val lower = explanation.lowercase()
    val isTectonics = lower.contains("tectonic") || lower.contains("plate") || lower.contains("fault") || lower.contains("subduction") || lower.contains("divergent")
    val isAtmosphere = lower.contains("troposphere") || lower.contains("stratosphere") || lower.contains("atmosphere") || lower.contains("ozone") || lower.contains("lapse rate")
    val isRiver = lower.contains("river") || lower.contains("meander") || lower.contains("delta") || lower.contains("drainage") || lower.contains("oxbow")
    val isCurrents = lower.contains("current") || lower.contains("ocean") || lower.contains("gyre") || lower.contains("gulf stream") || lower.contains("upwelling") || lower.contains("benguela") || lower.contains("humboldt") || lower.contains("kuroshio")
    val isMonsoon = lower.contains("monsoon") || lower.contains("enso") || lower.contains("el niño") || lower.contains("la niña") || lower.contains("iod") || lower.contains("walker") || lower.contains("western disturbance") || lower.contains("itcz")
    val isKoppen = lower.contains("koppen") || lower.contains("köppen") || lower.contains("amw") || lower.contains("bshw") || lower.contains("bwhw") || lower.contains("cwa") || lower.contains("cwg") || lower.contains("dfc") || lower.contains("savanna") || lower.contains("tundra") || lower.contains("climatic classification") || lower.contains("climatic zone")

    if (isTectonics) {
        TectonicBoundarySandbox()
    } else if (isAtmosphere) {
        AtmosphericProfileSandbox()
    } else if (isRiver) {
        RiverCourseSandbox()
    } else if (isCurrents) {
        OceanCurrentsSandbox()
    } else if (isMonsoon) {
        MonsoonTeleconnectionSandbox()
    } else if (isKoppen) {
        KoppenClimateDialSandbox()
    }
}

@Composable
fun OceanCurrentsSandbox() {
    var selectedOcean by remember { mutableIntStateOf(0) }
    val oceans = listOf("Atlantic Gyre", "Pacific Gyre", "Indian Ocean", "Desert Link")
    val warmCurrents = listOf(
        "Gulf Stream, North Atlantic Drift, Brazil Current, Florida Current",
        "Kuroshio (Japan Current), East Australian Current, North Equatorial",
        "Agulhas Current, Mozambique Current, South Equatorial Current",
        "Warm currents carry high moisture & heat -> heavy precipitation on Eastern margins of continents"
    )
    val coldCurrents = listOf(
        "Canary Current, Labrador Current, Benguela Current, Falkland Current",
        "California Current, Oyashio (Kuril) Current, Peru (Humboldt) Current",
        "West Australian Current, Somali Current (Upwelling phase in summer)",
        "Cold currents cause atmospheric stability (inversion) & low humidity -> form Atacama, Namib & Kalahari Deserts!"
    )
    val signaturePhenomena = listOf(
        "Grand Banks Fog & Fishery: Where warm Gulf Stream collides with freezing Labrador Current, plankton blooms create world-class fishing grounds.",
        "El Niño Teleconnection: Humboldt Current weakening triggers anomalous warm pool in Eastern Pacific, disrupting global atmospheric Walker Circulation.",
        "Reversal of Currents: North Indian Ocean currents reverse direction completely between SW Monsoon (clockwise) and NE Monsoon (counter-clockwise).",
        "West Coast Deserts Mystery: Cold offshore currents chill surface air, suppressing convection. Paired with offshore Trade Winds, rainfall is near zero (Atacama < 1mm/yr)."
    )

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, HydrosphereCyan.copy(alpha = 0.45f)),
        modifier = Modifier.fillMaxWidth().padding(top = 10.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "🌊", fontSize = 15.sp)
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "INTERACTIVE OCEANIC GYRE & CURRENTS MODEL",
                        color = HydrosphereCyan,
                        fontSize = 10.5.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.6.sp
                    )
                }
                Text(
                    text = "Tap Ocean ➔",
                    color = TopoContourMuted,
                    fontSize = 9.sp
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                oceans.forEachIndexed { idx, name ->
                    val isTabSelected = selectedOcean == idx
                    Surface(
                        color = if (isTabSelected) HydrosphereCyan else OceanicDark,
                        shape = RoundedCornerShape(6.dp),
                        border = BorderStroke(0.8.dp, HydrosphereCyan.copy(alpha = 0.4f)),
                        modifier = Modifier
                            .weight(1f)
                            .clickable { selectedOcean = idx }
                    ) {
                        Text(
                            text = name.replace(" Gyre", "").replace(" Ocean", ""),
                            color = if (isTabSelected) Color.Black else AtlasParchment,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.padding(vertical = 5.dp)
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            // Interactive Circulation Schematic Canvas
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(95.dp)
                    .background(OceanicDark, RoundedCornerShape(8.dp))
                    .border(0.8.dp, HydrosphereCyan.copy(alpha = 0.25f), RoundedCornerShape(8.dp))
            ) {
                Canvas(modifier = Modifier.fillMaxSize().padding(8.dp)) {
                    val w = size.width
                    val h = size.height
                    val cx = w / 2f
                    val cy = h / 2f

                    // Draw Equatorial line
                    drawLine(
                        color = Color.White.copy(alpha = 0.2f),
                        start = Offset(0f, cy),
                        end = Offset(w, cy),
                        strokeWidth = 1f
                    )

                    // Draw Northern Gyre (Clockwise in NH)
                    drawArc(
                        color = Color(0xFFEF4444).copy(alpha = 0.75f),
                        startAngle = 180f,
                        sweepAngle = 90f,
                        useCenter = false,
                        topLeft = Offset(cx - 70.dp.toPx(), cy - 35.dp.toPx()),
                        size = androidx.compose.ui.geometry.Size(140.dp.toPx(), 32.dp.toPx()),
                        style = androidx.compose.ui.graphics.drawscope.Stroke(width = 3.dp.toPx())
                    )
                    drawArc(
                        color = Color(0xFF00F0FF).copy(alpha = 0.75f),
                        startAngle = 270f,
                        sweepAngle = 90f,
                        useCenter = false,
                        topLeft = Offset(cx - 70.dp.toPx(), cy - 35.dp.toPx()),
                        size = androidx.compose.ui.geometry.Size(140.dp.toPx(), 32.dp.toPx()),
                        style = androidx.compose.ui.graphics.drawscope.Stroke(width = 3.dp.toPx())
                    )

                    // Draw Southern Gyre (Counter-Clockwise in SH)
                    drawArc(
                        color = Color(0xFF00F0FF).copy(alpha = 0.75f),
                        startAngle = 0f,
                        sweepAngle = 90f,
                        useCenter = false,
                        topLeft = Offset(cx - 70.dp.toPx(), cy + 3.dp.toPx()),
                        size = androidx.compose.ui.geometry.Size(140.dp.toPx(), 32.dp.toPx()),
                        style = androidx.compose.ui.graphics.drawscope.Stroke(width = 3.dp.toPx())
                    )
                    drawArc(
                        color = Color(0xFFEF4444).copy(alpha = 0.75f),
                        startAngle = 90f,
                        sweepAngle = 90f,
                        useCenter = false,
                        topLeft = Offset(cx - 70.dp.toPx(), cy + 3.dp.toPx()),
                        size = androidx.compose.ui.geometry.Size(140.dp.toPx(), 32.dp.toPx()),
                        style = androidx.compose.ui.graphics.drawscope.Stroke(width = 3.dp.toPx())
                    )
                }
                Row(
                    modifier = Modifier.fillMaxSize().padding(horizontal = 12.dp, vertical = 6.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("WESTERN MARGIN", fontSize = 9.sp, color = Color(0xFFEF4444), fontWeight = FontWeight.Black)
                        Text("🔥 WARM DRIFT", fontSize = 8.sp, color = Color(0xFFFCA5A5))
                        Text("High Rainfall", fontSize = 8.sp, color = AtlasParchment.copy(alpha = 0.7f))
                    }
                    Column(horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("EQUATOR (0°)", fontSize = 8.5.sp, color = Color.White.copy(alpha = 0.7f), fontWeight = FontWeight.Bold)
                        Text("NH: Clockwise ↻\nSH: Counter-Clockwise ↺", fontSize = 7.5.sp, color = SunstoneGold, textAlign = TextAlign.Center)
                    }
                    Column(horizontalAlignment = Alignment.End) {
                        Text("EASTERN MARGIN", fontSize = 9.sp, color = Color(0xFF00F0FF), fontWeight = FontWeight.Black)
                        Text("❄️ COLD UPWELLING", fontSize = 8.sp, color = Color(0xFF67E8F9))
                        Text("Desiccation & Aridity", fontSize = 8.sp, color = AtlasParchment.copy(alpha = 0.7f))
                    }
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            Surface(
                color = OceanicDark,
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(10.dp)) {
                    Text(
                        text = "🔥 Warm: ${warmCurrents[selectedOcean]}",
                        color = Color(0xFFFCA5A5),
                        fontSize = 10.5.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "❄️ Cold: ${coldCurrents[selectedOcean]}",
                        color = Color(0xFF67E8F9),
                        fontSize = 10.5.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "💡 Concept: ${signaturePhenomena[selectedOcean]}",
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
fun MonsoonTeleconnectionSandbox() {
    var selectedPhase by remember { mutableIntStateOf(0) }
    val phases = listOf("Normal Walker", "El Niño (Drought)", "La Niña (Bountiful)", "Positive IOD")
    val walkerStates = listOf(
        "Strong Trade Winds push warm water to Western Pacific (Indo-Pacific Warm Pool). Upwelling along Peru coast.",
        "Trade winds weaken or reverse. Warm pool shifts eastward to Central/East Pacific. Convection relocates away from India.",
        "Intense Trade Winds reinforce cold tongue in East Pacific. Extreme warm pool over Indonesia/Bay of Bengal with hyper-active convection.",
        "Western Indian Ocean becomes anomalously warmer than Eastern Indian Ocean. Creates robust low pressure fueling Indian Monsoon."
    )
    val monsoonImpacts = listOf(
        "🟢 Normal Monsoon: Balanced Tibetan anticyclone and Mascarene High drive 100% of Long Period Average (LPA) precipitation.",
        "🔴 Drought Threat: Sinking air over India suppresses cloud formation. ~60% of historic Indian droughts coincide with El Niño years.",
        "🌊 Bountiful Surplus: Abundant convective rainfall across Indian plains, enhanced flood frequency in Brahmaputra & Gangetic basins.",
        "⭐ Monsoon Booster: Acts as an atmospheric shield; can completely offset an El Niño's negative impact on Indian agriculture!"
    )
    val sstLabels = listOf(
        "West Pacific: 29°C Warm Pool  |  East Pacific: 22°C Cold Tongue",
        "West Pacific: 25°C Cooler   |  East Pacific: 29°C Anomalous Warm Pool",
        "West Pacific: 31°C Super Warm |  East Pacific: 19°C Deep Upwelling",
        "Arabian Sea: +1.5°C Positive Anomaly | Sumatra: -1.0°C Negative Anomaly"
    )

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, SunstoneGold.copy(alpha = 0.45f)),
        modifier = Modifier.fillMaxWidth().padding(top = 10.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "🌪️", fontSize = 15.sp)
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "MONSOON & TELECONNECTIONS ENGINE // ENSO / IOD",
                        color = SunstoneGold,
                        fontSize = 10.5.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.6.sp
                    )
                }
                Text(
                    text = "Tap Phase ➔",
                    color = TopoContourMuted,
                    fontSize = 9.sp
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                phases.forEachIndexed { idx, name ->
                    val isTabSelected = selectedPhase == idx
                    Surface(
                        color = if (isTabSelected) SunstoneGold else OceanicDark,
                        shape = RoundedCornerShape(6.dp),
                        border = BorderStroke(0.8.dp, SunstoneGold.copy(alpha = 0.4f)),
                        modifier = Modifier
                            .weight(1f)
                            .clickable { selectedPhase = idx }
                    ) {
                        Text(
                            text = name.split(" ")[0],
                            color = if (isTabSelected) Color.Black else AtlasParchment,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.padding(vertical = 5.dp)
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            // Interactive Teleconnection Diagram Canvas
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(95.dp)
                    .background(OceanicDark, RoundedCornerShape(8.dp))
                    .border(0.8.dp, SunstoneGold.copy(alpha = 0.25f), RoundedCornerShape(8.dp))
            ) {
                Canvas(modifier = Modifier.fillMaxSize().padding(8.dp)) {
                    val w = size.width
                    val h = size.height

                    // Sea level base line
                    drawLine(
                        color = Color(0xFF0284C7).copy(alpha = 0.4f),
                        start = Offset(0f, h * 0.75f),
                        end = Offset(w, h * 0.75f),
                        strokeWidth = 2.dp.toPx()
                    )

                    val isElNino = selectedPhase == 1
                    val isPositiveIod = selectedPhase == 3

                    val warmX = when {
                        isElNino -> w * 0.75f
                        isPositiveIod -> w * 0.25f
                        else -> w * 0.25f
                    }
                    val coldX = when {
                        isElNino -> w * 0.25f
                        else -> w * 0.75f
                    }

                    // Rising air plume at warm pool
                    drawLine(
                        color = Color(0xFFEF4444).copy(alpha = 0.8f),
                        start = Offset(warmX, h * 0.75f),
                        end = Offset(warmX, h * 0.25f),
                        strokeWidth = 3.dp.toPx()
                    )
                    drawCircle(
                        color = Color(0xFFEF4444).copy(alpha = 0.9f),
                        radius = 4.dp.toPx(),
                        center = Offset(warmX, h * 0.25f)
                    )

                    // Sinking air plume at cold pool
                    drawLine(
                        color = Color(0xFF38BDF8).copy(alpha = 0.8f),
                        start = Offset(coldX, h * 0.25f),
                        end = Offset(coldX, h * 0.75f),
                        strokeWidth = 3.dp.toPx()
                    )
                    drawCircle(
                        color = Color(0xFF38BDF8).copy(alpha = 0.9f),
                        radius = 4.dp.toPx(),
                        center = Offset(coldX, h * 0.75f)
                    )

                    // Upper tropospheric connecting wind
                    drawLine(
                        color = Color.White.copy(alpha = 0.35f),
                        start = Offset(warmX, h * 0.25f),
                        end = Offset(coldX, h * 0.25f),
                        strokeWidth = 1.5.dp.toPx()
                    )
                }

                Row(
                    modifier = Modifier.fillMaxSize().padding(horizontal = 12.dp, vertical = 6.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text("WEST (INDIA / ASIA)", fontSize = 8.5.sp, color = SunstoneGold, fontWeight = FontWeight.Bold)
                        Text(if (selectedPhase == 1) "Sinking Air ⬇️ (Suppressed)" else "Rising Air ⬆️ (Convective)", fontSize = 8.sp, color = AtlasParchment)
                    }
                    Column(horizontalAlignment = Alignment.End) {
                        Text("EAST (PACIFIC / AMERICAS)", fontSize = 8.5.sp, color = HydrosphereCyan, fontWeight = FontWeight.Bold)
                        Text(if (selectedPhase == 1) "Rising Air ⬆️ (Warm Pool)" else "Sinking Air ⬇️ (Cold Tongue)", fontSize = 8.sp, color = AtlasParchment)
                    }
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            Surface(
                color = OceanicDark,
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(10.dp)) {
                    Text(
                        text = "🌡️ SST Thermal State: ${sstLabels[selectedPhase]}",
                        color = SunstoneGold,
                        fontSize = 10.5.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "💨 Dynamics: ${walkerStates[selectedPhase]}",
                        color = AtlasParchment,
                        fontSize = 11.sp,
                        lineHeight = 15.sp
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "🇮🇳 Indian Monsoon: ${monsoonImpacts[selectedPhase]}",
                        color = if (selectedPhase == 1) Color(0xFFF87171) else Color(0xFF4ADE80),
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Bold,
                        lineHeight = 15.sp
                    )
                }
            }
        }
    }
}

@Composable
fun KoppenClimateDialSandbox() {
    var selectedRealm by remember { mutableIntStateOf(0) }
    val realms = listOf("Amw (Monsoon)", "BWh (Desert)", "Cs (Mediter.)", "Cwg (Gangetic)", "ET (Tundra)")
    val titles = listOf(
        "Amw: Tropical Monsoon (Windward Western Ghats & Northeast)",
        "BWhw: Hot Low-Latitude Desert (Thar Desert & Marusthali)",
        "Cs: Dry Summer Mediterranean (Winter Rain Westerlies)",
        "Cwg: Humid Subtropical with Dry Winter (Gangetic Plains)",
        "ET: Polar Tundra & Alpine Cold Desert (Trans-Himalaya & Ladakh)"
    )
    val thermalRegimes = listOf(
        "Mean monthly temperature > 18°C year-round. No winter season.",
        "Extreme diurnal temperature range (45°C day / 5°C night). P < 25 cm/yr.",
        "Warm dry summer (> 22°C), mild wet winter. Westerlies bring winter rain.",
        "Summer high > 40°C ('Loo' winds); cold dry winter with Western Disturbances.",
        "Warmest month between 0°C and 10°C. Continuous sub-zero winter freeze."
    )
    val pedologyFlora = listOf(
        "Vegetation: Tropical Wet Evergreen & Semi-Evergreen • Soils: Heavily leached Laterite & Red soils.",
        "Vegetation: Xerophytic thorny shrubs, Acacias, Cacti • Soils: Arid sandy soil with high soluble salts.",
        "Vegetation: Sclerophyllous scrub (Chaparral/Maquis), Cork oak, Olive • Soils: Terra Rossa / Brown earths.",
        "Vegetation: Tropical Moist & Dry Deciduous (Sal, Teak) • Soils: Fertile Khadar & Bhangar Alluvium.",
        "Vegetation: Mosses, lichens, alpine meadows (Bugyals) • Soils: Skeletal mountain soils with permafrost."
    )
    val prelimsTraps = listOf(
        "UPSC Trap: Examiner confuses 'Amw' with 'As' (Coromandel coast with dry summer & retreat monsoon rain)!",
        "UPSC Trap: Examiner claims deserts form due to distance from sea; reality: Subtropical High Pressure + Cold Offshore Currents!",
        "UPSC Trap: Mediterranean Cs has DRY summers, NOT wet summers—rainfall is strictly cyclonic winter Westerlies!",
        "UPSC Trap: Northern plains are 'Cwg', NOT 'Aw'. The 'w' denotes dry winter, 'g' denotes Gangetic temperature curve!",
        "UPSC Trap: Ladakh cold desert has low rainfall due to rain-shadow barrier of Greater Himalayas, NOT cold alone!"
    )

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, SunstoneGold.copy(alpha = 0.45f)),
        modifier = Modifier.fillMaxWidth().padding(top = 10.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "🌐", fontSize = 15.sp)
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "KÖPPEN CLIMATIC REALM DIAL // SCHEMATIC CANVAS",
                        color = SunstoneGold,
                        fontSize = 10.5.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.6.sp
                    )
                }
                Text(
                    text = "Tap Realm ➔",
                    color = TopoContourMuted,
                    fontSize = 9.sp
                )
            }

            Spacer(modifier = Modifier.height(10.dp))

            // 5-Realm Tabs
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                realms.forEachIndexed { idx, name ->
                    val isSelected = selectedRealm == idx
                    Surface(
                        color = if (isSelected) SunstoneGold else OceanicDark,
                        shape = RoundedCornerShape(6.dp),
                        border = BorderStroke(0.8.dp, SunstoneGold.copy(alpha = 0.4f)),
                        modifier = Modifier.clickable { selectedRealm = idx }
                    ) {
                        Text(
                            text = name,
                            color = if (isSelected) Color.Black else AtlasParchment,
                            fontSize = 10.5.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            // Climograph Canvas: Monthly Temperature Curve & Precipitation Bars
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(110.dp)
                    .background(OceanicDark, RoundedCornerShape(8.dp))
                    .border(0.8.dp, SlateBedrock, RoundedCornerShape(8.dp))
                    .padding(8.dp)
            ) {
                Canvas(modifier = Modifier.fillMaxSize()) {
                    val w = size.width
                    val h = size.height

                    // Grid baselines
                    drawLine(color = SlateBedrock.copy(alpha = 0.6f), start = Offset(0f, h * 0.5f), end = Offset(w, h * 0.5f), strokeWidth = 0.8f)
                    drawLine(color = SlateBedrock.copy(alpha = 0.6f), start = Offset(0f, h * 0.85f), end = Offset(w, h * 0.85f), strokeWidth = 0.8f)

                    // 12 Monthly Precipitation Bars (Jan to Dec)
                    val barWidth = (w / 12f) * 0.6f
                    val rainfallProfiles = listOf(
                        listOf(5f, 5f, 10f, 25f, 80f, 280f, 320f, 240f, 150f, 60f, 20f, 8f),
                        listOf(3f, 4f, 2f, 1f, 1f, 5f, 12f, 15f, 6f, 2f, 1f, 2f),
                        listOf(90f, 75f, 60f, 35f, 15f, 4f, 1f, 3f, 20f, 65f, 95f, 110f),
                        listOf(15f, 12f, 8f, 6f, 18f, 110f, 260f, 230f, 120f, 20f, 5f, 8f),
                        listOf(8f, 10f, 12f, 15f, 18f, 22f, 25f, 20f, 15f, 10f, 8f, 8f)
                    )
                    val currentRain = rainfallProfiles[selectedRealm]
                    val maxRain = currentRain.maxOrNull()?.coerceAtLeast(1f) ?: 1f

                    for (m in 0 until 12) {
                        val barHeight = (currentRain[m] / maxRain) * (h * 0.75f)
                        val x = (m + 0.5f) * (w / 12f) - (barWidth / 2f)
                        val y = h - barHeight
                        drawRect(
                            color = HydrosphereCyan.copy(alpha = 0.75f),
                            topLeft = Offset(x, y),
                            size = Size(barWidth, barHeight)
                        )
                    }

                    // Temperature curve
                    val tempProfiles = listOf(
                        listOf(0.7f, 0.72f, 0.78f, 0.85f, 0.82f, 0.75f, 0.72f, 0.72f, 0.74f, 0.75f, 0.73f, 0.7f),
                        listOf(0.35f, 0.45f, 0.65f, 0.85f, 0.95f, 0.92f, 0.88f, 0.85f, 0.8f, 0.68f, 0.48f, 0.38f),
                        listOf(0.4f, 0.45f, 0.52f, 0.6f, 0.72f, 0.82f, 0.9f, 0.88f, 0.78f, 0.65f, 0.52f, 0.42f),
                        listOf(0.35f, 0.42f, 0.6f, 0.82f, 0.94f, 0.9f, 0.82f, 0.8f, 0.78f, 0.68f, 0.5f, 0.38f),
                        listOf(0.1f, 0.12f, 0.18f, 0.25f, 0.35f, 0.48f, 0.52f, 0.5f, 0.4f, 0.25f, 0.15f, 0.1f)
                    )
                    val currentTemp = tempProfiles[selectedRealm]
                    val tempPath = Path()
                    for (m in 0 until 12) {
                        val px = (m + 0.5f) * (w / 12f)
                        val py = h * (1f - currentTemp[m] * 0.85f)
                        if (m == 0) tempPath.moveTo(px, py) else tempPath.lineTo(px, py)
                    }
                    drawPath(
                        path = tempPath,
                        color = SunstoneGold,
                        style = Stroke(width = 2.5f)
                    )
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            Surface(
                color = OceanicDark,
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(10.dp)) {
                    Text(
                        text = titles[selectedRealm],
                        color = SunstoneGold,
                        fontSize = 11.5.sp,
                        fontWeight = FontWeight.Black
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "• Thermal Regime: ${thermalRegimes[selectedRealm]}",
                        color = AtlasParchment,
                        fontSize = 11.sp,
                        lineHeight = 15.sp
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "• Flora & Pedology: ${pedologyFlora[selectedRealm]}",
                        color = ContourEmerald,
                        fontSize = 11.sp,
                        lineHeight = 15.sp
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = prelimsTraps[selectedRealm],
                        color = HydrosphereCyan,
                        fontSize = 10.5.sp,
                        fontWeight = FontWeight.SemiBold,
                        lineHeight = 14.sp
                    )
                }
            }
        }
    }
}

@Composable
fun TectonicBoundarySandbox() {
    var selectedBoundary by remember { mutableIntStateOf(0) }
    val titles = listOf("CONVERGENT (COLLISION)", "DIVERGENT (SPREADING)", "TRANSFORM (SHEAR)")
    val arrows = listOf("➡️  COLLISION  ⬅️", "⬅️  UPWELLING  ➡️", "⬆️  LATERAL SLIP  ⬇️")
    val landforms = listOf(
        "Fold Mountains (Himalayas), Volcanic Arcs, Deep Oceanic Trenches (Mariana)",
        "Mid-Oceanic Ridges (Mid-Atlantic), Rift Valleys (East Africa), Basaltic Magma",
        "San Andreas Fault, Strike-Slip Earthquakes, No Volcanism, Crust Preserved"
    )

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, HydrosphereCyan.copy(alpha = 0.45f)),
        modifier = Modifier.fillMaxWidth().padding(top = 10.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "🌋", fontSize = 15.sp)
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "INTERACTIVE TECTONIC MODEL // SLIDE & DISCOVER",
                        color = HydrosphereCyan,
                        fontSize = 10.5.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.6.sp
                    )
                }
                Text(
                    text = "Tap Tabs ➔",
                    color = TopoContourMuted,
                    fontSize = 9.sp
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                listOf("Convergent", "Divergent", "Transform").forEachIndexed { idx, tabName ->
                    val isTabSelected = selectedBoundary == idx
                    Surface(
                        color = if (isTabSelected) HydrosphereCyan else OceanicDark,
                        shape = RoundedCornerShape(6.dp),
                        border = BorderStroke(0.8.dp, HydrosphereCyan.copy(alpha = 0.4f)),
                        modifier = Modifier
                            .weight(1f)
                            .clickable { selectedBoundary = idx }
                    ) {
                        Text(
                            text = tabName,
                            color = if (isTabSelected) Color.Black else AtlasParchment,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.padding(vertical = 6.dp)
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            Surface(
                color = OceanicDark,
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(10.dp)) {
                    Text(
                        text = arrows[selectedBoundary],
                        color = SunstoneGold,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Black,
                        textAlign = TextAlign.Center,
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        text = "Signature Geography: ${landforms[selectedBoundary]}",
                        color = AtlasParchment,
                        fontSize = 11.sp,
                        lineHeight = 16.sp
                    )
                }
            }
        }
    }
}

@Composable
fun AtmosphericProfileSandbox() {
    var selectedLayer by remember { mutableIntStateOf(0) }
    val layers = listOf("Troposphere", "Stratosphere", "Mesosphere", "Thermosphere")
    val altitudes = listOf("0 - 12 km (Datum to Tropopause)", "12 - 50 km (Ozone Maximum)", "50 - 80 km (Coldest Layer -100°C)", "80 - 500 km (Ionosphere & Auroras)")
    val lapses = listOf(
        "Temperature DECREASES with height (-6.5°C/km Normal Lapse Rate). All weather phenomena occur here.",
        "Temperature INCREASES with height (Inversion) due to Ozone (O3) UV absorption. Ideal for supersonic jets.",
        "Temperature PLUMMETS to -100°C. Meteors burn up upon atmospheric entry in this layer.",
        "Temperature SURGES past 1,000°C due to high-energy solar X-rays. Ionized plasma enables global radio bounce."
    )

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, ContourEmerald.copy(alpha = 0.45f)),
        modifier = Modifier.fillMaxWidth().padding(top = 10.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "🌤️", fontSize = 15.sp)
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "INTERACTIVE ATMOSPHERE BAROMETER // PROFILE",
                        color = ContourEmerald,
                        fontSize = 10.5.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.6.sp
                    )
                }
                Text(
                    text = "Tap Layer ➔",
                    color = TopoContourMuted,
                    fontSize = 9.sp
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                layers.forEachIndexed { idx, layerName ->
                    val isLayerSelected = selectedLayer == idx
                    Surface(
                        color = if (isLayerSelected) ContourEmerald else OceanicDark,
                        shape = RoundedCornerShape(6.dp),
                        border = BorderStroke(0.8.dp, ContourEmerald.copy(alpha = 0.4f)),
                        modifier = Modifier
                            .weight(1f)
                            .clickable { selectedLayer = idx }
                    ) {
                        Text(
                            text = layerName.take(6),
                            color = if (isLayerSelected) Color.Black else AtlasParchment,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Bold,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.padding(vertical = 5.dp)
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            Surface(
                color = OceanicDark,
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(10.dp)) {
                    Text(
                        text = "${layers[selectedLayer]}: ${altitudes[selectedLayer]}",
                        color = SunstoneGold,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = lapses[selectedLayer],
                        color = AtlasParchment,
                        fontSize = 11.sp,
                        lineHeight = 16.sp
                    )
                }
            }
        }
    }
}

@Composable
fun RiverCourseSandbox() {
    var selectedStage by remember { mutableIntStateOf(0) }
    val stages = listOf("Youth (Upper)", "Mature (Middle)", "Old (Lower)")
    val profiles = listOf(
        "Steep V-Shaped Valleys, Gorges & Canyons, Waterfalls (Vertical Downcutting)",
        "Moderate Gradient, Meanders, Alluvial Fans, Floodplains (Lateral Erosion Dominant)",
        "Gentle Plain, Oxbow Lakes, Natural Levees, Braided Channels & Massive Deltas (Deposition)"
    )

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, HydrosphereCyan.copy(alpha = 0.45f)),
        modifier = Modifier.fillMaxWidth().padding(top = 10.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "🏞️", fontSize = 15.sp)
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "INTERACTIVE FLUVIAL VALLEY PROFILE // COURSE",
                        color = HydrosphereCyan,
                        fontSize = 10.5.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.6.sp
                    )
                }
                Text(
                    text = "Tap Stage ➔",
                    color = TopoContourMuted,
                    fontSize = 9.sp
                )
            }
            Spacer(modifier = Modifier.height(10.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                stages.forEachIndexed { idx, stageName ->
                    val isStageSelected = selectedStage == idx
                    Surface(
                        color = if (isStageSelected) HydrosphereCyan else OceanicDark,
                        shape = RoundedCornerShape(6.dp),
                        border = BorderStroke(0.8.dp, HydrosphereCyan.copy(alpha = 0.4f)),
                        modifier = Modifier
                            .weight(1f)
                            .clickable { selectedStage = idx }
                    ) {
                        Text(
                            text = stageName,
                            color = if (isStageSelected) Color.Black else AtlasParchment,
                            fontSize = 10.5.sp,
                            fontWeight = FontWeight.Bold,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.padding(vertical = 6.dp)
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            Surface(
                color = OceanicDark,
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(10.dp)) {
                    Text(
                        text = "Stage Action & Landforms:",
                        color = SunstoneGold,
                        fontSize = 11.5.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = profiles[selectedStage],
                        color = AtlasParchment,
                        fontSize = 11.sp,
                        lineHeight = 16.sp
                    )
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
    val context = androidx.compose.ui.platform.LocalContext.current
    var isSpeaking by remember { mutableStateOf(false) }
    var ttsInstance by remember { mutableStateOf<android.speech.tts.TextToSpeech?>(null) }
    val mainHandler = remember { android.os.Handler(android.os.Looper.getMainLooper()) }

    DisposableEffect(context) {
        val tts = android.speech.tts.TextToSpeech(context) { status ->
            if (status == android.speech.tts.TextToSpeech.SUCCESS) {
                // Initialized successfully
            }
        }
        tts.setOnUtteranceProgressListener(object : android.speech.tts.UtteranceProgressListener() {
            override fun onStart(utteranceId: String?) {
                mainHandler.post { isSpeaking = true }
            }
            override fun onDone(utteranceId: String?) {
                mainHandler.post { isSpeaking = false }
            }
            @Deprecated("Deprecated in Java")
            override fun onError(utteranceId: String?) {
                mainHandler.post { isSpeaking = false }
            }
        })
        ttsInstance = tts
        onDispose {
            try {
                tts.stop()
                tts.shutdown()
            } catch (e: Exception) {
                // ignore
            }
        }
    }

    LaunchedEffect(question.id) {
        if (isSpeaking) {
            ttsInstance?.stop()
            isSpeaking = false
        }
    }

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
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    IconButton(
                        onClick = {
                            val tts = ttsInstance
                            if (tts != null) {
                                if (isSpeaking) {
                                    tts.stop()
                                    isSpeaking = false
                                } else {
                                    val textToRead = question.questionText.replace("\n", ". ")
                                    tts.speak(textToRead, android.speech.tts.TextToSpeech.QUEUE_FLUSH, null, "QuestionTTS_${question.id}")
                                    isSpeaking = true
                                }
                            }
                        },
                        modifier = Modifier.size(32.dp)
                    ) {
                        Icon(
                            imageVector = if (isSpeaking) Icons.Filled.VolumeUp else Icons.Filled.VolumeOff,
                            contentDescription = if (isSpeaking) "Stop Narration" else "Read Question Aloud",
                            tint = if (isSpeaking) accentGold else deepBlue.copy(alpha = 0.5f),
                            modifier = Modifier.size(20.dp)
                        )
                    }
                    Icon(
                        imageVector = if (isBookmarked) Icons.Filled.Bookmark else Icons.Filled.BookmarkBorder,
                        contentDescription = "Bookmark",
                        tint = if (isBookmarked) accentGold else deepBlue.copy(alpha = 0.3f),
                        modifier = Modifier.clickable { onBookmarkClick() }.size(26.dp)
                    )
                }
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
fun GeodeticSurveyHudStrip(
    questionNumber: Int,
    totalQuestions: Int,
    tier: String,
    altitudeMeters: Int
) {
    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, ContourEmerald.copy(alpha = 0.35f)),
        modifier = Modifier.fillMaxWidth().padding(bottom = 4.dp)
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            // 1. Compass dial
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(28.dp)
                        .clip(CircleShape)
                        .background(OceanicDark)
                        .border(1.dp, SunstoneGold.copy(alpha = 0.6f), CircleShape),
                    contentAlignment = Alignment.Center
                ) {
                    Canvas(modifier = Modifier.size(20.dp)) {
                        val center = Offset(size.width / 2f, size.height / 2f)
                        val angle = (questionNumber * 42.5f) * (Math.PI / 180f)
                        val nx = center.x + (size.width * 0.42f) * sin(angle).toFloat()
                        val ny = center.y - (size.height * 0.42f) * cos(angle).toFloat()
                        val sx = center.x - (size.width * 0.35f) * sin(angle).toFloat()
                        val sy = center.y + (size.height * 0.35f) * cos(angle).toFloat()
                        // North needle (Red)
                        drawLine(
                            color = Color(0xFFEF4444),
                            start = center,
                            end = Offset(nx, ny),
                            strokeWidth = 2.5f
                        )
                        // South needle (Muted Cyan)
                        drawLine(
                            color = HydrosphereCyan.copy(alpha = 0.7f),
                            start = center,
                            end = Offset(sx, sy),
                            strokeWidth = 2f
                        )
                        drawCircle(color = SunstoneGold, radius = 2.5f, center = center)
                    }
                }
                Spacer(modifier = Modifier.width(8.dp))
                Column {
                    Text(
                        text = "FIELD STATION $questionNumber/$totalQuestions",
                        color = SunstoneGold,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.6.sp
                    )
                    Text(
                        text = "Barometer: ${if (tier.equals("Hard", ignoreCase = true)) "500 hPa (Apex)" else if (tier.equals("Medium", ignoreCase = true)) "850 hPa (Ridge)" else "1,013 hPa (Datum)"}",
                        color = TopoContourMuted,
                        fontSize = 9.sp
                    )
                }
            }

            // 2. Altimeter / Elevation indicator
            Surface(
                color = ContourEmerald.copy(alpha = 0.12f),
                shape = RoundedCornerShape(6.dp),
                border = BorderStroke(0.8.dp, ContourEmerald.copy(alpha = 0.3f))
            ) {
                Row(
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(text = "⛰️", fontSize = 11.sp)
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = "${altitudeMeters.coerceAtLeast(500)}m ELEV",
                        color = ContourEmerald,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Black
                    )
                }
            }
        }
    }
}

@Composable
fun ExamGloryHeader(examTarget: String?, tier: String) {
    val (badgeText, gloryQuote, badgeColor) = when {
        examTarget?.contains("UPSC", ignoreCase = true) == true -> Triple(
            "🏛️ MISSION LBSNAA • CIVIL SERVICES CADRE",
            "Sardar Patel's Steel Frame: 1 MCQ mastered today = 1 step closer to Mussoorie.",
            SunstoneGold
        )
        examTarget?.contains("BPSC", ignoreCase = true) == true -> Triple(
            "🌾 70TH BPSC CCE • BIHAR ADMINISTRATIVE (SDM/DSP)",
            "From Patna Secretariat to Sub-Divisional Magistrate: Every question builds your rank.",
            ContourEmerald
        )
        examTarget?.contains("SSC", ignoreCase = true) == true -> Triple(
            "⭐ CENTRAL SECRETARIAT (ASO) • MERIT RANK CORPS",
            "High-Speed Precision: 1 question saved from negative penalty = 5,000 ranks gained.",
            HydrosphereCyan
        )
        examTarget?.contains("RRB", ignoreCase = true) == true || examTarget?.contains("RAILWAY", ignoreCase = true) == true -> Triple(
            "🚆 INDIAN RAILWAYS EXECUTIVE CORPS • APEX SPEED",
            "The Lifeline of the Nation: Master India's terrain to command the tracks.",
            SunstoneGold
        )
        else -> Triple(
            "🏛️ PREMIER EXAMINATIONS CADRE",
            "Relentless Consistency: Build conceptual mastery one question at a time.",
            SunstoneGold
        )
    }

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(10.dp),
        border = BorderStroke(1.dp, badgeColor.copy(alpha = 0.45f)),
        modifier = Modifier.fillMaxWidth().padding(bottom = 4.dp)
    ) {
        Column(modifier = Modifier.padding(10.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = badgeText,
                    color = badgeColor,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Black,
                    letterSpacing = 0.8.sp
                )
                Spacer(modifier = Modifier.weight(1f))
                Surface(
                    color = badgeColor.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(4.dp)
                ) {
                    Text(
                        text = tier.uppercase(),
                        color = badgeColor,
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = gloryQuote,
                color = TopoContourMuted,
                fontSize = 11.sp,
                fontStyle = FontStyle.Italic
            )
        }
    }
}

@Composable
fun DopamineCognitiveFeedbackBanner(
    isCorrect: Boolean,
    streak: Int,
    points: Int,
    examTarget: String? = null
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
                    .size(46.dp)
                    .clip(CircleShape)
                    .background(borderColor.copy(alpha = 0.2f)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = if (isCorrect) "🔥" else "🛡️",
                    fontSize = 22.sp
                )
            }
            Spacer(modifier = Modifier.width(12.dp))
            Column(modifier = Modifier.weight(1f)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(
                        text = if (isCorrect) {
                            if (streak >= 5) "🏆 5-STREAK TOAST // TOP 1% ACCURACY"
                            else if (streak >= 3) "🔥 3-IN-A-ROW // DOPAMINE SURGE"
                            else "TRUE NORTH CONFIRMED // KNOWLEDGE LOCKED"
                        } else {
                            "🛡️ RANK SHIELD ACTIVATED // TRAP DEFUSED"
                        },
                        color = titleColor,
                        fontWeight = FontWeight.ExtraBold,
                        fontSize = 11.5.sp,
                        letterSpacing = 0.6.sp
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "+$points GP",
                        color = titleColor,
                        fontWeight = FontWeight.Black,
                        fontSize = 12.sp
                    )
                }
                Spacer(modifier = Modifier.height(3.dp))
                Text(
                    text = if (isCorrect) {
                        if (streak >= 3) "🔥 $streak Waypoint Streak! Neural pathways firing with lightning speed."
                        else "Geographic concept firmly locked in active working memory."
                    } else {
                        "Toppers don't avoid mistakes—they make them HERE so they never lose marks on exam day. You just saved -0.66 penalty in the real hall! 🎯 Estimated Rank Defense: +1,420 positions."
                    },
                    color = Color.White.copy(alpha = 0.9f),
                    fontSize = 11.5.sp,
                    lineHeight = 16.sp
                )
                if (!isCorrect) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "⚡ Cognitive trap defused! Inspect the examiner dissection below to seal this gap permanently.",
                        color = SunstoneGold,
                        fontSize = 10.5.sp,
                        fontWeight = FontWeight.SemiBold
                    )
                }
            }
        }
    }
}

@Composable
fun BrainChillCard(
    onDismiss: () -> Unit
) {
    val curiosities = remember {
        listOf(
            Pair("🌊 The Boiling River of Mayantuyacu", "Deep in the Peruvian Amazon flows Shanay-Timpishka, a 6.4 km river where water temperatures reach up to 100°C due to deep geothermal faults, boiling small animals instantly!"),
            Pair("🏜️ The Singing Sands of the Thar", "When high desert winds shear dry sand dunes at specific angles, acoustic resonance creates a low, eerie humming drone between 60-105 Hz known as 'singing sands'."),
            Pair("⚡ Catatumbo Everlasting Lightning", "At the mouth of Lake Maracaibo in Venezuela, atmospheric conditions ignite lightning storms for up to 300 nights a year, flashing 280 times per hour without thunder."),
            Pair("🌋 The Blue Lava of Kawah Ijen", "In East Java, sulfuric gases combust upon contact with air at 360°C, producing majestic electric-blue neon flames cascading down the volcanic caldera at night."),
            Pair("❄️ The Sailing Stones of Racetrack Playa", "In Death Valley, heavy rocks weighing hundreds of pounds slide across dry lake beds leaving long trails, propelled by thin melting ice sheets pushed by gentle winter winds.")
        )
    }
    val randomCuriosity = remember { curiosities.random() }

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.2.dp, HydrosphereCyan.copy(alpha = 0.5f)),
        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(36.dp)
                        .clip(CircleShape)
                        .background(HydrosphereCyan.copy(alpha = 0.15f)),
                    contentAlignment = Alignment.Center
                ) {
                    Text(text = "🧠", fontSize = 18.sp)
                }
                Spacer(modifier = Modifier.width(10.dp))
                Column {
                    Text(
                        text = "20-SECOND BRAIN CHILL // COGNITIVE RESET",
                        color = HydrosphereCyan,
                        fontSize = 11.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.8.sp
                    )
                    Text(
                        text = "Pause for 10 seconds to recharge neural pathways before the next climb.",
                        color = TopoContourMuted,
                        fontSize = 10.sp
                    )
                }
                Spacer(modifier = Modifier.weight(1f))
                IconButton(onClick = onDismiss, modifier = Modifier.size(28.dp)) {
                    Icon(Icons.Default.Close, contentDescription = "Close", tint = TopoContourMuted, modifier = Modifier.size(16.dp))
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            Surface(
                color = OceanicDark,
                shape = RoundedCornerShape(10.dp),
                border = BorderStroke(0.8.dp, HydrosphereCyan.copy(alpha = 0.2f)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(10.dp)) {
                    Text(
                        text = randomCuriosity.first,
                        color = SunstoneGold,
                        fontWeight = FontWeight.Bold,
                        fontSize = 12.5.sp
                    )
                    Spacer(modifier = Modifier.height(3.dp))
                    Text(
                        text = randomCuriosity.second,
                        color = AtlasParchment.copy(alpha = 0.9f),
                        fontSize = 11.sp,
                        lineHeight = 15.sp
                    )
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = "🫁 4-7-8 Reset: Inhale calm, exhale doubt.",
                    color = ContourEmerald,
                    fontSize = 10.5.sp,
                    fontWeight = FontWeight.Medium
                )
                Button(
                    onClick = onDismiss,
                    colors = ButtonDefaults.buttonColors(containerColor = SunstoneGold),
                    shape = RoundedCornerShape(8.dp),
                    contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "Mind Refreshed ⚡",
                        color = Color.Black,
                        fontWeight = FontWeight.Black,
                        fontSize = 11.sp
                    )
                }
            }
        }
    }
}

@Composable
fun StructuredQuestionContent(
    questionText: String,
    textColor: Color
) {
    val fontScale = LocalFontScale.current
    val currentTheme = LocalAppThemeMode.current
    val statementBoxBg = when (currentTheme) {
        com.example.repository.AppThemeMode.LIGHT -> Color(0xFFF1F5F9)
        com.example.repository.AppThemeMode.SEPIA -> Color(0xFF281D10)
        else -> Color(0xFF1E293B).copy(alpha = 0.6f)
    }

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
            fontSize = (17 * fontScale).sp,
            fontWeight = FontWeight.SemiBold,
            lineHeight = (25 * fontScale).sp,
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
                                .background(statementBoxBg)
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
                                    fontSize = (12 * fontScale).sp,
                                    fontWeight = FontWeight.ExtraBold
                                )
                            }
                            Spacer(modifier = Modifier.width(10.dp))
                            Text(
                                text = content,
                                color = textColor,
                                fontSize = (15 * fontScale).sp,
                                fontWeight = FontWeight.Medium,
                                lineHeight = (22 * fontScale).sp,
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
                                .background(statementBoxBg)
                                .padding(horizontal = 12.dp, vertical = 8.dp)
                        ) {
                            Text(
                                text = label.uppercase(),
                                color = Color(0xFFF59E0B),
                                fontSize = (11 * fontScale).sp,
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 0.8.sp
                            )
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = content,
                                color = textColor,
                                fontSize = (15 * fontScale).sp,
                                fontWeight = FontWeight.Medium,
                                lineHeight = (22 * fontScale).sp
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
                                    color = if (currentTheme == com.example.repository.AppThemeMode.LIGHT) Color(0xFF0284C7) else Color(0xFF00F0FF),
                                    fontSize = (15 * fontScale).sp,
                                    fontWeight = FontWeight.Bold,
                                    lineHeight = (22 * fontScale).sp
                                )
                            }
                        }
                    }
                    else -> {
                        Text(
                            text = line,
                            color = textColor.copy(alpha = 0.95f),
                            fontSize = (16 * fontScale).sp,
                            fontWeight = FontWeight.SemiBold,
                            lineHeight = (24 * fontScale).sp
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
    val haptic = LocalHapticFeedback.current
    val fontScale = LocalFontScale.current

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
                    modifier = Modifier
                        .alpha(if (isCrossedOut) 0.55f else 1f)
                        .fillMaxWidth()
                        .clickable(enabled = !isAnswerSubmitted && !isCrossedOut) { 
                            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                            onOptionSelected(option.id) 
                        }
                ) {
                    Box(modifier = Modifier.fillMaxWidth()) {
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
                                    color = if (isCrossedOut) errorRed else deepBlue,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = (14 * fontScale).sp
                                )
                            }
                            Spacer(modifier = Modifier.width(16.dp))
                            Text(
                                text = option.text,
                                textDecoration = if (isCrossedOut) androidx.compose.ui.text.style.TextDecoration.LineThrough else null,
                                modifier = Modifier.weight(1f),
                                color = if (isCrossedOut) deepBlue.copy(alpha = 0.5f) else deepBlue.copy(alpha = 0.9f),
                                fontSize = (16 * fontScale).sp,
                                lineHeight = (22 * fontScale).sp
                            )
                            if (!isAnswerSubmitted) {
                                IconButton(
                                    onClick = { 
                                        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                                        onOptionCrossOut(option.id) 
                                    },
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

                        // Tactile red ink diagonal strike line & stamp when eliminated
                        if (isCrossedOut) {
                            Canvas(modifier = Modifier.matchParentSize()) {
                                drawLine(
                                    color = Color(0xFFEF4444).copy(alpha = 0.45f),
                                    start = Offset(14.dp.toPx(), size.height * 0.72f),
                                    end = Offset(size.width - 44.dp.toPx(), size.height * 0.28f),
                                    strokeWidth = 2.5f
                                )
                            }
                            Surface(
                                color = Color(0xFFEF4444).copy(alpha = 0.12f),
                                shape = RoundedCornerShape(4.dp),
                                border = BorderStroke(0.6.dp, Color(0xFFEF4444).copy(alpha = 0.35f)),
                                modifier = Modifier
                                    .align(Alignment.TopEnd)
                                    .padding(top = 6.dp, end = 40.dp)
                            ) {
                                Text(
                                    text = "ELIMINATED ✂️",
                                    color = Color(0xFFEF4444),
                                    fontSize = 8.5.sp,
                                    fontWeight = FontWeight.Black,
                                    modifier = Modifier.padding(horizontal = 4.dp, vertical = 1.dp)
                                )
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
                            Icon(Icons.AutoMirrored.Filled.CompareArrows, contentDescription = "Confusion Pair", tint = color)
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
    val fontScale = LocalFontScale.current
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
                    fontSize = (12 * fontScale).sp,
                    letterSpacing = 1.sp
                )
                Spacer(modifier = Modifier.height(6.dp))
                Text(
                    text = message,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.8f),
                    fontSize = (14 * fontScale).sp,
                    lineHeight = (20 * fontScale).sp
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
