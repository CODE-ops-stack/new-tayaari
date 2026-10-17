package com.example.ui.components

import android.content.Context
import android.os.Build
import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ui.theme.*
import com.example.updater.AppUpdateManager

@Composable
fun InAppUpdateBanner(
    updateState: AppUpdateManager.UpdateState,
    onManualCheck: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current

    val hasInstallPermission = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
        context.packageManager.canRequestPackageInstalls()
    } else {
        true
    }

    // Show banner if active update state OR if one-time permission onboarding is needed
    val shouldShow = updateState !is AppUpdateManager.UpdateState.Idle || !hasInstallPermission

    AnimatedVisibility(
        visible = shouldShow,
        enter = fadeIn(),
        exit = fadeOut(),
        modifier = modifier
    ) {
        if (!hasInstallPermission && updateState is AppUpdateManager.UpdateState.Idle) {
            // One-Time Permission Onboarding ("Take permission for now")
            Surface(
                color = DeepBasalt,
                shape = RoundedCornerShape(12.dp),
                border = BorderStroke(1.5.dp, SunstoneGold.copy(alpha = 0.8f)),
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 6.dp)
                    .clickable { AppUpdateManager.requestInstallPermission(context) }
            ) {
                Row(
                    modifier = Modifier.padding(12.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = "⚡ ENABLE SILENT AUTO-UPDATES",
                            color = SunstoneGold,
                            fontWeight = FontWeight.Bold,
                            fontSize = 12.sp,
                            fontFamily = CoordinatesMonospace,
                            letterSpacing = 0.5.sp
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = "Grant 'Install unknown apps' once so future Geography curriculum updates install seamlessly in the background without prompting you again.",
                            color = AtlasParchment,
                            fontSize = 11.sp
                        )
                    }
                    Spacer(modifier = Modifier.width(8.dp))
                    Button(
                        onClick = { AppUpdateManager.requestInstallPermission(context) },
                        colors = ButtonDefaults.buttonColors(containerColor = SunstoneGold),
                        shape = RoundedCornerShape(8.dp),
                        contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                        modifier = Modifier.height(34.dp)
                    ) {
                        Text("Enable", color = AbyssNavy, fontWeight = FontWeight.Bold, fontSize = 11.sp)
                    }
                }
            }
        } else {
            when (updateState) {
                is AppUpdateManager.UpdateState.Checking -> {
                    Surface(
                        color = OceanicDark.copy(alpha = 0.95f),
                        shape = RoundedCornerShape(10.dp),
                        border = BorderStroke(1.dp, HydrosphereCyan.copy(alpha = 0.3f)),
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp)
                    ) {
                        Row(
                            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            CircularProgressIndicator(
                                color = GlacierAzure,
                                strokeWidth = 2.dp,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(10.dp))
                            Text(
                                text = "Checking cloud database for platform updates...",
                                color = GlacierAzure,
                                fontSize = 11.sp,
                                fontFamily = CoordinatesMonospace
                            )
                        }
                    }
                }

                is AppUpdateManager.UpdateState.Available -> {
                    Surface(
                        color = DeepBasalt,
                        shape = RoundedCornerShape(12.dp),
                        border = BorderStroke(1.dp, SunstoneGold),
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 6.dp)
                            .clickable { onManualCheck() }
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = "🚀 NEW PLATFORM UPDATE AVAILABLE (v${updateState.version})",
                                    color = SunstoneGold,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 12.sp,
                                    fontFamily = CoordinatesMonospace,
                                    letterSpacing = 0.5.sp
                                )
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = "Tap to automatically download & install Over-The-Air.",
                                    color = TopoContourMuted,
                                    fontSize = 11.sp
                                )
                            }
                            Button(
                                onClick = onManualCheck,
                                colors = ButtonDefaults.buttonColors(containerColor = SunstoneGold),
                                shape = RoundedCornerShape(8.dp),
                                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 4.dp),
                                modifier = Modifier.height(34.dp)
                            ) {
                                Text("Download", color = AbyssNavy, fontWeight = FontWeight.Bold, fontSize = 11.sp)
                            }
                        }
                    }
                }

                is AppUpdateManager.UpdateState.Downloading -> {
                    Surface(
                        color = DeepBasalt,
                        shape = RoundedCornerShape(12.dp),
                        border = BorderStroke(1.dp, GlacierAzure.copy(alpha = 0.6f)),
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp)
                    ) {
                        Column(modifier = Modifier.padding(12.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "⬇️ STREAMING GEOGRAPHY UPDATE OTA (${updateState.progressPercent}%)",
                                    color = GlacierAzure,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 11.sp,
                                    fontFamily = CoordinatesMonospace
                                )
                                val mbDownloaded = updateState.downloadedBytes / (1024 * 1024)
                                val mbTotal = updateState.totalBytes / (1024 * 1024)
                                Text(
                                    text = "${mbDownloaded}MB / ${mbTotal}MB",
                                    color = TopoContourMuted,
                                    fontSize = 10.sp,
                                    fontFamily = CoordinatesMonospace
                                )
                            }
                            Spacer(modifier = Modifier.height(8.dp))
                            LinearProgressIndicator(
                                progress = { updateState.progressPercent / 100f },
                                color = ContourEmerald,
                                trackColor = OceanicDark,
                                modifier = Modifier.fillMaxWidth().height(6.dp).clip(RoundedCornerShape(3.dp))
                            )
                        }
                    }
                }

                is AppUpdateManager.UpdateState.ReadyToInstall -> {
                    Surface(
                        color = DeepBasalt,
                        shape = RoundedCornerShape(12.dp),
                        border = BorderStroke(1.5.dp, ContourEmerald),
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 6.dp)
                            .clickable { AppUpdateManager.installApk(context, updateState.apkFile, updateState.version) }
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = "✨ UPDATE READY // v${updateState.version} DOWNLOADED",
                                    color = ContourEmerald,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 12.sp,
                                    fontFamily = CoordinatesMonospace,
                                    letterSpacing = 0.5.sp
                                )
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = "Tap here to install full Geography update now.",
                                    color = AtlasParchment,
                                    fontSize = 11.sp
                                )
                            }
                            Button(
                                onClick = { AppUpdateManager.installApk(context, updateState.apkFile, updateState.version) },
                                colors = ButtonDefaults.buttonColors(containerColor = ContourEmerald),
                                shape = RoundedCornerShape(8.dp),
                                contentPadding = PaddingValues(horizontal = 14.dp, vertical = 6.dp),
                                modifier = Modifier.height(36.dp)
                            ) {
                                Text("Install Now", color = AbyssNavy, fontWeight = FontWeight.Bold, fontSize = 12.sp)
                            }
                        }
                    }
                }

                is AppUpdateManager.UpdateState.Installing -> {
                    Surface(
                        color = DeepBasalt,
                        shape = RoundedCornerShape(12.dp),
                        border = BorderStroke(1.5.dp, ContourEmerald),
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 6.dp)
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            CircularProgressIndicator(
                                color = ContourEmerald,
                                strokeWidth = 2.5.dp,
                                modifier = Modifier.size(20.dp)
                            )
                            Spacer(modifier = Modifier.width(12.dp))
                            Column {
                                Text(
                                    text = "⚙️ SILENT UPDATE IN PROGRESS (v${updateState.version})",
                                    color = ContourEmerald,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 12.sp,
                                    fontFamily = CoordinatesMonospace
                                )
                                Text(
                                    text = "Android OS is finalizing background installation without prompts.",
                                    color = AtlasParchment,
                                    fontSize = 11.sp
                                )
                            }
                        }
                    }
                }

                is AppUpdateManager.UpdateState.PermissionRequired -> {
                    Surface(
                        color = DeepBasalt,
                        shape = RoundedCornerShape(12.dp),
                        border = BorderStroke(1.5.dp, SunstoneGold),
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 6.dp)
                            .clickable { AppUpdateManager.requestInstallPermission(context) }
                    ) {
                        Row(
                            modifier = Modifier.padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = "🔒 PERMISSION NEEDED // UPDATE DOWNLOADED",
                                    color = SunstoneGold,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 12.sp,
                                    fontFamily = CoordinatesMonospace,
                                    letterSpacing = 0.5.sp
                                )
                                Spacer(modifier = Modifier.height(2.dp))
                                Text(
                                    text = "Tap here to enable 'Install unknown apps' in Settings to complete installation.",
                                    color = AtlasParchment,
                                    fontSize = 11.sp
                                )
                            }
                            Button(
                                onClick = { AppUpdateManager.requestInstallPermission(context) },
                                colors = ButtonDefaults.buttonColors(containerColor = SunstoneGold),
                                shape = RoundedCornerShape(8.dp),
                                contentPadding = PaddingValues(horizontal = 12.dp, vertical = 6.dp),
                                modifier = Modifier.height(36.dp)
                            ) {
                                Text("Enable", color = AbyssNavy, fontWeight = FontWeight.Bold, fontSize = 11.sp)
                            }
                        }
                    }
                }

                is AppUpdateManager.UpdateState.Error -> {
                    Surface(
                        color = OceanicDark,
                        shape = RoundedCornerShape(10.dp),
                        border = BorderStroke(1.dp, MagmaCrimson.copy(alpha = 0.4f)),
                        modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp)
                    ) {
                        Row(
                            modifier = Modifier.padding(10.dp),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "⚠️ ${updateState.message}",
                                color = MagmaCrimson,
                                fontSize = 11.sp,
                                modifier = Modifier.weight(1f)
                            )
                            TextButton(
                                onClick = onManualCheck,
                                contentPadding = PaddingValues(horizontal = 8.dp, vertical = 2.dp)
                            ) {
                                Text("Retry", color = GlacierAzure, fontSize = 11.sp)
                            }
                        }
                    }
                }

                else -> Unit
            }
        }
    }
}
