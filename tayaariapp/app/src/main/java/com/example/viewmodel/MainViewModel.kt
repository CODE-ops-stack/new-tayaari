package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.model.ExamBlueprint
import com.example.repository.UserPreferencesRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MainViewModel(private val userPreferencesRepository: UserPreferencesRepository) : ViewModel() {

    private val _selectedProfiles = MutableStateFlow<List<ExamBlueprint>>(emptyList())
    val selectedProfiles: StateFlow<List<ExamBlueprint>> = _selectedProfiles

    private val _isLoading = MutableStateFlow(true)
    val isLoading: StateFlow<Boolean> = _isLoading

        private val _loggedInUserId = MutableStateFlow<Int?>(null)
    val loggedInUserId: StateFlow<Int?> = _loggedInUserId

    init {
        viewModelScope.launch {
            userPreferencesRepository.loggedInUserId.collect { userId ->
                _loggedInUserId.value = userId
            }
        }
        viewModelScope.launch {
            userPreferencesRepository.selectedExamProfiles.collect { profiles ->
                _selectedProfiles.value = profiles
                _isLoading.value = false
            }
        }
    }

        fun loginUser(userId: Int) {
        viewModelScope.launch {
            userPreferencesRepository.saveLoggedInUser(userId)
        }
    }

    fun logoutUser() {
        viewModelScope.launch {
            userPreferencesRepository.clearLoggedInUser()
            userPreferencesRepository.clearExamProfile()
        }
    }

    fun saveProfiles(profiles: List<ExamBlueprint>) {
        viewModelScope.launch {
            userPreferencesRepository.saveExamProfiles(profiles)
            
            // Also save to UserEntity if logged in
            val userId = _loggedInUserId.value
            if (userId != null) {
                // We don't have UserDao here directly, but in a real app we'd inject it or handle it via a UseCase.
                // For now, the datastore is enough for session state.
            }
        }
    }

    fun clearProfile() {
        viewModelScope.launch {
            userPreferencesRepository.clearExamProfile()
        }
    }
}
