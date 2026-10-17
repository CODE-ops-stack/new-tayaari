package com.example.updater

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageInstaller
import android.os.Build
import android.util.Log
import java.io.File

/**
 * InstallStatusReceiver
 *
 * Receives asynchronous status callbacks from Android's PackageInstaller session.
 * Enables silent unattended background OTA updates (Android 12+ / API 31+) via
 * `setRequireUserAction(USER_ACTION_NOT_REQUIRED)`.
 */
class InstallStatusReceiver : BroadcastReceiver() {

    companion object {
        const val ACTION_INSTALL_STATUS = "com.example.updater.INSTALL_STATUS"
        const val EXTRA_VERSION = "extra_version"
        const val EXTRA_APK_PATH = "extra_apk_path"
        private const val TAG = "InstallStatusReceiver"
    }

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != ACTION_INSTALL_STATUS) return

        val status = intent.getIntExtra(PackageInstaller.EXTRA_STATUS, PackageInstaller.STATUS_FAILURE)
        val message = intent.getStringExtra(PackageInstaller.EXTRA_STATUS_MESSAGE)
        val version = intent.getIntExtra(EXTRA_VERSION, 0)
        val apkPath = intent.getStringExtra(EXTRA_APK_PATH)

        Log.i(TAG, "PackageInstaller session callback: status=$status ($message), version=$version")

        when (status) {
            PackageInstaller.STATUS_PENDING_USER_ACTION -> {
                Log.i(TAG, "STATUS_PENDING_USER_ACTION: OS requested user confirmation.")
                val confirmationIntent = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    intent.getParcelableExtra(Intent.EXTRA_INTENT, Intent::class.java)
                } else {
                    @Suppress("DEPRECATION")
                    intent.getParcelableExtra(Intent.EXTRA_INTENT)
                }

                if (confirmationIntent != null) {
                    UpdateNotificationHelper.showPendingUserActionNotification(context, version, confirmationIntent)
                }
            }

            PackageInstaller.STATUS_SUCCESS -> {
                Log.i(TAG, "STATUS_SUCCESS: App updated silently and seamlessly to v$version!")
                // Clean up the cached APK to save device flash storage
                if (!apkPath.isNullOrEmpty()) {
                    try {
                        val file = File(apkPath)
                        if (file.exists()) file.delete()
                    } catch (e: Exception) {
                        Log.w(TAG, "Could not delete cached APK: ${e.message}")
                    }
                }
                UpdateNotificationHelper.showUpdateSuccessNotification(context, version)
            }

            PackageInstaller.STATUS_FAILURE,
            PackageInstaller.STATUS_FAILURE_ABORTED,
            PackageInstaller.STATUS_FAILURE_BLOCKED,
            PackageInstaller.STATUS_FAILURE_CONFLICT,
            PackageInstaller.STATUS_FAILURE_INCOMPATIBLE,
            PackageInstaller.STATUS_FAILURE_INVALID,
            PackageInstaller.STATUS_FAILURE_STORAGE -> {
                Log.e(TAG, "STATUS_FAILURE: Installation error status=$status, reason=$message")
                // If silent installation failed, fallback to standard interactive intent
                if (!apkPath.isNullOrEmpty()) {
                    val file = File(apkPath)
                    if (file.exists()) {
                        AppUpdateManager.launchStandardInstallIntent(context, file)
                    }
                }
            }

            else -> {
                Log.w(TAG, "Received unhandled PackageInstaller status: $status")
            }
        }
    }
}
