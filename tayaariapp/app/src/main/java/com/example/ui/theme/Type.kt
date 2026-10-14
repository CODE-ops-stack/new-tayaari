package com.example.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

// =========================================================================
// CARTOGRAPHIC ATLAS & GEOGRAPHY SCHOLARLY TYPOGRAPHY
// =========================================================================

val CartographicSerif = FontFamily.Serif
val GeodeticSans = FontFamily.SansSerif
val CoordinatesMonospace = FontFamily.Monospace

val Typography = Typography(
    displayLarge = TextStyle(
        fontFamily = CartographicSerif,
        fontWeight = FontWeight.Bold,
        fontSize = 32.sp,
        lineHeight = 38.sp,
        letterSpacing = 0.5.sp
    ),
    displayMedium = TextStyle(
        fontFamily = CartographicSerif,
        fontWeight = FontWeight.Bold,
        fontSize = 26.sp,
        lineHeight = 32.sp,
        letterSpacing = 0.25.sp
    ),
    titleLarge = TextStyle(
        fontFamily = CartographicSerif,
        fontWeight = FontWeight.Bold,
        fontSize = 22.sp,
        lineHeight = 28.sp,
        letterSpacing = 0.25.sp
    ),
    titleMedium = TextStyle(
        fontFamily = CartographicSerif,
        fontWeight = FontWeight.SemiBold,
        fontSize = 18.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.15.sp
    ),
    titleSmall = TextStyle(
        fontFamily = GeodeticSans,
        fontWeight = FontWeight.Bold,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.5.sp
    ),
    bodyLarge = TextStyle(
        fontFamily = GeodeticSans,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 25.sp,
        letterSpacing = 0.2.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = GeodeticSans,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 21.sp,
        letterSpacing = 0.2.sp
    ),
    bodySmall = TextStyle(
        fontFamily = GeodeticSans,
        fontWeight = FontWeight.Normal,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.3.sp
    ),
    labelLarge = TextStyle(
        fontFamily = GeodeticSans,
        fontWeight = FontWeight.Bold,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.8.sp
    ),
    labelMedium = TextStyle(
        fontFamily = GeodeticSans,
        fontWeight = FontWeight.SemiBold,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.6.sp
    ),
    labelSmall = TextStyle(
        fontFamily = CoordinatesMonospace,
        fontWeight = FontWeight.Medium,
        fontSize = 10.sp,
        lineHeight = 14.sp,
        letterSpacing = 1.0.sp
    )
)
