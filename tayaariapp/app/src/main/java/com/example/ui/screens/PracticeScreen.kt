package com.example.ui.screens

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
    onSubmitAnswerWithConfidence: (String) -> Unit = {},
    onBookmarkToggle: () -> Unit,
    onPrevious: () -> Unit,
    onSkip: () -> Unit,
    onNext: () -> Unit,
    onDashboardClick: () -> Unit,
    onRestart: () -> Unit,
    onBack: () -> Unit
) {
    // Premium color palette mapping to MaterialTheme
    val surfaceColor = MaterialTheme.colorScheme.surface
    val deepBlue = MaterialTheme.colorScheme.primary
    val accentGold = MaterialTheme.colorScheme.tertiary
    val cardColor = MaterialTheme.colorScheme.background
    val errorRed = MaterialTheme.colorScheme.error
    val successGreen = MaterialTheme.colorScheme.secondary
    val trapBackground = MaterialTheme.colorScheme.errorContainer

    Scaffold(
        containerColor = surfaceColor,
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
                        Text(
                            text = topicName.substringAfter(". ").trim(),
                            color = deepBlue,
                            fontWeight = FontWeight.ExtraBold,
                            fontSize = 20.sp,
                            maxLines = 1
                        )
                        Spacer(modifier = Modifier.height(6.dp))
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            BadgeChip(text = tier.uppercase(), color = accentGold, textColor = Color.White)
                            BadgeChip(text = format, color = deepBlue.copy(alpha = 0.1f), textColor = deepBlue)
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

                // Progress Bar
                if (!uiState.isTestFinished && uiState.totalQuestionsInSet > 0) {
                    LinearProgressIndicator(
                        progress = { uiState.questionNumber.toFloat() / uiState.totalQuestionsInSet },
                        modifier = Modifier.fillMaxWidth().height(4.dp),
                        color = accentGold,
                        trackColor = deepBlue.copy(alpha = 0.1f)
                    )
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
                        Button(
                            onClick = onBack,
                            colors = ButtonDefaults.buttonColors(containerColor = deepBlue)
                        ) {
                            Text("Back to Topics")
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
                            "Session Complete!",
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
                                        onSubmitAnswerWithConfidence = onSubmitAnswerWithConfidence,
                                        deepBlue = deepBlue,
                                        successGreen = successGreen,
                                        errorRed = errorRed,
                                        cardColor = cardColor,
                                        trapBackground = trapBackground
                                    )
                                }

                                // Always show correct explanation after any answer is submitted
                                if (uiState.selectedOptionId != null) {
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
        color = successGreen.copy(alpha = 0.05f),
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.dp, successGreen.copy(alpha = 0.2f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    Icons.Default.CheckCircleOutline,
                    contentDescription = null,
                    tint = successGreen,
                    modifier = Modifier.size(20.dp)
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "CORRECT ANSWER",
                    color = successGreen,
                    fontWeight = FontWeight.Black,
                    fontSize = 12.sp,
                    letterSpacing = 1.sp
                )
            }
            if (correctOption != null) {
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = correctOption.text,
                    color = deepBlue,
                    fontWeight = FontWeight.Bold,
                    fontSize = 15.sp,
                    lineHeight = 22.sp
                )
            }
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = explanation,
                color = deepBlue.copy(alpha = 0.8f),
                fontSize = 14.sp,
                lineHeight = 20.sp
            )
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
                    text = "QUESTION",
                    color = accentGold,
                    fontSize = 12.sp,
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
            if (!question.imageUrl.isNullOrEmpty()) {
                coil.compose.AsyncImage(
                    model = question.imageUrl,
                    contentDescription = "Question Image",
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                        .clip(RoundedCornerShape(8.dp)),
                    contentScale = androidx.compose.ui.layout.ContentScale.Crop
                )
                Spacer(modifier = Modifier.height(16.dp))
            }
            Text(
                text = question.questionText.trim(),
                color = deepBlue,
                fontSize = 18.sp,
                fontWeight = FontWeight.SemiBold,
                lineHeight = 26.sp
            )
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
    onSubmitAnswerWithConfidence: (String) -> Unit = {},
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

                // Trap Dissection â€” only for the incorrectly selected option
                AnimatedVisibility(visible = showTrapFeedback) {
                    val dissection = distractorDissections.find { it.optionId == option.id }
                    Spacer(modifier = Modifier.height(12.dp))
                    FeedbackBox(
                        title = "TRAP: ${dissection?.trapType?.uppercase() ?: "INCORRECT"}",
                        message = dissection?.dissection ?: "That is not the correct answer.",
                        color = errorRed,
                        bgColor = trapBackground
                    )
                }
            }

    // CONFUSION PAIR DISAMBIGUATION
        detectedConfusionPair?.let { result ->
            val pair = result.pair
            val evidenceLevel = result.evidenceLevel
            
            val (titleText, color) = when (evidenceLevel) {
                com.example.repository.ConfusionEvidenceLevel.CONFIRMED_CONFUSION -> "Recurring confusion" to Color(0xFFD32F2F)
                com.example.repository.ConfusionEvidenceLevel.CONFIRMED_CONTEXT -> "Recurring confusion" to Color(0xFFD32F2F)
                com.example.repository.ConfusionEvidenceLevel.EMERGING_CONFUSION -> "Pattern emerging" to Color(0xFFF57C00)
                com.example.repository.ConfusionEvidenceLevel.POSSIBLE_CONFUSION -> "Possible confusion" to Color(0xFFFBC02D)
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
                        Text("It seems you might be confusing two related concepts. Let's disambiguate:", fontSize = 14.sp, color = Color.DarkGray)
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

    // CONFIDENCE CALIBRATION UI
        AnimatedVisibility(visible = pendingOptionId != null && selectedOptionId == null) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(top = 16.dp)
                    .background(deepBlue.copy(alpha = 0.05f), RoundedCornerShape(12.dp))
                    .border(1.dp, deepBlue.copy(alpha = 0.1f), RoundedCornerShape(12.dp))
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(
                    text = "How confident are you?",
                    color = deepBlue,
                    fontWeight = FontWeight.Bold,
                    fontSize = 16.sp
                )
                Spacer(modifier = Modifier.height(12.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceEvenly
                ) {
                    val confidences = listOf("Certain", "Likely", "Unsure", "Guessing")
                    confidences.forEach { conf ->
                        Button(
                            onClick = { onSubmitAnswerWithConfidence(conf) },
                            colors = ButtonDefaults.buttonColors(containerColor = deepBlue),
                            shape = RoundedCornerShape(8.dp),
                            contentPadding = PaddingValues(horizontal = 12.dp, vertical = 8.dp)
                        ) {
                            Text(text = conf, fontSize = 12.sp)
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



