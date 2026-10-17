package com.example.ui.game

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.EmojiEvents
import androidx.compose.material.icons.filled.Flag
import androidx.compose.material.icons.filled.Speed
import androidx.compose.material.icons.filled.Terrain
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import com.example.model.TestUiState
import com.example.ui.theme.*

@Composable
fun SummitTriumphDialog(
    uiState: TestUiState,
    onDismiss: () -> Unit,
    onRestart: () -> Unit
) {
    Dialog(
        onDismissRequest = onDismiss,
        properties = DialogProperties(dismissOnBackPress = true, dismissOnClickOutside = false)
    ) {
        Surface(
            color = DeepBasalt,
            shape = RoundedCornerShape(20.dp),
            border = BorderStroke(2.dp, SunstoneGold),
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Column(
                modifier = Modifier.padding(20.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Summit Gold Medal Icon
                Box(
                    modifier = Modifier
                        .size(64.dp)
                        .clip(CircleShape)
                        .background(SunstoneGold.copy(alpha = 0.2f))
                        .padding(12.dp),
                    contentAlignment = Alignment.Center
                ) {
                    Icon(
                        imageVector = Icons.Default.EmojiEvents,
                        contentDescription = "Summit Trophy",
                        tint = SunstoneGold,
                        modifier = Modifier.size(36.dp)
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))

                Text(
                    text = "🏆 HIMALAYAN SUMMIT CONQUERED!",
                    color = SunstoneGold,
                    fontSize = 16.sp,
                    fontWeight = FontWeight.Black,
                    fontFamily = CoordinatesMonospace,
                    letterSpacing = 0.8.sp,
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.height(4.dp))

                Text(
                    text = "Expedition Transect Completed with High-Stakes Velocity",
                    color = TopoContourMuted,
                    fontSize = 11.sp,
                    textAlign = TextAlign.Center
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Stats Grid
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    // Altitude Card
                    Surface(
                        color = OceanicDark,
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier.weight(1f).padding(end = 4.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(10.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text("PEAK ALTITUDE", color = TopoContourMuted, fontSize = 9.sp, fontFamily = CoordinatesMonospace)
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                "%,dm".format(uiState.currentAltitudeMeters),
                                color = ContourEmerald,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    // Accuracy Card
                    Surface(
                        color = OceanicDark,
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier.weight(1f).padding(horizontal = 4.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(10.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text("ACCURACY", color = TopoContourMuted, fontSize = 9.sp, fontFamily = CoordinatesMonospace)
                            Spacer(modifier = Modifier.height(2.dp))
                            val accPercent = if (uiState.totalQuestionsInSet > 0) {
                                (uiState.totalCorrectCount * 100) / uiState.totalQuestionsInSet
                            } else 100
                            Text(
                                "$accPercent%",
                                color = GlacierAzure,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }

                    // Best Streak Card
                    Surface(
                        color = OceanicDark,
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier.weight(1f).padding(start = 4.dp)
                    ) {
                        Column(
                            modifier = Modifier.padding(10.dp),
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Text("BEST COMBO", color = TopoContourMuted, fontSize = 9.sp, fontFamily = CoordinatesMonospace)
                            Spacer(modifier = Modifier.height(2.dp))
                            Text(
                                "${maxOf(uiState.bestStreak, uiState.comboMultiplier)}x",
                                color = SunstoneGold,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Ranker Geodetic Badge
                Surface(
                    color = SunstoneGold.copy(alpha = 0.12f),
                    shape = RoundedCornerShape(10.dp),
                    border = BorderStroke(1.dp, SunstoneGold.copy(alpha = 0.4f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(10.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Icon(Icons.Default.Terrain, contentDescription = null, tint = SunstoneGold, modifier = Modifier.size(20.dp))
                        Spacer(modifier = Modifier.width(8.dp))
                        Column {
                            Text(
                                text = "RANKER'S CADASTRE BADGE UNLOCKED",
                                color = SunstoneGold,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold,
                                fontFamily = CoordinatesMonospace
                            )
                            Text(
                                text = "All ${uiState.totalQuestionsInSet} waypoints surveyed without persistent database footprints.",
                                color = AtlasParchment,
                                fontSize = 10.sp
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(20.dp))

                // Action Buttons
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(
                        onClick = onRestart,
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier.weight(1f).height(42.dp),
                        colors = ButtonDefaults.outlinedButtonColors(contentColor = GlacierAzure)
                    ) {
                        Text("Climb Again", fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    }

                    Button(
                        onClick = onDismiss,
                        shape = RoundedCornerShape(10.dp),
                        modifier = Modifier.weight(1f).height(42.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = SunstoneGold)
                    ) {
                        Text("Review Test", color = AbyssNavy, fontSize = 11.sp, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}
