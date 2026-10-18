package com.example.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.repository.AppThemeMode
import com.example.repository.FontScaleOption
import com.example.ui.theme.*

@Composable
fun AspirantSettingsDialog(
    themeMode: AppThemeMode,
    onThemeModeChange: (AppThemeMode) -> Unit,
    fontScaleOption: FontScaleOption,
    onFontScaleOptionChange: (FontScaleOption) -> Unit,
    isZenMode: Boolean,
    onZenModeChange: (Boolean) -> Unit,
    dailyTarget: Int = 20,
    onDailyTargetChange: (Int) -> Unit = {},
    showQuotaSection: Boolean = true,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        containerColor = MaterialTheme.colorScheme.surface,
        title = {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("⚙️", fontSize = 22.sp)
                Spacer(modifier = Modifier.width(8.dp))
                Column {
                    Text(
                        text = "Aspirant Field Ergonomics",
                        fontFamily = CartographicSerif,
                        fontWeight = FontWeight.Bold,
                        fontSize = 17.sp,
                        color = SunstoneGold
                    )
                    Text(
                        text = "Reading theme, typography & anti-panic focus",
                        fontSize = 11.sp,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        },
        text = {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp),
                verticalArrangement = Arrangement.spacedBy(14.dp)
            ) {
                // Section 1: Reading Theme
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(
                        text = "CARTOGRAPHIC READING THEME",
                        color = SunstoneGold,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.8.sp
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        val themes = listOf(
                            Triple(AppThemeMode.DARK, "🌑 Dark", "Basalt"),
                            Triple(AppThemeMode.LIGHT, "📜 Light", "Parchment"),
                            Triple(AppThemeMode.SEPIA, "🕯️ Sepia", "Lamp-Light")
                        )
                        themes.forEach { (mode, title, sub) ->
                            val isSelected = themeMode == mode
                            Surface(
                                modifier = Modifier
                                    .weight(1f)
                                    .clickable { onThemeModeChange(mode) },
                                shape = RoundedCornerShape(10.dp),
                                color = if (isSelected) SunstoneGold.copy(alpha = 0.18f) else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
                                border = BorderStroke(
                                    1.5.dp,
                                    if (isSelected) SunstoneGold else MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)
                                )
                            ) {
                                Column(
                                    modifier = Modifier.padding(vertical = 10.dp, horizontal = 4.dp),
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Text(
                                        text = title,
                                        fontSize = 11.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (isSelected) SunstoneGold else MaterialTheme.colorScheme.onSurface
                                    )
                                    Spacer(modifier = Modifier.height(2.dp))
                                    Text(
                                        text = sub,
                                        fontSize = 9.sp,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            }
                        }
                    }
                }

                // Section 2: Typography Scaler
                Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text(
                        text = "TYPOGRAPHY ZOOM (LEGIBILITY)",
                        color = SunstoneGold,
                        fontSize = 10.sp,
                        fontWeight = FontWeight.Black,
                        letterSpacing = 0.8.sp
                    )
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(8.dp)
                    ) {
                        val fontOptions = listOf(
                            Triple(FontScaleOption.NORMAL, "100%", "Standard"),
                            Triple(FontScaleOption.COMFORT, "115%", "Comfort"),
                            Triple(FontScaleOption.LARGE, "130%", "Enlarged")
                        )
                        fontOptions.forEach { (opt, percent, desc) ->
                            val isSelected = fontScaleOption == opt
                            Surface(
                                modifier = Modifier
                                    .weight(1f)
                                    .clickable { onFontScaleOptionChange(opt) },
                                shape = RoundedCornerShape(10.dp),
                                color = if (isSelected) HydrosphereCyan.copy(alpha = 0.18f) else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
                                border = BorderStroke(
                                    1.5.dp,
                                    if (isSelected) HydrosphereCyan else MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)
                                )
                            ) {
                                Column(
                                    modifier = Modifier.padding(vertical = 10.dp, horizontal = 4.dp),
                                    horizontalAlignment = Alignment.CenterHorizontally
                                ) {
                                    Text(
                                        text = percent,
                                        fontSize = 12.sp,
                                        fontWeight = FontWeight.Bold,
                                        color = if (isSelected) HydrosphereCyan else MaterialTheme.colorScheme.onSurface
                                    )
                                    Spacer(modifier = Modifier.height(2.dp))
                                    Text(
                                        text = desc,
                                        fontSize = 9.sp,
                                        color = MaterialTheme.colorScheme.onSurfaceVariant
                                    )
                                }
                            }
                        }
                    }
                }

                // Section 3: Zen Focus Mode (Anti-Panic)
                Surface(
                    shape = RoundedCornerShape(10.dp),
                    color = if (isZenMode) ContourEmerald.copy(alpha = 0.12f) else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
                    border = BorderStroke(1.dp, if (isZenMode) ContourEmerald.copy(alpha = 0.5f) else MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(
                        modifier = Modifier.padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Column(modifier = Modifier.weight(1f)) {
                            Row(verticalAlignment = Alignment.CenterVertically) {
                                Text("🧘", fontSize = 14.sp)
                                Spacer(modifier = Modifier.width(6.dp))
                                Text(
                                    text = "Zen Focus (Anti-Panic)",
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 12.sp,
                                    color = if (isZenMode) ContourEmerald else MaterialTheme.colorScheme.onSurface
                                )
                            }
                            Spacer(modifier = Modifier.height(3.dp))
                            Text(
                                text = "Hides countdown timer & combo streaks during practice to eliminate test anxiety.",
                                fontSize = 10.sp,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                lineHeight = 14.sp
                            )
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        Switch(
                            checked = isZenMode,
                            onCheckedChange = onZenModeChange,
                            colors = SwitchDefaults.colors(
                                checkedThumbColor = ContourEmerald,
                                checkedTrackColor = ContourEmerald.copy(alpha = 0.3f),
                                uncheckedThumbColor = TopoContourMuted,
                                uncheckedTrackColor = MaterialTheme.colorScheme.surfaceVariant
                            )
                        )
                    }
                }

                // Section 4: Daily Target Quota (Optional for in-practice screen)
                if (showQuotaSection) {
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            text = "DAILY QUESTION QUOTA",
                            color = SunstoneGold,
                            fontSize = 10.sp,
                            fontWeight = FontWeight.Black,
                            letterSpacing = 0.8.sp
                        )
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            val targets = listOf(10, 20, 30, 50)
                            targets.forEach { target ->
                                val isSelected = dailyTarget == target
                                Surface(
                                    modifier = Modifier
                                        .weight(1f)
                                        .clickable { onDailyTargetChange(target) },
                                    shape = RoundedCornerShape(8.dp),
                                    color = if (isSelected) SunstoneGold.copy(alpha = 0.2f) else MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f),
                                    border = BorderStroke(
                                        1.dp,
                                        if (isSelected) SunstoneGold else MaterialTheme.colorScheme.outline.copy(alpha = 0.3f)
                                    )
                                ) {
                                    Column(
                                        modifier = Modifier.padding(vertical = 8.dp),
                                        horizontalAlignment = Alignment.CenterHorizontally
                                    ) {
                                        Text(
                                            text = "$target",
                                            fontWeight = FontWeight.Bold,
                                            fontSize = 13.sp,
                                            color = if (isSelected) SunstoneGold else MaterialTheme.colorScheme.onSurface
                                        )
                                        Text(
                                            text = "MCQs",
                                            fontSize = 8.sp,
                                            color = MaterialTheme.colorScheme.onSurfaceVariant
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = onDismiss) {
                Text("Done", color = SunstoneGold, fontWeight = FontWeight.Bold)
            }
        }
    )
}
