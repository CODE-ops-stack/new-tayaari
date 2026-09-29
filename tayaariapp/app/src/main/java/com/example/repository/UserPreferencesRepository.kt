package com.example.repository

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.example.model.ExamBlueprint
import com.example.model.ExamBlueprintRegistry
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "user_prefs")

class UserPreferencesRepository(private val context: Context) {

    private val EXAM_PROFILE_KEY = stringPreferencesKey("exam_profile")

    val selectedExamProfile: Flow<ExamBlueprint?> = context.dataStore.data
        .map { preferences ->
            val examId = preferences[EXAM_PROFILE_KEY]
            if (examId != null) {
                ExamBlueprintRegistry.getBlueprint(examId)
            } else {
                null
            }
        }

    suspend fun saveExamProfile(blueprint: ExamBlueprint) {
        context.dataStore.edit { preferences ->
            preferences[EXAM_PROFILE_KEY] = blueprint.examId
        }
    }

    suspend fun clearExamProfile() {
        context.dataStore.edit { preferences ->
            preferences.remove(EXAM_PROFILE_KEY)
        }
    }
}
