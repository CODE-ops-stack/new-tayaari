package com.example.ui.mains

import androidx.compose.animation.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.automirrored.filled.ArrowForward
import androidx.compose.material.icons.automirrored.filled.MenuBook
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.*
import com.example.repository.MainsRepository
import kotlinx.coroutines.delay

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MainsPracticeScreen(
    questionId: String = "MAINS-Q1",
    mainsRepository: MainsRepository = remember { MainsRepository() },
    onNavigateQuestion: (String) -> Unit = {},
    onBack: () -> Unit = {}
) {
    val allQuestions = remember { mainsRepository.mainsQuestions }
    var currentQuestionId by remember(questionId) { mutableStateOf(questionId) }
    val currentIndex = remember(currentQuestionId) {
        allQuestions.indexOfFirst { it.id == currentQuestionId }.coerceAtLeast(0)
    }
    val question = remember(currentQuestionId) {
        mainsRepository.getQuestionById(currentQuestionId) ?: allQuestions.first()
    }

    // Stopwatch State (Allotted seconds based on question level: 7m, 11m, or 14m)
    var timeRemainingSeconds by remember { mutableIntStateOf(question.level.timeSeconds) }
    var isTimerRunning by remember { mutableStateOf(true) }

    // Interactive Tool Toggles
    var showSynapseBridge by remember { mutableStateOf(false) }
    var showFunAnalogy by remember { mutableStateOf(false) }
    var showDiagramCanvas by remember { mutableStateOf(false) }
    var showPhesgHud by remember { mutableStateOf(false) }
    var showModelSolution by remember { mutableStateOf(false) }

    // Selected P-H-E-S-G chips
    val selectedDimensions = remember { mutableStateMapOf<PhesgDimension, Boolean>() }

    // User Written Text & Evaluation State
    var userAnswerText by remember { mutableStateOf("") }
    var hasDiagramDrawn by remember { mutableStateOf(false) }
    var diagramStrokeAccuracy by remember { mutableFloatStateOf(0.85f) }
    var isEvaluating by remember { mutableStateOf(false) }
    var evaluationResult by remember { mutableStateOf<MainsEvaluationResult?>(null) }
    var attachedImagesCount by remember { mutableIntStateOf(0) }

    // Stopwatch Coroutine
    LaunchedEffect(isTimerRunning) {
        while (isTimerRunning && timeRemainingSeconds > 0) {
            delay(1000L)
            timeRemainingSeconds--
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "Mains Answer Architect",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "${question.chapterName} • ${question.level.label}",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                actions = {
                    // Stopwatch Pill
                    Surface(
                        shape = RoundedCornerShape(20.dp),
                        color = if (timeRemainingSeconds < 120) MaterialTheme.colorScheme.errorContainer else MaterialTheme.colorScheme.primaryContainer,
                        modifier = Modifier.padding(end = 12.dp)
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 6.dp)
                        ) {
                            Icon(
                                imageVector = if (isTimerRunning) Icons.Default.Timer else Icons.Default.Pause,
                                contentDescription = "Timer",
                                modifier = Modifier.size(16.dp),
                                tint = if (timeRemainingSeconds < 120) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            val minutes = timeRemainingSeconds / 60
                            val seconds = timeRemainingSeconds % 60
                            Text(
                                text = String.format("%02d:%02d", minutes, seconds),
                                style = MaterialTheme.typography.labelMedium,
                                fontWeight = FontWeight.ExtraBold,
                                color = if (timeRemainingSeconds < 120) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
                            )
                        }
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
                .padding(horizontal = 16.dp)
                .verticalScroll(rememberScrollState())
        ) {
            Spacer(modifier = Modifier.height(8.dp))

            // Metadata Chips (Marks, Words, Directive, PYQ)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                AssistChip(
                    onClick = {},
                    label = { Text("${question.level.marks} Marks • ${question.level.wordLimit}W") },
                    leadingIcon = { Icon(Icons.Default.Star, contentDescription = null, modifier = Modifier.size(14.dp)) }
                )
                AssistChip(
                    onClick = {},
                    label = { Text(question.directiveKeyword) },
                    colors = AssistChipDefaults.assistChipColors(containerColor = MaterialTheme.colorScheme.secondaryContainer.copy(alpha = 0.5f))
                )
                if (question.isPYQ) {
                    AssistChip(
                        onClick = {},
                        label = { Text(question.pyqYear ?: "PYQ") },
                        colors = AssistChipDefaults.assistChipColors(containerColor = MaterialTheme.colorScheme.tertiaryContainer)
                    )
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // The Question Card
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.6f)),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "QUESTION:",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.primary,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = question.questionText,
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.SemiBold,
                        lineHeight = 22.sp
                    )
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Tactical Pedagogy Quick-Action Buttons (Synapse, Diagram, Analogy, P-H-E-S-G)
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                // Synapse Bridge Button
                FilledTonalButton(
                    onClick = { showSynapseBridge = !showSynapseBridge },
                    shape = RoundedCornerShape(12.dp),
                    contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
                ) {
                    Icon(Icons.Default.ElectricBolt, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("⚡ Synapse", style = MaterialTheme.typography.labelSmall)
                }

                // 20s Micro-Diagram Canvas Button
                FilledTonalButton(
                    onClick = { showDiagramCanvas = !showDiagramCanvas },
                    shape = RoundedCornerShape(12.dp),
                    contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
                ) {
                    Icon(Icons.Default.Draw, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("📐 20s Diagram", style = MaterialTheme.typography.labelSmall)
                }

                // Fun Analogy Button
                FilledTonalButton(
                    onClick = { showFunAnalogy = !showFunAnalogy },
                    shape = RoundedCornerShape(12.dp),
                    contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
                ) {
                    Icon(Icons.Default.Lightbulb, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("💡 Analogy", style = MaterialTheme.typography.labelSmall)
                }

                // P-H-E-S-G HUD Button
                FilledTonalButton(
                    onClick = { showPhesgHud = !showPhesgHud },
                    shape = RoundedCornerShape(12.dp),
                    contentPadding = PaddingValues(horizontal = 10.dp, vertical = 6.dp)
                ) {
                    Icon(Icons.Default.Dashboard, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("P-H-E-S-G", style = MaterialTheme.typography.labelSmall)
                }
            }

            // Expandable: ⚡ Synapse Cross-Paper Bridge Card
            AnimatedVisibility(visible = showSynapseBridge) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF1E1B4B)), // Indigo deep
                    shape = RoundedCornerShape(14.dp)
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.ElectricBolt, contentDescription = null, tint = Color(0xFFA5B4FC), modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("⚡ Cross-Paper Synaptic Link (Paper 1 ⟷ Paper 2):", style = MaterialTheme.typography.labelMedium, color = Color(0xFFA5B4FC), fontWeight = FontWeight.Bold)
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        Text("• Paper 1 Theory Anchor: ${question.synapseBridge.paper1TheoreticalAnchor}", style = MaterialTheme.typography.bodySmall, color = Color.White)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("• Paper 2 Indian Context: ${question.synapseBridge.paper2IndianSpatialContext}", style = MaterialTheme.typography.bodySmall, color = Color.White)
                        Spacer(modifier = Modifier.height(4.dp))
                        Text("• Topper Quote Formula: \"${question.synapseBridge.topperQuoteFormula}\"", style = MaterialTheme.typography.bodySmall, color = Color(0xFFFDE68A), fontWeight = FontWeight.SemiBold)
                    }
                }
            }

            // Expandable: 💡 Fun Real-World Analogy Card
            AnimatedVisibility(visible = showFunAnalogy) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    colors = CardDefaults.cardColors(containerColor = Color(0xFF14532D)), // Forest green
                    shape = RoundedCornerShape(14.dp)
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(Icons.Default.Lightbulb, contentDescription = null, tint = Color(0xFF86EFAC), modifier = Modifier.size(18.dp))
                            Spacer(modifier = Modifier.width(6.dp))
                            Text("💡 First-Principles Fun Everyday Analogy:", style = MaterialTheme.typography.labelMedium, color = Color(0xFF86EFAC), fontWeight = FontWeight.Bold)
                        }
                        Spacer(modifier = Modifier.height(6.dp))
                        Text(text = question.funAnalogy, style = MaterialTheme.typography.bodySmall, color = Color.White, lineHeight = 18.sp)
                    }
                }
            }

            // Expandable: 📐 20-Second Micro-Diagram Interactive Ghost-Trace Canvas
            AnimatedVisibility(visible = showDiagramCanvas) {
                GhostTraceCanvas(
                    blueprint = question.microDiagram,
                    modifier = Modifier.padding(vertical = 8.dp),
                    onCompleted = { timeTaken, accuracy ->
                        hasDiagramDrawn = true
                        diagramStrokeAccuracy = accuracy
                    },
                    onDismiss = { showDiagramCanvas = false }
                )
            }

            // Expandable: 🧠 30-Second P-H-E-S-G Brainstorming HUD
            AnimatedVisibility(visible = showPhesgHud) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant),
                    shape = RoundedCornerShape(14.dp)
                ) {
                    Column(modifier = Modifier.padding(14.dp)) {
                        Text(
                            text = "🧠 30s P-H-E-S-G Dimensional Check (Tap to anchor):",
                            style = MaterialTheme.typography.labelMedium,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            PhesgDimension.values().forEach { dim ->
                                val isSelected = selectedDimensions[dim] == true
                                FilterChip(
                                    selected = isSelected,
                                    onClick = { selectedDimensions[dim] = !isSelected },
                                    label = { Text("${dim.code} - ${dim.title.split(" ").first()}") }
                                )
                            }
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Handwritten Page Scan & Answer Input Section
            Text(
                text = "📝 Aspirant's Answer Submission",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(6.dp))

            // Camera Scan & Attachment Banner
            Surface(
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                color = MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.4f),
                border = BorderStroke(1.dp, MaterialTheme.colorScheme.primary.copy(alpha = 0.3f))
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Default.CameraAlt, contentDescription = null, tint = MaterialTheme.colorScheme.primary)
                        Spacer(modifier = Modifier.width(10.dp))
                        Column {
                            Text(
                                text = if (attachedImagesCount > 0) "📷 $attachedImagesCount Answer Sheet(s) Attached" else "📷 Scan Real Paper Answer Sheets",
                                style = MaterialTheme.typography.labelMedium,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "Preserve pen & paper muscle memory • Multimodal OCR",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }

                    Button(
                        onClick = {
                            attachedImagesCount = (attachedImagesCount + 1).coerceAtMost(3)
                            hasDiagramDrawn = true
                        },
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp)
                    ) {
                        Text(if (attachedImagesCount == 0) "Scan Paper" else "+ Add Page")
                    }
                }
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Text Draft Editor / Voice Dictation Input
            OutlinedTextField(
                value = userAnswerText,
                onValueChange = { userAnswerText = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(160.dp),
                placeholder = {
                    Text(
                        text = "Or type / transcribe your answer outline here...\n(Include theorists like Alfred Weber, D.M. Smith, Material Index, sucrose metrics, etc.)",
                        style = MaterialTheme.typography.bodySmall
                    )
                },
                shape = RoundedCornerShape(12.dp)
            )

            Spacer(modifier = Modifier.height(16.dp))

            // Submit for Chief Examiner Evaluation Button
            Button(
                onClick = {
                    isEvaluating = true
                    // Simulate fast evaluation call against Chief Evaluator Rubric
                    val textToEvaluate = if (userAnswerText.isNotBlank()) userAnswerText else {
                        "Alfred Weber Least Cost Theory with Material Index MI formula. Steel plants shifted to coastal ports like Vizag and Hazira due to imported Australian coking coal. Sugar mills shifted to Maharashtra due to higher sucrose recovery 12% and cooperative bagasse cogeneration. D.M. Smith spatial margins to profitability."
                    }
                    val result = mainsRepository.evaluateAnswer(
                        questionId = question.id,
                        userWrittenText = textToEvaluate,
                        hasDiagramDrawn = hasDiagramDrawn || attachedImagesCount > 0,
                        diagramStrokeAccuracy = diagramStrokeAccuracy,
                        timeTakenSeconds = question.level.timeSeconds - timeRemainingSeconds
                    )
                    evaluationResult = result
                    isEvaluating = false
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(50.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(Icons.Default.Analytics, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text("🚀 Submit for Chief Examiner Evaluation", fontWeight = FontWeight.Bold)
            }

            Spacer(modifier = Modifier.height(10.dp))

            // Part II Master Solution Reveal Toggle
            OutlinedButton(
                onClick = { showModelSolution = !showModelSolution },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(48.dp),
                shape = RoundedCornerShape(12.dp)
            ) {
                Icon(Icons.AutoMirrored.Filled.MenuBook, contentDescription = null, modifier = Modifier.size(18.dp))
                Spacer(modifier = Modifier.width(8.dp))
                Text(if (showModelSolution) "Hide Master Model Solution" else "📖 Reveal Part II Master Model Solution")
            }

            // Master Model Solution Content (Part II)
            AnimatedVisibility(visible = showModelSolution) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 12.dp),
                    colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
                    shape = RoundedCornerShape(16.dp),
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.primary.copy(alpha = 0.3f))
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = "📖 PART II: MASTER EVALUATOR SOLUTION",
                            style = MaterialTheme.typography.titleSmall,
                            fontWeight = FontWeight.Black,
                            color = MaterialTheme.colorScheme.primary
                        )
                        Spacer(modifier = Modifier.height(8.dp))

                        Text(
                            text = "📐 30-Second Micro-Structure Blueprint:",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold
                        )
                        question.microStructureBlueprint.forEach { step ->
                            Text(text = "• $step", style = MaterialTheme.typography.bodySmall, fontSize = 12.sp, modifier = Modifier.padding(start = 4.dp, top = 2.dp))
                        }

                        Spacer(modifier = Modifier.height(12.dp))

                        Text(
                            text = "📝 Topper Model Answer Text:",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold
                        )
                        Spacer(modifier = Modifier.height(4.dp))
                        Text(
                            text = question.modelAnswerText,
                            style = MaterialTheme.typography.bodySmall,
                            fontSize = 12.sp,
                            lineHeight = 17.sp,
                            fontFamily = FontFamily.SansSerif
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(14.dp))

            // Seamless Question Navigation (Previous / Current of Total / Next)
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 6.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                OutlinedButton(
                    onClick = {
                        if (currentIndex > 0) {
                            val prevId = allQuestions[currentIndex - 1].id
                            currentQuestionId = prevId
                            timeRemainingSeconds = allQuestions[currentIndex - 1].level.timeSeconds
                            isTimerRunning = true
                            userAnswerText = ""
                            hasDiagramDrawn = false
                            showModelSolution = false
                            showSynapseBridge = false
                            showFunAnalogy = false
                            showDiagramCanvas = false
                            showPhesgHud = false
                            evaluationResult = null
                            selectedDimensions.clear()
                            onNavigateQuestion(prevId)
                        }
                    },
                    enabled = currentIndex > 0,
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = null, modifier = Modifier.size(16.dp))
                    Spacer(modifier = Modifier.width(6.dp))
                    Text("Previous", fontSize = 13.sp)
                }

                Surface(
                    shape = RoundedCornerShape(16.dp),
                    color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.7f),
                    border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant)
                ) {
                    Text(
                        text = "Question ${currentIndex + 1} of ${allQuestions.size}",
                        style = MaterialTheme.typography.labelMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary,
                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                    )
                }

                OutlinedButton(
                    onClick = {
                        if (currentIndex < allQuestions.size - 1) {
                            val nextId = allQuestions[currentIndex + 1].id
                            currentQuestionId = nextId
                            timeRemainingSeconds = allQuestions[currentIndex + 1].level.timeSeconds
                            isTimerRunning = true
                            userAnswerText = ""
                            hasDiagramDrawn = false
                            showModelSolution = false
                            showSynapseBridge = false
                            showFunAnalogy = false
                            showDiagramCanvas = false
                            showPhesgHud = false
                            evaluationResult = null
                            selectedDimensions.clear()
                            onNavigateQuestion(nextId)
                        }
                    },
                    enabled = currentIndex < allQuestions.size - 1,
                    shape = RoundedCornerShape(12.dp)
                ) {
                    Text("Next", fontSize = 13.sp)
                    Spacer(modifier = Modifier.width(6.dp))
                    Icon(Icons.AutoMirrored.Filled.ArrowForward, contentDescription = null, modifier = Modifier.size(16.dp))
                }
            }

            Spacer(modifier = Modifier.height(28.dp))
        }
    }

    // Modal Evaluation Report Card
    evaluationResult?.let { result ->
        MainsEvaluationResultDialog(
            result = result,
            onDismiss = { evaluationResult = null },
            onReattempt = {
                evaluationResult = null
                userAnswerText = ""
                timeRemainingSeconds = question.level.timeSeconds
                isTimerRunning = true
            },
            onRevealModelAnswer = {
                evaluationResult = null
                showModelSolution = true
            }
        )
    }
}
