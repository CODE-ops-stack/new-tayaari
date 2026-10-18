package com.example.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.expandVertically
import androidx.compose.animation.shrinkVertically
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.foundation.gestures.detectTapGestures
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
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.R
import com.example.model.ExamBlueprint
import com.example.repository.AppThemeMode
import com.example.repository.FontScaleOption
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
    syncStatusMessage: String = "Online Stream (v${com.example.BuildConfig.VERSION_NAME} • 5,551 MCQs) • Zero Local Asset",
    updateState: com.example.updater.AppUpdateManager.UpdateState = com.example.updater.AppUpdateManager.UpdateState.Idle,
    themeMode: AppThemeMode = AppThemeMode.DARK,
    onThemeModeChange: (AppThemeMode) -> Unit = {},
    fontScaleOption: FontScaleOption = FontScaleOption.NORMAL,
    onFontScaleOptionChange: (FontScaleOption) -> Unit = {},
    isZenMode: Boolean = false,
    onZenModeChange: (Boolean) -> Unit = {},
    dailyTarget: Int = 20,
    onDailyTargetChange: (Int) -> Unit = {},
    todaySolvedCount: Int = 0,
    onTopicSelected: (topicName: String, tier: String, format: String) -> Unit,
    onBookmarksClick: () -> Unit = {},
    onAnalyticsClick: () -> Unit = {},
    onRevisionClick: () -> Unit = {},
    onPaperTwinClick: () -> Unit = {},
    onReadinessClick: () -> Unit = {},
    onMainsPracticeClick: () -> Unit = {},
    onChangeExam: () -> Unit = {},
    onRefreshSync: () -> Unit = {},
    onCheckUpdate: () -> Unit = {},
    onInvestorPreviewClick: () -> Unit = {},
    onRoadmapClick: () -> Unit = {}
) {
    val surfaceColor = MaterialTheme.colorScheme.surface
    val cardColor = MaterialTheme.colorScheme.background
    val deepBlue = MaterialTheme.colorScheme.primary
    val warningRed = MaterialTheme.colorScheme.error
    val accentGold = MaterialTheme.colorScheme.tertiary

    var isHardcoreMode by remember { mutableStateOf(false) }
    var showExamSwitcherDialog by remember { mutableStateOf(false) }
    var showSettingsDialog by remember { mutableStateOf(false) }
    var searchQuery by remember { mutableStateOf("") }

    // Group topics by module, filtering by search query if present
    val filteredTopics = remember(topics, searchQuery) {
        if (searchQuery.isBlank()) {
            topics
        } else {
            val q = searchQuery.trim().lowercase()
            topics.filter {
                it.topic.name.lowercase().contains(q) ||
                it.topic.module.lowercase().contains(q)
            }
        }
    }

    val groupedTopics = remember(filteredTopics) {
        filteredTopics.groupBy { it.topic.module }
    }

    // Expand all modules by default so all 30 chapters are visible immediately
    val expandedStates = remember { mutableStateMapOf<String, Boolean>() }
    var selectedPhysiographyFilter by remember { mutableStateOf("ALL") }
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
                                        "Civil Services Geography Cadastre • v${com.example.BuildConfig.VERSION_NAME}",
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

                            // Aspirant Field Ergonomics Settings Shortcut
                            IconButton(onClick = { showSettingsDialog = true }) {
                                Icon(
                                    imageVector = Icons.Default.Settings,
                                    contentDescription = "Aspirant Field Ergonomics",
                                    tint = SunstoneGold
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
                            onClick = onRoadmapClick,
                            icon = { Icon(Icons.Default.Psychology, contentDescription = "Master Roadmap") },
                            label = { Text("Roadmap", fontSize = 10.sp, fontWeight = FontWeight.Bold) },
                            colors = NavigationBarItemDefaults.colors(
                                unselectedIconColor = HydrosphereCyan,
                                unselectedTextColor = HydrosphereCyan,
                                indicatorColor = HydrosphereCyan.copy(alpha = 0.15f)
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
                        NavigationBarItem(
                            selected = false,
                            onClick = onInvestorPreviewClick,
                            icon = { Icon(Icons.Default.Star, contentDescription = "Expert Preview") },
                            label = { Text("Preview", fontSize = 10.sp, fontWeight = FontWeight.Bold) },
                            colors = NavigationBarItemDefaults.colors(
                                unselectedIconColor = SunstoneGold,
                                unselectedTextColor = SunstoneGold,
                                indicatorColor = SunstoneGold.copy(alpha = 0.15f)
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
                        // ZERO-TO-HERO MASTER ROADMAP HERO BANNER
                        // ==========================================
                        item {
                            Surface(
                                color = DeepBasalt,
                                shape = RoundedCornerShape(16.dp),
                                border = BorderStroke(1.5.dp, SunstoneGold.copy(alpha = 0.8f)),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .clickable { onRoadmapClick() }
                            ) {
                                Column(modifier = Modifier.padding(14.dp)) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.SpaceBetween
                                    ) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Surface(
                                                color = SunstoneGold.copy(alpha = 0.2f),
                                                shape = RoundedCornerShape(8.dp)
                                            ) {
                                                Text(
                                                    text = "🗺️ ZERO-TO-HERO",
                                                    color = SunstoneGold,
                                                    fontSize = 10.sp,
                                                    fontWeight = FontWeight.Black,
                                                    letterSpacing = 0.8.sp,
                                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                                )
                                            }
                                            Spacer(modifier = Modifier.width(8.dp))
                                            Surface(
                                                color = ContourEmerald.copy(alpha = 0.2f),
                                                shape = RoundedCornerShape(8.dp)
                                            ) {
                                                Text(
                                                    text = "90%+ BLUEPRINT",
                                                    color = ContourEmerald,
                                                    fontSize = 10.sp,
                                                    fontWeight = FontWeight.Black,
                                                    letterSpacing = 0.8.sp,
                                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                                )
                                            }
                                        }
                                        Icon(
                                            imageVector = Icons.Default.Explore,
                                            contentDescription = null,
                                            tint = SunstoneGold,
                                            modifier = Modifier.size(18.dp)
                                        )
                                    }

                                    Spacer(modifier = Modifier.height(10.dp))

                                    Text(
                                        text = "The One-Stop NCERT Chapter Study Order",
                                        color = AtlasParchment,
                                        fontSize = 15.sp,
                                        fontWeight = FontWeight.Black
                                    )
                                    Spacer(modifier = Modifier.height(3.dp))
                                    Text(
                                        text = "Not a random quiz app. Follow our verified 4-stage pedagogical sequence (Physical ➔ Indian ➔ Economic ➔ Maps) to complete your syllabus chapter-by-chapter.",
                                        color = TopoContourMuted,
                                        fontSize = 11.5.sp,
                                        lineHeight = 16.sp
                                    )

                                    Spacer(modifier = Modifier.height(12.dp))

                                    Button(
                                        onClick = onRoadmapClick,
                                        colors = ButtonDefaults.buttonColors(containerColor = SunstoneGold),
                                        shape = RoundedCornerShape(10.dp),
                                        modifier = Modifier.fillMaxWidth()
                                    ) {
                                        Text(
                                            text = "Open Interactive Roadmap & Chapter Sequence ➔",
                                            color = AbyssNavy,
                                            fontWeight = FontWeight.Black,
                                            fontSize = 12.sp
                                        )
                                    }
                                }
                            }
                        }

                        // ==========================================
                        // PRELIMS COUNTDOWN & DAILY TARGET QUOTA HUD CARD
                        // ==========================================
                        item {
                            val (examName, daysLeft, examCenter) = getExamCountdownInfo(profile?.examId)
                            val quotaProgress = (todaySolvedCount.toFloat() / dailyTarget.coerceAtLeast(1).toFloat()).coerceIn(0f, 1f)

                            Surface(
                                color = DeepBasalt,
                                shape = RoundedCornerShape(16.dp),
                                border = BorderStroke(1.dp, SunstoneGold.copy(alpha = 0.5f)),
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 2.dp)
                            ) {
                                Column(modifier = Modifier.padding(14.dp)) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.SpaceBetween
                                    ) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Text("⏳", fontSize = 16.sp)
                                            Spacer(modifier = Modifier.width(6.dp))
                                            Column {
                                                Text(
                                                    text = examName,
                                                    color = SunstoneGold,
                                                    fontSize = 12.sp,
                                                    fontWeight = FontWeight.Bold
                                                )
                                                Text(
                                                    text = examCenter,
                                                    color = TopoContourMuted,
                                                    fontSize = 9.sp,
                                                    fontWeight = FontWeight.Medium,
                                                    letterSpacing = 0.6.sp
                                                )
                                            }
                                        }
                                        Surface(
                                            color = MagmaCrimson.copy(alpha = 0.2f),
                                            shape = RoundedCornerShape(8.dp),
                                            border = BorderStroke(1.dp, MagmaCrimson.copy(alpha = 0.4f))
                                        ) {
                                            Text(
                                                text = "$daysLeft DAYS REMAINING",
                                                color = Color(0xFFFF6B6B),
                                                fontWeight = FontWeight.Black,
                                                fontSize = 11.sp,
                                                letterSpacing = 0.6.sp,
                                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                            )
                                        }
                                    }

                                    Spacer(modifier = Modifier.height(12.dp))
                                    HorizontalDivider(color = TopoContourMuted.copy(alpha = 0.2f), thickness = 1.dp)
                                    Spacer(modifier = Modifier.height(10.dp))

                                    // Daily Quota Progress
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.SpaceBetween
                                    ) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Text("🎯", fontSize = 14.sp)
                                            Spacer(modifier = Modifier.width(6.dp))
                                            Text(
                                                text = "Today's Target Quota",
                                                color = Color.White,
                                                fontSize = 11.sp,
                                                fontWeight = FontWeight.SemiBold
                                            )
                                        }
                                        Text(
                                            text = "$todaySolvedCount / $dailyTarget MCQs Solved",
                                            color = if (todaySolvedCount >= dailyTarget) ContourEmerald else SunstoneGold,
                                            fontSize = 11.sp,
                                            fontWeight = FontWeight.Bold
                                        )
                                    }

                                    Spacer(modifier = Modifier.height(8.dp))

                                    // Progress bar
                                    LinearProgressIndicator(
                                        progress = { quotaProgress },
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .height(6.dp)
                                            .clip(RoundedCornerShape(3.dp)),
                                        color = if (todaySolvedCount >= dailyTarget) ContourEmerald else SunstoneGold,
                                        trackColor = DeepBasalt.copy(alpha = 0.8f)
                                    )

                                    Spacer(modifier = Modifier.height(8.dp))

                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.SpaceBetween
                                    ) {
                                        Text(
                                            text = if (todaySolvedCount >= dailyTarget) "🎉 Daily target achieved! Unstoppable discipline." else "💡 1 question every morning builds civil services rank.",
                                            color = if (todaySolvedCount >= dailyTarget) ContourEmerald else TopoContourMuted,
                                            fontSize = 10.sp,
                                            fontWeight = FontWeight.Medium
                                        )
                                        TextButton(
                                            onClick = { showSettingsDialog = true },
                                            contentPadding = PaddingValues(0.dp),
                                            modifier = Modifier.height(24.dp)
                                        ) {
                                            Text(
                                                text = "Customize Target ⚙️",
                                                color = HydrosphereCyan,
                                                fontSize = 10.sp,
                                                fontWeight = FontWeight.Bold
                                            )
                                        }
                                    }
                                }
                            }
                        }

                        // ==========================================
                        // DAILY GEOGRAPHIC MYSTERY / CURIOSITY HOOK
                        // ==========================================
                        item {
                            val mysteries = remember {
                                listOf(
                                    Triple(
                                        "🌊 THE ATACAMA PARADOX",
                                        "Why is the Atacama Desert on the Pacific Ocean the driest non-polar desert on Earth, despite sitting next to millions of square miles of ocean water?",
                                        "🌧️ Indian Climate & Monsoon" to "🌧️ Indian Climate & Monsoon"
                                    ),
                                    Triple(
                                        "⚡ THE REVERSING RIVERS",
                                        "Why do Narmada and Tapi flow West into the Arabian Sea while Godavari, Krishna, and Mahanadi flow East to build massive deltas?",
                                        "🏞️ Drainage System of India" to "🏞️ Drainage System of India"
                                    ),
                                    Triple(
                                        "🌧️ THE CHERRAPUNJI ENIGMA",
                                        "Why does Cherrapunji receive 11,000 mm of rain while Shillong just 50 km away on the plateau receives less than 2,000 mm?",
                                        "🌧️ Indian Climate & Monsoon" to "🌧️ Indian Climate & Monsoon"
                                    ),
                                    Triple(
                                        "🌋 THE TECTONIC SHADOW",
                                        "Why do seismic S-waves abruptly vanish at 2,900 km depth, proving the Earth's outer core is a boiling sea of molten iron?",
                                        "🌋 Earth's Interior, Rocks & Plate Tectonics" to "🌋 Earth's Interior, Rocks & Plate Tectonics"
                                    )
                                )
                            }
                            var activeMysteryIdx by remember { mutableIntStateOf(0) }
                            val currentMystery = mysteries[activeMysteryIdx % mysteries.size]

                            Surface(
                                color = OceanicDark,
                                shape = RoundedCornerShape(14.dp),
                                border = BorderStroke(1.dp, HydrosphereCyan.copy(alpha = 0.5f)),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Column(modifier = Modifier.padding(14.dp)) {
                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.SpaceBetween
                                    ) {
                                        Row(verticalAlignment = Alignment.CenterVertically) {
                                            Text(text = "🔍", fontSize = 14.sp)
                                            Spacer(modifier = Modifier.width(6.dp))
                                            Text(
                                                text = currentMystery.first,
                                                color = HydrosphereCyan,
                                                fontSize = 10.5.sp,
                                                fontWeight = FontWeight.Black,
                                                letterSpacing = 0.8.sp
                                            )
                                        }
                                        Text(
                                            text = "Next Mystery ❯",
                                            color = TopoContourMuted,
                                            fontSize = 10.sp,
                                            fontWeight = FontWeight.Bold,
                                            modifier = Modifier.clickable { activeMysteryIdx = (activeMysteryIdx + 1) % mysteries.size }
                                        )
                                    }

                                    Spacer(modifier = Modifier.height(6.dp))

                                    Text(
                                        text = currentMystery.second,
                                        color = AtlasParchment,
                                        fontSize = 12.sp,
                                        lineHeight = 17.sp,
                                        fontWeight = FontWeight.Medium
                                    )

                                    Spacer(modifier = Modifier.height(10.dp))

                                    Row(
                                        modifier = Modifier.fillMaxWidth(),
                                        verticalAlignment = Alignment.CenterVertically,
                                        horizontalArrangement = Arrangement.SpaceBetween
                                    ) {
                                        Surface(
                                            color = HydrosphereCyan.copy(alpha = 0.15f),
                                            shape = RoundedCornerShape(6.dp)
                                        ) {
                                            Text(
                                                text = "Curiosity Drill",
                                                color = HydrosphereCyan,
                                                fontSize = 9.sp,
                                                fontWeight = FontWeight.Bold,
                                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                            )
                                        }

                                        TextButton(
                                            onClick = {
                                                onTopicSelected(currentMystery.third.first, "Basic", "All")
                                            },
                                            contentPadding = PaddingValues(horizontal = 10.dp, vertical = 4.dp)
                                        ) {
                                            Text(
                                                text = "Solve This Mystery ➔",
                                                color = SunstoneGold,
                                                fontWeight = FontWeight.Bold,
                                                fontSize = 11.5.sp
                                            )
                                        }
                                    }
                                }
                            }
                        }

                        // ==========================================
                        // SUMMIT ASCENT EXPEDITION PROGRESS STRIP
                        // ==========================================
                        item {
                            val totalCount = topics.sumOf { it.availableCount }.let { if (it > 0) it else 5551 }
                            SummitAscentProgressStrip(
                                totalQuestions = totalCount,
                                profile = profile
                            )
                        }

                        // ==========================================
                        // CADRE FIRE // TOPPER & LEADER INSPIRATION
                        // ==========================================
                        item {
                            DailyFireTopperWidget(profile = profile)
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
                        // CADRE MEDAL TROPHY SHOWCASE
                        // ==========================================
                        item {
                            CadreMedalTrophyShowcase(profile = profile)
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
                        // ==========================================
                        // INSTANT CADRE CHAPTER SEARCH BAR
                        // ==========================================
                        item {
                            OutlinedTextField(
                                value = searchQuery,
                                onValueChange = { searchQuery = it },
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(vertical = 4.dp),
                                placeholder = {
                                    Text(
                                        "🔍 Search 30 chapters (e.g. Monsoon, Soils, Rocks)...",
                                        color = TopoContourMuted,
                                        fontSize = 12.5.sp
                                    )
                                },
                                leadingIcon = {
                                    Icon(
                                        imageVector = Icons.Default.Search,
                                        contentDescription = "Search",
                                        tint = SunstoneGold
                                    )
                                },
                                trailingIcon = {
                                    if (searchQuery.isNotEmpty()) {
                                        IconButton(onClick = { searchQuery = "" }) {
                                            Icon(
                                                imageVector = Icons.Default.Clear,
                                                contentDescription = "Clear",
                                                tint = TopoContourMuted
                                            )
                                        }
                                    }
                                },
                                singleLine = true,
                                shape = RoundedCornerShape(12.dp),
                                colors = OutlinedTextFieldDefaults.colors(
                                    focusedBorderColor = SunstoneGold,
                                    unfocusedBorderColor = TopoContourMuted.copy(alpha = 0.4f),
                                    focusedTextColor = if (themeMode == AppThemeMode.LIGHT) Color(0xFF0F172A) else Color.White,
                                    unfocusedTextColor = if (themeMode == AppThemeMode.LIGHT) Color(0xFF0F172A) else Color.White,
                                    focusedContainerColor = if (themeMode == AppThemeMode.LIGHT) Color(0xFFFFFFFF) else DeepBasalt,
                                    unfocusedContainerColor = if (themeMode == AppThemeMode.LIGHT) Color(0xFFFFFFFF) else DeepBasalt
                                )
                            )
                        }

                        if (filteredTopics.isEmpty()) {
                            item {
                                Surface(
                                    color = DeepBasalt,
                                    shape = RoundedCornerShape(14.dp),
                                    border = BorderStroke(1.dp, TopoContourMuted.copy(alpha = 0.3f)),
                                    modifier = Modifier.fillMaxWidth().padding(vertical = 16.dp)
                                ) {
                                    Column(
                                        modifier = Modifier.padding(20.dp),
                                        horizontalAlignment = Alignment.CenterHorizontally
                                    ) {
                                        Text("🔍", fontSize = 28.sp)
                                        Spacer(modifier = Modifier.height(8.dp))
                                        Text(
                                            text = "No chapters found matching \"$searchQuery\"",
                                            color = Color.White,
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 14.sp
                                        )
                                        Spacer(modifier = Modifier.height(4.dp))
                                        Text(
                                            text = "Try searching for Monsoon, Drainage, Rocks, Agriculture, or Census",
                                            color = TopoContourMuted,
                                            fontSize = 11.sp,
                                            textAlign = TextAlign.Center
                                        )
                                        Spacer(modifier = Modifier.height(12.dp))
                                        OutlinedButton(
                                            onClick = { searchQuery = "" },
                                            border = BorderStroke(1.dp, SunstoneGold),
                                            shape = RoundedCornerShape(8.dp)
                                        ) {
                                            Text("Clear Search & Show All Chapters", color = SunstoneGold, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                                        }
                                    }
                                }
                            }
                        }

                        // ==========================================
                        // INTERACTIVE INDIA PHYSIOGRAPHY MAP SELECTOR
                        // ==========================================
                        item {
                            IndiaPhysiographyMapSelector(
                                selectedZone = selectedPhysiographyFilter,
                                onZoneSelected = { selectedPhysiographyFilter = it }
                            )
                        }

                        allModules.forEach { moduleName ->
                            val rawTopics = groupedTopics[moduleName]
                            val moduleTopics = if (rawTopics == null || selectedPhysiographyFilter == "ALL") rawTopics
                            else {
                                rawTopics.filter { item ->
                                    val name = item.topic.name.lowercase()
                                    when (selectedPhysiographyFilter) {
                                        "HIMALAYAS" -> name.contains("physiography") || name.contains("interior") || name.contains("landforms") || name.contains("geomorphic")
                                        "PLAINS" -> name.contains("plain") || name.contains("soil") || name.contains("vegetation") || name.contains("agriculture")
                                        "PLATEAU" -> name.contains("plateau") || name.contains("minerals") || name.contains("energy") || name.contains("industries")
                                        "COASTS" -> name.contains("location") || name.contains("neighbours") || name.contains("ocean") || name.contains("coastal")
                                        "RIVERS" -> name.contains("drainage") || name.contains("water") || name.contains("climate") || name.contains("monsoon")
                                        else -> true
                                    }
                                }
                            }
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

    if (showSettingsDialog) {
        AspirantSettingsDialog(
            themeMode = themeMode,
            onThemeModeChange = onThemeModeChange,
            fontScaleOption = fontScaleOption,
            onFontScaleOptionChange = onFontScaleOptionChange,
            isZenMode = isZenMode,
            onZenModeChange = onZenModeChange,
            dailyTarget = dailyTarget,
            onDailyTargetChange = onDailyTargetChange,
            onDismiss = { showSettingsDialog = false }
        )
    }
}

fun getExamCountdownInfo(examId: String?): Triple<String, Int, String> {
    val (name, targetDateStr, badge) = when {
        examId?.contains("BPSC", ignoreCase = true) == true -> Triple("BPSC 72nd CCE", "2026-12-13", "BPSC PATNA")
        examId?.contains("SSC", ignoreCase = true) == true -> Triple("SSC CGL Tier 1", "2026-09-15", "SSC NEW DELHI")
        examId?.contains("RRB", ignoreCase = true) == true -> Triple("RRB NTPC CBT", "2026-11-10", "RAILWAYS CEN")
        else -> Triple("UPSC CSE Prelims 2026", "2026-05-24", "DHOLPUR HOUSE")
    }
    val diffDays = try {
        val sdf = java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.US)
        val targetTime = sdf.parse(targetDateStr)?.time ?: System.currentTimeMillis()
        val now = System.currentTimeMillis()
        ((targetTime - now) / (1000 * 60 * 60 * 24)).toInt().coerceAtLeast(0)
    } catch (e: Exception) {
        180
    }
    return Triple(name, diffDays, badge)
}

@Composable
fun AspirantSettingsDialog(
    themeMode: AppThemeMode,
    onThemeModeChange: (AppThemeMode) -> Unit,
    fontScaleOption: FontScaleOption,
    onFontScaleOptionChange: (FontScaleOption) -> Unit,
    isZenMode: Boolean,
    onZenModeChange: (Boolean) -> Unit,
    dailyTarget: Int,
    onDailyTargetChange: (Int) -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = DeepBasalt,
        title = {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("⚙️", fontSize = 22.sp)
                Spacer(modifier = Modifier.width(8.dp))
                Column {
                    Text(
                        text = "Aspirant Field Ergonomics",
                        fontFamily = CartographicSerif,
                        fontWeight = FontWeight.Bold,
                        fontSize = 17.sp,
                        color = SunstoneGold
                    )
                    Text(
                        text = "Reading theme, typography & anti-panic focus",
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
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                // Section 1: Reading Theme
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(
                        text = "CARTOGRAPHIC READING THEME",
                        color = SunstoneGold,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.8.sp
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        val themes = listOf(
                            Triple(AppThemeMode.DARK, "🌑 Dark", "Basalt"),
                            Triple(AppThemeMode.LIGHT, "📜 Light", "Parchment"),
                            Triple(AppThemeMode.SEPIA, "🕯️ Sepia", "Lamp-Light")
                        )
                        themes.forEach { (mode, title, sub) ->
                            val isSelected = themeMode == mode
                            Surface(
                                modifier = Modifier
                                    .weight(1f)
                                    .clickable { onThemeModeChange(mode) },
                                shape = RoundedCornerShape(10.dp),
                                color = if (isSelected) SunstoneGold.copy(alpha = 0.18f) else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
                                border = BorderStroke(
                                    1.5.dp,
                                    if (isSelected) SunstoneGold else TopoContourMuted.copy(alpha = 0.3f)
                                )
                            ) {
                                Column(
                                    modifier = Modifier.padding(vertical = 10.dp, horizontal = 4.dp),
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Text(
                                        text = title,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (isSelected) SunstoneGold else Color.White
                                    )
                                    Spacer(modifier = Modifier.height(2.dp))
                                    Text(
                                        text = sub,
                                        fontSize = 9.sp,
                                        color = TopoContourMuted
                                    )
                                }
                            }
                        }
                    }
                }

                // Section 2: Typography Scaler
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(
                        text = "TYPOGRAPHY ZOOM (LEGIBILITY)",
                        color = SunstoneGold,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.8.sp
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        val fontOptions = listOf(
                            Triple(FontScaleOption.NORMAL, "100%", "Standard"),
                            Triple(FontScaleOption.COMFORT, "115%", "Comfort"),
                            Triple(FontScaleOption.LARGE, "130%", "Enlarged")
                        )
                        fontOptions.forEach { (opt, percent, desc) ->
                            val isSelected = fontScaleOption == opt
                            Surface(
                                modifier = Modifier
                                    .weight(1f)
                                    .clickable { onFontScaleOptionChange(opt) },
                                shape = RoundedCornerShape(10.dp),
                                color = if (isSelected) HydrosphereCyan.copy(alpha = 0.18f) else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
                                border = BorderStroke(
                                    1.5.dp,
                                    if (isSelected) HydrosphereCyan else TopoContourMuted.copy(alpha = 0.3f)
                                )
                            ) {
                                Column(
                                    modifier = Modifier.padding(vertical = 10.dp, horizontal = 4.dp),
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Text(
                                        text = percent,
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (isSelected) HydrosphereCyan else Color.White
                                    )
                                    Spacer(modifier = Modifier.height(2.dp))
                                    Text(
                                        text = desc,
                                        fontSize = 9.sp,
                                        color = TopoContourMuted
                                    )
                                }
                            }
                        }
                    }
                }

                // Section 3: Zen Focus Mode (Anti-Panic)
                Surface(
                    shape = RoundedCornerShape(10.dp),
                    color = if (isZenMode) ContourEmerald.copy(alpha = 0.12f) else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.25f),
                    border = BorderStroke(1.dp, if (isZenMode) ContourEmerald.copy(alpha = 0.5f) else TopoContourMuted.copy(alpha = 0.3f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("🧘", fontSize = 14.sp)
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = "Zen Focus (Anti-Panic)",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 12.sp,
                                    color = if (isZenMode) ContourEmerald else Color.White
                                )
                            }
                            Spacer(modifier = Modifier.height(3.dp))
                            Text(
                                text = "Hides countdown timer & combo streaks during practice to eliminate test anxiety.",
                                fontSize = 10.sp,
                                color = TopoContourMuted,
                                lineHeight = 14.sp
                            )
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        Switch(
                            checked = isZenMode,
                            onCheckedChange = onZenModeChange,
                            colors = SwitchDefaults.colors(
                                checkedThumbColor = ContourEmerald,
                                checkedTrackColor = ContourEmerald.copy(alpha = 0.3f),
                                uncheckedThumbColor = TopoContourMuted,
                                uncheckedTrackColor = DeepBasalt
                            )
                        )
                    }
                }

                // Section 4: Daily Target Quota
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(
                        text = "DAILY QUESTION QUOTA",
                        color = SunstoneGold,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.8.sp
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        val targets = listOf(10, 20, 30, 50)
                        targets.forEach { target ->
                            val isSelected = dailyTarget == target
                            Surface(
                                modifier = Modifier
                                    .weight(1f)
                                    .clickable { onDailyTargetChange(target) },
                                shape = RoundedCornerShape(8.dp),
                                color = if (isSelected) SunstoneGold.copy(alpha = 0.2f) else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.25f),
                                border = BorderStroke(
                                    1.dp,
                                    if (isSelected) SunstoneGold else TopoContourMuted.copy(alpha = 0.3f)
                                )
                            ) {
                                Column(
                                    modifier = Modifier.padding(vertical = 8.dp),
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Text(
                                        text = "$target",
                                        fontWeight = FontWeight.Bold,
                                        fontSize = 13.sp,
                                        color = if (isSelected) SunstoneGold else Color.White
                                    )
                                    Text(
                                        text = "MCQs",
                                        fontSize = 8.sp,
                                        color = TopoContourMuted
                                    )
                                }
                            }
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Done", color = SunstoneGold, fontWeight = FontWeight.Bold)
            }
        }
    )
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

