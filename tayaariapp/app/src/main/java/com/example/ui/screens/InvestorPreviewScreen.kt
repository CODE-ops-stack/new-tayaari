package com.example.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.*
import androidx.compose.foundation.shape.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
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
import kotlinx.coroutines.*
import org.json.JSONArray
import org.json.JSONObject
import java.net.URL

// ─────────────────────────────────────────────────────────────────────────────
// Data Models
// ─────────────────────────────────────────────────────────────────────────────

data class PreviewQuestion(
    val id: Int,
    val stem: String,
    val optA: String,
    val optB: String,
    val optC: String,
    val optD: String,
    val correctAnswer: String,
    val explanation: String,
    val format: String,
    val tier: String,
    val examTarget: String,
    val subTopic: String,
    val trapInfo: String,
    val provenance: String
)

data class PreviewTopic(
    val topicId: Int,
    val topicName: String,
    val totalCount: Int,
    val basicCount: Int,
    val mediumCount: Int,
    val hardCount: Int
)

val TOPIC_NAMES = mapOf(
    1 to "Earth & Universe", 2 to "Lithosphere & Interior",
    3 to "Maps, GIS & Projections", 4 to "Plate Tectonics & Rocks",
    5 to "Geomorphology & Landforms", 6 to "Atmosphere & Weather",
    7 to "Oceanography", 8 to "Biogeography & Ecology",
    9 to "India — Location & Neighbours", 10 to "India — Physiography",
    11 to "India — Drainage System", 12 to "India — Climate & Monsoon",
    13 to "India — Soils & Vegetation", 14 to "Wildlife & Protected Areas",
    15 to "Agriculture & Cropping", 16 to "Water Resources & Dams",
    17 to "Minerals & Energy", 18 to "Industries & Manufacturing",
    19 to "Transport & Infrastructure", 20 to "Population & Settlement",
    21 to "Human Development & Economy", 22 to "World Regional Geography",
    23 to "Bihar Special Geography", 24 to "Physical Geography — Advanced",
    25 to "Human Geography — Advanced", 26 to "Economic Geography — Advanced",
    27 to "Regional Geography India", 28 to "Political Geography",
    29 to "Environmental Geography", 30 to "Geographical Thought & Models"
)

val EXAM_LABELS = listOf("All Exams", "UPSC CSE", "BPSC CCE", "SSC CGL", "RRB NTPC")
val EXAM_IDS    = listOf("ALL", "UPSC_CSE", "BPSC_CCE", "SSC_CGL", "RRB_NTPC")

val EXAM_COLORS = mapOf(
    "ALL"      to Color(0xFF7C3AED),
    "UPSC_CSE" to Color(0xFF1D4ED8),
    "BPSC_CCE" to Color(0xFF065F46),
    "SSC_CGL"  to Color(0xFFB45309),
    "RRB_NTPC" to Color(0xFF9F1239)
)

val FORMAT_ICONS = mapOf(
    "Statement Based"  to "📋",
    "Direct Fact"      to "⚡",
    "Assertion-Reason" to "🔗",
    "Match the Following" to "🔄",
    "Sequence Ordering" to "📊"
)

val TIER_COLORS = mapOf(
    "Basic"  to Color(0xFF16A34A),
    "Medium" to Color(0xFFD97706),
    "Hard"   to Color(0xFFDC2626)
)

