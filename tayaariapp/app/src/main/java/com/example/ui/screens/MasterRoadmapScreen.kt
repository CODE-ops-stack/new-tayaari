package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.*
import androidx.compose.ui.draw.*
import androidx.compose.ui.graphics.*
import androidx.compose.ui.text.*
import androidx.compose.ui.text.font.*
import androidx.compose.ui.text.style.*
import androidx.compose.ui.unit.*
import com.example.ui.theme.*

// ─────────────────────────────────────────────────────────────────────────────
// Data Models for Roadmap
// ─────────────────────────────────────────────────────────────────────────────

data class RoadmapTopic(
    val sequenceNumber: Int,
    val topicId: Int,
    val topicName: String,
    val ncertMapping: String,
    val curiosityHook: String,
    val questionCount: Int,
    val highYieldExamTag: String
)

data class RoadmapStage(
    val stageNumber: Int,
    val title: String,
    val subtitle: String,
    val badgeColor: Color,
    val topics: List<RoadmapTopic>
)

data class RoadmapFaq(
    val question: String,
    val answer: String,
    val category: String
)

// ─────────────────────────────────────────────────────────────────────────────
// Recommended 4-Stage Pedagogical Curriculum
// ─────────────────────────────────────────────────────────────────────────────

val ROADMAP_STAGES = listOf(
    RoadmapStage(
        stageNumber = 1,
        title = "Stage 1: Physical Foundations",
        subtitle = "Master the mechanical and atmospheric laws of the Earth",
        badgeColor = HydrosphereCyan,
        topics = listOf(
            RoadmapTopic(
                sequenceNumber = 1,
                topicId = 1,
                topicName = "Universe, Solar System & Earth Motions",
                ncertMapping = "NCERT Class 6 Ch 1, 2 • Class 11 Physical Ch 2",
                curiosityHook = "Why is Earth closest to the Sun (Perihelion) during freezing January in the Northern Hemisphere?",
                questionCount = 150,
                highYieldExamTag = "UPSC / SSC CORE"
            ),
            RoadmapTopic(
                sequenceNumber = 2,
                topicId = 2,
                topicName = "Globe, Latitudes, Longitudes & Time",
                ncertMapping = "NCERT Class 6 Ch 2 • Class 11 Practical Geography",
                curiosityHook = "How do aircraft cross the International Date Line (180°) and gain an entire 24-hour calendar day?",
                questionCount = 143,
                highYieldExamTag = "TIME CALCULATIONS"
            ),
            RoadmapTopic(
                sequenceNumber = 3,
                topicId = 4,
                topicName = "Earth's Interior, Rocks & Plate Tectonics",
                ncertMapping = "NCERT Class 11 Physical Ch 3 & 4 (Fundamentals)",
                curiosityHook = "How do seismic S-waves completely vanish at 2,900 km depth, proving the outer core is liquid iron?",
                questionCount = 368,
                highYieldExamTag = "HIGH-YIELD PRELIMS"
            ),
            RoadmapTopic(
                sequenceNumber = 4,
                topicId = 5,
                topicName = "Geomorphic Processes & Landforms",
                ncertMapping = "NCERT Class 11 Physical Ch 5, 6 & 7",
                curiosityHook = "How does desert wind carve balanced mushroom rocks while groundwater hollows out stalactite caves?",
                questionCount = 335,
                highYieldExamTag = "UPSC GS1 / BPSC"
            ),
            RoadmapTopic(
                sequenceNumber = 5,
                topicId = 6,
                topicName = "Atmosphere, Winds & Climate Systems",
                ncertMapping = "NCERT Class 11 Physical Ch 8 to 11",
                curiosityHook = "Why do all the world's great hot deserts lie strictly along 20°–30° latitudes under subtropical highs?",
                questionCount = 155,
                highYieldExamTag = "CLIMATOLOGY CORE"
            ),
            RoadmapTopic(
                sequenceNumber = 6,
                topicId = 7,
                topicName = "Oceanography: Relief, Currents & Tides",
                ncertMapping = "NCERT Class 11 Physical Ch 13 & 14",
                curiosityHook = "Why does the calm Sargasso Sea have zero land borders, and why do cold currents starve adjacent lands of rain?",
                questionCount = 312,
                highYieldExamTag = "OCEAN DYNAMICS"
            )
        )
    ),
    RoadmapStage(
        stageNumber = 2,
        title = "Stage 2: India's Physical Architecture",
        subtitle = "Connect India's terrain, river systems, monsoons and forest cover",
        badgeColor = ContourEmerald,
        topics = listOf(
            RoadmapTopic(
                sequenceNumber = 7,
                topicId = 9,
                topicName = "India: Location, Size & Neighbours",
                ncertMapping = "NCERT Class 9 Ch 1 • Class 11 India Physical Ch 1",
                curiosityHook = "Why is there a 2-hour sun time gap between Kibithu (Arunachal) and Ghuar Mota (Gujarat) despite 82°30'E IST?",
                questionCount = 139,
                highYieldExamTag = "BORDER DISPUTES"
            ),
            RoadmapTopic(
                sequenceNumber = 8,
                topicId = 10,
                topicName = "Physiography of India: Mountains, Plains & Plateaus",
                ncertMapping = "NCERT Class 9 Ch 2 • Class 11 India Physical Ch 2",
                curiosityHook = "Why do rivers disappear underground in the pebble-rich Bhabar and burst out into the malaria Terai?",
                questionCount = 403,
                highYieldExamTag = "TOP RANKER PRIORITY"
            ),
            RoadmapTopic(
                sequenceNumber = 9,
                topicId = 11,
                topicName = "Drainage System of India: River Basins & Deltas",
                ncertMapping = "NCERT Class 9 Ch 3 • Class 11 India Physical Ch 3",
                curiosityHook = "Why do the Narmada and Tapi flow west into rift grabens while the Godavari and Krishna build massive eastern deltas?",
                questionCount = 410,
                highYieldExamTag = "RIVER CONFLUENCES"
            ),
            RoadmapTopic(
                sequenceNumber = 10,
                topicId = 12,
                topicName = "Indian Climate & Monsoon Mechanisms",
                ncertMapping = "NCERT Class 9 Ch 4 • Class 11 India Physical Ch 4",
                curiosityHook = "How does thermal heating of the Tibetan Plateau 4,000 km away pump the entire Indian summer monsoon engine?",
                questionCount = 145,
                highYieldExamTag = "ENSO / IOD / KOPPEN"
            ),
            RoadmapTopic(
                sequenceNumber = 11,
                topicId = 13,
                topicName = "Soils & Natural Vegetation of India",
                ncertMapping = "NCERT Class 9 Ch 5 • Class 11 India Physical Ch 5 & 6",
                curiosityHook = "Why does Deccan black regur soil self-plough with deep cracks, and why are Sholas trapped in high Nilgiri folds?",
                questionCount = 159,
                highYieldExamTag = "ICAR SOILS & FORESTS"
            ),
            RoadmapTopic(
                sequenceNumber = 12,
                topicId = 14,
                topicName = "Wildlife, Protected Areas & Conservation",
                ncertMapping = "NCERT Class 11 India Physical Ch 5",
                curiosityHook = "How do floating phumdis in Loktak Lake keep the world's only dancing deer (Sangai) afloat without sinking?",
                questionCount = 126,
                highYieldExamTag = "NATIONAL PARKS / RAMSAR"
            )
        )
    ),
    RoadmapStage(
        stageNumber = 3,
        title = "Stage 3: Resource & Human Geography",
        subtitle = "Master the spatial distribution of agriculture, minerals, industries and cities",
        badgeColor = SunstoneGold,
        topics = listOf(
            RoadmapTopic(
                sequenceNumber = 13,
                topicId = 15,
                topicName = "Agriculture & Cropping Systems",
                ncertMapping = "NCERT Class 10 Ch 4 • Class 12 India People & Economy Ch 5",
                curiosityHook = "Why did India's sugar industry migrate from Uttar Pradesh to Maharashtra and Tamil Nadu?",
                questionCount = 327,
                highYieldExamTag = "CROPPING SEASONS"
            ),
            RoadmapTopic(
                sequenceNumber = 14,
                topicId = 16,
                topicName = "Water Resources, Irrigation & Dams",
                ncertMapping = "NCERT Class 10 Ch 3 • Class 12 India People & Economy Ch 6",
                curiosityHook = "How did traditional earthen johads revive the dead Arvari river under community-led water governance?",
                questionCount = 115,
                highYieldExamTag = "INTER-LINKING & DAMS"
            ),
            RoadmapTopic(
                sequenceNumber = 15,
                topicId = 17,
                topicName = "Minerals & Energy Resources",
                ncertMapping = "NCERT Class 10 Ch 5 • Class 12 India People & Economy Ch 7",
                curiosityHook = "Why is 98% of India's commercial coal locked into ancient Gondwana basins along the Damodar and Son?",
                questionCount = 250,
                highYieldExamTag = "ORE BELTS & COAL"
            ),
            RoadmapTopic(
                sequenceNumber = 16,
                topicId = 18,
                topicName = "Industries & Manufacturing",
                ncertMapping = "NCERT Class 10 Ch 6 • Class 12 India People & Economy Ch 8",
                curiosityHook = "Why do iron and steel plants strictly follow Alfred Weber's raw-material location weight-loss rule?",
                questionCount = 122,
                highYieldExamTag = "WEBER LEAST-COST"
            ),
            RoadmapTopic(
                sequenceNumber = 17,
                topicId = 19,
                topicName = "Transport, Communication & Trade",
                ncertMapping = "NCERT Class 10 Ch 7 • Class 12 India People & Economy Ch 10 & 11",
                curiosityHook = "Why is Kolkata Port India's only major riverine port, requiring constant dredging 232 km inland from the sea?",
                questionCount = 153,
                highYieldExamTag = "PORTS & FREIGHT"
            ),
            RoadmapTopic(
                sequenceNumber = 18,
                topicId = 20,
                topicName = "Population, Migration & Settlements",
                ncertMapping = "NCERT Class 12 Human Ch 2 • Class 12 India Ch 1 to 4",
                curiosityHook = "Why do rural settlements split into hamleted units like panna, para, and dhani, and where is India on the demographic curve?",
                questionCount = 197,
                highYieldExamTag = "CENSUS & DEMOGRAPHY"
            ),
            RoadmapTopic(
                sequenceNumber = 19,
                topicId = 21,
                topicName = "Human Development & Economic Activities",
                ncertMapping = "NCERT Class 12 Human Geography Ch 3 to 7",
                curiosityHook = "Why do gold-collar quinary executives shape trillion-dollar policies despite forming less than 1% of the workforce?",
                questionCount = 103,
                highYieldExamTag = "HDI & ECONOMIC MODELS"
            )
        )
    ),
    RoadmapStage(
        stageNumber = 4,
        title = "Stage 4: Regional Specialization & Cartography",
        subtitle = "Attain master-level distinction in map skills, world chokepoints and state exams",
        badgeColor = TectonicPurple,
        topics = listOf(
            RoadmapTopic(
                sequenceNumber = 20,
                topicId = 3,
                topicName = "Maps, Scale, Projections & GIS",
                ncertMapping = "NCERT Class 11 Practical Geography Ch 1 to 4",
                curiosityHook = "Why can no flat paper map represent both true shape and true area of continents at the same time?",
                questionCount = 143,
                highYieldExamTag = "CARTOGRAPHY & GIS"
            ),
            RoadmapTopic(
                sequenceNumber = 21,
                topicId = 22,
                topicName = "World Regional Geography & Chokepoints",
                ncertMapping = "Global Physical & Geopolitical Framework",
                curiosityHook = "How does the 2.8 km narrow funnel of the Strait of Malacca command over 25% of all global seaborne commerce?",
                questionCount = 120,
                highYieldExamTag = "GLOBAL STRAITS"
            ),
            RoadmapTopic(
                sequenceNumber = 22,
                topicId = 23,
                topicName = "Bihar Geography: Complete Regional Atlas",
                ncertMapping = "BPSC CCE State Geography & Economic Survey",
                curiosityHook = "Why does the Kosi river swing 150 km westward across its alluvial cone to earn the title 'Sorrow of Bihar'?",
                questionCount = 62,
                highYieldExamTag = "BPSC 100% MUST"
            ),
            RoadmapTopic(
                sequenceNumber = 23,
                topicId = 24,
                topicName = "Advanced Human Thought, Regional Models & Theories",
                ncertMapping = "UPSC Geography Optional & University Curriculum (Topics 24 to 30)",
                curiosityHook = "How do Christaller's Central Place Theory and Von Thunen's Isolated State predict modern urban sprawl?",
                questionCount = 420,
                highYieldExamTag = "MAINS ADVANCED"
            )
        )
    )
)

