package com.example.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircleOutline
import androidx.compose.material.icons.filled.DeleteOutline
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.model.ExamQuestion
import com.example.model.MCQQuestion
import com.example.viewmodel.BookmarksViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BookmarksScreen(
    viewModel: BookmarksViewModel,
    onBack: () -> Unit
) {
    val questions by viewModel.bookmarkedQuestions.collectAsState()
    val availableTopics by viewModel.availableTopics.collectAsState()
    val selectedTopic by viewModel.selectedTopic.collectAsState()

    com.example.ui.components.AtlasBackground {
        com.example.ui.components.TopographicBackground(lineColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.035f)) {
            Scaffold(
                containerColor = Color.Transparent,
                topBar = {
                    TopAppBar(
                        title = { 
                            Column {
                                Text(
                                    "Saved Folios & Waypoints 📍",
                                    color = com.example.ui.theme.SummitGold,
                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 18.sp
                                )
                                Text(
                                    "FIELD CADASTRE REPOSITORY",
                                    color = com.example.ui.theme.GlacierAzure,
                                    fontFamily = com.example.ui.theme.CoordinatesMonospace,
                                    fontSize = 10.sp,
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
                            containerColor = com.example.ui.theme.OceanicDark.copy(alpha = 0.95f)
                        )
                    )
                }
            ) { paddingValues ->
                Column(
                    modifier = Modifier
                        .padding(paddingValues)
                        .fillMaxSize()
                ) {
                    Spacer(modifier = Modifier.height(8.dp))
                    Box(modifier = Modifier.padding(horizontal = 16.dp)) {
                        com.example.ui.components.CartographicCoordinatesBanner(
                            coordinatesText = "📍 GEOGRAPHIC FIELD FOLIO // ${questions.size} RECORDED WAYPOINTS"
                        )
                    }

                    if (availableTopics.size > 1) {
                        LazyRow(
                            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 10.dp),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            items(availableTopics) { topic ->
                                val isSelected = topic == selectedTopic
                                Surface(
                                    color = if (isSelected) com.example.ui.theme.DeepBasalt else com.example.ui.theme.OceanicDark,
                                    shape = RoundedCornerShape(8.dp),
                                    border = BorderStroke(
                                        1.dp, 
                                        if (isSelected) com.example.ui.theme.SunstoneGold else com.example.ui.theme.SlateBedrock
                                    ),
                                    modifier = Modifier.clickable { viewModel.filterByTopic(topic) }
                                ) {
                                    Text(
                                        text = "🗺️ $topic",
                                        color = if (isSelected) com.example.ui.theme.SummitGold else com.example.ui.theme.TopoContourMuted,
                                        fontSize = 12.sp,
                                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Medium,
                                        modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp)
                                    )
                                }
                            }
                        }
                    }

                    if (questions.isEmpty()) {
                        Box(modifier = Modifier.fillMaxSize().padding(32.dp), contentAlignment = Alignment.Center) {
                            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                                Text(
                                    text = "🧭",
                                    fontSize = 48.sp
                                )
                                Spacer(modifier = Modifier.height(12.dp))
                                Text(
                                    text = "No Field Waypoints Recorded", 
                                    fontFamily = com.example.ui.theme.CartographicSerif,
                                    color = com.example.ui.theme.AtlasParchment,
                                    fontSize = 18.sp,
                                    fontWeight = FontWeight.Bold
                                )
                                Spacer(modifier = Modifier.height(6.dp))
                                Text(
                                    text = "Tap the bookmark ribbon (🔖) during any expedition transect to save crucial map questions, diagrams, and memory keys to your folio.",
                                    color = com.example.ui.theme.TopoContourMuted,
                                    fontSize = 13.sp,
                                    lineHeight = 18.sp,
                                    textAlign = androidx.compose.ui.text.style.TextAlign.Center
                                )
                            }
                        }
                    } else {
                        LazyColumn(
                            modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp),
                            contentPadding = PaddingValues(top = 8.dp, bottom = 24.dp),
                            verticalArrangement = Arrangement.spacedBy(14.dp)
                        ) {
                            items(questions, key = { it.id }) { q ->
                                PremiumBookmarkCard(
                                    question = q,
                                    onRemove = { viewModel.removeBookmark(q.id) }
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun PremiumBookmarkCard(
    question: ExamQuestion,
    onRemove: () -> Unit
) {
    com.example.ui.components.AtlasCard(
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Top
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    val formatText = (question as? MCQQuestion)?.questionFormatType ?: "Direct Cartography"
                    Row(
                        horizontalArrangement = Arrangement.spacedBy(8.dp), 
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Surface(
                            color = com.example.ui.theme.OceanicDark,
                            shape = RoundedCornerShape(4.dp),
                            border = BorderStroke(1.dp, com.example.ui.theme.SlateBedrock)
                        ) {
                            Text(
                                text = "🧭 ${formatText.uppercase()}",
                                color = com.example.ui.theme.GlacierAzure,
                                fontSize = 10.sp,
                                fontFamily = com.example.ui.theme.CoordinatesMonospace,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.padding(horizontal = 6.dp, vertical = 2.dp)
                            )
                        }
                        Text(
                            text = "📍 ${question.chapterCode}",
                            color = com.example.ui.theme.SunstoneGold,
                            fontSize = 11.sp,
                            fontFamily = com.example.ui.theme.CoordinatesMonospace,
                            fontWeight = FontWeight.Bold
                        )
                    }
                }
                IconButton(onClick = onRemove, modifier = Modifier.size(24.dp)) {
                    Icon(
                        Icons.Filled.DeleteOutline, 
                        contentDescription = "Remove Bookmark", 
                        tint = com.example.ui.theme.MagmaCrimson
                    )
                }
            }
            
            Spacer(modifier = Modifier.height(12.dp))
            
            Text(
                text = question.questionText.trim(),
                color = com.example.ui.theme.AtlasParchment,
                fontFamily = com.example.ui.theme.CartographicSerif,
                fontSize = 15.sp,
                fontWeight = FontWeight.SemiBold,
                lineHeight = 22.sp
            )

            val mcq = question as? MCQQuestion
            if (mcq != null) {
                Spacer(modifier = Modifier.height(14.dp))
                val correctOption = mcq.options.find { it.id == mcq.correctAnswerId }
                
                Surface(
                    color = com.example.ui.theme.OceanicDark,
                    shape = RoundedCornerShape(10.dp),
                    border = BorderStroke(1.dp, com.example.ui.theme.ContourEmerald.copy(alpha = 0.5f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                Icons.Filled.CheckCircleOutline, 
                                contentDescription = null, 
                                tint = com.example.ui.theme.ContourEmerald, 
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = "SURVEYOR GENERAL KEY: ${correctOption?.text ?: "Unknown"}",
                                color = com.example.ui.theme.ContourEmerald,
                                fontSize = 13.sp,
                                fontWeight = FontWeight.Bold,
                                lineHeight = 18.sp
                            )
                        }
                        if (mcq.correctExplanation.isNotBlank()) {
                            Spacer(modifier = Modifier.height(6.dp))
                            Text(
                                text = "🗺️ ${mcq.correctExplanation}",
                                color = com.example.ui.theme.TopoContourMuted,
                                fontSize = 12.sp,
                                lineHeight = 17.sp
                            )
                        }
                    }
                }
            }
        }
    }
}
