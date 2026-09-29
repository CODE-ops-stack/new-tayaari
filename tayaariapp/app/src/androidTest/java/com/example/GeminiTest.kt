package com.example

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.database.AppDatabase
import com.example.repository.GeminiRepository
import com.example.repository.LocalRepository
import kotlinx.coroutines.runBlocking
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class GeminiTest {
    @Test
    fun testLiveGeneration(): Unit = runBlocking {
        val appContext = InstrumentationRegistry.getInstrumentation().targetContext
        val database = AppDatabase.getDatabase(appContext)
        val localRepository = LocalRepository(database.bookmarkDao(), database.trapAnalyticsDao(), database.appDao())
        val geminiRepo = GeminiRepository(localRepository)
        println("STARTING GEMINI LIVE GENERATION TEST")
        android.util.Log.i("GeminiTest", "STARTING GEMINI LIVE GENERATION TEST")
        
        try {
            val question = geminiRepo.generateNextQuestion(
                topicName = "24. Structure and Physiography",
                tier = "Advanced",
                format = "Statement-based",
                documentContext = null
            )
            println("GENERATED QUESTION: " + question.questionText)
            android.util.Log.i("GeminiTest", "GENERATED QUESTION: " + question.questionText)
            android.util.Log.i("GeminiTest", "IS FALLBACK (Earth's Interior): " + question.questionText.contains("Earth's interior"))
        } catch (e: Exception) {
            android.util.Log.e("GeminiTest", "FAILED", e)
        }
    }
}
