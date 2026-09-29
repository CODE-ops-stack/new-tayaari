package com.example.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import kotlinx.coroutines.launch

import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

@Database(entities = [BookmarkedQuestionEntity::class, TrapAnalyticsEntity::class, Topic::class, Question::class, TestSession::class, RevisionItemEntity::class, QuestionAttemptEntity::class, ConfusionEventEntity::class, ReplayOutcomeEntity::class], version = 21, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun bookmarkDao(): BookmarkDao
    abstract fun confusionEventDao(): ConfusionEventDao
    abstract fun trapAnalyticsDao(): TrapAnalyticsDao
    abstract fun mistakeReplayDao(): MistakeReplayDao
    abstract fun appDao(): AppDao
    abstract fun revisionDao(): RevisionDao
    abstract fun questionAttemptDao(): QuestionAttemptDao
    abstract fun analyticsDao(): AnalyticsDao

    companion object {
        val MIGRATION_20_21 = object : Migration(20, 21) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("ALTER TABLE topics ADD COLUMN module TEXT NOT NULL DEFAULT 'Miscellaneous Topics'")
            }
        }
        val MIGRATION_19_20 = object : Migration(19, 20) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("CREATE TABLE IF NOT EXISTS `replay_outcomes` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `originalQuestionId` TEXT NOT NULL, `transferQuestionId` TEXT, `replayTimestamp` INTEGER NOT NULL, `initialEvidenceType` TEXT NOT NULL, `outcomeState` TEXT NOT NULL)")
            }
        }
        val MIGRATION_18_19 = object : Migration(18, 19) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("CREATE TABLE IF NOT EXISTS `confusion_events` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `pairId` TEXT NOT NULL, `questionId` TEXT NOT NULL, `selectedOptionText` TEXT NOT NULL, `timestamp` INTEGER NOT NULL, `evidenceLevel` TEXT NOT NULL)")
            }
        }

        val MIGRATION_17_18 = object : Migration(17, 18) {
            override fun migrate(database: SupportSQLiteDatabase) {
                database.execSQL("ALTER TABLE questions ADD COLUMN familyId TEXT")
                database.execSQL("ALTER TABLE questions ADD COLUMN familyStage TEXT")
            }
        }

        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "tayaari_database"
                )
                
                .addMigrations(MIGRATION_17_18, MIGRATION_18_19, MIGRATION_19_20, MIGRATION_20_21)
                .addCallback(object : RoomDatabase.Callback() {
                    override fun onOpen(db: androidx.sqlite.db.SupportSQLiteDatabase) {
                        super.onOpen(db)
                        kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
                            try {
                                val dao = getDatabase(context).appDao()
                                // Populate if topics OR questions are empty
                                val topicCount = dao.getTopicsCount()
                                val questionCount = dao.getQuestionCount()
                                if (topicCount == 0 || questionCount == 0) {
                                    val mdContent = context.assets.open("consolidated_grounding.md").bufferedReader().use { it.readText() }
                                    com.example.repository.DataImporter.importFromMarkdown(context, mdContent)
                                }
                            } catch (e: Exception) {
                                e.printStackTrace()
                            }
                        }
                    }
                })
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}


