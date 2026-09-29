package com.example.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.BookmarkBorder
import androidx.compose.material.icons.filled.Cancel
import androidx.compose.material.icons.filled.RemoveCircleOutline
import androidx.compose.material3.*
import androidx.compose.material3.IconButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.foundation.clickable
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ExamQuestion
import com.example.model.MCQQuestion

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ResultsScreen(
    questions: List<ExamQuestion>,
    userAnswers: Map<String, String>,
    score: java.math.BigDecimal,
    onDashboardClick: () -> Unit
) {
    val parchmentColor = Color(0xFFF4F1E1)
    val deepOceanBlue = Color(0xFF1B3B5A)
    val forestGreen = Color(0xFF2E7D32)
    val terracotta = Color(0xFFE07A5F)

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Test Results", fontWeight = FontWeight.Bold) },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = deepOceanBlue,
                    titleContentColor = parchmentColor
                )
            )
        },
        containerColor = parchmentColor
    ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                ScoreHeader(score, questions.size, deepOceanBlue)
            }
            item {
                ElevationProfileVisualization(questions, userAnswers, forestGreen, terracotta)
            }
            item {
                BreakdownSection(questions, userAnswers, deepOceanBlue, forestGreen)
            }
            item {
                Text(
                    text = "Question Review",
                    style = MaterialTheme.typography.titleLarge,
                    color = deepOceanBlue,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(top = 16.dp, bottom = 8.dp)
                )
            }
            items(questions) { q ->
                val mcq = q as? MCQQuestion
                if (mcq != null) {
                    val userAnswerId = userAnswers[mcq.id]
                    val isSkipped = userAnswerId == null
                    val opt = mcq.options.find { it.id == userAnswerId }
                    val isAbstain = opt?.role == com.example.model.OptionRole.ABSTAIN
                    
                    val outcome = when {
                        isSkipped -> com.example.model.AttemptOutcome.UNANSWERED
                        isAbstain -> com.example.model.AttemptOutcome.ABSTAINED
                        userAnswerId == mcq.correctAnswerId -> com.example.model.AttemptOutcome.CORRECT
                        else -> com.example.model.AttemptOutcome.INCORRECT
                    }

                    ReviewCard(
                        question = mcq,
                        userAnswerId = userAnswerId,
                        outcome = outcome,
                        deepOceanBlue = deepOceanBlue,
                        forestGreen = forestGreen,
                        terracotta = terracotta
                    )
                }
            }
            
            item {
                Button(
                    onClick = onDashboardClick,
                    modifier = Modifier.fillMaxWidth().padding(vertical = 16.dp),
                    colors = ButtonDefaults.buttonColors(containerColor = deepOceanBlue)
                ) {
                    Text("Return to Dashboard", color = parchmentColor, fontWeight = FontWeight.Bold)
                }
            }
        }
    }
}

@Composable
fun ScoreHeader(score: java.math.BigDecimal, total: Int, textColor: Color) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(24.dp).fillMaxWidth(),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text("Overall Score", style = MaterialTheme.typography.titleMedium, color = Color.Gray)
            Text(
                text = "${score.setScale(2, java.math.RoundingMode.HALF_UP).stripTrailingZeros().toPlainString()} / $total",
                style = MaterialTheme.typography.displayLarge,
                color = textColor,
                fontWeight = FontWeight.Bold
            )
            val percentage = if (total > 0) (score.toFloat() / total * 100).toInt() else 0
            Text("$percentage%", style = MaterialTheme.typography.titleMedium, color = textColor)
        }
    }
}

@Composable
fun ElevationProfileVisualization(
    questions: List<ExamQuestion>,
    userAnswers: Map<String, String>,
    forestGreen: Color,
    terracotta: Color
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Performance Profile", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
            Spacer(modifier = Modifier.height(16.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Bottom
            ) {
                questions.forEachIndexed { index, q ->
                    val mcq = q as? MCQQuestion
                    val ans = userAnswers[mcq?.id]
                    val isSkipped = mcq != null && ans == null
                    val option = mcq?.options?.find { it.id == ans }
                    val isAbstain = option?.role == com.example.model.OptionRole.ABSTAIN
                    val isCorrect = mcq != null && ans == mcq.correctAnswerId
                    
                    val barColor = when {
                        isSkipped -> Color.LightGray
                        isAbstain -> Color.Gray
                        isCorrect -> forestGreen
                        else -> terracotta
                    }
                    val height = if (isCorrect) 60.dp else if (isAbstain) 30.dp else if (isSkipped) 20.dp else 10.dp
                    
                    Box(
                        modifier = Modifier
                            .width(16.dp)
                            .height(height)
                            .clip(RoundedCornerShape(topStart = 4.dp, topEnd = 4.dp))
                            .background(barColor)
                    )
                }
            }
        }
    }
}

