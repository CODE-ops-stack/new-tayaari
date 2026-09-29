package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.model.ExamBlueprint
import com.example.repository.UserPreferencesRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

class MainViewModel(private val userPreferencesRepository: UserPreferencesRepository) : ViewModel() {

    private val _selectedProfile = MutableStateFlow<ExamBlueprint?>(null)
    val selectedProfile: StateFlow<ExamBlueprint?> = _selectedProfile

    private val _isLoading = MutableStateFlow(true)
    val isLoading: StateFlow<Boolean> = _isLoading

    init {
        viewModelScope.launch {
            userPreferencesRepository.selectedExamProfile.collect { profile ->
                _selectedProfile.value = profile
                _isLoading.value = false
            }
        }
    }

    fun saveProfile(profile: ExamBlueprint) {
        viewModelScope.launch {
            userPreferencesRepository.saveExamProfile(profile)
        }
    }

    fun clearProfile() {
        viewModelScope.launch {
            userPreferencesRepository.clearExamProfile()
        }
    }
}
