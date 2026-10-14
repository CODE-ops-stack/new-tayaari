package com.example.repository

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.example.model.ExamBlueprint
import com.example.model.ExamBlueprintRegistry
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "user_prefs")

class UserPreferencesRepository(private val context: Context) {

    private val EXAM_PROFILE_KEY = stringPreferencesKey("exam_profile")
    private val LOGGED_IN_USER_KEY = intPreferencesKey("logged_in_user_id")

    val selectedExamProfiles: Flow<List<ExamBlueprint>> = context.dataStore.data
        .map { preferences ->
            val examIdsStr = preferences[EXAM_PROFILE_KEY]
            if (examIdsStr.isNullOrEmpty()) {
                emptyList()
            } else {
                val ids = examIdsStr.split(",")
                ids.mapNotNull { ExamBlueprintRegistry.getBlueprint(it) }
            }
        }

    val loggedInUserId: Flow<Int?> = context.dataStore.data
        .map { preferences ->
            preferences[LOGGED_IN_USER_KEY]
        }

    suspend fun saveLoggedInUser(userId: Int) {
        context.dataStore.edit { preferences ->
            preferences[LOGGED_IN_USER_KEY] = userId
        }
    }

    suspend fun clearLoggedInUser() {
        context.dataStore.edit { preferences ->
            preferences.remove(LOGGED_IN_USER_KEY)
        }
    }

    suspend fun saveExamProfiles(blueprints: List<ExamBlueprint>) {
        context.dataStore.edit { preferences ->
            preferences[EXAM_PROFILE_KEY] = blueprints.joinToString(",") { it.examId }
        }
    }

    suspend fun clearExamProfile() {
        context.dataStore.edit { preferences ->
            preferences.remove(EXAM_PROFILE_KEY)
        }
    }
}