// ─────────────────────────────────────────────────────────────────────────────
// Main Screen
// ─────────────────────────────────────────────────────────────────────────────

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun InvestorPreviewScreen(
    onBack: () -> Unit
) {
    val cdnBase = "https://raw.githubusercontent.com/CODE-ops-stack/my-new-ready-app/main/topics"
    val coroutineScope = rememberCoroutineScope()

    // State
    var selectedExamIdx by remember { mutableIntStateOf(0) }
    var selectedTopicId by remember { mutableIntStateOf(-1) }
    var selectedTier by remember { mutableStateOf("All") }
    var allQuestions by remember { mutableStateOf<List<PreviewQuestion>>(emptyList()) }
    var filteredQuestions by remember { mutableStateOf<List<PreviewQuestion>>(emptyList()) }
    var currentQIndex by remember { mutableIntStateOf(0) }
    var isLoading by remember { mutableStateOf(false) }
    var loadError by remember { mutableStateOf("") }
    var revealAnswer by remember { mutableStateOf(false) }
    var selectedOption by remember { mutableStateOf("") }
    var topicMeta by remember { mutableStateOf<List<PreviewTopic>>(emptyList()) }

    // Load topic metadata from manifest
    LaunchedEffect(Unit) {
        isLoading = true
        withContext(Dispatchers.IO) {
            try {
                val ts = System.currentTimeMillis()
                val manifestUrl = "https://raw.githubusercontent.com/CODE-ops-stack/my-new-ready-app/main/topics/manifest.json?cb=$ts"
                val manifest = JSONObject(URL(manifestUrl).readText())
                val topicsArr = manifest.optJSONArray("topics")
                val list = mutableListOf<PreviewTopic>()
                if (topicsArr != null) {
                    for (j in 0 until topicsArr.length()) {
                        val t = topicsArr.getJSONObject(j)
                        val tid = t.optInt("topicId", j + 1)
                        list.add(PreviewTopic(
                            topicId = tid,
                            topicName = TOPIC_NAMES[tid] ?: "Topic $tid",
                            totalCount = t.optInt("questionCount", 0),
                            basicCount = 0, mediumCount = 0, hardCount = 0
                        ))
                    }
                } else {
                    for (k in 1..30) {
                        list.add(PreviewTopic(k, TOPIC_NAMES[k] ?: "Topic $k", 0, 0, 0, 0))
                    }
                }
                topicMeta = list
            } catch (e: Exception) {
                loadError = "Cannot load topic list: ${e.message}"
            }
        }
        isLoading = false
    }

    // Load questions when topic selected
    fun loadTopic(topicId: Int) {
        coroutineScope.launch {
            isLoading = true
            loadError = ""
            revealAnswer = false
            selectedOption = ""
            currentQIndex = 0
            withContext(Dispatchers.IO) {
                try {
                    val ts = System.currentTimeMillis()
                    val url = "$cdnBase/topic_$topicId.json?cb=$ts"
                    val arr = JSONArray(URL(url).readText())
                    val list = mutableListOf<PreviewQuestion>()
                    for (j in 0 until arr.length()) {
                        val q = arr.getJSONObject(j)
                        val opts = q.optJSONObject("options") ?: JSONObject()
                        val dds = q.optJSONArray("distractorDissections")
                        val trapInfo = if (dds != null && dds.length() > 0) {
                            val dd0 = dds.optJSONObject(0)
                            val trapType = dd0?.optString("trapType", "") ?: ""
                            val dissection = dd0?.optString("dissection", "") ?: ""
                            if (trapType.isNotBlank()) "🪤 $trapType — $dissection" else ""
                        } else ""
                        list.add(PreviewQuestion(
                            id = q.optInt("id"),
                            stem = q.optString("stem", ""),
                            optA = opts.optString("opt_a", ""),
                            optB = opts.optString("opt_b", ""),
                            optC = opts.optString("opt_c", ""),
                            optD = opts.optString("opt_d", ""),
                            correctAnswer = q.optString("correctAnswer", "opt_a"),
                            explanation = q.optString("explanation", ""),
                            format = q.optString("format", "Direct Fact"),
                            tier = q.optString("tier", "Medium"),
                            examTarget = q.optString("examTarget", "UPSC_CSE"),
                            subTopic = q.optString("subTopic", ""),
                            trapInfo = trapInfo.take(300),
                            provenance = q.optString("provenance", "expert_authored")
                        ))
                    }
                    allQuestions = list
                } catch (e: Exception) {
                    loadError = "Failed to load topic $topicId: ${e.message}"
                }
            }
            isLoading = false
        }
    }

    // Filter questions when exam/tier filter changes
    LaunchedEffect(allQuestions, selectedExamIdx, selectedTier) {
        val examId = EXAM_IDS[selectedExamIdx]
        filteredQuestions = allQuestions.filter { q ->
            val examMatch = examId == "ALL" || q.examTarget == examId ||
                (examId == "UPSC_CSE" && q.examTarget.contains("UPSC")) ||
                (examId == "BPSC_CCE" && q.examTarget.contains("BPSC")) ||
                (examId == "SSC_CGL" && q.examTarget.contains("SSC")) ||
                (examId == "RRB_NTPC" && q.examTarget.contains("RRB"))
            val tierMatch = selectedTier == "All" || q.tier == selectedTier
            examMatch && tierMatch
        }.sortedBy { tierSortOrder(it.tier) }
        currentQIndex = 0
        revealAnswer = false
        selectedOption = ""
    }

    val bgColor = Color(0xFF0A0E1A)
    val cardBg = Color(0xFF111827)
    val goldColor = Color(0xFFD4AF37)
    val accentBlue = Color(0xFF3B82F6)

    Box(modifier = Modifier.fillMaxSize().background(bgColor)) {
        Column(modifier = Modifier.fillMaxSize().statusBarsPadding().navigationBarsPadding()) {
            // ── TOP BAR ──────────────────────────────────────────────────────
            Surface(color = Color(0xFF0D1117), shadowElevation = 8.dp) {
                Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 12.dp)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        IconButton(onClick = onBack) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, null, tint = Color.White)
                        }
                        Spacer(Modifier.width(8.dp))
                        Column(modifier = Modifier.weight(1f)) {
                            Text(
                                "🏆 Expert Question Preview",
                                color = goldColor,
                                fontWeight = FontWeight.Black,
                                fontSize = 18.sp,
                                letterSpacing = 0.3.sp
                            )
                            Text(
                                "5,551 Gold-Standard Questions • 30 Chapters • 4 Exams",
                                color = Color(0xFF9CA3AF),
                                fontSize = 11.sp,
                                letterSpacing = 0.5.sp
                            )
                        }
                        // Live badge
                        Surface(
                            color = Color(0xFF16A34A).copy(alpha = 0.2f),
                            shape = RoundedCornerShape(20.dp),
                            border = BorderStroke(1.dp, Color(0xFF16A34A))
                        ) {
                            Row(
                                modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Box(
                                    Modifier.size(6.dp).background(Color(0xFF16A34A), CircleShape)
                                )
                                Spacer(Modifier.width(4.dp))
                                Text("LIVE CDN", color = Color(0xFF16A34A), fontSize = 9.sp, fontWeight = FontWeight.Bold)
                            }
                        }
                    }

                    Spacer(Modifier.height(12.dp))

                    // ── EXAM FILTER CHIPS ─────────────────────────────────────
                    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        itemsIndexed(EXAM_LABELS) { idx, label ->
                            val examId = EXAM_IDS[idx]
                            val color = EXAM_COLORS[examId] ?: accentBlue
                            val selected = selectedExamIdx == idx
                            Surface(
                                onClick = { selectedExamIdx = idx },
                                color = if (selected) color else Color.Transparent,
                                shape = RoundedCornerShape(20.dp),
                                border = BorderStroke(1.dp, if (selected) color else Color(0xFF374151))
                            ) {
                                Text(
                                    label,
                                    modifier = Modifier.padding(horizontal = 14.dp, vertical = 6.dp),
                                    color = if (selected) Color.White else Color(0xFF9CA3AF),
                                    fontSize = 12.sp,
                                    fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal
                                )
                            }
                        }
                    }
                }
            }

            Row(modifier = Modifier.fillMaxSize()) {
                // ── LEFT SIDEBAR — TOPIC LIST ─────────────────────────────────
                Surface(
                    color = Color(0xFF0D1117),
                    modifier = Modifier.width(200.dp).fillMaxHeight()
                ) {
                    Column {
                        // Tier filter
                        Row(
                            modifier = Modifier.fillMaxWidth().padding(8.dp),
                            horizontalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            listOf("All", "Basic", "Medium", "Hard").forEach { tier ->
                                val tierColor = TIER_COLORS[tier] ?: accentBlue
                                val sel = selectedTier == tier
                                Surface(
                                    onClick = { selectedTier = tier },
                                    color = if (sel) tierColor.copy(alpha = 0.2f) else Color.Transparent,
                                    shape = RoundedCornerShape(4.dp),
                                    border = BorderStroke(1.dp, if (sel) tierColor else Color(0xFF1F2937)),
                                    modifier = Modifier.weight(1f)
                                ) {
                                    Text(
                                        tier.take(3),
                                        modifier = Modifier.padding(vertical = 4.dp).fillMaxWidth(),
                                        color = if (sel) tierColor else Color(0xFF6B7280),
                                        fontSize = 9.sp,
                                        textAlign = TextAlign.Center,
                                        fontWeight = if (sel) FontWeight.Bold else FontWeight.Normal
                                    )
                                }
                            }
                        }

                        HorizontalDivider(color = Color(0xFF1F2937))

                        LazyColumn {
                            if (topicMeta.isEmpty() && !isLoading) {
                                // Fallback
                                items(30) { idx ->
                                    val tid = idx + 1
                                    TopicSidebarItem(
                                        topicId = tid,
                                        name = TOPIC_NAMES[tid] ?: "Topic $tid",
                                        count = 0,
                                        isSelected = selectedTopicId == tid,
                                        examColor = EXAM_COLORS[EXAM_IDS[selectedExamIdx]] ?: accentBlue,
                                        onClick = {
                                            selectedTopicId = tid
                                            loadTopic(tid)
                                        }
                                    )
                                }
                            } else {
                                items(topicMeta) { topic ->
                                    TopicSidebarItem(
                                        topicId = topic.topicId,
                                        name = topic.topicName,
                                        count = topic.totalCount,
                                        isSelected = selectedTopicId == topic.topicId,
                                        examColor = EXAM_COLORS[EXAM_IDS[selectedExamIdx]] ?: accentBlue,
                                        onClick = {
                                            selectedTopicId = topic.topicId
                                            loadTopic(topic.topicId)
                                        }
                                    )
                                }
                            }
                        }
                    }
                }

                // ── RIGHT PANEL — QUESTION VIEWER ─────────────────────────────
                Box(modifier = Modifier.weight(1f).fillMaxHeight().padding(16.dp)) {
                    when {
                        isLoading -> {
                            Column(
                                modifier = Modifier.fillMaxSize(),
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Center
                            ) {
                                CircularProgressIndicator(color = goldColor, modifier = Modifier.size(48.dp))
                                Spacer(Modifier.height(16.dp))
                                Text("Loading from CDN...", color = Color(0xFF9CA3AF))
                            }
                        }

                        selectedTopicId == -1 -> {
                            WelcomePanel(goldColor = goldColor, accentBlue = accentBlue)
                        }

                        loadError.isNotBlank() -> {
                            Column(
                                modifier = Modifier.fillMaxSize(),
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Center
                            ) {
                                Icon(Icons.Default.Warning, null, tint = Color(0xFFEF4444), modifier = Modifier.size(48.dp))
                                Spacer(Modifier.height(8.dp))
                                Text(loadError, color = Color(0xFFEF4444), textAlign = TextAlign.Center)
                            }
                        }

                        filteredQuestions.isEmpty() -> {
                            Column(
                                modifier = Modifier.fillMaxSize(),
                                horizontalAlignment = Alignment.CenterHorizontally,
                                verticalArrangement = Arrangement.Center
                            ) {
                                Text("No questions match this filter.", color = Color(0xFF6B7280), fontSize = 16.sp)
                            }
                        }

                        else -> {
                            val q = filteredQuestions[currentQIndex]
                            QuestionPreviewCard(
                                question = q,
                                questionNumber = currentQIndex + 1,
                                totalQuestions = filteredQuestions.size,
                                revealAnswer = revealAnswer,
                                selectedOption = selectedOption,
                                onOptionSelected = { opt ->
                                    selectedOption = opt
                                    revealAnswer = true
                                },
                                onReveal = { revealAnswer = !revealAnswer },
                                onPrev = {
                                    if (currentQIndex > 0) {
                                        currentQIndex--
                                        revealAnswer = false
                                        selectedOption = ""
                                    }
                                },
                                onNext = {
                                    if (currentQIndex < filteredQuestions.size - 1) {
                                        currentQIndex++
                                        revealAnswer = false
                                        selectedOption = ""
                                    }
                                },
                                examColor = EXAM_COLORS[EXAM_IDS[selectedExamIdx]] ?: accentBlue,
                                goldColor = goldColor,
                                cardBg = cardBg
                            )
                        }
                    }
                }
            }
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Topic Sidebar Item
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun TopicSidebarItem(
    topicId: Int,
    name: String,
    count: Int,
    isSelected: Boolean,
    examColor: Color,
    onClick: () -> Unit
) {
    Surface(
        onClick = onClick,
        color = if (isSelected) examColor.copy(alpha = 0.15f) else Color.Transparent,
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Chapter number badge
            Surface(
                color = if (isSelected) examColor else Color(0xFF1F2937),
                shape = CircleShape,
                modifier = Modifier.size(22.dp)
            ) {
                Text(
                    "$topicId",
                    color = if (isSelected) Color.White else Color(0xFF6B7280),
                    fontSize = 9.sp,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.wrapContentSize(Alignment.Center),
                    textAlign = TextAlign.Center
                )
            }
            Spacer(Modifier.width(8.dp))
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    name,
                    color = if (isSelected) Color.White else Color(0xFF9CA3AF),
                    fontSize = 10.sp,
                    fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal,
                    maxLines = 2,
                    overflow = TextOverflow.Ellipsis,
                    lineHeight = 13.sp
                )
                if (count > 0) {
                    Text(
                        "$count Q",
                        color = if (isSelected) examColor else Color(0xFF4B5563),
                        fontSize = 9.sp
                    )
                }
            }
        }
    }
    HorizontalDivider(color = Color(0xFF1A2030), thickness = 0.5.dp)
}

