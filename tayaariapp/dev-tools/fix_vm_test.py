with open("app/src/test/java/com/example/viewmodel/MainViewModelTest.kt", "r") as f:
    content = f.read()

import re

new_content = """package com.example.viewmodel

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.example.model.ExamProfile
import com.example.repository.UserPreferencesRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Before
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import kotlinx.coroutines.test.UnconfinedTestDispatcher
import kotlinx.coroutines.test.advanceUntilIdle

@OptIn(ExperimentalCoroutinesApi::class)
@RunWith(RobolectricTestRunner::class)
class MainViewModelTest {

    private val testDispatcher = UnconfinedTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun testDataStorePersistence() = runTest(testDispatcher) {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val repo = UserPreferencesRepository(context)
        val viewModel = MainViewModel(repo)
        
        // Save a profile
        viewModel.saveProfile(ExamProfile.GROUP_A)
        
        // Advance all background tasks
        advanceUntilIdle()
        
        // Since DataStore runs on IO, let's wait slightly
        kotlinx.coroutines.delay(100)
        
        // Read directly from a new flow reference
        val repo2 = UserPreferencesRepository(context)
        val profile = repo2.selectedExamProfile.first()
        
        assertEquals(ExamProfile.GROUP_A, profile)
        println("Persistence verified! Profile is $profile")
    }
}"""

with open("app/src/test/java/com/example/viewmodel/MainViewModelTest.kt", "w") as f:
    f.write(new_content)
