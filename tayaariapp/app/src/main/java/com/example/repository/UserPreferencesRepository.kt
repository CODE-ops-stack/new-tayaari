package com.example.repository

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.example.model.ExamBlueprint
import com.example.model.ExamBlueprintRegistry
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

enum class AppThemeMode {
    DARK,   // Abyssal Basalt
    LIGHT,  // Atlas Parchment
    SEPIA   // Lamp-Light Cartography (Eye-Care Amber)
}

enum class FontScaleOption(val scale: Float, val label: String) {
    NORMAL(1.0f, "Standard (100%)"),
    COMFORT(1.15f, "Comfort (115%)"),
    LARGE(1.30f, "Enlarged (130%)")
}

val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "user_prefs")

class UserPreferencesRepository(private val context: Context) {

    private val EXAM_PROFILE_KEY = stringPreferencesKey("exam_profile")
    private val ACTIVE_EXAM_KEY = stringPreferencesKey("active_exam_id")
    private val LOGGED_IN_USER_KEY = intPreferencesKey("logged_in_user_id")

    private val THEME_MODE_KEY = stringPreferencesKey("theme_mode")
    private val FONT_SCALE_KEY = stringPreferencesKey("font_scale")
    private val ZEN_MODE_KEY = booleanPreferencesKey("zen_mode")
    private val DAILY_TARGET_KEY = intPreferencesKey("daily_target")
    private val TODAY_SOLVED_KEY = intPreferencesKey("today_solved")
    private val TODAY_DATE_KEY = stringPreferencesKey("today_date")

    val selectedExamProfiles: Flow<List<ExamBlueprint>> = context.dataStore.data
        .map { preferences ->
            val examIdsStr = preferences[EXAM_PROFILE_KEY]
            val activeExamId = preferences[ACTIVE_EXAM_KEY]
            if (examIdsStr.isNullOrEmpty()) {
                emptyList()
            } else {
                val ids = examIdsStr.split(",")
                val blueprints = ids.mapNotNull { ExamBlueprintRegistry.getBlueprint(it.trim()) }
                if (activeExamId != null) {
                    val active = blueprints.find { it.examId == activeExamId }
                    if (active != null) {
                        listOf(active) + blueprints.filter { it.examId != activeExamId }
                    } else {
                        blueprints
                    }
                } else {
                    blueprints
                }
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
            if (blueprints.isNotEmpty()) {
                val currentActive = preferences[ACTIVE_EXAM_KEY]
                if (currentActive == null || blueprints.none { it.examId == currentActive }) {
                    preferences[ACTIVE_EXAM_KEY] = blueprints.first().examId
                }
            }
        }
    }

    suspend fun setActiveExam(examId: String) {
        context.dataStore.edit { preferences ->
            preferences[ACTIVE_EXAM_KEY] = examId
        }
    }

    suspend fun clearExamProfile() {
        context.dataStore.edit { preferences ->
            preferences.remove(EXAM_PROFILE_KEY)
            preferences.remove(ACTIVE_EXAM_KEY)
        }
    }

    // ==========================================
    // ASPIRANT STUDY ERGONOMICS & PREFERENCES
    // ==========================================

    val themeMode: Flow<AppThemeMode> = context.dataStore.data.map { preferences ->
        when (preferences[THEME_MODE_KEY]) {
            "LIGHT" -> AppThemeMode.LIGHT
            "SEPIA" -> AppThemeMode.SEPIA
            else -> AppThemeMode.DARK
        }
    }

    val fontScaleOption: Flow<FontScaleOption> = context.dataStore.data.map { preferences ->
        when (preferences[FONT_SCALE_KEY]) {
            "COMFORT" -> FontScaleOption.COMFORT
            "LARGE" -> FontScaleOption.LARGE
            else -> FontScaleOption.NORMAL
        }
    }

    val isZenMode: Flow<Boolean> = context.dataStore.data.map { preferences ->
        preferences[ZEN_MODE_KEY] ?: false
    }

    val dailyTarget: Flow<Int> = context.dataStore.data.map { preferences ->
        preferences[DAILY_TARGET_KEY] ?: 20
    }

    val todaySolvedCount: Flow<Int> = context.dataStore.data.map { preferences ->
        val savedDate = preferences[TODAY_DATE_KEY]
        val today = java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.US).format(java.util.Date())
        if (savedDate == today) {
            preferences[TODAY_SOLVED_KEY] ?: 0
        } else {
            0
        }
    }

    suspend fun setThemeMode(mode: AppThemeMode) {
        context.dataStore.edit { preferences ->
            preferences[THEME_MODE_KEY] = mode.name
        }
    }

    suspend fun setFontScaleOption(option: FontScaleOption) {
        context.dataStore.edit { preferences ->
            preferences[FONT_SCALE_KEY] = option.name
        }
    }

    suspend fun setZenMode(enabled: Boolean) {
        context.dataStore.edit { preferences ->
            preferences[ZEN_MODE_KEY] = enabled
        }
    }

    suspend fun setDailyTarget(target: Int) {
        context.dataStore.edit { preferences ->
            preferences[DAILY_TARGET_KEY] = target
        }
    }

    suspend fun incrementTodaySolved() {
        val today = java.text.SimpleDateFormat("yyyy-MM-dd", java.util.Locale.US).format(java.util.Date())
        context.dataStore.edit { preferences ->
            val savedDate = preferences[TODAY_DATE_KEY]
            val currentCount = if (savedDate == today) (preferences[TODAY_SOLVED_KEY] ?: 0) else 0
            preferences[TODAY_DATE_KEY] = today
            preferences[TODAY_SOLVED_KEY] = currentCount + 1
        }
    }
}
