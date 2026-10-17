package com.example.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.viewmodel.AuthUiState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.ui.text.font.FontWeight

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AuthScreen(
    uiState: AuthUiState,
    onUsernameChange: (String) -> Unit,
    onPasswordChange: (String) -> Unit,
    onToggleMode: () -> Unit,
    onSubmit: () -> Unit,
    onGuestLogin: () -> Unit = {}
) {
    com.example.ui.components.AtlasBackground {
        com.example.ui.components.TopographicBackground(lineColor = com.example.ui.theme.ContourEmerald.copy(alpha = 0.035f)) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                com.example.ui.components.CartographicCoordinatesBanner(
                    coordinatesText = "📍 TAYAARI GEOGRAPHY // UPSC • BPSC • SSC • RRB"
                )
                Spacer(modifier = Modifier.height(16.dp))

                com.example.ui.components.AtlasCard(
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Column(
                        modifier = Modifier.padding(24.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "🧭",
                            fontSize = 36.sp
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            text = if (uiState.isLoginMode) "Aspirant Sign-In" else "Create Aspirant Account",
                            style = MaterialTheme.typography.headlineSmall,
                            fontFamily = com.example.ui.theme.CartographicSerif,
                            color = com.example.ui.theme.SummitGold,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "Integrated Civil Services Examination Platform",
                            style = MaterialTheme.typography.bodySmall,
                            color = com.example.ui.theme.GlacierAzure
                        )
                        Spacer(modifier = Modifier.height(24.dp))

                        OutlinedTextField(
                            value = uiState.username,
                            onValueChange = onUsernameChange,
                            label = { Text("Aspirant Identifier / Username") },
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(12.dp)
                        )
                        Spacer(modifier = Modifier.height(14.dp))
                        OutlinedTextField(
                            value = uiState.password,
                            onValueChange = onPasswordChange,
                            label = { Text("Password") },
                            visualTransformation = PasswordVisualTransformation(),
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(12.dp)
                        )
                        
                        if (uiState.error != null) {
                            Spacer(modifier = Modifier.height(10.dp))
                            Text(
                                text = "⚠️ ${uiState.error}", 
                                color = MaterialTheme.colorScheme.error,
                                style = MaterialTheme.typography.bodySmall
                            )
                        }

                        Spacer(modifier = Modifier.height(20.dp))
                        Button(
                            onClick = onSubmit,
                            modifier = Modifier.fillMaxWidth().height(50.dp),
                            shape = RoundedCornerShape(12.dp),
                            colors = ButtonDefaults.buttonColors(containerColor = com.example.ui.theme.ContourEmerald)
                        ) {
                            Text(
                                text = if (uiState.isLoginMode) "Sign In & Begin Preparation 🧭" else "Create Account & Start 🗺️",
                                fontWeight = FontWeight.Bold,
                                color = com.example.ui.theme.AbyssNavy
                            )
                        }

                        Spacer(modifier = Modifier.height(10.dp))
                        OutlinedButton(
                            onClick = onGuestLogin,
                            modifier = Modifier.fillMaxWidth().height(48.dp),
                            shape = RoundedCornerShape(12.dp),
                            border = androidx.compose.foundation.BorderStroke(1.dp, com.example.ui.theme.SunstoneGold)
                        ) {
                            Text(
                                text = "⚡ Instant Guest Access (No Sign-In Required)",
                                color = com.example.ui.theme.SunstoneGold,
                                fontWeight = FontWeight.Bold,
                                fontSize = 13.sp
                            )
                        }

                        Spacer(modifier = Modifier.height(12.dp))
                        TextButton(onClick = onToggleMode) {
                            Text(
                                text = if (uiState.isLoginMode) "New Aspirant? Create Free Account" else "Already Registered? Sign In Here",
                                color = com.example.ui.theme.GlacierAzure,
                                fontSize = 13.sp
                            )
                        }
                    }
                }
            }
        }
    }
}
