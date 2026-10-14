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
import androidx.compose.ui.unit.sp
import com.example.viewmodel.ReadinessViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ReadinessEvidenceScreen(
    viewModel: ReadinessViewModel,
    onBack: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()

    com.example.ui.components.AtlasBackground {
      com.example.ui.components.TopographicBackground(lineColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.035f)) {
        Scaffold(
            containerColor = androidx.compose.ui.graphics.Color.Transparent,
            topBar = {
            TopAppBar(
                title = { 
                    Column {
                        Text(
                            "Field Readiness Radar 🧭", 
                            fontFamily = com.example.ui.theme.CartographicSerif,
                            fontWeight = FontWeight.Bold,
                            color = com.example.ui.theme.SummitGold,
                            fontSize = 18.sp
                        )
                        Text(
                            "GEODETIC READINESS AUDIT",
                            fontFamily = com.example.ui.theme.CoordinatesMonospace,
                            fontSize = 10.sp,
                            color = com.example.ui.theme.GlacierAzure,
                            letterSpacing = 1.sp
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack, 
                            contentDescription = "Back",
                            tint = com.example.ui.theme.AtlasParchment
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = com.example.ui.theme.OceanicDark.copy(alpha = 0.95f),
                    titleContentColor = com.example.ui.theme.SummitGold,
                    navigationIconContentColor = com.example.ui.theme.AtlasParchment
                )
            )
        }
    ) { padding ->
        if (uiState.isLoading) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator(color = com.example.ui.theme.GlacierAzure)
            }
        } else {
            LazyColumn(
                modifier = Modifier.padding(padding).padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    com.example.ui.components.CartographicCoordinatesBanner(
                        coordinatesText = "📍 BEHAVIORAL FIELD AUDIT // 4-PILLAR CADASTRE"
                    )
                    Spacer(modifier = Modifier.height(12.dp))
                    Text(
                        "Are You Summit Ready? ⛰️",
                        style = MaterialTheme.typography.headlineSmall,
                        fontFamily = com.example.ui.theme.CartographicSerif,
                        fontWeight = FontWeight.Bold,
                        color = com.example.ui.theme.AtlasParchment
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Text(
                        "Forget rank speculation. This radar provides empirical behavioral evidence of your real geodetic readiness across 4 crucial field pillars.",
                        style = MaterialTheme.typography.bodySmall,
                        color = com.example.ui.theme.TopoContourMuted
                    )
                }
                
                items(uiState.pillars) { pillar ->
                    val statusText = when (pillar.status) {
                        "STRONG" -> "🟢 SUMMIT READY"
                        "WATCH" -> "🟡 TOPOGRAPHIC WATCH"
                        "INSUFFICIENT DATA" -> "⚪ INSUFFICIENT DATA"
                        else -> "🔴 COURSE CORRECTION NEEDED"
                    }
                    val statusColor = when (pillar.status) {
                        "STRONG" -> com.example.ui.theme.ContourEmerald
                        "WATCH" -> com.example.ui.theme.SunstoneGold
                        "INSUFFICIENT DATA" -> com.example.ui.theme.MeridianMuted
                        else -> com.example.ui.theme.MagmaCrimson
                    }
                    val icon = when (pillar.status) {
                        "STRONG" -> Icons.Default.CheckCircle
                        "WATCH" -> Icons.Default.Warning
                        "INSUFFICIENT DATA" -> Icons.Default.Warning
                        else -> Icons.Default.Error
                    }

                    com.example.ui.components.AtlasCard(
                        modifier = Modifier.fillMaxWidth(),
                        borderColor = statusColor.copy(alpha = 0.4f)
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.weight(1f)) {
                                    Icon(icon, contentDescription = pillar.status, tint = statusColor, modifier = Modifier.size(20.dp))
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text(
                                        text = pillar.title,
                                        style = MaterialTheme.typography.titleMedium,
                                        fontFamily = com.example.ui.theme.CartographicSerif,
                                        fontWeight = FontWeight.Bold,
                                        color = com.example.ui.theme.AtlasParchment
                                    )
                                }
                                Surface(
                                    color = statusColor.copy(alpha = 0.15f),
                                    shape = androidx.compose.foundation.shape.RoundedCornerShape(6.dp),
                                    border = androidx.compose.foundation.BorderStroke(1.dp, statusColor.copy(alpha = 0.3f))
                                ) {
                                    Text(
                                        text = statusText,
                                        color = statusColor,
                                        fontFamily = com.example.ui.theme.CoordinatesMonospace,
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold,
                                        modifier = Modifier.padding(horizontal = 8.dp, vertical = 3.dp)
                                    )
                                }
                            }
                            Spacer(modifier = Modifier.height(8.dp))
                            Text(
                                pillar.description,
                                style = MaterialTheme.typography.bodySmall,
                                color = com.example.ui.theme.TopoContourMuted
                            )
                            Spacer(modifier = Modifier.height(12.dp))
                            pillar.evidence.forEach { ev ->
                                Text(
                                    "🧭 $ev",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = com.example.ui.theme.AtlasParchment.copy(alpha = 0.9f),
                                    modifier = Modifier.padding(bottom = 4.dp)
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
