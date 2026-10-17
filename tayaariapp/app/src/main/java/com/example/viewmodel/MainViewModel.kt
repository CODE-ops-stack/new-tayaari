package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.database.UserDao
import com.example.model.ExamBlueprint
import com.example.model.ExamBlueprintRegistry
import com.example.repository.UserPreferencesRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

class MainViewModel(
    private val userPreferencesRepository: UserPreferencesRepository,
    private val userDao: UserDao? = null
) : ViewModel() {

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

    fun loginAsGuest(defaultProfiles: List<ExamBlueprint>) {
        viewModelScope.launch {
            if (userDao != null) {
                val examIdsStr = defaultProfiles.joinToString(",") { it.examId }
                val existing = userDao.getUserById(1)
                if (existing == null) {
                    userDao.insertUser(
                        com.example.database.UserEntity(
                            id = 1,
                            username = "Guest Aspirant",
                            passwordHash = "guest",
                            targetExamIds = examIdsStr
                        )
                    )
                } else if (existing.targetExamIds.isNullOrBlank()) {
                    userDao.updateTargetExams(1, examIdsStr)
                }
            }
            userPreferencesRepository.saveLoggedInUser(1)
            userPreferencesRepository.saveExamProfiles(defaultProfiles)
            _loggedInUserId.value = 1
            _selectedProfiles.value = defaultProfiles
        }
    }

    fun loginUser(userId: Int) {
        viewModelScope.launch {
            userPreferencesRepository.saveLoggedInUser(userId)
            _loggedInUserId.value = userId

            // Strictly restore the user's saved exam from their account in SQLite
            val user = userDao?.getUserById(userId)
            val savedExamIds = user?.targetExamIds
            if (!savedExamIds.isNullOrBlank()) {
                val blueprints = savedExamIds.split(",")
                    .mapNotNull { ExamBlueprintRegistry.getBlueprint(it.trim()) }
                if (blueprints.isNotEmpty()) {
                    userPreferencesRepository.saveExamProfiles(blueprints)
                    _selectedProfiles.value = blueprints
                }
            }
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
            _selectedProfiles.value = profiles
            
            // Strictly persist selected exam to UserEntity in SQLite
            val userId = _loggedInUserId.value ?: runCatching { userPreferencesRepository.loggedInUserId.first() }.getOrNull()
            if (userId != null && userDao != null) {
                val examIdsStr = profiles.joinToString(",") { it.examId }
                val user = userDao.getUserById(userId)
                if (user == null) {
                    userDao.insertUser(
                        com.example.database.UserEntity(
                            id = userId,
                            username = if (userId == 1) "Guest Aspirant" else "Aspirant #$userId",
                            passwordHash = "active",
                            targetExamIds = examIdsStr
                        )
                    )
                } else {
                    userDao.updateTargetExams(userId, examIdsStr)
                }
            }
        }
    }

    fun setActiveProfile(examId: String) {
        viewModelScope.launch {
            userPreferencesRepository.setActiveExam(examId)
        }
    }

    fun clearProfile() {
        viewModelScope.launch {
            userPreferencesRepository.clearExamProfile()
            val userId = _loggedInUserId.value
            if (userId != null && userDao != null) {
                userDao.updateTargetExams(userId, null)
            }
        }
    }
}
