package com.example.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

// ==========================================
// CARTOGRAPHIC ATLAS SCHEME (High-Legibility Oceanic & Topographic)
// ==========================================
private val AtlasDarkColorScheme = darkColorScheme(
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

private val AtlasLightColorScheme = lightColorScheme(
    primary = Color(0xFF0369A1),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE0F2FE),
    onPrimaryContainer = Color(0xFF075985),
    secondary = Color(0xFF047857),
    onSecondary = Color.White,
    tertiary = Color(0xFFB45309),
    onTertiary = Color.White,
    background = AbyssNavy,
    onBackground = Color.White,
    surface = OceanicDark,
    onSurface = Color.White,
    surfaceVariant = DeepBasalt,
    onSurfaceVariant = Color(0xFFCBD5E1),
    error = MagmaCrimson,
    onError = Color.White
)

@Composable
fun MyApplicationTheme(
    darkTheme: Boolean = true, // Default to Cartographic Atlas Dark Mode for deep immersive field learning
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) AtlasDarkColorScheme else AtlasLightColorScheme
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = AbyssNavy.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = false
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