val ROADMAP_FAQS = listOf(
    RoadmapFaq(
        question = "I have zero geography background. Where should I begin?",
        answer = "Start strictly at Stage 1, Topic 1 (Universe & Solar System) on Basic Tier. Do not guess. Tap the question, read the explanation, and note the 💡 MEMORY ANCHOR. You will build a rock-solid mental scaffold before advancing.",
        category = "Beginner"
    ),
    RoadmapFaq(
        question = "How does this app complement my NCERT and standard books?",
        answer = "Use the 'Sandwich Technique': Read the textbook chapter (e.g. NCERT Class 11 Ch 3) $\\rightarrow$ Open Topic 4 in the app $\\rightarrow$ Solve 30 Basic & Medium questions $\\rightarrow$ Review the Distractor Dissections. You will discover exactly how examiners craft traps from textbook lines.",
        category = "Methodology"
    ),
    RoadmapFaq(
        question = "What should I do if my accuracy in a topic drops below 60%?",
        answer = "A drop below 60% is a signal to slow down, not give up. Switch the tier filter to Basic, open 'Preview' mode, and read through the first 25 questions in open-book mode. Re-test on Medium Tier the next day.",
        category = "Accuracy"
    ),
    RoadmapFaq(
        question = "How many questions should I solve each day?",
        answer = "Consistency beats binge-study. Beginners should solve 40–50 Basic questions/day. Intermediate aspirants should solve 60 Medium questions/day. Pre-exam aspirants should solve 75–100 mixed questions/day with strict negative marking.",
        category = "Routine"
    ),
    RoadmapFaq(
        question = "How do I master Map-based questions without forgetting?",
        answer = "Never memorize maps passively. Use our Sequence Ordering and Match the Following formats in Topics 9, 10, 11, 14, and 22. Anchor extreme geographic coordinates (North-to-South, West-to-East) using the Memory Anchors.",
        category = "Maps"
    ),
    RoadmapFaq(
        question = "How does the app protect me from negative marking traps?",
        answer = "Every question provides Distractor Dissections revealing the exact trap type: Absolute Overgeneralization (words like 'only', 'always'), Bilateral Geographic Swaps, or Chronological Inversions. Practicing these makes you trap-immune.",
        category = "Exam Tactics"
    )
)

