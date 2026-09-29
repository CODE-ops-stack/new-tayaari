package com.example.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Error
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.viewmodel.MistakeReplayViewModel
import com.example.viewmodel.ReplayState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MistakeReplayScreen(
    viewModel: MistakeReplayViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Mistake Replay") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primary,
                    titleContentColor = MaterialTheme.colorScheme.onPrimary,
                    navigationIconContentColor = MaterialTheme.colorScheme.onPrimary
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier.padding(padding).padding(16.dp).fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            when (uiState.currentState) {
                ReplayState.LOADING -> {
                    CircularProgressIndicator()
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("Finding highest priority mistake...")
                }
                ReplayState.NO_CANDIDATES -> {
                    Icon(Icons.Default.CheckCircle, contentDescription = "Clear", modifier = Modifier.size(64.dp), tint = MaterialTheme.colorScheme.primary)
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("All Clear!", style = MaterialTheme.typography.headlineMedium)
                    Text("You have no pending mistakes to replay.", color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
                ReplayState.REVIEW_MISTAKE -> {
                    val candidate = uiState.candidate!!
                    Text("Mistake Detected", style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.error)
                    Spacer(modifier = Modifier.height(16.dp))
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text("Type: ${candidate.evidenceType}", fontWeight = FontWeight.Bold)
                            Text("Context: ${candidate.context}")
                            Spacer(modifier = Modifier.height(16.dp))
                            Text("Original Question:", fontWeight = FontWeight.Bold)
                            Text(candidate.originalQuestion.questionText)
                        }
                    }
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(onClick = { viewModel.commitToRepair() }) {
                        Text("Begin Repair (${candidate.repairRoute})")
                    }
                }
                ReplayState.REPAIR -> {
                    val candidate = uiState.candidate!!
                    Text("Concept Repair", style = MaterialTheme.typography.headlineSmall)
                    Spacer(modifier = Modifier.height(16.dp))
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text("Review the core concept you missed:", fontWeight = FontWeight.Bold)
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(candidate.originalQuestion.explanation ?: "Review the standard solution for this topic.")
                        }
                    }
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(onClick = { viewModel.proceedToAlternate() }) {
                        Text("Test My Transfer")
                    }
                }
                ReplayState.ALTERNATE_QUESTION -> {
                    val altQuestion = uiState.alternateQuestion!!
                    Text("Transfer Test", style = MaterialTheme.typography.headlineSmall, color = MaterialTheme.colorScheme.primary)
                    Spacer(modifier = Modifier.height(16.dp))
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(altQuestion.questionText)
                            Spacer(modifier = Modifier.height(16.dp))
                            val options = uiState.altOptions
                            options.forEachIndexed { index, opt ->
                                Row(
                                    modifier = Modifier.fillMaxWidth().padding(vertical = 4.dp),
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    RadioButton(
                                        selected = uiState.selectedOptionIndex == index,
                                        onClick = { viewModel.selectOption(index) }
                                    )
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(opt)
                                }
                            }
                        }
                    }
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(
                        onClick = { 
                            val isCorrect = (uiState.selectedOptionIndex == uiState.altCorrectIndex)
                            viewModel.submitAlternateAnswer(isCorrect)
                        },
                        enabled = uiState.selectedOptionIndex != null
                    ) {
                        Text("Submit")
                    }
                }
                ReplayState.RESULT -> {
                    val improved = uiState.outcomeState == "IMPROVED"
                    Icon(
                        imageVector = if (improved) Icons.Default.CheckCircle else Icons.Default.Error,
                        contentDescription = "Result",
                        modifier = Modifier.size(64.dp),
                        tint = if (improved) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = if (improved) "Repair Successful!" else "Still Struggling",
                        style = MaterialTheme.typography.headlineMedium
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("Next Action: ${uiState.nextBestAction}")
                    Spacer(modifier = Modifier.height(24.dp))
                    Button(onClick = { viewModel.loadCandidate() }) {
                        Text("Next Mistake")
                    }
                }
            }
        }
    }
}

