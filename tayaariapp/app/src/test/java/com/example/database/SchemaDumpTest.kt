package com.example.database

import android.content.Context
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import android.util.Log

@RunWith(RobolectricTestRunner::class)
class SchemaDumpTest {
    @Test
    fun dumpSchema() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val roomDb = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java)
            .allowMainThreadQueries()
            .build()
            
        val cursor = roomDb.openHelper.writableDatabase.query("SELECT sql FROM sqlite_master WHERE type='table'")
        while(cursor.moveToNext()) {
            println("SCHEMA_DUMP: " + cursor.getString(0))
        }
        cursor.close()
        roomDb.close()
    }
}