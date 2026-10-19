package com.example.updater

import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.content.pm.PackageInstaller
import android.net.Uri
import android.os.Build
import android.provider.Settings
import android.util.Log
import androidx.core.content.FileProvider
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.TimeUnit

/**
 * AppUpdateManager
 *
 * Provides autonomous, wireless Over-The-Air (OTA) APK updates for Android devices
 * operating without physical PC/cable connections.
 *
 * Unattended / Silent Architecture:
 * 1. Proactive permission onboarding: prompts user ONCE to grant "Install unknown apps" ("take permission for now").
 * 2. Unattended background updates: once permission is granted, uses Android 12+ (API 31+) PackageInstaller
 *    session with `USER_ACTION_NOT_REQUIRED` to stream and commit updates completely silently ("auto update without permission").
 * 3. Fallback: on Android < 12 or if permission not yet granted, gracefully falls back to the system 1-tap confirmation.
 */
object AppUpdateManager {

    private const val TAG = "AppUpdateManager"

    // Default baseline version
    const val CURRENT_APP_VERSION = 1

    fun getInstalledVersionCode(context: Context): Int {
        return try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                context.packageManager.getPackageInfo(context.packageName, 0).longVersionCode.toInt()
            } else {
                @Suppress("DEPRECATION")
                context.packageManager.getPackageInfo(context.packageName, 0).versionCode
            }
        } catch (e: Exception) {
            CURRENT_APP_VERSION
        }
    }

    private const val RAW_METADATA_URL = "https://raw.githubusercontent.com/CODE-ops-stack/my-new-ready-app/main/metadata.json"
    private const val CDN_METADATA_URL = "https://cdn.jsdelivr.net/gh/CODE-ops-stack/my-new-ready-app@main/metadata.json"

    private val client = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()

    data class CloudMetadata(
        val version: com.google.gson.JsonElement? = null,
        val versionCode: Int? = null,
        val totalQuestions: Int = 0,
        val apkSha256: String? = null,
        val apkSizeBytes: Long? = null,
        val apkDownloadUrl: String = "",
        val releaseNotes: String? = null
    ) {
        val resolvedVersionCode: Int
            get() {
                if (versionCode != null && versionCode > 0) return versionCode
                if (version != null) {
                    try {
                        if (version.isJsonPrimitive) {
                            val prim = version.asJsonPrimitive
                            if (prim.isNumber) return prim.asInt
                            if (prim.isString) {
                                val s = prim.asString
                                val digitsOnly = s.replace(Regex("[^0-9.]"), "").substringBefore(".")
                                return digitsOnly.toIntOrNull() ?: 1
                            }
                        }
                    } catch (e: Exception) {
                        Log.w(TAG, "Error parsing version element: ${e.message}")
                    }
                }
                return 1
            }
    }

    sealed class UpdateState {
        object Idle : UpdateState()
        object Checking : UpdateState()
        data class Available(
            val version: Int,
            val releaseNotes: String,
            val sizeBytes: Long,
            val downloadUrl: String
        ) : UpdateState()
        data class Downloading(
            val progressPercent: Int,
            val downloadedBytes: Long,
            val totalBytes: Long
        ) : UpdateState()
        data class ReadyToInstall(
            val apkFile: File,
            val version: Int
        ) : UpdateState()
        data class Installing(
            val version: Int
        ) : UpdateState()
        data class PermissionRequired(
            val apkFile: File,
            val version: Int
        ) : UpdateState()
        data class Error(val message: String) : UpdateState()
    }

    private val _updateState = MutableStateFlow<UpdateState>(UpdateState.Idle)
    val updateState = _updateState.asStateFlow()

    private val updateMutex = Mutex()

    /**
     * Checks cloud metadata on app launch, resume, or background alarm.
     * If [autoDownload] is true, immediately streams the update in the background.
     */
    suspend fun checkForUpdates(context: Context, autoDownload: Boolean = true): UpdateState = withContext(Dispatchers.IO) {
        updateMutex.withLock {
            _updateState.value = UpdateState.Checking
            val metadata = fetchCloudMetadata()

            if (metadata == null) {
                Log.w(TAG, "Failed to fetch cloud update metadata")
                val err = UpdateState.Error("Could not reach update server")
                _updateState.value = err
                return@withContext err
            }

            val cloudVersionCode = metadata.resolvedVersionCode
            val installedVersion = getInstalledVersionCode(context)
            Log.i(TAG, "Cloud version: $cloudVersionCode, Installed version: $installedVersion")

            if (cloudVersionCode > installedVersion) {
                val available = UpdateState.Available(
                    version = cloudVersionCode,
                    releaseNotes = metadata.releaseNotes ?: "New Geography Learning Platform release available.",
                    sizeBytes = metadata.apkSizeBytes ?: 0L,
                    downloadUrl = metadata.apkDownloadUrl
                )
                _updateState.value = available

                if (autoDownload) {
                    return@withContext downloadAndPrepareApk(context, metadata)
                } else {
                    return@withContext available
                }
            } else {
                _updateState.value = UpdateState.Idle
                return@withContext UpdateState.Idle
            }
        }
    }

    /**
     * Downloads the APK file to the app's cache directory and triggers installation.
     */
    suspend fun downloadAndPrepareApk(context: Context, metadata: CloudMetadata): UpdateState = withContext(Dispatchers.IO) {
        try {
            val updatesDir = File(context.cacheDir, "updates")
            if (!updatesDir.exists()) updatesDir.mkdirs()

            val cloudVersionCode = metadata.resolvedVersionCode
            val apkFile = File(updatesDir, "tayaari-update-v${cloudVersionCode}.apk")

            // If already downloaded and matches expected size, mark ready, pop notification and trigger install
            if (apkFile.exists() && metadata.apkSizeBytes != null && apkFile.length() == metadata.apkSizeBytes) {
                val ready = UpdateState.ReadyToInstall(apkFile, cloudVersionCode)
                _updateState.value = ready
                UpdateNotificationHelper.showUpdateNotification(context, cloudVersionCode, metadata.totalQuestions, apkFile)
                withContext(Dispatchers.Main) {
                    installApk(context, apkFile, cloudVersionCode)
                }
                return@withContext ready
            }

            val request = Request.Builder()
                .url("${metadata.apkDownloadUrl}?cb=${System.currentTimeMillis() / 60000}")
                .header("Cache-Control", "no-cache, no-store")
                .build()

            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    val err = UpdateState.Error("Server returned code ${response.code}")
                    _updateState.value = err
                    return@withContext err
                }

                val body = response.body ?: throw IllegalStateException("Empty response body")
                val totalLength = if (body.contentLength() > 0) body.contentLength() else (metadata.apkSizeBytes ?: 33788213L)

                body.byteStream().use { input ->
                    FileOutputStream(apkFile).use { output ->
                        val buffer = ByteArray(16 * 1024)
                        var bytesRead: Int
                        var downloaded = 0L
                        var lastReportTime = 0L

                        while (input.read(buffer).also { bytesRead = it } != -1) {
                            output.write(buffer, 0, bytesRead)
                            downloaded += bytesRead

                            val now = System.currentTimeMillis()
                            if (now - lastReportTime > 250) { // Throttle UI state emissions
                                lastReportTime = now
                                val percent = if (totalLength > 0) ((downloaded * 100) / totalLength).toInt().coerceIn(0, 100) else 0
                                _updateState.value = UpdateState.Downloading(
                                    progressPercent = percent,
                                    downloadedBytes = downloaded,
                                    totalBytes = totalLength
                                )
                            }
                        }
                        output.flush()
                    }
                }
            }

            val ready = UpdateState.ReadyToInstall(apkFile, metadata.resolvedVersionCode)
            _updateState.value = ready
            Log.i(TAG, "Downloaded APK successfully: ${apkFile.absolutePath} (${apkFile.length()} bytes)")
            UpdateNotificationHelper.showUpdateNotification(context, metadata.resolvedVersionCode, metadata.totalQuestions, apkFile)
            withContext(Dispatchers.Main) {
                installApk(context, apkFile, metadata.resolvedVersionCode)
            }
            return@withContext ready

        } catch (e: Exception) {
            Log.e(TAG, "APK download failed", e)
            val err = UpdateState.Error("Download failed: ${e.localizedMessage}")
            _updateState.value = err
            return@withContext err
        }
    }

    /**
     * Installs the downloaded APK.
     * If user has granted permission ("take permission for now"), performs silent unattended install without prompt.
     * Otherwise, requests permission from the user.
     */
    fun installApk(context: Context, apkFile: File, version: Int = 0) {
        try {
            if (!apkFile.exists() || apkFile.length() == 0L) {
                Log.e(TAG, "Cannot install: APK file does not exist or is empty")
                return
            }

            // Step 1: Check if permission has been granted ("take permission for now")
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                if (!context.packageManager.canRequestPackageInstalls()) {
                    _updateState.value = UpdateState.PermissionRequired(apkFile, version)
                    Log.w(TAG, "Install permission required. Requesting permission from user...")
                    requestInstallPermission(context)
                    return
                }
            }

            // Step 2: Permission IS granted! Attempt silent unattended update without prompt ("auto update without permission")
            val silentInitiated = installApkSilently(context, apkFile, version)
            if (silentInitiated) {
                _updateState.value = UpdateState.Installing(version)
                Log.i(TAG, "Initiated silent PackageInstaller session for v$version")
                return
            }

            // Step 3: Fallback to standard interactive installer (for Android < 12)
            Log.i(TAG, "Falling back to standard PackageInstaller UI intent")
            launchStandardInstallIntent(context, apkFile)

        } catch (e: Exception) {
            Log.e(TAG, "Failed to launch package installer", e)
        }
    }

    /**
     * Silent / unattended installation using Android 12+ PackageInstaller session API.
     * Does NOT show any user prompt or require confirmation ("auto update without permission").
     */
    fun installApkSilently(context: Context, apkFile: File, version: Int): Boolean {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.S) {
            return false // USER_ACTION_NOT_REQUIRED is API 31+
        }

        if (!context.packageManager.canRequestPackageInstalls()) {
            Log.w(TAG, "Cannot install silently: REQUEST_INSTALL_PACKAGES not granted yet")
            return false
        }

        var session: PackageInstaller.Session? = null
        try {
            val packageInstaller = context.packageManager.packageInstaller
            val params = PackageInstaller.SessionParams(PackageInstaller.SessionParams.MODE_FULL_INSTALL).apply {
                setAppPackageName(context.packageName)
                setRequireUserAction(PackageInstaller.SessionParams.USER_ACTION_NOT_REQUIRED)
                setSize(apkFile.length())
            }

            val sessionId = packageInstaller.createSession(params)
            session = packageInstaller.openSession(sessionId)

            apkFile.inputStream().use { input ->
                session.openWrite("base.apk", 0, apkFile.length()).use { output ->
                    input.copyTo(output)
                    session.fsync(output)
                }
            }

            val callbackIntent = Intent(context, InstallStatusReceiver::class.java).apply {
                action = InstallStatusReceiver.ACTION_INSTALL_STATUS
                putExtra(InstallStatusReceiver.EXTRA_VERSION, version)
                putExtra(InstallStatusReceiver.EXTRA_APK_PATH, apkFile.absolutePath)
            }

            val pendingIntent = PendingIntent.getBroadcast(
                context,
                sessionId,
                callbackIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_MUTABLE
            )

            session.commit(pendingIntent.intentSender)
            Log.i(TAG, "Successfully committed unattended PackageInstaller session $sessionId for v$version")
            return true

        } catch (e: Exception) {
            Log.e(TAG, "Silent PackageInstaller session failed", e)
            try {
                session?.abandon()
            } catch (abandonEx: Exception) {
                Log.w(TAG, "Could not abandon session: ${abandonEx.message}")
            }
            return false
        } finally {
            try {
                session?.close()
            } catch (ignored: Exception) {}
        }
    }

    /**
     * Standard interactive installation via FileProvider and Intent.ACTION_VIEW (Fallback).
     */
    fun launchStandardInstallIntent(context: Context, apkFile: File) {
        try {
            val apkUri: Uri = FileProvider.getUriForFile(
                context,
                "${context.packageName}.fileprovider",
                apkFile
            )

            val installIntent = Intent(Intent.ACTION_VIEW).apply {
                setDataAndType(apkUri, "application/vnd.android.package-archive")
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }

            context.startActivity(installIntent)
            Log.i(TAG, "Launched standard PackageInstaller for URI: $apkUri")
        } catch (e: Exception) {
            Log.e(TAG, "Failed to launch standard PackageInstaller intent", e)
        }
    }

    /**
     * Directs the user to Android Settings to enable "Install unknown apps" ("take permission for now").
     */
    fun requestInstallPermission(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            try {
                val settingsIntent = Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES).apply {
                    data = Uri.parse("package:${context.packageName}")
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                }
                context.startActivity(settingsIntent)
            } catch (e: Exception) {
                try {
                    val genericIntent = Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES).apply {
                        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    }
                    context.startActivity(genericIntent)
                } catch (e2: Exception) {
                    val secIntent = Intent(Settings.ACTION_SECURITY_SETTINGS).apply {
                        addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                    }
                    context.startActivity(secIntent)
                }
            }
        }
    }

    fun fetchCloudMetadata(): CloudMetadata? {
        val urls = listOf(RAW_METADATA_URL, CDN_METADATA_URL)
        val cacheBuster = System.currentTimeMillis() / 60000

        for (url in urls) {
            try {
                val req = Request.Builder()
                    .url("$url?cb=$cacheBuster")
                    .header("Cache-Control", "no-cache, no-store")
                    .build()

                client.newCall(req).execute().use { resp ->
                    if (resp.isSuccessful) {
                        val body = resp.body?.string()
                        if (!body.isNullOrBlank()) {
                            return Gson().fromJson(body, CloudMetadata::class.java)
                        }
                    }
                }
            } catch (e: Exception) {
                Log.w(TAG, "Failed to fetch metadata from $url: ${e.message}")
            }
        }
        return null
    }

    /**
     * Schedules periodic background update checks via Android AlarmManager.
     * Ensures update checks fire periodically even when the app is completely closed.
     */
    fun schedulePeriodicCheck(context: Context) {
        try {
            val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as android.app.AlarmManager
            val intent = Intent(context, UpdateCheckReceiver::class.java).apply {
                action = "com.example.CHECK_FOR_UPDATE"
            }
            val pendingIntent = PendingIntent.getBroadcast(
                context,
                2001,
                intent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            // Repeat every 2 hours
            val intervalMillis = 2 * 60 * 60 * 1000L
            val triggerAtMillis = System.currentTimeMillis() + intervalMillis
            alarmManager.setInexactRepeating(
                android.app.AlarmManager.RTC_WAKEUP,
                triggerAtMillis,
                intervalMillis,
                pendingIntent
            )
            Log.i(TAG, "Scheduled periodic update check alarm")
        } catch (e: Exception) {
            Log.w(TAG, "Could not schedule periodic update alarm: ${e.message}")
        }
    }
}
