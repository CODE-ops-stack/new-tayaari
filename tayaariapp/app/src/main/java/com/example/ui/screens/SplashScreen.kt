package com.example.ui.screens

import androidx.compose.animation.core.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.alpha
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.R
import kotlinx.coroutines.delay

@Composable
fun SplashScreen() {
    val scale = remember { Animatable(0.5f) }
    val alpha = remember { Animatable(0f) }

    LaunchedEffect(Unit) {
        // Parallel animations for fade in and scale up
        scale.animateTo(
            targetValue = 1.2f,
            animationSpec = tween(
                durationMillis = 800,
                easing = FastOutSlowInEasing
            )
        )
        // Slight bounce back
        scale.animateTo(
            targetValue = 1f,
            animationSpec = spring(
                dampingRatio = Spring.DampingRatioMediumBouncy,
                stiffness = Spring.StiffnessLow
            )
        )
    }

    LaunchedEffect(Unit) {
        alpha.animateTo(
            targetValue = 1f,
            animationSpec = tween(
                durationMillis = 1000,
                easing = LinearEasing
            )
        )
    }

    com.example.ui.components.AtlasBackground {
      com.example.ui.components.TopographicBackground(lineColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.045f)) {
        Box(
            modifier = Modifier
                .fillMaxSize()
                .systemBarsPadding()
                .background(androidx.compose.ui.graphics.Color.Transparent),
            contentAlignment = Alignment.Center
        ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Image(
                painter = painterResource(id = R.mipmap.ic_launcher),
                contentDescription = "Tayaari Pakki Logo",
                modifier = Modifier
                    .size(120.dp)
                    .scale(scale.value)
                    .alpha(alpha.value)
                    .clip(CircleShape)
            )
            Spacer(modifier = Modifier.height(24.dp))
            Text(
                text = "Tayaari Pakki",
                fontSize = 34.sp,
                fontFamily = com.example.ui.theme.CartographicSerif,
                fontWeight = FontWeight.Bold,
                color = com.example.ui.theme.SummitGold,
                modifier = Modifier.alpha(alpha.value)
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = "CIVIL SERVICES GEOGRAPHY CADASTRE",
                fontSize = 13.sp,
                fontFamily = com.example.ui.theme.CoordinatesMonospace,
                fontWeight = FontWeight.Bold,
                letterSpacing = 1.2.sp,
                color = com.example.ui.theme.GlacierAzure,
                modifier = Modifier.alpha(alpha.value)
            )
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = "UPSC • State PSC • Terrestrial Atlas Engine",
                fontSize = 14.sp,
                fontWeight = FontWeight.Medium,
                color = com.example.ui.theme.AtlasParchment.copy(alpha = 0.85f),
                modifier = Modifier.alpha(alpha.value)
            )
            Spacer(modifier = Modifier.height(16.dp))
            com.example.ui.components.CartographicCoordinatesBanner(
                modifier = Modifier.alpha(alpha.value),
                coordinatesText = "📍 82°30′E IST // 23°30′N TROPIC OF CANCER"
            )
        }
    }
      }
    }
}
