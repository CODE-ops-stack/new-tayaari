package com.example.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.filled.Error
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.example.viewmodel.ReadinessViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReadinessEvidenceScreen(
    viewModel: ReadinessViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Pre-Exam Readiness") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface,
                    titleContentColor = MaterialTheme.colorScheme.primary,
                    navigationIconContentColor = MaterialTheme.colorScheme.primary
                )
            )
        }
    ) { padding ->
        if (uiState.isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier.padding(padding).padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    Text(
                        "Are you actually ready?",
                        style = MaterialTheme.typography.headlineMedium,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        "Do not rely on rank prediction. This dashboard provides concrete behavioral evidence of your exam readiness.",
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                }
                
                items(uiState.pillars) { pillar ->
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                val icon = when (pillar.status) {
                                    "STRONG" -> Icons.Default.CheckCircle
                                    "WATCH" -> Icons.Default.Warning
                                    "INSUFFICIENT DATA" -> Icons.Default.Warning
                                    else -> Icons.Default.Error
                                }
                                val color = when (pillar.status) {
                                    "STRONG" -> MaterialTheme.colorScheme.primary
                                    "WATCH" -> MaterialTheme.colorScheme.tertiary
                                    "INSUFFICIENT DATA" -> androidx.compose.ui.graphics.Color.Gray
                                    else -> MaterialTheme.colorScheme.error
                                }
                                Icon(icon, contentDescription = pillar.status, tint = color)
                                Spacer(modifier = Modifier.width(8.dp))
                                Text(pillar.title, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, color = color)
                            }
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(pillar.description, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            Spacer(modifier = Modifier.height(12.dp))
                            pillar.evidence.forEach { ev ->
                                Text("• $ev", style = MaterialTheme.typography.bodyMedium, modifier = Modifier.padding(bottom = 4.dp))
                            }
                        }
                    }
                }
            }
        }
    }
}




