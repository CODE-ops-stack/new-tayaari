package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.PlayCircle
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.CartographicSerif
import com.example.ui.theme.DeepBasalt
import com.example.ui.theme.SunstoneGold
import com.example.ui.theme.HydrosphereCyan
import com.example.ui.theme.ContourEmerald

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RevisionDashboardScreen(
    dueCount: Int,
    onStartRevision: () -> Unit,
    onBack: () -> Unit
) {
    val lightText = Color(0xFFF8FAFC)

    com.example.ui.components.AtlasBackground {
      com.example.ui.components.TopographicBackground(lineColor = ContourEmerald.copy(alpha = 0.035f)) {
        Scaffold(
            topBar = {
                TopAppBar(
                    title = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Text("🧭", fontSize = 20.sp)
                            Spacer(modifier = Modifier.width(8.dp))
                            Column {
                                Text("Atlas Spaced Cadastre Revision", fontFamily = CartographicSerif, fontWeight = FontWeight.Bold, color = lightText, fontSize = 18.sp)
                                Text("Spaced Active Recall for Civil Services Geography", fontSize = 10.sp, color = lightText.copy(alpha = 0.7f))
                            }
                        }
                    },
                    navigationIcon = {
                        IconButton(onClick = onBack) {
                            Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = lightText)
                        }
                    },
                    colors = TopAppBarDefaults.topAppBarColors(containerColor = Color.Transparent)
                )
            },
            containerColor = Color.Transparent
        ) { padding ->
            LazyColumn(
                modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                item {
                    RevisionCard(
                        title = "Today's Cadastre Review 📍",
                        subtitle = "$dueCount Geographic Waypoints Due for Spaced Recall",
                        reason = "Reinforce vulnerable physical, Indian, and climatic concepts before forgetting occurs.",
                        count = dueCount,
                        icon = Icons.Filled.Schedule,
                        cardColor = DeepBasalt,
                        lightText = lightText,
                        accentGold = SunstoneGold,
                        onClick = {
                            if (dueCount > 0) onStartRevision()
                        }
                    )
                }
                item {
                    RevisionCard(
                        title = "High-Priority Hazard Points 🛡️",
                        subtitle = "Repeatedly Conflated Geomorphic & Climatic Traps",
                        reason = "Prioritized because you previously tripped on adjacent concepts or spatial inversion traps.",
                        count = null,
                        icon = Icons.Filled.Warning,
                        cardColor = DeepBasalt,
                        lightText = lightText,
                        accentGold = SunstoneGold,
                        onClick = onStartRevision
                    )
                }
                item {
                    RevisionCard(
                        title = "Expedition Continuity ⛰️",
                        subtitle = "Recently Surveyed Topographic Topics",
                        reason = "Solidify conceptual mastery of recently studied river basins, biomes, and rock strata.",
                        count = null,
                        icon = Icons.Filled.PlayCircle,
                        cardColor = DeepBasalt,
                        lightText = lightText,
                        accentGold = SunstoneGold,
                        onClick = onStartRevision
                    )
                }
            }
        }
      }
    }
}

@Composable
fun RevisionCard(
    title: String,
    subtitle: String,
    reason: String,
    count: Int?,
    icon: ImageVector,
    cardColor: Color,
    lightText: Color,
    accentGold: Color,
    onClick: () -> Unit
) {
    Card(
        modifier = Modifier.fillMaxWidth().clickable { onClick() },
        colors = CardDefaults.cardColors(containerColor = cardColor),
        shape = RoundedCornerShape(16.dp),
        border = BorderStroke(1.dp, HydrosphereCyan.copy(alpha = 0.25f)),
        elevation = CardDefaults.cardElevation(defaultElevation = 3.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
                modifier = Modifier.fillMaxWidth()
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .background(accentGold.copy(alpha = 0.15f), RoundedCornerShape(8.dp)),
                        contentAlignment = Alignment.Center
                    ) {
                        Icon(icon, contentDescription = null, tint = accentGold, modifier = Modifier.size(24.dp))
                    }
                    Spacer(modifier = Modifier.width(12.dp))
                    Column {
                        Text(title, fontWeight = FontWeight.Bold, color = lightText, fontSize = 16.sp, fontFamily = CartographicSerif)
                        Text(subtitle, fontSize = 12.sp, color = lightText.copy(alpha = 0.7f))
                    }
                }
                if (count != null) {
                    Surface(
                        color = if (count > 0) accentGold else Color.Gray.copy(alpha = 0.2f),
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text(
                            text = "$count DUE",
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                            fontSize = 12.sp,
                            fontWeight = FontWeight.Bold,
                            color = if (count > 0) Color.Black else lightText
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(12.dp))
            Text(reason, fontSize = 13.sp, color = lightText.copy(alpha = 0.8f), lineHeight = 18.sp)
        }
    }
}
