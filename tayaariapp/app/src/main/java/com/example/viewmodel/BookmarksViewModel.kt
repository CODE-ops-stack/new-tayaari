package com.example.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.database.BookmarkedQuestionEntity
import com.example.model.ExamQuestion
import com.example.model.MCQQuestion
import com.example.model.DescriptiveQuestion
import com.example.repository.LocalRepository
import com.squareup.moshi.Moshi
import com.squareup.moshi.kotlin.reflect.KotlinJsonAdapterFactory
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

class BookmarksViewModel(private val localRepository: LocalRepository) : ViewModel() {

    private val moshi = Moshi.Builder().add(KotlinJsonAdapterFactory()).build()
    private val mcqAdapter = moshi.adapter(MCQQuestion::class.java)
    private val descriptiveAdapter = moshi.adapter(DescriptiveQuestion::class.java)

    private val allBookmarksFlow = localRepository.getAllBookmarks()

    private val _selectedTopic = MutableStateFlow<String?>("All")
    val selectedTopic: StateFlow<String?> = _selectedTopic

    val bookmarkedQuestions: StateFlow<List<ExamQuestion>> = allBookmarksFlow
        .combine(_selectedTopic) { entities, topic ->
            val parsedQuestions = entities.mapNotNull { entity ->
                try {
                    when (entity.format) {
                        com.example.model.QuestionFormat.PRELIMS_MCQ -> mcqAdapter.fromJson(entity.payloadJson)
                        com.example.model.QuestionFormat.MAINS_DESCRIPTIVE -> descriptiveAdapter.fromJson(entity.payloadJson)
                    }
                } catch (e: Exception) {
                    null
                }
            }

            if (topic == null || topic == "All") {
                parsedQuestions
            } else {
                parsedQuestions.filter { it.chapterCode == topic }
            }
        }
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    val availableTopics: StateFlow<List<String>> = allBookmarksFlow
        .combine(MutableStateFlow(Unit)) { entities, _ ->
            val parsedQuestions = entities.mapNotNull { entity ->
                try {
                    when (entity.format) {
                        com.example.model.QuestionFormat.PRELIMS_MCQ -> mcqAdapter.fromJson(entity.payloadJson)
                        com.example.model.QuestionFormat.MAINS_DESCRIPTIVE -> descriptiveAdapter.fromJson(entity.payloadJson)
                    }
                } catch (e: Exception) {
                    null
                }
            }
            listOf("All") + parsedQuestions.map { it.chapterCode }.distinct().sorted()
        }
        .stateIn(viewModelScope, SharingStarted.Lazily, listOf("All"))

    fun filterByTopic(topic: String) {
        _selectedTopic.value = topic
    }

    fun removeBookmark(id: String) {
        viewModelScope.launch {
            localRepository.removeBookmark(id)
        }
    }
}
