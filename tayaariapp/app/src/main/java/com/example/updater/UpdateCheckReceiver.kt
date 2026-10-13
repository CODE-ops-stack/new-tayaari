package com.example.updater

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import java.io.File

class UpdateCheckReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        val action = intent.action
        Log.i("UpdateCheckReceiver", "Received broadcast action: $action")

        val pendingResult = goAsync()
        CoroutineScope(Dispatchers.IO).launch {
            try {
                if (action == "com.example.TRIGGER_UPDATE_NOTIFICATION") {
                    // Force display update notification immediately
                    val meta = AppUpdateManager.fetchCloudMetadata()
                    val version = meta?.version ?: 19
                    val questions = meta?.totalQuestions ?: 3942

                    val updatesDir = File(context.cacheDir, "updates")
                    val apkFile = File(updatesDir, "tayaari-update-v$version.apk")

                    UpdateNotificationHelper.showUpdateNotification(
                        context = context,
                        version = version,
                        totalQuestions = questions,
                        apkFile = if (apkFile.exists() && apkFile.length() > 0) apkFile else null
                    )
                } else {
                    // Background check when phone boots or alarm fires
                    val meta = AppUpdateManager.fetchCloudMetadata()
                    if (meta != null) {
                        val installedVersion = AppUpdateManager.getInstalledVersionCode(context)
                        if (meta.version > installedVersion) {
                            // Download APK in background if not already present
                            val state = AppUpdateManager.downloadAndPrepareApk(context, meta)
                            val apkFile = if (state is AppUpdateManager.UpdateState.ReadyToInstall) state.apkFile else null

                            UpdateNotificationHelper.showUpdateNotification(
                                context = context,
                                version = meta.version,
                                totalQuestions = meta.totalQuestions,
                                apkFile = apkFile
                            )
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e("UpdateCheckReceiver", "Background update check error", e)
            } finally {
                pendingResult.finish()
            }
        }
    }
}