// ─────────────────────────────────────────────────────────────────────────────
// Welcome Panel
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun WelcomePanel(goldColor: Color, accentBlue: Color) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(20.dp),
        contentPadding = PaddingValues(vertical = 40.dp)
    ) {
        item {
            Text("🏆", fontSize = 64.sp)
        }
        item {
            Text(
                "Gold-Standard Question Bank",
                color = goldColor,
                fontWeight = FontWeight.Black,
                fontSize = 22.sp,
                textAlign = TextAlign.Center
            )
        }
        item {
            Text(
                "5,551 Expert-Crafted Questions\nDesigned to guarantee 90%+ in Geography",
                color = Color(0xFF9CA3AF),
                textAlign = TextAlign.Center,
                lineHeight = 22.sp
            )
        }

        item {
            // Stats grid
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                StatCard("5,551", "Total Questions", accentBlue)
                StatCard("30", "Chapters", Color(0xFF8B5CF6))
                StatCard("4", "Exam Types", Color(0xFF16A34A))
            }
        }

        item {
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                StatCard("54%", "Statement Based", Color(0xFF1D4ED8))
                StatCard("34%", "Direct Fact", Color(0xFFD97706))
                StatCard("8%", "Assertion-Reason", Color(0xFF9F1239))
            }
        }

        item {
            Surface(
                color = goldColor.copy(alpha = 0.1f),
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(1.dp, goldColor.copy(alpha = 0.3f)),
                modifier = Modifier.fillMaxWidth(0.85f)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "← Select a chapter to preview",
                        color = goldColor,
                        fontWeight = FontWeight.Bold,
                        fontSize = 14.sp
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        "Filter by exam (UPSC / BPSC / SSC / RRB) and difficulty tier to see how precisely the question bank is calibrated to each exam's actual pattern.",
                        color = Color(0xFFD1D5DB),
                        fontSize = 12.sp,
                        lineHeight = 18.sp
                    )
                }
            }
        }
    }
}

