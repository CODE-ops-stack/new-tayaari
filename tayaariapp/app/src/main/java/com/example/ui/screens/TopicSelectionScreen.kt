package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.slideInVertically
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.filled.Lightbulb
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Analytics
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.Explore
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material.icons.filled.FlashOn
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ExamBlueprint
import com.example.viewmodel.TopicUIModel
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TopicSelectionScreen(
    onInsightsClick: () -> Unit = {},
    topics: List<TopicUIModel>,
    nextAction: com.example.model.RecommendedAction?,
    profile: ExamBlueprint?,
    onTopicSelected: (topicName: String, tier: String, format: String) -> Unit,
    onBookmarksClick: () -> Unit = {},
    onAnalyticsClick: () -> Unit = {},
    onRevisionClick: () -> Unit = {},
    onPaperTwinClick: () -> Unit = {},
    onReadinessClick: () -> Unit = {},
    onChangeExam: () -> Unit = {}
) {
    val surfaceColor = MaterialTheme.colorScheme.surface
    val cardColor = MaterialTheme.colorScheme.background
    val deepBlue = MaterialTheme.colorScheme.primary
    val warningRed = MaterialTheme.colorScheme.error
    val accentGold = MaterialTheme.colorScheme.tertiary

    var isHardcoreMode by remember { mutableStateOf(false) }
    
    // Group topics by module
    val groupedTopics = remember(topics) {
        topics.groupBy { it.topic.module }
    }
    
    // State to track expanded modules
    val expandedStates = remember { mutableStateMapOf<String, Boolean>() }
    // Expand Physical Geography by default
    LaunchedEffect(Unit) {
        if (expandedStates.isEmpty()) {
            expandedStates["Physical Geography"] = true
        }
    }
    Scaffold(
        containerColor = surfaceColor,
        topBar = {
            TopAppBar(
                title = {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        androidx.compose.foundation.Image(
                            painter = androidx.compose.ui.res.painterResource(id = com.example.R.mipmap.ic_launcher),
                            contentDescription = "App Logo",
                            modifier = Modifier
                                .size(36.dp)
                                .clip(CircleShape)
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Text(
                            "Tayaari Pakki",
                            color = deepBlue,
                            fontWeight = FontWeight.ExtraBold,
                            fontSize = 22.sp
                        )
                    }
                },
                actions = {
                    IconButton(onClick = onChangeExam) {
                        Icon(
                            imageVector = androidx.compose.material.icons.Icons.Default.Explore,
                            contentDescription = "Change Exam",
                            tint = deepBlue
                        )
                    }
                    IconButton(onClick = onAnalyticsClick) {
                        Icon(
                            imageVector = Icons.Default.Analytics,
                            contentDescription = "Analytics",
                            tint = deepBlue
                        )
                    }
                    IconButton(onClick = onRevisionClick) {
                        Icon(
                            imageVector = Icons.Default.Schedule,
                            contentDescription = "Revision",
                            tint = deepBlue
                        )
                    }
                    IconButton(onClick = onBookmarksClick) {
                        Icon(
                            imageVector = Icons.Default.Bookmark,
                            contentDescription = "Bookmarks",
                            tint = deepBlue
                        )
                    }
                    IconButton(onClick = onPaperTwinClick) {
                        Icon(
                            imageVector = Icons.Default.FlashOn,
                            contentDescription = "Paper Twin Mock",
                            tint = accentGold
                        )
                    }
                    IconButton(onClick = onReadinessClick) {
                        Icon(
                            imageVector = Icons.Default.CheckCircle,
                            contentDescription = "Readiness Evidence",
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
        if (topics.isEmpty()) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = accentGold)
            }
        } else {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
            ) {
                if (nextAction != null) {
                    NextBestActionCard(action = nextAction, onTopicSelected = onTopicSelected, onRevisionClick = onRevisionClick, onAnalyticsClick = onAnalyticsClick)
                }
                // Profile & Hardcore Toggle Section
                Surface(
                    color = cardColor,
                    shadowElevation = 4.dp,
                    shape = RoundedCornerShape(bottomStart = 24.dp, bottomEnd = 24.dp),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        verticalArrangement = Arrangement.spacedBy(16.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column {
                                Text(
                                    "Target Goal",
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = deepBlue.copy(alpha = 0.6f),
                                    letterSpacing = 1.sp
                                )
                                Text(
                                    text = profile?.displayName ?: "All Exams",
                                    fontSize = 16.sp,
                                    fontWeight = FontWeight.ExtraBold,
                                    color = deepBlue
                                )
                            }
                            
                            // Hardcore Mode Toggle
                            Surface(
                                color = if (isHardcoreMode) warningRed.copy(alpha = 0.1f) else deepBlue.copy(alpha = 0.05f),
                                shape = RoundedCornerShape(12.dp),
                                modifier = Modifier.clickable { isHardcoreMode = !isHardcoreMode }
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Icon(
                                        imageVector = Icons.Default.FlashOn,
                                        contentDescription = "Hardcore Mode",
                                        tint = if (isHardcoreMode) warningRed else deepBlue.copy(alpha = 0.5f),
                                        modifier = Modifier.size(18.dp)
                                    )
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text(
                                        text = "Hardcore",
                                        color = if (isHardcoreMode) warningRed else deepBlue.copy(alpha = 0.6f),
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 14.sp
                                    )
                                }
                            }
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Modules Accordion List
                LazyColumn(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(horizontal = 16.dp),
                    contentPadding = PaddingValues(bottom = 24.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    item {
                        Card(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(bottom = 16.dp)
                                .clickable {
                                    val tier = profile?.allowedTiers?.firstOrNull() ?: "Medium"
                                    onTopicSelected("Global", tier, "Paper Twin")
                                },
                            colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.secondaryContainer)
                        ) {
                            Row(
                                modifier = Modifier.padding(16.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Icon(Icons.Default.Explore, contentDescription = "Paper Twin", tint = MaterialTheme.colorScheme.onSecondaryContainer, modifier = Modifier.size(32.dp))
                                Spacer(modifier = Modifier.width(16.dp))
                                Column {
                                    Text("Paper Twin", style = MaterialTheme.typography.titleMedium, fontWeight = androidx.compose.ui.text.font.FontWeight.Bold, color = MaterialTheme.colorScheme.onSecondaryContainer)
                                    Text("Generate a mock test mirroring the exact DNA of ", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSecondaryContainer.copy(alpha = 0.8f))
                                }
                            }
                        }
                    }
                    
                    val orderedModules = listOf("Physical Geography", "Indian Geography", "World Geography", "Human & Economic Geography", "Miscellaneous Topics")
                    
                    orderedModules.forEach { moduleName ->
                        val moduleTopics = groupedTopics[moduleName]
                        if (moduleTopics != null && moduleTopics.isNotEmpty()) {
                            item {
                                val isExpanded = expandedStates[moduleName] == true
                                
                                // Module Header
                                Surface(
                                    color = deepBlue,
                                    shape = RoundedCornerShape(12.dp),
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .clickable { expandedStates[moduleName] = !isExpanded }
                                ) {
                                    Row(
                                        modifier = Modifier.padding(16.dp),
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.SpaceBetween
                                    ) {
                                        Text(
                                            text = moduleName,
                                            color = Color.White,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 18.sp
                                        )
                                        Icon(
                                            imageVector = if (isExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                                            contentDescription = "Toggle",
                                            tint = Color.White
                                        )
                                    }
                                }
                                
                                // Module Topics
                                AnimatedVisibility(
                                    visible = isExpanded,
                                    enter = expandVertically(),
                                    exit = shrinkVertically()
                                ) {
                                    Column(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(top = 8.dp),
                                        verticalArrangement = Arrangement.spacedBy(8.dp)
                                    ) {
                                        moduleTopics.forEach { item ->
                                            PremiumTopicCard(
                                                item = item,
                                                profile = profile,
                                                isHardcoreMode = isHardcoreMode,
                                                onClick = {
                                                    val selectedTier = if (isHardcoreMode) {
                                                        profile?.allowedTiers?.lastOrNull() ?: "Basic"
                                                    } else {
                                                        profile?.allowedTiers?.firstOrNull() ?: "Basic"
                                                    }
                                                    onTopicSelected(item.topic.name, selectedTier, "")
                                                },
                                                deepBlue = deepBlue,
                                                warningRed = warningRed,
                                                accentGold = accentGold,
                                                cardColor = cardColor
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

@Composable
fun PremiumTopicCard(
    item: TopicUIModel,
    profile: ExamBlueprint?,
    isHardcoreMode: Boolean,
    onClick: () -> Unit,
    deepBlue: Color,
    warningRed: Color,
    accentGold: Color,
    cardColor: Color
) {
    val isZeroAvailable = item.availableCount == 0

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = cardColor),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Icon Background
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .background(
                        if (isZeroAvailable) Color.LightGray.copy(alpha = 0.2f)
                        else deepBlue.copy(alpha = 0.05f),
                        CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Icon(
                    imageVector = Icons.Default.Explore,
                    contentDescription = null,
                    modifier = Modifier.size(24.dp),
                    tint = if (isZeroAvailable) Color.Gray.copy(alpha = 0.5f) else accentGold
                )
            }
            
            Spacer(modifier = Modifier.width(16.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.topic.name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.ExtraBold,
                    color = if (isZeroAvailable) Color.Gray else deepBlue,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    fontSize = 16.sp
                )
                
                Spacer(modifier = Modifier.height(4.dp))
                
                Row(verticalAlignment = Alignment.CenterVertically) {
                    if (isZeroAvailable) {
                        Icon(
                            imageVector = Icons.Default.Warning,
                            contentDescription = "Zero questions available",
                            tint = warningRed,
                            modifier = Modifier.size(12.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                    }
                    Text(
                        text = "${item.availableCount} Questions",
                        style = MaterialTheme.typography.bodySmall,
                        fontWeight = FontWeight.Medium,
                        color = if (isZeroAvailable) accentGold else deepBlue.copy(alpha = 0.6f)
                    )
                }
            }
            
            // Expected Difficulty Indicator
            val activeTier = if (isHardcoreMode) profile?.allowedTiers?.lastOrNull() else profile?.allowedTiers?.firstOrNull()
            if (activeTier != null) {
                val isAdvanced = activeTier == "Advanced"
                val bgColor = if (isAdvanced) accentGold.copy(alpha = 0.15f) else deepBlue.copy(alpha = 0.08f)
                val txtColor = if (isAdvanced) accentGold else deepBlue.copy(alpha = 0.8f)
                
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(6.dp))
                        .background(bgColor)
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = activeTier.uppercase(),
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Black,
                        color = txtColor,
                        letterSpacing = 0.5.sp
                    )
                }
            }
        }
    }
}







