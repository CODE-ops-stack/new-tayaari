package com.example.database

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import kotlinx.coroutines.launch

import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

@Database(entities = [BookmarkedQuestionEntity::class, TrapAnalyticsEntity::class, Topic::class, Question::class, TestSession::class, RevisionItemEntity::class, QuestionAttemptEntity::class, ConfusionEventEntity::class, ReplayOutcomeEntity::class, UserEntity::class], version = 24, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun bookmarkDao(): BookmarkDao
    abstract fun confusionEventDao(): ConfusionEventDao
    abstract fun trapAnalyticsDao(): TrapAnalyticsDao
    abstract fun mistakeReplayDao(): MistakeReplayDao
    abstract fun appDao(): AppDao
    abstract fun revisionDao(): RevisionDao
    abstract fun questionAttemptDao(): QuestionAttemptDao
    abstract fun analyticsDao(): AnalyticsDao

    companion object {
        
                        val MIGRATION_23_24 = object : Migration(23, 24) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("ALTER TABLE `users` RENAME COLUMN `targetExamId` TO `targetExamIds`")
            }
        }

        val MIGRATION_22_23 = object : Migration(22, 23) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("CREATE TABLE IF NOT EXISTS `users` (`id` INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, `username` TEXT NOT NULL, `passwordHash` TEXT NOT NULL, `targetExamId` TEXT)")
            }
        }

        val MIGRATION_21_22 = object : Migration(21, 22) {
            override fun migrate(db: SupportSQLiteDatabase) {
                // No-op: Data sync handled dynamically by CloudQuestionSyncService
            }
        }

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
                
                .addMigrations(MIGRATION_17_18, MIGRATION_18_19, MIGRATION_19_20, MIGRATION_20_21, MIGRATION_21_22, MIGRATION_22_23, MIGRATION_23_24)
                .addCallback(object : RoomDatabase.Callback() {
                    override fun onCreate(db: androidx.sqlite.db.SupportSQLiteDatabase) {
                        super.onCreate(db)
                        // Pre-populate default Guest Aspirant in SQLite on initial database creation
                        db.execSQL("INSERT OR IGNORE INTO `users` (`id`, `username`, `passwordHash`, `targetExamIds`) VALUES (1, 'Guest Aspirant', 'guest', 'UPSC_CSE_2026')")
                    }
                    override fun onOpen(db: androidx.sqlite.db.SupportSQLiteDatabase) {
                        super.onOpen(db)
                        kotlinx.coroutines.CoroutineScope(kotlinx.coroutines.Dispatchers.IO).launch {
                            try {
                                val dbInstance = getDatabase(context)
                                val dao = dbInstance.appDao()
                                val userDao = dbInstance.userDao()
                                if (userDao.getUserById(1) == null) {
                                    userDao.insertUser(UserEntity(id = 1, username = "Guest Aspirant", passwordHash = "guest", targetExamIds = "UPSC_CSE_2026"))
                                }
                                val topicCount = dao.getTopicsCount()
                                if (topicCount == 0) {
                                    dao.insertTopics(com.example.repository.CloudQuestionSyncService.canonicalTopicsList)
                                    com.example.repository.CloudQuestionSyncService.syncWithCloud(context, force = true)
                                }
                            } catch (e: Exception) {
                                android.util.Log.e("AppDatabase", "Error initializing topics catalog from cloud", e)
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


