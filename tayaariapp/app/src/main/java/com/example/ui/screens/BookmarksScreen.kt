package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircleOutline
import androidx.compose.material.icons.filled.DeleteOutline
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ExamQuestion
import com.example.model.MCQQuestion
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

    // Premium color palette
    val surfaceColor = Color(0xFFFDFCF8)
    val deepBlue = Color(0xFF1B3B5A)
    val accentGold = Color(0xFFF4A261)
    val cardColor = Color.White
    val errorRed = Color(0xFFE07A5F)
    val successGreen = Color(0xFF2E7D32)

    Scaffold(
        containerColor = surfaceColor,
        topBar = {
            TopAppBar(
                title = { 
                    Text(
                        "Saved Questions",
                        color = deepBlue,
                        fontWeight = FontWeight.ExtraBold,
                        fontSize = 22.sp
                    ) 
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = deepBlue)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = surfaceColor)
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .padding(paddingValues)
                .fillMaxSize()
        ) {
            if (availableTopics.size > 1) {
                LazyRow(
                    modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 12.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(availableTopics) { topic ->
                        val isSelected = topic == selectedTopic
                        Surface(
                            color = if (isSelected) accentGold else Color.Transparent,
                            shape = CircleShape,
                            border = BorderStroke(1.dp, if (isSelected) accentGold else deepBlue.copy(alpha = 0.1f)),
                            modifier = Modifier.clickable { viewModel.filterByTopic(topic) }
                        ) {
                            Text(
                                text = topic,
                                color = if (isSelected) Color.White else deepBlue.copy(alpha = 0.7f),
                                fontSize = 14.sp,
                                fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
                            )
                        }
                    }
                }
            }

            if (questions.isEmpty()) {
                Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                    Text(
                        text = "No bookmarked questions.", 
                        color = deepBlue.copy(alpha = 0.5f),
                        fontSize = 16.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize().padding(horizontal = 20.dp),
                    contentPadding = PaddingValues(bottom = 24.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    items(questions, key = { it.id }) { q ->
                        PremiumBookmarkCard(
                            question = q,
                            onRemove = { viewModel.removeBookmark(q.id) },
                            deepBlue = deepBlue,
                            accentGold = accentGold,
                            successGreen = successGreen,
                            errorRed = errorRed,
                            cardColor = cardColor
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun PremiumBookmarkCard(
    question: ExamQuestion,
    onRemove: () -> Unit,
    deepBlue: Color,
    accentGold: Color,
    successGreen: Color,
    errorRed: Color,
    cardColor: Color
) {
    Surface(
        color = cardColor,
        shape = RoundedCornerShape(16.dp),
        shadowElevation = 2.dp,
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(20.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    val formatText = (question as? MCQQuestion)?.questionFormatType ?: "Direct Fact"
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .background(accentGold, RoundedCornerShape(4.dp))
                                .padding(horizontal = 6.dp, vertical = 2.dp)
                        ) {
                            Text(
                                text = formatText.uppercase(),
                                color = Color.White,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Black,
                                letterSpacing = 0.5.sp
                            )
                        }
                        Text(
                            text = question.chapterCode,
                            color = deepBlue.copy(alpha = 0.6f),
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
                IconButton(onClick = onRemove, modifier = Modifier.size(24.dp)) {
                    Icon(Icons.Filled.DeleteOutline, contentDescription = "Remove Bookmark", tint = errorRed)
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = question.questionText.trim(),
                color = deepBlue,
                fontSize = 16.sp,
                fontWeight = FontWeight.SemiBold,
                lineHeight = 24.sp
            )

            val mcq = question as? MCQQuestion
            if (mcq != null) {
                Spacer(modifier = Modifier.height(16.dp))
                val correctOption = mcq.options.find { it.id == mcq.correctAnswerId }
                
                Surface(
                    color = successGreen.copy(alpha = 0.05f),
                    shape = RoundedCornerShape(12.dp),
                    border = BorderStroke(1.dp, successGreen.copy(alpha = 0.2f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Filled.CheckCircleOutline, contentDescription = null, tint = successGreen, modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = correctOption?.text ?: "Unknown",
                                color = successGreen,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                lineHeight = 20.sp
                            )
                        }
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = mcq.correctExplanation,
                            color = deepBlue.copy(alpha = 0.8f),
                            fontSize = 13.sp,
                            lineHeight = 18.sp
                        )
                    }
                }
            }
        }
    }
}