@Composable
fun SummitAscentProgressStrip(
    totalQuestions: Int,
    profile: ExamBlueprint?
) {
    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, SunstoneGold.copy(alpha = 0.5f)),
        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "🏔️", fontSize = 16.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Column {
                        Text(
                            text = "EXPEDITION ALTITUDE // SUMMIT ASCENT",
                            color = SunstoneGold,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Black,
                            letterSpacing = 0.8.sp
                        )
                        Text(
                            text = "Everest Geo-Summit (8,848m Target)",
                            color = AtlasParchment,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
                Surface(
                    color = SunstoneGold.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text(
                        text = "5,364m ➔ 8,848m",
                        color = SunstoneGold,
                        fontWeight = FontWeight.Black,
                        fontSize = 10.sp,
                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                    )
                }
            }
            Spacer(modifier = Modifier.height(10.dp))
            LinearProgressIndicator(
                progress = { 0.22f },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(6.dp)
                    .clip(RoundedCornerShape(3.dp)),
                color = SunstoneGold,
                trackColor = DeepBasalt.copy(alpha = 0.6f)
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "🏕️ Base Camp (5,364m)",
                    color = ContourEmerald,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.SemiBold
                )
                Text(
                    text = "❄️ South Col (7,920m)",
                    color = TopoContourMuted,
                    fontSize = 10.sp
                )
                Text(
                    text = "🚩 Summit (8,848m)",
                    color = SunstoneGold,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}

@Composable
fun DailyFireTopperWidget(profile: ExamBlueprint?) {
    val quotes = remember {
        listOf(
            Triple(
                "DR. B.R. AMBEDKAR",
                "Cultivation of mind should be the ultimate aim of human existence.",
                "🏛️ Constitution Architect • Discipline of Steel"
            ),
            Triple(
                "SARDAR VALLABHBHAI PATEL",
                "Along with your intellect, let your heart be strong and courageous. You are the steel frame of this country.",
                "⚔️ Iron Man of India • LBSNAA Legacy"
            ),
            Triple(
                "DR. A.P.J. ABDUL KALAM",
                "Excellence is a continuous process and not an accident. Conquer geography before conquering governance.",
                "🚀 People's President • Relentless Pursuit"
            ),
            Triple(
                "LAL BAHADUR SHASTRI",
                "True discipline is that which leads to self-mastery and selfless service to the nation.",
                "🌾 Mussoorie Academy Foundation • Utmost Integrity"
            )
        )
    }
    var activeIdx by remember { mutableIntStateOf(0) }
    val currentQuote = quotes[activeIdx % quotes.size]

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(12.dp),
        border = BorderStroke(1.dp, ContourEmerald.copy(alpha = 0.35f)),
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp)
            .clickable {
                activeIdx = (activeIdx + 1) % quotes.size
            }
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "🔥", fontSize = 14.sp)
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "CADRE FIRE // ${currentQuote.first}",
                        color = SunstoneGold,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.8.sp
                    )
                }
                Text(
                    text = "Tap to rotate ↻",
                    color = TopoContourMuted,
                    fontSize = 9.sp
                )
            }
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = "\"${currentQuote.second}\"",
                color = AtlasParchment,
                fontSize = 11.5.sp,
                fontStyle = FontStyle.Italic,
                lineHeight = 16.sp
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = currentQuote.third,
                color = ContourEmerald,
                fontSize = 10.sp,
                fontWeight = FontWeight.SemiBold
            )
        }
    }
}

