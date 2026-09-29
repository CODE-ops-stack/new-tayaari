package com.example.database

import android.content.Context
import android.database.sqlite.SQLiteDatabase
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class RealMigrationTest {

    @Test
    fun testMigration17To19_preservesDataAndAddsColumns() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val dbFile = context.getDatabasePath("migration_test.db")
        if (dbFile.exists()) {
            dbFile.delete()
        }
        dbFile.parentFile?.mkdirs()

        // 1. Create version 17 database manually using raw SQLite
        val rawDb = SQLiteDatabase.openOrCreateDatabase(dbFile, null)
        rawDb.version = 17
        
        
        rawDb.execSQL("CREATE TABLE `bookmarks` (`id` TEXT NOT NULL, `format` TEXT NOT NULL, `payloadJson` TEXT NOT NULL, PRIMARY KEY(`id`))")
        rawDb.execSQL("CREATE TABLE `trap_analytics` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `trapType` TEXT NOT NULL, `frequency` INTEGER NOT NULL, `failedQuestionsJson` TEXT NOT NULL)")
        rawDb.execSQL("CREATE TABLE `topics` (`id` INTEGER NOT NULL, `name` TEXT NOT NULL, `source` TEXT NOT NULL, PRIMARY KEY(`id`))")
        
        // V17 questions table without familyId and familyStage
        rawDb.execSQL("CREATE TABLE `questions` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `topicId` INTEGER NOT NULL, `tier` TEXT NOT NULL, `format` TEXT NOT NULL, `examRelevance` TEXT NOT NULL, `source` TEXT NOT NULL, `specificExam` TEXT NOT NULL, `questionText` TEXT NOT NULL, `options` TEXT NOT NULL, `correctAnswer` TEXT NOT NULL, `explanation` TEXT NOT NULL, `distractorDissections` TEXT NOT NULL, `imageUrl` TEXT NOT NULL)")
        
        rawDb.execSQL("CREATE TABLE `test_sessions` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `timestamp` INTEGER NOT NULL, `examProfile` TEXT NOT NULL, `score` INTEGER NOT NULL, `totalQuestions` INTEGER NOT NULL)")
        rawDb.execSQL("CREATE TABLE `revision_items` (`questionId` TEXT NOT NULL, `firstAttemptTime` INTEGER NOT NULL, `lastAttemptTime` INTEGER NOT NULL, `attemptCount` INTEGER NOT NULL, `correctCount` INTEGER NOT NULL, `incorrectCount` INTEGER NOT NULL, `masteryState` TEXT NOT NULL, `nextRevisionDate` INTEGER NOT NULL, `priority` INTEGER NOT NULL, `associatedTrap` TEXT, PRIMARY KEY(`questionId`))")
        rawDb.execSQL("CREATE TABLE `question_attempts` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `questionId` TEXT NOT NULL, `timestamp` INTEGER NOT NULL, `outcome` TEXT NOT NULL, `confidence` TEXT, `timeSpentSeconds` INTEGER NOT NULL, `trapFallenInto` TEXT)")
        rawDb.execSQL("CREATE TABLE room_master_table (id INTEGER PRIMARY KEY,identity_hash TEXT)")
        
        // Insert realistic data
        rawDb.execSQL(
            "INSERT INTO `questions` (`id`, `topicId`, `tier`, `format`, `examRelevance`, `source`, `specificExam`, `questionText`, `options`, `correctAnswer`, `explanation`, `distractorDissections`, `imageUrl`) " +
            "VALUES (1, 1, 'TIER_1', 'MCQ', 'HIGH', 'SOURCE', 'EXAM', 'Q Text', '[]', 'A', 'Expl', '[]', '')"
        )
        rawDb.execSQL(
            "INSERT INTO `bookmarks` (`id`, `format`, `payloadJson`) VALUES ('q1', 'MCQ', '{}')"
        )
        rawDb.execSQL(
            "INSERT INTO `topics` (`id`, `name`, `source`) VALUES (1, 'Test Topic', 'Test Source')"
        )
        rawDb.close()

        // 2. Open with Room version 18, supplying MIGRATION_17_18
        val roomDb = Room.databaseBuilder(context, AppDatabase::class.java, "migration_test.db")
            .addMigrations(AppDatabase.MIGRATION_17_18, AppDatabase.MIGRATION_18_19, AppDatabase.MIGRATION_19_20, AppDatabase.MIGRATION_20_21)
            .allowMainThreadQueries()
            .build()

        // 3. Verify data preservation and column nullability
        val cursor = roomDb.query("SELECT * FROM questions WHERE id = 1", null)
        assertTrue("Record should exist", cursor.moveToFirst())
        
        val familyIdIndex = cursor.getColumnIndex("familyId")
        val familyStageIndex = cursor.getColumnIndex("familyStage")
        
        assertTrue("familyId column should exist", familyIdIndex != -1)
        assertTrue("familyStage column should exist", familyStageIndex != -1)
        
        assertTrue("familyId should be null for old record", cursor.isNull(familyIdIndex))
        assertTrue("familyStage should be null for old record", cursor.isNull(familyStageIndex))
        
        assertEquals("Q Text", cursor.getString(cursor.getColumnIndexOrThrow("questionText")))
        
        cursor.close()
        
        val bookmarkCursor = roomDb.query("SELECT * FROM bookmarks WHERE id = 'q1'", null)
        assertTrue("Bookmark record should be preserved", bookmarkCursor.moveToFirst())
        
        bookmarkCursor.close()
        
        val confusionCursor = roomDb.query("SELECT * FROM sqlite_master WHERE type='table' AND name='confusion_events'", null)
        assertTrue("confusion_events table should exist", confusionCursor.moveToFirst())
        confusionCursor.close()

        
        
        val topicCursor = roomDb.query("SELECT * FROM topics WHERE id = 1", null)
        assertTrue("Topic record should exist", topicCursor.moveToFirst())
        
        val moduleIndex = topicCursor.getColumnIndex("module")
        assertTrue("module column should exist", moduleIndex != -1)
        assertEquals("Miscellaneous Topics", topicCursor.getString(moduleIndex))
        assertEquals("Test Topic", topicCursor.getString(topicCursor.getColumnIndexOrThrow("name")))
        topicCursor.close()

        roomDb.close()
    }
}