package com.example.ui.screens

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

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RevisionDashboardScreen(
    dueCount: Int,
    onStartRevision: () -> Unit,
    onBack: () -> Unit
) {
    val deepBlue = Color(0xFF0F172A)
    val accentGold = Color(0xFFEAB308)
    val cardColor = Color(0xFF1E293B)
    val lightText = Color(0xFFF8FAFC)

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Smart Revision", fontWeight = FontWeight.Bold, color = lightText) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Back", tint = lightText)
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = deepBlue)
            )
        },
        containerColor = deepBlue
    ) { padding ->
        LazyColumn(
            modifier = Modifier.fillMaxSize().padding(padding).padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                RevisionCard(
                    title = "Today's Revision",
                    subtitle = "Questions due today",
                    reason = "Due because you previously missed or need to review these questions.",
                    count = dueCount,
                    icon = Icons.Filled.Schedule,
                    cardColor = cardColor,
                    lightText = lightText,
                    accentGold = accentGold,
                    onClick = {
                        if (dueCount > 0) onStartRevision()
                    }
                )
            }
            item {
                RevisionCard(
                    title = "High Priority",
                    subtitle = "Repeated mistakes & weak traps",
                    reason = "Priority because you have made these traps multiple times.",
                    count = null,
                    icon = Icons.Filled.Warning,
                    cardColor = cardColor,
                    lightText = lightText,
                    accentGold = accentGold,
                    onClick = onStartRevision
                )
            }
            item {
                RevisionCard(
                    title = "Continue Learning",
                    subtitle = "Recently studied material",
                    reason = "Recently missed questions that you are improving on.",
                    count = null,
                    icon = Icons.Filled.PlayCircle,
                    cardColor = cardColor,
                    lightText = lightText,
                    accentGold = accentGold,
                    onClick = onStartRevision
                )
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
        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(icon, contentDescription = null, tint = accentGold, modifier = Modifier.size(28.dp))
                Spacer(modifier = Modifier.width(12.dp))
                Column(modifier = Modifier.weight(1f)) {
                    Text(title, fontSize = 18.sp, fontWeight = FontWeight.Bold, color = lightText)
                    Text(subtitle, fontSize = 14.sp, color = lightText.copy(alpha = 0.7f))
                }
                if (count != null) {
                    Surface(
                        color = accentGold,
                        shape = RoundedCornerShape(12.dp)
                    ) {
                        Text(
                            text = count.toString(),
                            fontWeight = FontWeight.Black,
                            color = Color.Black,
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(12.dp))
            Surface(
                color = Color.Black.copy(alpha = 0.2f),
                shape = RoundedCornerShape(8.dp),
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = reason,
                    fontSize = 12.sp,
                    color = lightText.copy(alpha = 0.6f),
                    modifier = Modifier.padding(12.dp)
                )
            }
        }
    }
}