// ─────────────────────────────────────────────────────────────────────────────
// Master Roadmap Composable Screen
// ─────────────────────────────────────────────────────────────────────────────

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MasterRoadmapScreen(
    onBackClick: () -> Unit = {},
    onTopicSelect: (topicName: String, tier: String, format: String) -> Unit = { _, _, _ -> }
) {
    var selectedStageIndex by remember { mutableIntStateOf(0) }
    var expandedFaqIndex by remember { mutableIntStateOf(-1) }

    val fontScale = LocalFontScale.current

    com.example.ui.components.AtlasBackground {
        com.example.ui.components.TopographicBackground(lineColor = ContourEmerald.copy(alpha = 0.035f)) {
            Scaffold(
                topBar = {
                    TopAppBar(
                        title = {
                            Column {
                                Text(
                                    text = "Interactive Master Roadmap",
                                    color = MaterialTheme.colorScheme.onSurface,
                                    fontWeight = FontWeight.Black,
                                    fontSize = 18.sp
                                )
                                Text(
                                    text = "Zero-Knowledge to 90%+ Exam Mastery Blueprint",
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    fontSize = 11.sp
                                )
                            }
                        },
                        navigationIcon = {
                            IconButton(onClick = onBackClick) {
                                Icon(
                                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                    contentDescription = "Back",
                                    tint = MaterialTheme.colorScheme.onSurface
                                )
                            }
                        },
                        colors = TopAppBarDefaults.topAppBarColors(
                            containerColor = Color.Transparent
                        )
                    )
                },
                containerColor = Color.Transparent
            ) { paddingValues ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 16.dp),
            contentPadding = PaddingValues(top = 12.dp, bottom = 32.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // ─────────────────────────────────────────────────────────────────
            // 1. ONE-STOP MANIFESTO HERO CARD
            // ─────────────────────────────────────────────────────────────────
            item {
                Surface(
                    color = MaterialTheme.colorScheme.surfaceVariant,
                    shape = RoundedCornerShape(16.dp),
                    border = BorderStroke(1.5.dp, SunstoneGold.copy(alpha = 0.6f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Surface(
                                color = SunstoneGold.copy(alpha = 0.2f),
                                shape = CircleShape
                            ) {
                                Text(
                                    text = "🏆",
                                    fontSize = 20.sp,
                                    modifier = Modifier.padding(8.dp)
                                )
                            }
                            Spacer(modifier = Modifier.width(12.dp))
                            Column {
                                Text(
                                    text = "NOT A RANDOM TRIVIA QUIZ",
                                    color = SunstoneGold,
                                    fontWeight = FontWeight.Black,
                                    fontSize = 11.sp,
                                    letterSpacing = 1.sp
                                )
                                Text(
                                    text = "Your Definitive One-Stop NCERT Companion",
                                    color = MaterialTheme.colorScheme.onSurface,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = (15 * fontScale).sp
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(12.dp))

                        Text(
                            text = "Every question in this platform is reverse-engineered from NCERT Classes 6–12 and standard reference textbooks (GC Leong, Majid Husain, Khullar). Follow our recommended 4-stage chapter order below for guaranteed conceptual dominance.",
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            fontSize = (13 * fontScale).sp,
                            lineHeight = (18 * fontScale).sp
                        )

                        Spacer(modifier = Modifier.height(14.dp))

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            RoadmapStatChip(label = "Verified MCQs", value = "5,551")
                            RoadmapStatChip(label = "NCERT Terms", value = "100% Grounded")
                            RoadmapStatChip(label = "Core Stages", value = "4 Tiers")
                        }
                    }
                }
            }

            // ─────────────────────────────────────────────────────────────────
            // 2. STAGE SELECTOR TABS
            // ─────────────────────────────────────────────────────────────────
            item {
                Text(
                    text = "RECOMMENDED STUDY SEQUENCE",
                    color = SunstoneGold,
                    fontWeight = FontWeight.Black,
                    fontSize = 12.sp,
                    letterSpacing = 1.sp
                )

                Spacer(modifier = Modifier.height(8.dp))

                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState()),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    ROADMAP_STAGES.forEachIndexed { index, stage ->
                        val isSelected = selectedStageIndex == index
                        Surface(
                            color = if (isSelected) stage.badgeColor.copy(alpha = 0.2f) else MaterialTheme.colorScheme.surfaceVariant,
                            shape = RoundedCornerShape(10.dp),
                            border = BorderStroke(
                                1.dp,
                                if (isSelected) stage.badgeColor else MaterialTheme.colorScheme.outline.copy(alpha = 0.35f)
                            ),
                            modifier = Modifier.clickable { selectedStageIndex = index }
                        ) {
                            Column(
                                modifier = Modifier.padding(horizontal = 14.dp, vertical = 8.dp),
                                horizontalAlignment = Alignment.CenterHorizontally
                            ) {
                                Text(
                                    text = "STAGE ${stage.stageNumber}",
                                    color = if (isSelected) stage.badgeColor else MaterialTheme.colorScheme.onSurfaceVariant,
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Black
                                )
                                Text(
                                    text = stage.title.substringAfter(": "),
                                    color = if (isSelected) MaterialTheme.colorScheme.onSurface else MaterialTheme.colorScheme.onSurfaceVariant,
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                        }
                    }
                }
            }

            // ─────────────────────────────────────────────────────────────────
            // 3. ACTIVE STAGE DESCRIPTION BANNER
            // ─────────────────────────────────────────────────────────────────
            item {
                val activeStage = ROADMAP_STAGES[selectedStageIndex]
                Surface(
                    color = MaterialTheme.colorScheme.surfaceVariant,
                    shape = RoundedCornerShape(12.dp),
                    border = BorderStroke(1.dp, activeStage.badgeColor.copy(alpha = 0.35f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(14.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .clip(CircleShape)
                                .background(activeStage.badgeColor.copy(alpha = 0.2f)),
                            contentAlignment = Alignment.Center
                        ) {
                            Text(
                                text = "${activeStage.stageNumber}",
                                color = activeStage.badgeColor,
                                fontWeight = FontWeight.Black,
                                fontSize = 16.sp
                            )
                        }
                        Spacer(modifier = Modifier.width(12.dp))
                        Column {
                            Text(
                                text = activeStage.title,
                                color = MaterialTheme.colorScheme.onSurface,
                                fontWeight = FontWeight.Bold,
                                fontSize = (14 * fontScale).sp
                            )
                            Text(
                                text = activeStage.subtitle,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                fontSize = (12 * fontScale).sp
                            )
                        }
                    }
                }
            }

            // ─────────────────────────────────────────────────────────────────
            // 4. CHAPTER CARDS FOR ACTIVE STAGE
            // ─────────────────────────────────────────────────────────────────
            val currentTopics = ROADMAP_STAGES[selectedStageIndex].topics
            items(currentTopics) { topic ->
                RoadmapTopicCard(
                    topic = topic,
                    badgeColor = ROADMAP_STAGES[selectedStageIndex].badgeColor,
                    onPracticeClick = {
                        onTopicSelect(topic.topicName, "Basic", "All")
                    }
                )
            }

            // ─────────────────────────────────────────────────────────────────
            // 5. INTERACTIVE ASPIRANT PROBLEM-SOLVING FAQ ACCORDION
            // ─────────────────────────────────────────────────────────────────
            item {
                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = "ASPIRANT PROBLEM-SOLVER FAQ",
                    color = SunstoneGold,
                    fontWeight = FontWeight.Black,
                    fontSize = 12.sp,
                    letterSpacing = 1.sp
                )
                Text(
                    text = "Tap any question to decrypt real-world preparation blockers",
                    color = TopoContourMuted,
                    fontSize = 11.sp
                )
            }

            itemsIndexed(ROADMAP_FAQS) { index, faq ->
                val isExpanded = expandedFaqIndex == index
                Surface(
                    color = MaterialTheme.colorScheme.surfaceVariant,
                    shape = RoundedCornerShape(12.dp),
                    border = BorderStroke(1.dp, if (isExpanded) ContourEmerald else MaterialTheme.colorScheme.outline.copy(alpha = 0.35f)),
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable {
                            expandedFaqIndex = if (isExpanded) -1 else index
                        }
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Row(
                                modifier = Modifier.weight(1f),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Surface(
                                    color = ContourEmerald.copy(alpha = 0.15f),
                                    shape = RoundedCornerShape(6.dp)
                                ) {
                                    Text(
                                        text = faq.category,
                                        color = ContourEmerald,
                                        fontSize = 9.sp,
                                        fontWeight = FontWeight.Bold,
                                        modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                                    )
                                }
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(
                                    text = faq.question,
                                    color = MaterialTheme.colorScheme.onSurface,
                                    fontSize = (13 * fontScale).sp,
                                    fontWeight = FontWeight.SemiBold
                                )
                            }
                            Icon(
                                imageVector = if (isExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                                contentDescription = "Toggle",
                                tint = if (isExpanded) ContourEmerald else MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }

                        AnimatedVisibility(
                            visible = isExpanded,
                            enter = expandVertically() + fadeIn(),
                            exit = shrinkVertically() + fadeOut()
                        ) {
                            Column(modifier = Modifier.padding(top = 10.dp)) {
                                HorizontalDivider(color = MaterialTheme.colorScheme.outline.copy(alpha = 0.25f), thickness = 0.5.dp)
                                Spacer(modifier = Modifier.height(10.dp))
                                Text(
                                    text = faq.answer,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    fontSize = (12.5 * fontScale).sp,
                                    lineHeight = (18 * fontScale).sp
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

// ─────────────────────────────────────────────────────────────────────────────
// Subcomponents
// ─────────────────────────────────────────────────────────────────────────────

@Composable
fun RoadmapTopicCard(
    topic: RoadmapTopic,
    badgeColor: Color,
    onPracticeClick: () -> Unit
) {
    val fontScale = LocalFontScale.current
    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant,
        shape = RoundedCornerShape(14.dp),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.35f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Surface(
                        color = badgeColor.copy(alpha = 0.2f),
                        shape = RoundedCornerShape(6.dp)
                    ) {
                        Text(
                            text = "#%02d".format(topic.sequenceNumber),
                            color = badgeColor,
                            fontWeight = FontWeight.Black,
                            fontSize = 11.sp,
                            modifier = Modifier.padding(horizontal = 7.dp, vertical = 3.dp)
                        )
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Surface(
                        color = SunstoneGold.copy(alpha = 0.15f),
                        shape = RoundedCornerShape(6.dp)
                    ) {
                        Text(
                            text = topic.highYieldExamTag,
                            color = SunstoneGold,
                            fontWeight = FontWeight.Bold,
                            fontSize = 9.sp,
                            modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                        )
                    }
                }

                Text(
                    text = "${topic.questionCount} MCQs",
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Medium
                )
            }

            Spacer(modifier = Modifier.height(10.dp))

            Text(
                text = topic.topicName,
                color = MaterialTheme.colorScheme.onSurface,
                fontSize = (14 * fontScale).sp,
                fontWeight = FontWeight.Bold
            )

            Spacer(modifier = Modifier.height(4.dp))

            Text(
                text = "📚 ${topic.ncertMapping}",
                color = HydrosphereCyan,
                fontSize = (11 * fontScale).sp,
                fontWeight = FontWeight.Medium
            )

            Spacer(modifier = Modifier.height(8.dp))

            Surface(
                color = MaterialTheme.colorScheme.surface,
                shape = RoundedCornerShape(8.dp),
                border = BorderStroke(0.5.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(10.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Text(text = "💡", fontSize = 14.sp)
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = topic.curiosityHook,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        fontSize = (11.5 * fontScale).sp,
                        lineHeight = (16 * fontScale).sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(12.dp))

            Button(
                onClick = onPracticeClick,
                colors = ButtonDefaults.buttonColors(
                    containerColor = badgeColor.copy(alpha = 0.2f)
                ),
                shape = RoundedCornerShape(8.dp),
                border = BorderStroke(1.dp, badgeColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = "Practice Topic #%02d Now ➔".format(topic.sequenceNumber),
                    color = badgeColor,
                    fontWeight = FontWeight.Bold,
                    fontSize = 12.sp
                )
            }
        }
    }
}

@Composable
fun RoadmapStatChip(label: String, value: String) {
    Surface(
        color = MaterialTheme.colorScheme.surface,
        shape = RoundedCornerShape(8.dp),
        border = BorderStroke(0.5.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.35f))
    ) {
        Column(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = value,
                color = MaterialTheme.colorScheme.onSurface,
                fontWeight = FontWeight.Black,
                fontSize = 13.sp
            )
            Text(
                text = label,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                fontSize = 9.sp
            )
        }
    }
}
