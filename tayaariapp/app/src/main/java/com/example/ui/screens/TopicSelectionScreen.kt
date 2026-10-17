package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AddCircleOutline
import androidx.compose.material.icons.filled.Analytics
import androidx.compose.material.icons.filled.Bookmark
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Explore
import androidx.compose.material.icons.filled.FlashOn
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material.icons.filled.Psychology
import androidx.compose.material.icons.filled.RadioButtonUnchecked
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.R
import com.example.model.ExamBlueprint
import com.example.ui.theme.*
import com.example.viewmodel.TopicUIModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TopicSelectionScreen(
    onInsightsClick: () -> Unit = {},
    topics: List<TopicUIModel>,
    nextAction: com.example.model.RecommendedAction?,
    profile: ExamBlueprint?,
    allSelectedProfiles: List<ExamBlueprint> = emptyList(),
    onSelectActiveProfile: (ExamBlueprint) -> Unit = {},
    isSyncing: Boolean = false,
    syncStatusMessage: String = "Online Stream (v24.0 • 4,851 MCQs) • Zero Local Asset",
    updateState: com.example.updater.AppUpdateManager.UpdateState = com.example.updater.AppUpdateManager.UpdateState.Idle,
    onTopicSelected: (topicName: String, tier: String, format: String) -> Unit,
    onBookmarksClick: () -> Unit = {},
    onAnalyticsClick: () -> Unit = {},
    onRevisionClick: () -> Unit = {},
    onPaperTwinClick: () -> Unit = {},
    onReadinessClick: () -> Unit = {},
    onMainsPracticeClick: () -> Unit = {},
    onChangeExam: () -> Unit = {},
    onRefreshSync: () -> Unit = {},
    onCheckUpdate: () -> Unit = {}
) {
    val surfaceColor = MaterialTheme.colorScheme.surface
    val cardColor = MaterialTheme.colorScheme.background
    val deepBlue = MaterialTheme.colorScheme.primary
    val warningRed = MaterialTheme.colorScheme.error
    val accentGold = MaterialTheme.colorScheme.tertiary

    var isHardcoreMode by remember { mutableStateOf(false) }
    var showExamSwitcherDialog by remember { mutableStateOf(false) }

    // Group topics by module
    val groupedTopics = remember(topics) {
        topics.groupBy { it.topic.module }
    }

    // Expand all modules by default so all 30 chapters are visible immediately
    val expandedStates = remember { mutableStateMapOf<String, Boolean>() }
    LaunchedEffect(groupedTopics) {
        groupedTopics.keys.forEach { moduleName ->
            if (!expandedStates.containsKey(moduleName)) {
                expandedStates[moduleName] = true
            }
        }
    }

    com.example.ui.components.AtlasBackground {
        com.example.ui.components.TopographicBackground(lineColor = ContourEmerald.copy(alpha = 0.035f)) {
            Scaffold(
                containerColor = Color.Transparent,
                topBar = {
                    TopAppBar(
                        title = {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Image(
                                    painter = painterResource(id = R.mipmap.ic_launcher),
                                    contentDescription = "App Logo",
                                    modifier = Modifier
                                        .size(34.dp)
                                        .clip(CircleShape)
                                )
                                Spacer(modifier = Modifier.width(10.dp))
                                Column {
                                    Text(
                                        "Tayaari Pakki",
                                        color = deepBlue,
                                        fontFamily = CartographicSerif,
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 18.sp,
                                        maxLines = 1,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                    Text(
                                        "Civil Services Geography Cadastre • v24.0",
                                        color = deepBlue.copy(alpha = 0.7f),
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Medium,
                                        letterSpacing = 0.4.sp
                                    )
                                }
                            }
                        },
                        actions = {
                            // Target Examination Expedition Switcher Chip (Tap to Switch Active Commission)
                            Surface(
                                color = DeepBasalt.copy(alpha = 0.9f),
                                shape = RoundedCornerShape(20.dp),
                                border = BorderStroke(1.dp, SunstoneGold.copy(alpha = 0.6f)),
                                modifier = Modifier.clickable { showExamSwitcherDialog = true }
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Text("🧭", fontSize = 12.sp)
                                    Spacer(modifier = Modifier.width(4.dp))
                                    Text(
                                        text = profile?.displayName ?: "UPSC CSE",
                                        color = SunstoneGold,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.Bold,
                                        maxLines = 1
                                    )
                                    Spacer(modifier = Modifier.width(2.dp))
                                    Icon(
                                        imageVector = Icons.Default.KeyboardArrowDown,
                                        contentDescription = "Switch Commission",
                                        tint = SunstoneGold,
                                        modifier = Modifier.size(16.dp)
                                    )
                                }
                            }

                            Spacer(modifier = Modifier.width(4.dp))

                            // Field Readiness Radar Shortcut
                            IconButton(onClick = onReadinessClick) {
                                Icon(
                                    imageVector = Icons.Default.CheckCircle,
                                    contentDescription = "Field Readiness Radar",
                                    tint = ContourEmerald
                                )
                            }

                            // Cloud Sync Refresh Trigger
                            IconButton(onClick = onRefreshSync) {
                                Icon(
                                    imageVector = Icons.Default.Refresh,
                                    contentDescription = "Sync Cloud Cadastre",
                                    tint = deepBlue
                                )
                            }
                        },
                        colors = TopAppBarDefaults.topAppBarColors(
                            containerColor = Color.Transparent
                        )
                    )
                },
                bottomBar = {
                    NavigationBar(
                        containerColor = DeepBasalt.copy(alpha = 0.96f),
                        tonalElevation = 8.dp
                    ) {
                        NavigationBarItem(
                            selected = true,
                            onClick = { /* Currently active on Cadastre / Home */ },
                            icon = { Icon(Icons.Default.Explore, contentDescription = "Cadastre Syllabus") },
                            label = { Text("Cadastre", fontSize = 10.sp, fontWeight = FontWeight.Bold) },
                            colors = NavigationBarItemDefaults.colors(
                                selectedIconColor = SunstoneGold,
                                selectedTextColor = SunstoneGold,
                                indicatorColor = SunstoneGold.copy(alpha = 0.2f),
                                unselectedIconColor = TopoContourMuted,
                                unselectedTextColor = TopoContourMuted
                            )
                        )
                        NavigationBarItem(
                            selected = false,
                            onClick = onPaperTwinClick,
                            icon = { Icon(Icons.Default.FlashOn, contentDescription = "Paper Twin Simulation") },
                            label = { Text("Paper Twin", fontSize = 10.sp, fontWeight = FontWeight.Medium) },
                            colors = NavigationBarItemDefaults.colors(
                                unselectedIconColor = TopoContourMuted,
                                unselectedTextColor = TopoContourMuted
                            )
                        )
                        NavigationBarItem(
                            selected = false,
                            onClick = onRevisionClick,
                            icon = { Icon(Icons.Default.Schedule, contentDescription = "Spaced Active Revision") },
                            label = { Text("Revision", fontSize = 10.sp, fontWeight = FontWeight.Medium) },
                            colors = NavigationBarItemDefaults.colors(
                                unselectedIconColor = TopoContourMuted,
                                unselectedTextColor = TopoContourMuted
                            )
                        )
                        NavigationBarItem(
                            selected = false,
                            onClick = onAnalyticsClick,
                            icon = { Icon(Icons.Default.Analytics, contentDescription = "Examiner Trap Radar") },
                            label = { Text("Traps", fontSize = 10.sp, fontWeight = FontWeight.Medium) },
                            colors = NavigationBarItemDefaults.colors(
                                unselectedIconColor = TopoContourMuted,
                                unselectedTextColor = TopoContourMuted
                            )
                        )
                        NavigationBarItem(
                            selected = false,
                            onClick = onBookmarksClick,
                            icon = { Icon(Icons.Default.Bookmark, contentDescription = "Saved Geographic Waypoints") },
                            label = { Text("Saved", fontSize = 10.sp, fontWeight = FontWeight.Medium) },
                            colors = NavigationBarItemDefaults.colors(
                                unselectedIconColor = TopoContourMuted,
                                unselectedTextColor = TopoContourMuted
                            )
                        )
                    }
                }
            ) { paddingValues ->
                if (topics.isEmpty()) {
                    Box(modifier = Modifier.fillMaxSize().padding(paddingValues), contentAlignment = Alignment.Center) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally,
                            verticalArrangement = Arrangement.Center,
                            modifier = Modifier.padding(32.dp)
                        ) {
                            CircularProgressIndicator(color = accentGold)
                            Spacer(modifier = Modifier.height(20.dp))
                            Text(
                                text = "Connecting to Geography Network...",
                                color = deepBlue,
                                fontWeight = FontWeight.Bold,
                                fontSize = 18.sp
                            )
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                text = "Synchronizing syllabus catalog & high-yield question streams.",
                                color = TopoContourMuted,
                                fontSize = 13.sp,
                                textAlign = androidx.compose.ui.text.style.TextAlign.Center
                            )
                            Spacer(modifier = Modifier.height(24.dp))
                            OutlinedButton(
                                onClick = onRefreshSync,
                                border = androidx.compose.foundation.BorderStroke(1.dp, accentGold),
                                shape = RoundedCornerShape(12.dp)
                            ) {
                                Text("Tap to Retry Cloud Stream 🔄", color = accentGold, fontWeight = FontWeight.Bold)
                            }
                        }
                    }
                } else {
                    LazyColumn(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(paddingValues)
                            .padding(horizontal = 16.dp),
                        contentPadding = PaddingValues(bottom = 24.dp),
                        verticalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        // ==========================================
                        // IN-APP OVER-THE-AIR (OTA) AUTO-UPDATE BANNER
                        // ==========================================
                        item {
                            com.example.ui.components.InAppUpdateBanner(
                                updateState = updateState,
                                onManualCheck = onCheckUpdate
                            )
                        }

                        // ==========================================
                        // SATELLITE GEODETIC CADASTRE HUD BANNER
                        // ==========================================
                        item {
                            Surface(
                                color = DeepBasalt,
                                shape = RoundedCornerShape(14.dp),
                                border = BorderStroke(1.dp, ContourEmerald.copy(alpha = 0.45f)),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 2.dp)
                                    .clickable { onRefreshSync() }
                            ) {
                                Row(
                                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Box(
                                            modifier = Modifier
                                                .size(10.dp)
                                                .clip(CircleShape)
                                                .background(if (isSyncing) SunstoneGold else ContourEmerald)
                                        )
                                        Spacer(modifier = Modifier.width(10.dp))
                                        Column {
                                            Text(
                                                text = if (isSyncing) "🛰️ SATELLITE CADASTRE STREAMING..." else "🛰️ SATELLITE GEODETIC CADASTRE",
                                                color = if (isSyncing) SunstoneGold else ContourEmerald,
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.Black,
                                                letterSpacing = 0.8.sp
                                            )
                                            val totalCount = topics.sumOf { it.availableCount }.let { if (it > 0) it else 3942 }
                                            Text(
                                                text = "Live Cloud Stream • %,d Field Waypoints (0 on Disk)".format(totalCount),
                                                color = TopoContourMuted,
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.Medium
                                            )
                                        }
                                    }
                                    Surface(
                                        color = if (isSyncing) SunstoneGold.copy(alpha = 0.15f) else ContourEmerald.copy(alpha = 0.15f),
                                        shape = RoundedCornerShape(6.dp)
                                    ) {
                                        Text(
                                            text = if (isSyncing) "SYNCING" else "ONLINE 🌐",
                                            color = if (isSyncing) SunstoneGold else ContourEmerald,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 10.sp,
                                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                        )
                                    }
                                }
                            }
                        }

                        // ==========================================
                        // EXPEDITION COMMAND HUB (PRIMARY QUICK ACCESS GRID)
                        // ==========================================
                        item {
                            Column(
                                modifier = Modifier.fillMaxWidth(),
                                verticalArrangement = Arrangement.spacedBy(8.dp)
                            ) {
                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    // 1. UPSC Paper Twin
                                    CommandHubCard(
                                        modifier = Modifier.weight(1f),
                                        icon = "🎯",
                                        title = "Paper Twin",
                                        subtitle = "Mock Exam DNA",
                                        tag = "SIMULATION",
                                        accentColor = SunstoneGold,
                                        onClick = onPaperTwinClick
                                    )

                                    // 2. Spaced Active Revision
                                    CommandHubCard(
                                        modifier = Modifier.weight(1f),
                                        icon = "🔄",
                                        title = "Active Revision",
                                        subtitle = "Spaced Recall Queue",
                                        tag = "SMART SRS",
                                        accentColor = HydrosphereCyan,
                                        onClick = onRevisionClick
                                    )
                                }

                                Row(
                                    modifier = Modifier.fillMaxWidth(),
                                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                                ) {
                                    // 3. Cognitive Trap Radar
                                    CommandHubCard(
                                        modifier = Modifier.weight(1f),
                                        icon = "⚠️",
                                        title = "Trap Radar",
                                        subtitle = "Examiner Biases",
                                        tag = "ANALYTICS",
                                        accentColor = MagmaCrimson,
                                        onClick = onAnalyticsClick
                                    )

                                    // 4. Blindspot & Insights Lab
                                    CommandHubCard(
                                        modifier = Modifier.weight(1f),
                                        icon = "🔬",
                                        title = "Blindspot Lab",
                                        subtitle = "AI Diagnostics",
                                        tag = "CALIBRATION",
                                        accentColor = ContourEmerald,
                                        onClick = onInsightsClick
                                    )
                                }

                                // 5. Mains Answer Architect (Chief Evaluator Portal) - STRICTLY FOR UPSC ASPIRANTS ONLY
                                val isUpsc = profile?.examId?.contains("UPSC", ignoreCase = true) == true
                                if (isUpsc) {
                                    CommandHubCard(
                                        modifier = Modifier.fillMaxWidth(),
                                        icon = "🏛️",
                                        title = "Mains Answer Architect",
                                        subtitle = "7m/11m/14m Timers • 20s Diagram Tracing • Infinite Chief Evaluator Scoring",
                                        tag = "300+ MAINS PORTAL",
                                        accentColor = SunstoneGold,
                                        onClick = onMainsPracticeClick
                                    )
                                } else {
                                    val isBpsc = profile?.examId?.contains("BPSC", ignoreCase = true) == true
                                    if (isBpsc) {
                                        CommandHubCard(
                                            modifier = Modifier.fillMaxWidth(),
                                            icon = "🌾",
                                            title = "State PCS Bihar Special Drills",
                                            subtitle = "Bihar Physiography • Drainage • Soils • High-Yield BPSC Focus",
                                            tag = "BPSC SPECIAL",
                                            accentColor = ContourEmerald,
                                            onClick = {
                                                onTopicSelected("Bihar Geography: Physiography, Rivers & Resources", "Medium", "Smart Practice")
                                            }
                                        )
                                    } else {
                                        CommandHubCard(
                                            modifier = Modifier.fillMaxWidth(),
                                            icon = "⚡",
                                            title = "Speed & Accuracy Sprint",
                                            subtitle = "CBT-1 Rapid Fire Mode • 100% Negative Marking Simulation",
                                            tag = "${profile?.displayName ?: "CBT"} SPRINT",
                                            accentColor = SunstoneGold,
                                            onClick = {
                                                onTopicSelected("Global", "Basic", "Speed + Accuracy")
                                            }
                                        )
                                    }
                                }
                            }
                        }

                        // ==========================================
                        // NEXT BEST ACTION RECOMMENDER CARD
                        // ==========================================
                        if (nextAction != null) {
                            item {
                                NextBestActionCard(
                                    action = nextAction,
                                    onTopicSelected = onTopicSelected,
                                    onRevisionClick = onRevisionClick,
                                    onAnalyticsClick = onAnalyticsClick
                                )
                            }
                        }

                        // ==========================================
                        // EXPEDITION STREAK & COMMAND HUD
                        // ==========================================
                        item {
                            Surface(
                                color = DeepBasalt,
                                shape = RoundedCornerShape(16.dp),
                                border = BorderStroke(1.dp, HydrosphereCyan.copy(alpha = 0.25f)),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 2.dp)
                            ) {
                                Row(
                                    modifier = Modifier.padding(14.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.SpaceBetween
                                ) {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Box(
                                            modifier = Modifier
                                                .size(40.dp)
                                                .clip(CircleShape)
                                                .background(SunstoneGold.copy(alpha = 0.15f)),
                                            contentAlignment = Alignment.Center
                                        ) {
                                            Text("🧭", fontSize = 20.sp)
                                        }
                                        Spacer(modifier = Modifier.width(10.dp))
                                        Column {
                                            Text(
                                                text = "FIELD EXPEDITION LOG",
                                                fontSize = 10.sp,
                                                fontWeight = FontWeight.Bold,
                                                color = SunstoneGold,
                                                letterSpacing = 0.8.sp
                                            )
                                            Text(
                                                text = "Day 5 Transect 🧭 (Top 3% Cartographer)",
                                                fontSize = 13.sp,
                                                fontWeight = FontWeight.ExtraBold,
                                                color = Color.White
                                            )
                                        }
                                    }
                                    Box(
                                        modifier = Modifier
                                            .clip(RoundedCornerShape(8.dp))
                                            .background(HydrosphereCyan.copy(alpha = 0.15f))
                                            .padding(horizontal = 8.dp, vertical = 4.dp)
                                    ) {
                                        Text(
                                            text = "SUMMIT READY ⛰️",
                                            fontSize = 10.sp,
                                            fontWeight = FontWeight.Bold,
                                            color = HydrosphereCyan
                                        )
                                    }
                                }
                            }
                        }

                        // ==========================================
                        // TARGET GOAL & HARDCORE MODE TOGGLE
                        // ==========================================
                        item {
                            Surface(
                                color = cardColor,
                                shadowElevation = 4.dp,
                                shape = RoundedCornerShape(16.dp),
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
                                                text = profile?.displayName ?: "UPSC CSE Prelims",
                                                fontSize = 16.sp,
                                                fontWeight = FontWeight.ExtraBold,
                                                color = deepBlue
                                            )
                                        }

                                        // Hardcore Mode Switch
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
                        }

                        // ==========================================
                        // SYLLABUS MODULE SECTIONS & CHAPTER CARDS
                        // ==========================================
                        val orderedModules = listOf(
                            "Physical Geography",
                            "Indian Geography",
                            "World & Human Geography",
                            "🎓 UPSC Geography Optional"
                        )
                        val allModules = (orderedModules + (groupedTopics.keys - orderedModules.toSet())).distinct()

                        allModules.forEach { moduleName ->
                            val moduleTopics = groupedTopics[moduleName]
                            if (moduleTopics != null && moduleTopics.isNotEmpty()) {
                                item {
                                    val isExpanded = expandedStates[moduleName] != false
                                    val totalModuleQuestions = moduleTopics.sumOf { it.availableCount }
                                    val isOptionalModule = moduleName.contains("Optional")

                                    // Module Header Accordion
                                    Surface(
                                        color = if (isOptionalModule) deepBlue.copy(alpha = 0.95f) else deepBlue,
                                        shape = RoundedCornerShape(12.dp),
                                        border = if (isOptionalModule) androidx.compose.foundation.BorderStroke(1.dp, SunstoneGold.copy(alpha = 0.7f)) else null,
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .clickable { expandedStates[moduleName] = !isExpanded }
                                    ) {
                                        Row(
                                            modifier = Modifier.padding(16.dp),
                                            verticalAlignment = Alignment.CenterVertically,
                                            horizontalArrangement = Arrangement.SpaceBetween
                                        ) {
                                            Column {
                                                Row(verticalAlignment = Alignment.CenterVertically) {
                                                    Text(
                                                        text = moduleName,
                                                        color = if (isOptionalModule) SummitGold else Color.White,
                                                        fontWeight = FontWeight.Bold,
                                                        fontSize = 17.sp
                                                    )
                                                    if (isOptionalModule) {
                                                        Spacer(modifier = Modifier.width(8.dp))
                                                        Surface(
                                                            color = SummitGold.copy(alpha = 0.2f),
                                                            shape = RoundedCornerShape(4.dp)
                                                        ) {
                                                            Text(
                                                                text = "ADVANCED MAINS",
                                                                color = SummitGold,
                                                                fontSize = 9.sp,
                                                                fontWeight = FontWeight.ExtraBold,
                                                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                                            )
                                                        }
                                                    }
                                                }
                                                Text(
                                                    text = if (isOptionalModule)
                                                        "${moduleTopics.size} Specialized Papers • $totalModuleQuestions Master MCQs"
                                                    else
                                                        "${moduleTopics.size} Chapters • $totalModuleQuestions MCQs",
                                                    color = if (isOptionalModule) GlacierAzure else SunstoneGold,
                                                    fontWeight = FontWeight.Medium,
                                                    fontSize = 11.sp
                                                )
                                            }
                                            Icon(
                                                imageVector = if (isExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                                                contentDescription = "Toggle",
                                                tint = Color.White
                                            )
                                        }
                                    }

                                    // Module Chapter Cards
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
                                                            profile?.allowedTiers?.lastOrNull() ?: "Hard"
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

    if (showExamSwitcherDialog) {
        AlertDialog(
            onDismissRequest = { showExamSwitcherDialog = false },
            containerColor = DeepBasalt,
            title = {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("🧭", fontSize = 22.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Column {
                        Text(
                            "Target Commission Calibration",
                            fontFamily = CartographicSerif,
                            fontWeight = FontWeight.Bold,
                            fontSize = 17.sp,
                            color = SunstoneGold
                        )
                        Text(
                            "Switch active curriculum transect & syllabus",
                            fontSize = 11.sp,
                            color = TopoContourMuted
                        )
                    }
                }
            },
            text = {
                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 4.dp),
                    verticalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    val displayList = if (allSelectedProfiles.isNotEmpty()) allSelectedProfiles else listOfNotNull(profile)
                    displayList.forEach { bp ->
                        val isActive = bp.examId == profile?.examId
                        Surface(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable {
                                    onSelectActiveProfile(bp)
                                    showExamSwitcherDialog = false
                                },
                            shape = RoundedCornerShape(12.dp),
                            color = if (isActive) SunstoneGold.copy(alpha = 0.12f) else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
                            border = BorderStroke(
                                1.5.dp,
                                if (isActive) SunstoneGold else TopoContourMuted.copy(alpha = 0.3f)
                            )
                        ) {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(12.dp),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Column(modifier = Modifier.weight(1f)) {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Text(
                                            text = bp.displayName,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 13.sp,
                                            color = if (isActive) SunstoneGold else Color.White
                                        )
                                        if (isActive) {
                                            Spacer(modifier = Modifier.width(6.dp))
                                            Surface(
                                                color = ContourEmerald.copy(alpha = 0.2f),
                                                shape = RoundedCornerShape(4.dp)
                                            ) {
                                                Text(
                                                    text = "ACTIVE",
                                                    color = ContourEmerald,
                                                    fontSize = 9.sp,
                                                    fontWeight = FontWeight.ExtraBold,
                                                    modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                                                )
                                            }
                                        }
                                    }
                                    Spacer(modifier = Modifier.height(3.dp))
                                    Text(
                                        text = bp.recommendedPracticeMode,
                                        fontSize = 10.sp,
                                        color = TopoContourMuted,
                                        maxLines = 2,
                                        overflow = TextOverflow.Ellipsis
                                    )
                                }
                                Icon(
                                    imageVector = if (isActive) Icons.Default.CheckCircle else Icons.Default.RadioButtonUnchecked,
                                    contentDescription = null,
                                    tint = if (isActive) SunstoneGold else TopoContourMuted.copy(alpha = 0.6f),
                                    modifier = Modifier.size(20.dp)
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(4.dp))
                    OutlinedButton(
                        onClick = {
                            showExamSwitcherDialog = false
                            onChangeExam()
                        },
                        modifier = Modifier.fillMaxWidth(),
                        shape = RoundedCornerShape(10.dp),
                        border = BorderStroke(1.dp, GlacierAzure.copy(alpha = 0.6f))
                    ) {
                        Icon(
                            imageVector = Icons.Default.AddCircleOutline,
                            contentDescription = null,
                            tint = GlacierAzure,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Add / Change Selected Exams",
                            color = GlacierAzure,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            },
            confirmButton = {
                TextButton(onClick = { showExamSwitcherDialog = false }) {
                    Text("Close", color = TopoContourMuted, fontWeight = FontWeight.Bold)
                }
            }
        )
    }
}

/**
 * Command Hub Card for High-Impact Direct Destination Access
 */
@Composable
fun CommandHubCard(
    modifier: Modifier = Modifier,
    icon: String,
    title: String,
    subtitle: String,
    tag: String,
    accentColor: Color,
    onClick: () -> Unit
) {
    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, accentColor.copy(alpha = 0.35f)),
        modifier = modifier.clickable { onClick() }
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(text = icon, fontSize = 20.sp)
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(4.dp))
                        .background(accentColor.copy(alpha = 0.15f))
                        .padding(horizontal = 6.dp, vertical = 2.dp)
                ) {
                    Text(
                        text = tag,
                        color = accentColor,
                        fontSize = 9.sp,
                        fontFamily = CoordinatesMonospace,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = title,
                fontFamily = CartographicSerif,
                fontWeight = FontWeight.Bold,
                fontSize = 14.sp,
                color = Color.White,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )

            Text(
                text = subtitle,
                fontSize = 11.sp,
                color = TopoContourMuted,
                maxLines = 1,
                overflow = TextOverflow.Ellipsis
            )
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
    val isOptionalTopic = item.topic.module.contains("Optional")

    // Extract authentic leading emoji from topic name if present, else resolve via comprehensive mapping
    val leadingEmojiMatch = Regex("^[\\p{So}\\p{Sk}\\p{Sm}\\p{Sc}]").find(item.topic.name.trim())
    val topicIcon = if (leadingEmojiMatch != null) {
        leadingEmojiMatch.value
    } else when {
        item.topic.name.contains("Universe", ignoreCase = true) || item.topic.name.contains("Solar", ignoreCase = true) -> "🌌"
        item.topic.name.contains("Globe", ignoreCase = true) || item.topic.name.contains("Latitude", ignoreCase = true) -> "🌐"
        item.topic.name.contains("Map", ignoreCase = true) || item.topic.name.contains("GIS", ignoreCase = true) -> "🗺️"
        item.topic.name.contains("Interior", ignoreCase = true) || item.topic.name.contains("Plate Tectonics", ignoreCase = true) -> "🌋"
        item.topic.name.contains("Geomorphic", ignoreCase = true) || item.topic.name.contains("Landforms", ignoreCase = true) || item.topic.name.contains("Geomorphology", ignoreCase = true) -> "⛰️"
        item.topic.name.contains("Atmosphere", ignoreCase = true) || item.topic.name.contains("Wind", ignoreCase = true) || item.topic.name.contains("Climate Systems", ignoreCase = true) -> "🌪️"
        item.topic.name.contains("Oceanography", ignoreCase = true) || item.topic.name.contains("Ocean", ignoreCase = true) -> "🌊"
        item.topic.name.contains("Biogeography", ignoreCase = true) || item.topic.name.contains("Ecosystem", ignoreCase = true) -> "🌿"
        item.topic.name.contains("Neighbours", ignoreCase = true) || item.topic.name.contains("Location", ignoreCase = true) -> "🇮🇳"
        item.topic.name.contains("Physiography", ignoreCase = true) -> "🏔️"
        item.topic.name.contains("Drainage", ignoreCase = true) || item.topic.name.contains("River", ignoreCase = true) -> "🏞️"
        item.topic.name.contains("Monsoon", ignoreCase = true) || item.topic.name.contains("Indian Climate", ignoreCase = true) -> "🌧️"
        item.topic.name.contains("Soil", ignoreCase = true) || item.topic.name.contains("Vegetation", ignoreCase = true) -> "🌱"
        item.topic.name.contains("Wildlife", ignoreCase = true) || item.topic.name.contains("Conservation", ignoreCase = true) -> "🐅"
        item.topic.name.contains("Agriculture", ignoreCase = true) -> "🌾"
        item.topic.name.contains("Water Resources", ignoreCase = true) || item.topic.name.contains("Dams", ignoreCase = true) -> "💧"
        item.topic.name.contains("Minerals", ignoreCase = true) || item.topic.name.contains("Energy", ignoreCase = true) -> "⛏️"
        item.topic.name.contains("Industries", ignoreCase = true) -> "🏭"
        item.topic.name.contains("Transport", ignoreCase = true) || item.topic.name.contains("Trade", ignoreCase = true) -> "🚆"
        item.topic.name.contains("Population", ignoreCase = true) || item.topic.name.contains("Settlement", ignoreCase = true) -> "👥"
        item.topic.name.contains("Human Development", ignoreCase = true) -> "📈"
        item.topic.name.contains("World Regional", ignoreCase = true) -> "🗺️"
        item.topic.name.contains("Bihar", ignoreCase = true) -> "📍"
        item.topic.name.contains("Perspectives", ignoreCase = true) || item.topic.name.contains("Thought", ignoreCase = true) -> "🧠"
        item.topic.name.contains("Models", ignoreCase = true) || item.topic.name.contains("Theories", ignoreCase = true) || item.topic.name.contains("Laws", ignoreCase = true) -> "📐"
        item.topic.name.contains("Regional Planning", ignoreCase = true) || item.topic.name.contains("Regionalisation", ignoreCase = true) -> "🗺️"
        item.topic.name.contains("Cultural Setting", ignoreCase = true) -> "👥"
        item.topic.name.contains("Political Aspects", ignoreCase = true) -> "🏛️"
        else -> "📍"
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick),
        colors = CardDefaults.cardColors(containerColor = cardColor),
        elevation = CardDefaults.cardElevation(defaultElevation = if (isOptionalTopic) 4.dp else 3.dp),
        border = BorderStroke(
            1.dp,
            if (isOptionalTopic) SunstoneGold.copy(alpha = 0.5f) else SlateBedrock.copy(alpha = 0.5f)
        ),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Geographic Avatar Circle
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .background(
                        if (isZeroAvailable) Color.LightGray.copy(alpha = 0.2f)
                        else if (isOptionalTopic) SunstoneGold.copy(alpha = 0.15f)
                        else OceanicDark.copy(alpha = 0.6f),
                        CircleShape
                    ),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = topicIcon,
                    fontSize = 22.sp
                )
            }

            Spacer(modifier = Modifier.width(14.dp))

            Column(modifier = Modifier.weight(1f)) {
                // Strip redundant leading emoji from topic name if present to avoid duplicate emoji
                val cleanedName = remember(item.topic.name) {
                    item.topic.name.replace(Regex("^[\\p{So}\\p{Sk}\\p{Sm}\\p{Sc}\\s]+"), "").trim()
                }
                Text(
                    text = if (cleanedName.isNotEmpty()) cleanedName else item.topic.name,
                    fontFamily = CartographicSerif,
                    fontWeight = FontWeight.Bold,
                    color = if (isZeroAvailable) Color.Gray else deepBlue,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    fontSize = 16.sp,
                    lineHeight = 21.sp
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
                        text = if (isOptionalTopic) {
                            "🎓 ${item.availableCount} Master MCQs • Optional Paper: CH${item.topic.id}"
                        } else {
                            "📍 ${item.availableCount} Field MCQs • Lat: CH${item.topic.id}"
                        },
                        style = MaterialTheme.typography.bodySmall,
                        fontFamily = CoordinatesMonospace,
                        fontWeight = FontWeight.Medium,
                        color = if (isZeroAvailable) accentGold else if (isOptionalTopic) SummitGold else deepBlue.copy(alpha = 0.7f),
                        fontSize = 11.sp
                    )
                }
            }

            Spacer(modifier = Modifier.width(8.dp))

            // Expected Difficulty Indicator
            val activeTier = if (isHardcoreMode) profile?.allowedTiers?.lastOrNull() else profile?.allowedTiers?.firstOrNull()
            if (activeTier != null) {
                com.example.ui.components.ElevationTierPill(tier = activeTier)
            }
        }
    }
}
