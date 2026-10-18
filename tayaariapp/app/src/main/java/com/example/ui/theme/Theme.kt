package com.example.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat
import com.example.repository.AppThemeMode

// ==========================================
// CARTOGRAPHIC READING SCHEMES
// ==========================================

// 1. Dark Mode ("Abyssal Basalt") - Default for immersive study & OLED efficiency
val AtlasDarkColorScheme = darkColorScheme(
    primary = HydrosphereCyan,
    onPrimary = OceanicDark,
    primaryContainer = DeepBasalt,
    onPrimaryContainer = HydrosphereCyan,
    secondary = ContourEmerald,
    onSecondary = OceanicDark,
    secondaryContainer = SlateBedrock,
    onSecondaryContainer = ContourEmerald,
    tertiary = SunstoneGold,
    onTertiary = OceanicDark,
    background = AbyssNavy,
    onBackground = AtlasParchment,
    surface = OceanicDark,
    onSurface = AtlasParchment,
    surfaceVariant = DeepBasalt,
    onSurfaceVariant = TopoContourMuted,
    error = MagmaCrimson,
    onError = AtlasParchment
)

// 2. Light Mode ("Atlas Parchment") - Mapmaker's Warm Ivory Paper for bright daytime reading
val AtlasLightColorScheme = lightColorScheme(
    primary = Color(0xFF0284C7),          // Alpine Sky Blue
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE0F2FE),
    onPrimaryContainer = Color(0xFF0369A1),
    secondary = Color(0xFF059669),        // Topographic Forest Emerald
    onSecondary = Color.White,
    secondaryContainer = Color(0xFFD1FAE5),
    onSecondaryContainer = Color(0xFF065F46),
    tertiary = Color(0xFFD97706),         // Compass Brass Amber
    onTertiary = Color.White,
    background = Color(0xFFFBF8F1),       // Warm Cartographic Ivory Parchment
    onBackground = Color(0xFF0F172A),     // Sharp Slate Ink
    surface = Color(0xFFFFFFFF),          // Pure Daylight Paper Surface
    onSurface = Color(0xFF0F172A),        // Sharp Slate Ink
    surfaceVariant = Color(0xFFF1ECE1),   // Topographic Muted Parchment
    onSurfaceVariant = Color(0xFF475569), // Contour Gray
    error = MagmaCrimson,
    onError = Color.White
)

// 3. Eye-Care Sepia Mode ("Lamp-Light Cartography") - 0% Blue Light for late-night 2 AM revision
val AtlasSepiaColorScheme = darkColorScheme(
    primary = Color(0xFFF59E0B),          // Warm Lamp Amber
    onPrimary = Color(0xFF1C140A),
    primaryContainer = Color(0xFF382915),
    onPrimaryContainer = Color(0xFFFDE68A),
    secondary = Color(0xFF10B981),        // Muted Sage Emerald
    onSecondary = Color(0xFF1C140A),
    secondaryContainer = Color(0xFF243828),
    onSecondaryContainer = Color(0xFFA7F3D0),
    tertiary = Color(0xFFFBBF24),
    onTertiary = Color(0xFF1C140A),
    background = Color(0xFF1C140A),       // Deep Night Amber
    onBackground = Color(0xFFF5E6D3),     // Warm Antique Parchment
    surface = Color(0xFF291E10),          // Warm Night Surface
    onSurface = Color(0xFFF5E6D3),        // Warm Antique Parchment
    surfaceVariant = Color(0xFF382915),
    onSurfaceVariant = Color(0xFFD4B996), // Soft Sepia
    error = Color(0xFFEF4444),
    onError = Color.White
)

val LocalAppThemeMode = compositionLocalOf { AppThemeMode.DARK }
val LocalFontScale = compositionLocalOf { 1.0f }
val LocalZenMode = compositionLocalOf { false }

@Composable
fun MyApplicationTheme(
    themeMode: AppThemeMode = AppThemeMode.DARK,
    fontScale: Float = 1.0f,
    zenMode: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = when (themeMode) {
        AppThemeMode.DARK -> AtlasDarkColorScheme
        AppThemeMode.LIGHT -> AtlasLightColorScheme
        AppThemeMode.SEPIA -> AtlasSepiaColorScheme
    }

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            val statusBarColor = when (themeMode) {
                AppThemeMode.DARK -> AbyssNavy.toArgb()
                AppThemeMode.LIGHT -> Color(0xFFFBF8F1).toArgb()
                AppThemeMode.SEPIA -> Color(0xFF1C140A).toArgb()
            }
            window.statusBarColor = statusBarColor
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = (themeMode == AppThemeMode.LIGHT)
        }
    }

    CompositionLocalProvider(
        LocalAppThemeMode provides themeMode,
        LocalFontScale provides fontScale,
        LocalZenMode provides zenMode
    ) {
        MaterialTheme(
            colorScheme = colorScheme,
            typography = Typography,
            content = content
        )
    }
}
