package com.example.updater

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.core.app.NotificationCompat
import androidx.core.content.FileProvider
import com.example.MainActivity
import com.example.R
import java.io.File

object UpdateNotificationHelper {

    const val CHANNEL_ID = "channel_tayaari_updates"
    const val NOTIFICATION_ID_AVAILABLE = 1001
    const val NOTIFICATION_ID_SUCCESS = 1002
    const val NOTIFICATION_ID_PENDING_ACTION = 1003

    fun createNotificationChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "App Updates & Syllabus Expansions"
            val descriptionText = "Notifications for new UPSC Geography questions, features, and app updates"
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel(CHANNEL_ID, name, importance).apply {
                description = descriptionText
                enableVibration(true)
                enableLights(true)
            }
            val notificationManager: NotificationManager =
                context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    /**
     * Heads-up notification when an update is available or downloaded.
     */
    fun showUpdateNotification(
        context: Context,
        version: Int,
        totalQuestions: Int,
        apkFile: File? = null
    ) {
        createNotificationChannel(context)

        val hasInstallPermission = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            context.packageManager.canRequestPackageInstalls()
        } else {
            true
        }

        // Determine click action
        val contentPendingIntent = if (!hasInstallPermission) {
            // User needs to grant permission once ("take permission for now")
            val settingsIntent = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES).apply {
                    data = Uri.parse("package:${context.packageName}")
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                }
            } else {
                Intent(Settings.ACTION_SECURITY_SETTINGS).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                }
            }
            PendingIntent.getActivity(
                context,
                101,
                settingsIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
        } else if (apkFile != null && apkFile.exists() && apkFile.length() > 0) {
            // Direct launch into Android Package Installer
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
            PendingIntent.getActivity(
                context,
                102,
                installIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
        } else {
            // Open MainActivity with automatic update trigger
            val mainIntent = Intent(context, MainActivity::class.java).apply {
                putExtra("EXTRA_TRIGGER_UPDATE", true)
                addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
            }
            PendingIntent.getActivity(
                context,
                103,
                mainIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
        }

        val title = "🚀 Tayaari Pakki v$version Update Available!"
        val actionText = if (!hasInstallPermission) "ENABLE & INSTALL" else "INSTALL UPDATE"
        val message = if (!hasInstallPermission) {
            "New UPSC Geography Optional track ($totalQuestions MCQs) ready. Tap to enable auto-update and install."
        } else {
            "New UPSC Geography Optional track ($totalQuestions MCQs across 30 chapters) ready. Tap to install now."
        }

        val builder = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_STATUS)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setAutoCancel(true)
            .setDefaults(NotificationCompat.DEFAULT_ALL)
            .setContentIntent(contentPendingIntent)
            .addAction(
                R.mipmap.ic_launcher,
                actionText,
                contentPendingIntent
            )

        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify(NOTIFICATION_ID_AVAILABLE, builder.build())
    }

    /**
     * Fired when silent background installation succeeds without user intervention.
     */
    fun showUpdateSuccessNotification(context: Context, version: Int) {
        createNotificationChannel(context)

        val mainIntent = Intent(context, MainActivity::class.java).apply {
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        }
        val pendingIntent = PendingIntent.getActivity(
            context,
            104,
            mainIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val title = "🎉 Tayaari Pakki Updated to v$version!"
        val message = "Platform updated silently in the background. Full 30-chapter UPSC Geography curriculum with 3,942 MCQs is live."

        val builder = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_STATUS)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .addAction(R.mipmap.ic_launcher, "OPEN APP", pendingIntent)

        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify(NOTIFICATION_ID_SUCCESS, builder.build())
    }

    /**
     * Fired when system requests a single-tap confirmation dialog.
     */
    fun showPendingUserActionNotification(context: Context, version: Int, confirmationIntent: Intent) {
        createNotificationChannel(context)

        confirmationIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        val pendingIntent = PendingIntent.getActivity(
            context,
            105,
            confirmationIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val title = "⚡ Confirm Tayaari Pakki v$version Update"
        val message = "One tap required by Android OS to finalize the installation. Tap here to complete."

        val builder = NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .addAction(R.mipmap.ic_launcher, "CONFIRM UPDATE", pendingIntent)

        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationManager.notify(NOTIFICATION_ID_PENDING_ACTION, builder.build())
    }
}
