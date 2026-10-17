package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.database.UserDao
import com.example.database.UserEntity
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class AuthViewModel(private val userDao: UserDao) : ViewModel() {
    private val _uiState = MutableStateFlow(AuthUiState())
    val uiState: StateFlow<AuthUiState> = _uiState

    fun onUsernameChange(username: String) {
        _uiState.value = _uiState.value.copy(username = username, error = null)
    }

    fun onPasswordChange(password: String) {
        _uiState.value = _uiState.value.copy(password = password, error = null)
    }

    fun toggleMode() {
        _uiState.value = _uiState.value.copy(isLoginMode = !_uiState.value.isLoginMode, error = null)
    }

    fun authenticate(onSuccess: (Int) -> Unit) {
        val state = _uiState.value
        if (state.username.isBlank() || state.password.isBlank()) {
            _uiState.value = state.copy(error = "Fields cannot be empty")
            return
        }

        viewModelScope.launch {
            if (state.isLoginMode) {
                val user = userDao.getUserByUsername(state.username)
                if (user != null && user.passwordHash == state.password) {
                    onSuccess(user.id)
                } else if (user == null) {
                    _uiState.value = state.copy(error = "Account '${state.username}' not found. Tap 'Create Free Account' below or continue as Guest.")
                } else {
                    _uiState.value = state.copy(error = "Incorrect password. Please verify your password.")
                }
            } else {
                val existing = userDao.getUserByUsername(state.username)
                if (existing != null) {
                    _uiState.value = state.copy(error = "Username already exists")
                } else {
                    val newUser = UserEntity(username = state.username, passwordHash = state.password)
                    val id = userDao.insertUser(newUser)
                    onSuccess(id.toInt())
                }
            }
        }
    }
}

data class AuthUiState(
    val username: String = "",
    val password: String = "",
    val isLoginMode: Boolean = true,
    val error: String? = null
)