@Composable
fun IndiaPhysiographyMapSelector(
    selectedZone: String,
    onZoneSelected: (String) -> Unit
) {
    val zones = listOf(
        Triple("ALL", "🗺️ All India", "Complete NCERT Syllabus"),
        Triple("HIMALAYAS", "🏔️ Northern Arc", "Shiwalik, Himadri & Passes"),
        Triple("PLAINS", "🌾 Great Plains", "Bhabhar, Terai, Khadar & Alluvium"),
        Triple("PLATEAU", "🌋 Peninsular Core", "Deccan Traps & Central Highlands"),
        Triple("COASTS", "🏖️ Coasts & Islands", "Konkan, Malabar, Coromandel & Andamans"),
        Triple("RIVERS", "🌊 Hydro Systems", "Himalayan & Peninsular Drainage")
    )

    val provinceDetails = mapOf(
        "ALL" to "Complete 30-Chapter Spatial Syllabus active across all physiographic provinces.",
        "HIMALAYAS" to "Tertiary Alpine Orogeny • 8,848m Peak Datum • Great Himalayan Arc • Trans-Himalayan Zanskar & Ladakh Ranges • High Strategic Passes.",
        "PLAINS" to "Pleistocene Foreland Depression • 150m-2000m Alluvial Aggradation • Bhabhar Boulders, Terai Marshes, Bhangar Kankar & Khadar Silt.",
        "PLATEAU" to "Pre-Cambrian Gondwana Shield • Cretaceous Deccan Basalt Traps • Sahyadri Western Ghats Escarpment • Relict Eastern Ghats Residual Hills.",
        "COASTS" to "Submergent Malabar/Konkan Ria Coasts • Emergent Coromandel Deltaic Plain • Lakshadweep Coral Atolls • Andaman Volcanic Arc.",
        "RIVERS" to "Antecedent Himalayan Gorge Cutters (Indus, Brahmaputra) • Rift Valley Superimposed Flows (Narmada, Tapi) • Peninsular Gradients."
    )

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.2.dp, SunstoneGold.copy(alpha = 0.5f)),
        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "🇮🇳", fontSize = 16.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Column {
                        Text(
                            text = "INTERACTIVE PHYSIOGRAPHY MAP SELECTOR",
                            color = SunstoneGold,
                            fontSize = 10.5.sp,
                            fontWeight = FontWeight.Black,
                            letterSpacing = 0.8.sp
                        )
                        Text(
                            text = "Touch map or chips to filter curriculum by geomorphic zone",
                            color = TopoContourMuted,
                            fontSize = 10.sp
                        )
                    }
                }
                Surface(
                    color = SunstoneGold.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(6.dp)
                ) {
                    Text(
                        text = "VECTOR ATLAS",
                        color = SunstoneGold,
                        fontSize = 9.sp,
                        fontWeight = FontWeight.ExtraBold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Interactive Vector India Relief Canvas
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(165.dp)
                    .background(OceanicDark, RoundedCornerShape(12.dp))
                    .border(1.dp, HydrosphereCyan.copy(alpha = 0.35f), RoundedCornerShape(12.dp))
                    .pointerInput(Unit) {
                        detectTapGestures { offset ->
                            val h = size.height.toFloat()
                            val w = size.width.toFloat()
                            val normY = offset.y / h
                            val normX = offset.x / w

                            when {
                                normY < 0.34f -> onZoneSelected("HIMALAYAS")
                                normY in 0.34f..0.54f -> onZoneSelected("PLAINS")
                                normY > 0.54f && normX in 0.28f..0.72f -> onZoneSelected("PLATEAU")
                                normY > 0.54f && (normX < 0.28f || normX > 0.72f) -> onZoneSelected("COASTS")
                                else -> onZoneSelected("RIVERS")
                            }
                        }
                    }
            ) {
                Canvas(modifier = Modifier.fillMaxSize().padding(8.dp)) {
                    val w = size.width
                    val h = size.height

                    // 1. Graticule coordinate grid
                    for (i in 1..4) {
                        val gx = w * (i * 0.2f)
                        drawLine(
                            color = Color.White.copy(alpha = 0.05f),
                            start = Offset(gx, 0f),
                            end = Offset(gx, h),
                            strokeWidth = 0.8f
                        )
                    }
                    for (j in 1..3) {
                        val gy = h * (j * 0.25f)
                        drawLine(
                            color = Color.White.copy(alpha = 0.05f),
                            start = Offset(0f, gy),
                            end = Offset(w, gy),
                            strokeWidth = 0.8f
                        )
                    }

                    // 2. Northern Arc (Himalayas)
                    val himalayanPath = Path().apply {
                        moveTo(w * 0.20f, h * 0.30f)
                        lineTo(w * 0.30f, h * 0.12f) // Pamir / Karakoram
                        lineTo(w * 0.42f, h * 0.08f) // Ladakh
                        lineTo(w * 0.55f, h * 0.16f) // Nepal Himalaya
                        lineTo(w * 0.68f, h * 0.18f) // Sikkim / Bhutan
                        lineTo(w * 0.82f, h * 0.26f) // Arunachal Syntaxis
                        lineTo(w * 0.75f, h * 0.34f)
                        lineTo(w * 0.48f, h * 0.26f)
                        close()
                    }
                    val isHimSelected = selectedZone == "HIMALAYAS"
                    drawPath(
                        path = himalayanPath,
                        color = if (isHimSelected) Color(0xFF38BDF8) else Color(0xFF0284C7).copy(alpha = 0.45f)
                    )
                    if (isHimSelected) {
                        drawPath(
                            path = himalayanPath,
                            color = Color(0xFFF59E0B),
                            style = Stroke(width = 2.5.dp.toPx())
                        )
                    }

                    // 3. Great Plains (Indo-Gangetic Basin)
                    val plainsPath = Path().apply {
                        moveTo(w * 0.18f, h * 0.36f) // Punjab
                        lineTo(w * 0.48f, h * 0.28f)
                        lineTo(w * 0.74f, h * 0.35f)
                        lineTo(w * 0.82f, h * 0.44f) // Assam / Brahmaputra
                        lineTo(w * 0.72f, h * 0.52f) // Bengal Delta
                        lineTo(w * 0.50f, h * 0.50f) // UP / Bihar
                        lineTo(w * 0.26f, h * 0.46f) // Rajasthan fringe
                        close()
                    }
                    val isPlainSelected = selectedZone == "PLAINS"
                    drawPath(
                        path = plainsPath,
                        color = if (isPlainSelected) Color(0xFF10B981) else Color(0xFF059669).copy(alpha = 0.4f)
                    )
                    if (isPlainSelected) {
                        drawPath(
                            path = plainsPath,
                            color = Color(0xFFF59E0B),
                            style = Stroke(width = 2.5.dp.toPx())
                        )
                    }

                    // Meandering Ganga & Brahmaputra river vectors
                    drawLine(
                        color = Color(0xFF67E8F9).copy(alpha = 0.85f),
                        start = Offset(w * 0.42f, h * 0.30f),
                        end = Offset(w * 0.71f, h * 0.52f),
                        strokeWidth = 1.8.dp.toPx()
                    )
                    drawLine(
                        color = Color(0xFF67E8F9).copy(alpha = 0.85f),
                        start = Offset(w * 0.80f, h * 0.28f),
                        end = Offset(w * 0.73f, h * 0.52f),
                        strokeWidth = 1.8.dp.toPx()
                    )

                    // 4. Peninsular Core / Plateau (Deccan Shield)
                    val plateauPath = Path().apply {
                        moveTo(w * 0.28f, h * 0.52f) // Malwa / Gujarat fringe
                        lineTo(w * 0.68f, h * 0.54f) // Chota Nagpur
                        lineTo(w * 0.62f, h * 0.76f) // Andhra / Telangana
                        lineTo(w * 0.50f, h * 0.88f) // Kanyakumari Apex
                        lineTo(w * 0.34f, h * 0.74f) // Karnataka / Kerala
                        close()
                    }
                    val isPlateauSelected = selectedZone == "PLATEAU"
                    drawPath(
                        path = plateauPath,
                        color = if (isPlateauSelected) Color(0xFFF59E0B) else Color(0xFFD97706).copy(alpha = 0.4f)
                    )
                    if (isPlateauSelected) {
                        drawPath(
                            path = plateauPath,
                            color = Color(0xFFF59E0B),
                            style = Stroke(width = 2.5.dp.toPx())
                        )
                    }

                    // Western Ghats ridge line (Sahyadri)
                    drawLine(
                        color = Color(0xFFEF4444).copy(alpha = 0.9f),
                        start = Offset(w * 0.32f, h * 0.56f),
                        end = Offset(w * 0.48f, h * 0.86f),
                        strokeWidth = 2.2.dp.toPx()
                    )

                    // 5. Coasts & Island Archipelagos
                    val isCoastSelected = selectedZone == "COASTS"
                    val coastColor = if (isCoastSelected) Color(0xFF00F0FF) else Color(0xFF06B6D4).copy(alpha = 0.45f)

                    // Malabar / Konkan coastal strip
                    drawLine(
                        color = coastColor,
                        start = Offset(w * 0.28f, h * 0.54f),
                        end = Offset(w * 0.46f, h * 0.88f),
                        strokeWidth = 3.dp.toPx()
                    )
                    // Coromandel coastal strip
                    drawLine(
                        color = coastColor,
                        start = Offset(w * 0.70f, h * 0.54f),
                        end = Offset(w * 0.52f, h * 0.88f),
                        strokeWidth = 3.dp.toPx()
                    )

                    // Andaman & Nicobar Archipelago dots
                    drawCircle(color = coastColor, radius = 3.dp.toPx(), center = Offset(w * 0.84f, h * 0.74f))
                    drawCircle(color = coastColor, radius = 2.5.dp.toPx(), center = Offset(w * 0.85f, h * 0.80f))
                    drawCircle(color = coastColor, radius = 2.dp.toPx(), center = Offset(w * 0.86f, h * 0.86f))

                    // Lakshadweep Atoll dots
                    drawCircle(color = coastColor, radius = 2.5.dp.toPx(), center = Offset(w * 0.22f, h * 0.78f))
                    drawCircle(color = coastColor, radius = 2.dp.toPx(), center = Offset(w * 0.24f, h * 0.83f))
                }

                // Interactive Region Legend Overlays
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(10.dp),
                    verticalArrangement = Arrangement.SpaceBetween
                ) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Surface(
                            color = Color.Black.copy(alpha = 0.55f),
                            shape = RoundedCornerShape(4.dp)
                        ) {
                            Text(
                                text = "▲ NORTHERN ARC [Himalayas 8,848m]",
                                color = Color(0xFF38BDF8),
                                fontSize = 8.5.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                            )
                        }
                        Surface(
                            color = Color.Black.copy(alpha = 0.55f),
                            shape = RoundedCornerShape(4.dp)
                        ) {
                            Text(
                                text = "🌾 GREAT PLAINS [Alluvium]",
                                color = Color(0xFF10B981),
                                fontSize = 8.5.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                            )
                        }
                    }

                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.Bottom
                    ) {
                        Surface(
                            color = Color.Black.copy(alpha = 0.55f),
                            shape = RoundedCornerShape(4.dp)
                        ) {
                            Text(
                                text = "🏖️ LAKSHADWEEP",
                                color = Color(0xFF00F0FF),
                                fontSize = 8.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                            )
                        }
                        Surface(
                            color = Color.Black.copy(alpha = 0.55f),
                            shape = RoundedCornerShape(4.dp)
                        ) {
                            Text(
                                text = "▼ DECCAN TRAPS [Gondwana]",
                                color = Color(0xFFF59E0B),
                                fontSize = 8.5.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                            )
                        }
                        Surface(
                            color = Color.Black.copy(alpha = 0.55f),
                            shape = RoundedCornerShape(4.dp)
                        ) {
                            Text(
                                text = "🏝️ ANDAMAN & NICOBAR",
                                color = Color(0xFF00F0FF),
                                fontSize = 8.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 4.dp, vertical = 2.dp)
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Active Province Geomorphic Inspector Card
            Surface(
                color = OceanicDark,
                shape = RoundedCornerShape(8.dp),
                border = BorderStroke(0.8.dp, SunstoneGold.copy(alpha = 0.35f)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(10.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = when (selectedZone) {
                            "HIMALAYAS" -> "🏔️"
                            "PLAINS" -> "🌾"
                            "PLATEAU" -> "🌋"
                            "COASTS" -> "🏖️"
                            "RIVERS" -> "🌊"
                            else -> "🇮🇳"
                        },
                        fontSize = 18.sp
                    )
                    Spacer(modifier = Modifier.width(10.dp))
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "ACTIVE ZONE: ${selectedZone}",
                            color = SunstoneGold,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.ExtraBold,
                            letterSpacing = 0.5.sp
                        )
                        Text(
                            text = provinceDetails[selectedZone] ?: provinceDetails["ALL"]!!,
                            color = AtlasParchment,
                            fontSize = 10.5.sp,
                            lineHeight = 14.5.sp
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Interactive Physiographic Zone Quick Chips (Row 1)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                zones.take(3).forEach { (key, label, _) ->
                    val isSelected = selectedZone == key
                    Surface(
                        color = if (isSelected) SunstoneGold else OceanicDark,
                        shape = RoundedCornerShape(8.dp),
                        border = BorderStroke(0.8.dp, if (isSelected) SunstoneGold else HydrosphereCyan.copy(alpha = 0.3f)),
                        modifier = Modifier
                            .weight(1f)
                            .clickable { onZoneSelected(key) }
                    ) {
                        Text(
                            text = label,
                            color = if (isSelected) AbyssNavy else AtlasParchment,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.padding(vertical = 8.dp)
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(6.dp))

            // Interactive Physiographic Zone Quick Chips (Row 2)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                zones.drop(3).forEach { (key, label, _) ->
                    val isSelected = selectedZone == key
                    Surface(
                        color = if (isSelected) SunstoneGold else OceanicDark,
                        shape = RoundedCornerShape(8.dp),
                        border = BorderStroke(0.8.dp, if (isSelected) SunstoneGold else HydrosphereCyan.copy(alpha = 0.3f)),
                        modifier = Modifier
                            .weight(1f)
                            .clickable { onZoneSelected(key) }
                    ) {
                        Text(
                            text = label,
                            color = if (isSelected) AbyssNavy else AtlasParchment,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.Bold,
                            textAlign = TextAlign.Center,
                            modifier = Modifier.padding(vertical = 8.dp)
                        )
                    }
                }
            }
        }
    }
}

@Composable
fun CadreMedalTrophyShowcase(profile: ExamBlueprint?) {
    val medals = listOf(
        Triple("🏛️ LBSNAA", "Civil Services Steel Frame", SunstoneGold),
        Triple("🌾 BIHAR SDM", "Patna Secretariat Corps", ContourEmerald),
        Triple("⭐ CSS ASO", "Central Secretariat Merit Star", HydrosphereCyan),
        Triple("🚆 RAILWAY", "Indian Railways Speed Corps", SunstoneGold)
    )

    Surface(
        color = DeepBasalt,
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.2.dp, SunstoneGold.copy(alpha = 0.5f)),
        modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp)
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text(text = "🎖️", fontSize = 16.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Column {
                        Text(
                            text = "CADRE GLORY MEDAL SHOWCASE // TROPHY ROOM",
                            color = SunstoneGold,
                            fontSize = 10.5.sp,
                            fontWeight = FontWeight.Black,
                            letterSpacing = 0.8.sp
                        )
                        Text(
                            text = "Conquer questions to permanently etch your name in the service roll",
                            color = TopoContourMuted,
                            fontSize = 10.sp
                        )
                    }
                }
                Surface(
                    color = SunstoneGold.copy(alpha = 0.15f),
                    shape = RoundedCornerShape(4.dp)
                ) {
                    Text(
                        text = "4 CADRES",
                        color = SunstoneGold,
                        fontSize = 9.sp,
                        fontWeight = FontWeight.Bold,
                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                medals.forEach { (name, desc, color) ->
                    val isActive = profile?.displayName?.contains(name.substringAfter(" ").take(4), ignoreCase = true) == true || (name.contains("LBSNAA") && profile?.examId?.contains("UPSC", ignoreCase = true) == true)
                    Surface(
                        color = if (isActive) OceanicDark else DeepBasalt.copy(alpha = 0.6f),
                        shape = RoundedCornerShape(10.dp),
                        border = BorderStroke(1.dp, if (isActive) color else TopoContourMuted.copy(alpha = 0.25f)),
                        modifier = Modifier.weight(1f)
                    ) {
                        Column(
                            modifier = Modifier.padding(8.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text(text = name.substringBefore(" "), fontSize = 20.sp)
                            Spacer(modifier = Modifier.height(4.dp))
                            Text(
                                text = name.substringAfter(" "),
                                color = if (isActive) color else TopoContourMuted,
                                fontSize = 9.sp,
                                fontWeight = FontWeight.Black,
                                textAlign = TextAlign.Center,
                                maxLines = 1
                            )
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                text = if (isActive) "ACTIVE" else "LOCKED",
                                color = if (isActive) ContourEmerald else TopoContourMuted.copy(alpha = 0.6f),
                                fontSize = 8.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }
            }
        }
    }
}

