package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.repository.LocalRepository
import com.example.repository.GeneratedPaper
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

data class PaperTwinUiState(
    val isGenerating: Boolean = false,
    val paper: GeneratedPaper? = null,
    val error: String? = null
)

class PaperTwinViewModel(private val repository: LocalRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(PaperTwinUiState())
    val uiState: StateFlow<PaperTwinUiState> = _uiState

    fun generatePaper(examId: String, targetCount: Int = 50) {
        _uiState.value = PaperTwinUiState(isGenerating = true)
        viewModelScope.launch {
            try {
                val generated = repository.generatePaperTwin(examId, targetCount)
                _uiState.value = PaperTwinUiState(paper = generated)
            } catch (e: Exception) {
                _uiState.value = PaperTwinUiState(error = e.message ?: "Failed to generate paper")
            }
        }
    }
}