@Composable
fun BreakdownSection(
    questions: List<ExamQuestion>,
    userAnswers: Map<String, String>,
    deepOceanBlue: Color,
    forestGreen: Color
) {
    val formatStats = mutableMapOf<String, Pair<Int, Int>>() // Format -> (Correct, Total)
    // Note: Since we don't store Tier per question directly in ExamQuestion, 
    // we might just show breakdown by Format for now. 
    // If we want Tier, we can try to extract it or we just stick to Format.

    questions.forEach { q ->
        val mcq = q as? MCQQuestion
        if (mcq != null) {
            val ans = userAnswers[mcq.id]
            val option = mcq.options.find { it.id == ans }
            val isAbstain = option?.role == com.example.model.OptionRole.ABSTAIN
            val isSkipped = ans == null
            
            if (!isAbstain && !isSkipped) {
                val isCorrect = ans == mcq.correctAnswerId
                val format = mcq.questionFormatType
                
                val current = formatStats.getOrDefault(format, Pair(0, 0))
                formatStats[format] = Pair(
                    current.first + (if (isCorrect) 1 else 0),
                    current.second + 1
                )
            }
        }
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text("Breakdown by Format", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = deepOceanBlue)
            Spacer(modifier = Modifier.height(8.dp))
            formatStats.forEach { (format, stats) ->
                Row(
                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(format, style = MaterialTheme.typography.bodyMedium)
                    val percentage = if (stats.second > 0) (stats.first * 100 / stats.second) else 0
                    Text("${stats.first}/${stats.second} ($percentage%)", style = MaterialTheme.typography.bodyMedium, color = if (percentage >= 50) forestGreen else Color.Gray)
                }
            }
        }
    }
}

@Composable
fun ReviewCard(
    question: MCQQuestion,
    userAnswerId: String?,
    outcome: com.example.model.AttemptOutcome,
    deepOceanBlue: Color,
    forestGreen: Color,
    terracotta: Color
) {
    val borderColor = when (outcome) {
        com.example.model.AttemptOutcome.CORRECT -> forestGreen
        com.example.model.AttemptOutcome.INCORRECT -> terracotta
        com.example.model.AttemptOutcome.ABSTAINED -> Color.Gray
        com.example.model.AttemptOutcome.UNANSWERED -> Color.LightGray
    }
    val icon = when (outcome) {
        com.example.model.AttemptOutcome.CORRECT -> Icons.Filled.CheckCircle
        com.example.model.AttemptOutcome.ABSTAINED -> Icons.Filled.RemoveCircleOutline
        else -> Icons.Filled.Cancel
    }

    Card(
        modifier = Modifier.fillMaxWidth(),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(containerColor = Color.White),
        border = BorderStroke(1.dp, borderColor),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = icon,
                    contentDescription = outcome.name,
                    tint = borderColor
                )
                Spacer(modifier = Modifier.width(8.dp))
                Text(
                    text = "Format: ${question.questionFormatType}",
                    style = MaterialTheme.typography.labelSmall,
                    color = Color.Gray
                )
            }
            Spacer(modifier = Modifier.height(8.dp))
            
            Text(
                text = question.questionText,
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium,
                color = deepOceanBlue
            )
            
            Spacer(modifier = Modifier.height(12.dp))
            
            val userOption = question.options.find { it.id == userAnswerId }
            val correctOption = question.options.find { it.id == question.correctAnswerId }
            
            if (userAnswerId != null) {
                Text(
                    text = "Your Answer: ${userOption?.text ?: "Unknown"}",
                    style = MaterialTheme.typography.bodySmall,
                    color = borderColor,
                    fontWeight = FontWeight.Bold
                )
            } else {
                Text(
                    text = "Your Answer: Skipped",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray,
                    fontWeight = FontWeight.Bold
                )
            }
            
            if (outcome != com.example.model.AttemptOutcome.CORRECT) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "Correct Answer: ${correctOption?.text ?: "Unknown"}",
                    style = MaterialTheme.typography.bodySmall,
                    color = forestGreen,
                    fontWeight = FontWeight.Bold
                )
            }
            
            Spacer(modifier = Modifier.height(8.dp))
            
            Surface(
                color = borderColor.copy(alpha = 0.1f),
                shape = RoundedCornerShape(8.dp)
            ) {
                Text(
                    text = "Explanation: ${question.correctExplanation}",
                    style = MaterialTheme.typography.bodySmall,
                    modifier = Modifier.padding(8.dp),
                    color = Color.DarkGray
                )
            }
        }
    }
}
