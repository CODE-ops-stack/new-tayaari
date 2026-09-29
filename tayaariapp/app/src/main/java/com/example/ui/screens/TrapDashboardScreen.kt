package com.example.ui.screens

import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.clickable
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Analytics
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.WarningAmber
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.database.TrapAnalyticsEntity
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TrapDashboardScreen(
    trapAnalytics: List<TrapAnalyticsEntity>,
    onPracticeTrap: (String) -> Unit,
    onBack: () -> Unit
) {
    // Premium color palette
    val surfaceColor = MaterialTheme.colorScheme.surface
    val cardColor = MaterialTheme.colorScheme.background
    val deepBlue = MaterialTheme.colorScheme.primary
    val warningRed = MaterialTheme.colorScheme.error
    val accentGold = MaterialTheme.colorScheme.tertiary

    Scaffold(
        containerColor = surfaceColor,
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Analytics,
                            contentDescription = null,
                            tint = deepBlue,
                            modifier = Modifier.size(24.dp)
                        )
                        Spacer(modifier = Modifier.width(8.dp))
                        Text(
                            "Trap Analytics",
                            color = deepBlue,
                            fontWeight = FontWeight.ExtraBold,
                            fontSize = 22.sp
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                            tint = deepBlue
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = surfaceColor
                )
            )
        }
    ) { paddingValues ->
        if (trapAnalytics.isEmpty()) {
            // Premium Empty State
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(32.dp),
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
                        imageVector = Icons.Default.WarningAmber,
                        contentDescription = null,
                        tint = deepBlue.copy(alpha = 0.5f),
                        modifier = Modifier.size(64.dp)
                    )
                }
                Spacer(modifier = Modifier.height(24.dp))
                Text(
                    text = "No Traps Encountered",
                    fontSize = 20.sp,
                    fontWeight = FontWeight.Bold,
                    color = deepBlue
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "You haven't fallen for any cognitive traps yet. Keep up the rigorous practice!",
                    fontSize = 16.sp,
                    color = deepBlue.copy(alpha = 0.7f),
                    textAlign = TextAlign.Center
                )
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .padding(horizontal = 16.dp),
                contentPadding = PaddingValues(vertical = 16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    Text(
                        text = "Identify your cognitive vulnerabilities. The higher the frequency, the more susceptible you are to that specific trap format.",
                        fontSize = 14.sp,
                        color = deepBlue.copy(alpha = 0.6f),
                        modifier = Modifier.padding(bottom = 8.dp)
                    )
                    HorizontalDivider(
                        color = deepBlue.copy(alpha = 0.1f)
                    )
                }

                val maxFreq = trapAnalytics.maxOfOrNull { it.frequency } ?: 1
                items(trapAnalytics.sortedByDescending { it.frequency }) { trap ->
                    EnhancedTrapStatCard(
                        trap = trap,
                        maxFreq = maxFreq,
                        deepBlue = deepBlue,
                        warningRed = warningRed,
                        accentGold = accentGold,
                        cardColor = cardColor,
                        onPracticeTrap = onPracticeTrap
                    )
                }
            }
        }
    }
}

@Composable
fun EnhancedTrapStatCard(
    trap: TrapAnalyticsEntity,
    maxFreq: Int,
    deepBlue: Color,
    warningRed: Color,
    accentGold: Color,
    cardColor: Color,
    onPracticeTrap: (String) -> Unit
) {
    val targetFraction = if (maxFreq > 0) trap.frequency.toFloat() / maxFreq else 0f
    var animationPlayed by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) {
        delay(100) // Slight delay for stagger effect
        animationPlayed = true
    }

    val animatedProgress by animateFloatAsState(
        targetValue = if (animationPlayed) targetFraction else 0f,
        animationSpec = tween(durationMillis = 1000, easing = FastOutSlowInEasing),
        label = "progressAnimation"
    )

    // Color code based on severity
    val barColor = when {
        targetFraction > 0.7f -> warningRed
        targetFraction > 0.4f -> accentGold
        else -> deepBlue.copy(alpha = 0.6f)
    }

    var expanded by remember { mutableStateOf(false) }
    
    val failedQuestions = remember(trap.failedQuestionsJson) {
        try {
            val arr = org.json.JSONArray(trap.failedQuestionsJson)
            val list = mutableListOf<org.json.JSONObject>()
            for (i in 0 until arr.length()) list.add(arr.getJSONObject(i))
            list
        } catch (e: Exception) { emptyList() }
    }

    Card(
        modifier = Modifier.fillMaxWidth().clickable { expanded = !expanded },
        shape = RoundedCornerShape(16.dp),
        colors = CardDefaults.cardColors(containerColor = cardColor),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier.padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = trap.trapType.uppercase(),
                    color = deepBlue,
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.2.sp
                )
                Surface(
                    shape = RoundedCornerShape(24.dp),
                    color = barColor.copy(alpha = 0.1f)
                ) {
                    Text(
                        text = "${trap.frequency} TRIPPED",
                        color = barColor,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Black,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 4.dp)
                    )
                }
            }

            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(10.dp)
                    .clip(RoundedCornerShape(5.dp))
                    .background(Color.LightGray.copy(alpha = 0.3f))
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxWidth(animatedProgress)
                        .height(10.dp)
                        .clip(RoundedCornerShape(5.dp))
                        .background(barColor)
                )
            }
            
            AnimatedVisibility(
                visible = expanded,
                enter = expandVertically(),
                exit = shrinkVertically()
            ) {
                Column(modifier = Modifier.padding(top = 16.dp)) {
                    Divider(color = Color.LightGray.copy(alpha = 0.5f), thickness = 1.dp)
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    if (failedQuestions.isEmpty()) {
                        Text(
                            text = "No detailed history available for this trap.",
                            color = deepBlue.copy(alpha = 0.6f),
                            fontSize = 14.sp
                        )
                    } else {
                        failedQuestions.forEachIndexed { index, q ->
                            Column(modifier = Modifier.padding(bottom = 16.dp)) {
                                Text(
                                    text = "Question ${index + 1}:",
                                    color = accentGold,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 12.sp
                                )
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = q.optString("questionText", "Unknown"),
                                    color = deepBlue,
                                    fontSize = 14.sp,
                                    lineHeight = 20.sp
                                )
                                Spacer(modifier = Modifier.height(8.dp))
                                Surface(
                                    color = warningRed.copy(alpha = 0.05f),
                                    shape = RoundedCornerShape(8.dp),
                                    modifier = Modifier.fillMaxWidth()
                                ) {
                                    Column(modifier = Modifier.padding(12.dp)) {
                                        Text(
                                            text = "Why you fell for it:",
                                            color = warningRed,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 12.sp
                                        )
                                        Text(
                                            text = q.optString("dissection", ""),
                                            color = deepBlue.copy(alpha = 0.8f),
                                            fontSize = 14.sp
                                        )
                                    }
                                }
                            }
                        }
                        
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(
                            onClick = { onPracticeTrap(trap.trapType) },
                            colors = ButtonDefaults.buttonColors(containerColor = accentGold),
                            modifier = Modifier.fillMaxWidth().height(48.dp),
                            shape = RoundedCornerShape(12.dp)
                        ) {
                            Text("Practice This Trap", fontWeight = FontWeight.Bold, color = Color.White)
                        }
                    }
                }
            }
        }
    }
}