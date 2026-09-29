package com.example.database

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query

@Entity(tableName = "confusion_events")
data class ConfusionEventEntity(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val pairId: String,
    val questionId: String,
    val selectedOptionText: String,
    val timestamp: Long,
    val evidenceLevel: String
)

@Dao
interface ConfusionEventDao {
    @Insert
    fun insertEvent(event: ConfusionEventEntity)

    @Query("SELECT * FROM confusion_events WHERE pairId = :pairId")
    fun getEventsForPair(pairId: String): List<ConfusionEventEntity>

    @Query("SELECT * FROM confusion_events")
    suspend fun getAllEventsSync(): List<ConfusionEventEntity>
}