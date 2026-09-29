package com.example.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.viewmodel.PaperTwinViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PaperTwinScreen(
    viewModel: PaperTwinViewModel,
    examId: String,
    onBack: () -> Unit,
    onStartTest: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Paper Twin") },
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
            if (uiState.paper == null && !uiState.isGenerating && uiState.error == null) {
                Text(
                    text = "Generate a highly-accurate synthetic mock exam matching the true tier distributions of $examId.",
                    style = MaterialTheme.typography.bodyLarge
                )
                Spacer(modifier = Modifier.height(24.dp))
                Button(onClick = { viewModel.generatePaper(examId, 50) }) {
                    Text("Generate Paper Twin (50 Qs)")
                }
            } else if (uiState.isGenerating) {
                CircularProgressIndicator()
                Spacer(modifier = Modifier.height(16.dp))
                Text("Analyzing blueprint and synthesizing questions...")
            } else if (uiState.error != null) {
                Text("Error: ${uiState.error}", color = MaterialTheme.colorScheme.error)
            } else if (uiState.paper != null) {
                val paper = uiState.paper!!
                Text("Paper Generated!", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                Spacer(modifier = Modifier.height(16.dp))
                
                Card(modifier = Modifier.fillMaxWidth().padding(16.dp)) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text("Validation Report", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                        Spacer(modifier = Modifier.height(8.dp))
                        Text("Status: ${if (paper.report.passedValidation) "PASSED" else "WARNING"}", color = if (paper.report.passedValidation) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error)
                        Text("Target Count: ${paper.report.targetCount}")
                        Text("Actual Count: ${paper.report.actualCount}")
                    }
                }
                
                Spacer(modifier = Modifier.height(24.dp))
                Button(onClick = onStartTest) {
                    Text("Start Mock Exam Now")
                }
            }
        }
    }
}