@Composable
private fun StatCard(value: String, label: String, color: Color) {
    Surface(
        color = color.copy(alpha = 0.1f),
        shape = RoundedCornerShape(10.dp),
        border = BorderStroke(1.dp, color.copy(alpha = 0.3f)),
        modifier = Modifier.width(100.dp)
    ) {
        Column(
            modifier = Modifier.padding(12.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(value, color = color, fontWeight = FontWeight.Black, fontSize = 18.sp)
            Text(label, color = Color(0xFF9CA3AF), fontSize = 9.sp, textAlign = TextAlign.Center)
        }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Question Preview Card — The Showpiece
// ─────────────────────────────────────────────────────────────────────────────

@Composable
private fun QuestionPreviewCard(
    question: PreviewQuestion,
    questionNumber: Int,
    totalQuestions: Int,
    revealAnswer: Boolean,
    selectedOption: String,
    onOptionSelected: (String) -> Unit,
    onReveal: () -> Unit,
    onPrev: () -> Unit,
    onNext: () -> Unit,
    examColor: Color,
    goldColor: Color,
    cardBg: Color
) {
    val correctOptKey = question.correctAnswer
    val correctText = when (correctOptKey) {
        "opt_a" -> question.optA
        "opt_b" -> question.optB
        "opt_c" -> question.optC
        else -> question.optD
    }
    val optionLetters = listOf("A", "B", "C", "D")
    val optionKeys = listOf("opt_a", "opt_b", "opt_c", "opt_d")
    val optionTexts = listOf(question.optA, question.optB, question.optC, question.optD)

    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // ── Question Header ──────────────────────────────────────────────────
        item {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Format + Exam badges
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    // Format badge
                    val fmtIcon = FORMAT_ICONS[question.format] ?: "📝"
                    Surface(
                        color = examColor.copy(alpha = 0.15f),
                        shape = RoundedCornerShape(20.dp),
                        border = BorderStroke(1.dp, examColor.copy(alpha = 0.5f))
                    ) {
                        Text(
                            "$fmtIcon ${question.format}",
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                            color = examColor,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }

                    // Tier badge
                    val tierColor = TIER_COLORS[question.tier] ?: Color.Gray
                    Surface(
                        color = tierColor.copy(alpha = 0.15f),
                        shape = RoundedCornerShape(20.dp),
                        border = BorderStroke(1.dp, tierColor.copy(alpha = 0.5f))
                    ) {
                        Text(
                            question.tier,
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                            color = tierColor,
                            fontSize = 11.sp,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }

                // Q counter
                Text(
                    "$questionNumber / $totalQuestions",
                    color = Color(0xFF6B7280),
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium
                )
            }
        }

        // SubTopic tag
        if (question.subTopic.isNotBlank()) {
            item {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Default.Folder, null, tint = Color(0xFF4B5563), modifier = Modifier.size(12.dp))
                    Spacer(Modifier.width(4.dp))
                    Text(
                        question.subTopic,
                        color = Color(0xFF6B7280),
                        fontSize = 10.sp,
                        letterSpacing = 0.5.sp
                    )
                }
            }
        }

        // ── Stem Card ────────────────────────────────────────────────────────
        item {
            Surface(
                color = cardBg,
                shape = RoundedCornerShape(16.dp),
                border = BorderStroke(1.dp, Color(0xFF1F2937)),
                modifier = Modifier.fillMaxWidth()
            ) {
                Column(modifier = Modifier.padding(20.dp)) {
                    Text(
                        "Q$questionNumber",
                        color = goldColor.copy(alpha = 0.6f),
                        fontSize = 10.sp,
                        letterSpacing = 1.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(Modifier.height(8.dp))
                    Text(
                        question.stem,
                        color = Color(0xFFF3F4F6),
                        fontSize = 15.sp,
                        lineHeight = 24.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }

        // ── Options ──────────────────────────────────────────────────────────
        items(4) { idx ->
            val key = optionKeys[idx]
            val text = optionTexts[idx]
            val letter = optionLetters[idx]
            if (text.isBlank()) return@items

            val isSelected = selectedOption == key
            val isCorrect = key == correctOptKey
            val isWrong = isSelected && !isCorrect

            val bgColor: Color
            val borderColor: Color
            val textColor: Color

            when {
                revealAnswer && isCorrect -> {
                    bgColor = Color(0xFF16A34A).copy(alpha = 0.15f)
                    borderColor = Color(0xFF16A34A)
                    textColor = Color(0xFF86EFAC)
                }
                revealAnswer && isWrong -> {
                    bgColor = Color(0xFFDC2626).copy(alpha = 0.15f)
                    borderColor = Color(0xFFDC2626)
                    textColor = Color(0xFFFCA5A5)
                }
                isSelected -> {
                    bgColor = examColor.copy(alpha = 0.15f)
                    borderColor = examColor
                    textColor = Color.White
                }
                else -> {
                    bgColor = cardBg
                    borderColor = Color(0xFF1F2937)
                    textColor = Color(0xFFD1D5DB)
                }
            }

            Surface(
                onClick = { if (!revealAnswer) onOptionSelected(key) },
                color = bgColor,
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(1.dp, borderColor),
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(
                    modifier = Modifier.padding(14.dp),
                    verticalAlignment = Alignment.Top
                ) {
                    Surface(
                        color = borderColor.copy(alpha = 0.2f),
                        shape = CircleShape,
                        modifier = Modifier.size(26.dp)
                    ) {
                        Text(
                            letter,
                            color = borderColor,
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.wrapContentSize(Alignment.Center),
                            textAlign = TextAlign.Center
                        )
                    }
                    Spacer(Modifier.width(12.dp))
                    Text(text, color = textColor, fontSize = 13.sp, lineHeight = 20.sp, modifier = Modifier.weight(1f))
                    if (revealAnswer && isCorrect) {
                        Icon(Icons.Default.CheckCircle, null, tint = Color(0xFF16A34A), modifier = Modifier.size(20.dp))
                    }
                    if (revealAnswer && isWrong) {
                        Icon(Icons.Default.Close, null, tint = Color(0xFFDC2626), modifier = Modifier.size(20.dp))
                    }
                }
            }
        }

        // ── Reveal Button ────────────────────────────────────────────────────
        item {
            if (!revealAnswer) {
                Button(
                    onClick = onReveal,
                    modifier = Modifier.fillMaxWidth(),
                    colors = ButtonDefaults.buttonColors(containerColor = goldColor),
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(Icons.Default.Visibility, null, tint = Color.Black)
                    Spacer(Modifier.width(8.dp))
                    Text("Reveal Answer & Expert Analysis", color = Color.Black, fontWeight = FontWeight.Bold)
                }
            }
        }

        // ── Expert Analysis Panel ─────────────────────────────────────────────
        item {
            AnimatedVisibility(
                visible = revealAnswer,
                enter = fadeIn() + expandVertically()
            ) {
                Surface(
                    color = Color(0xFF052E16).copy(alpha = 0.8f),
                    shape = RoundedCornerShape(16.dp),
                    border = BorderStroke(1.dp, Color(0xFF16A34A).copy(alpha = 0.5f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(18.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
                        // Correct answer header
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.CheckCircle, null, tint = Color(0xFF16A34A), modifier = Modifier.size(20.dp))
                            Spacer(Modifier.width(8.dp))
                            Text(
                                "CORRECT: $correctText",
                                color = Color(0xFF86EFAC),
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp
                            )
                        }

                        HorizontalDivider(color = Color(0xFF16A34A).copy(alpha = 0.2f))

                        // Expert Explanation
                        Column {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Icon(Icons.Default.School, null, tint = Color(0xFF60A5FA), modifier = Modifier.size(14.dp))
                                Spacer(Modifier.width(6.dp))
                                Text(
                                    "EXPERT EXPLANATION",
                                    color = Color(0xFF60A5FA),
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Bold,
                                    letterSpacing = 1.sp
                                )
                            }
                            Spacer(Modifier.height(6.dp))
                            Text(
                                question.explanation,
                                color = Color(0xFFD1D5DB),
                                fontSize = 13.sp,
                                lineHeight = 21.sp
                            )
                        }

                        // Examiner Trap
                        if (question.trapInfo.isNotBlank()) {
                            Surface(
                                color = Color(0xFF7C2D12).copy(alpha = 0.4f),
                                shape = RoundedCornerShape(10.dp),
                                border = BorderStroke(1.dp, Color(0xFFF97316).copy(alpha = 0.4f)),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Column(modifier = Modifier.padding(12.dp)) {
                                    Text(
                                        "EXAMINER TRAP DECODED",
                                        color = Color(0xFFFBBF24),
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold,
                                        letterSpacing = 1.sp
                                    )
                                    Spacer(Modifier.height(4.dp))
                                    Text(
                                        question.trapInfo,
                                        color = Color(0xFFFED7AA),
                                        fontSize = 12.sp,
                                        lineHeight = 18.sp
                                    )
                                }
                            }
                        }
                    }
                }
            }
        }

        // ── Navigation ────────────────────────────────────────────────────────
        item {
            Row(
                modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                OutlinedButton(
                    onClick = onPrev,
                    enabled = questionNumber > 1,
                    border = BorderStroke(1.dp, if (questionNumber > 1) examColor else Color(0xFF374151)),
                    shape = RoundedCornerShape(10.dp)
                ) {
                    Icon(Icons.AutoMirrored.Filled.ArrowBack, null, tint = if (questionNumber > 1) examColor else Color(0xFF374151))
                    Spacer(Modifier.width(6.dp))
                    Text("Previous", color = if (questionNumber > 1) examColor else Color(0xFF374151))
                }

                // Progress dots
                Text(
                    "$questionNumber / $totalQuestions",
                    color = Color(0xFF4B5563),
                    fontSize = 12.sp,
                    modifier = Modifier.align(Alignment.CenterVertically)
                )

                Button(
                    onClick = onNext,
                    enabled = questionNumber < totalQuestions,
                    colors = ButtonDefaults.buttonColors(containerColor = if (questionNumber < totalQuestions) examColor else Color(0xFF1F2937)),
                    shape = RoundedCornerShape(10.dp)
                ) {
                    Text("Next", color = if (questionNumber < totalQuestions) Color.White else Color(0xFF374151))
                    Spacer(Modifier.width(6.dp))
                    Icon(Icons.AutoMirrored.Filled.ArrowForward, null, tint = if (questionNumber < totalQuestions) Color.White else Color(0xFF374151))
                }
            }
        }

        item { Spacer(Modifier.height(32.dp)) }
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper
// ─────────────────────────────────────────────────────────────────────────────

private fun tierSortOrder(tier: String) = when (tier) {
    "Basic" -> 0; "Medium" -> 1; else -> 2
}
