with open("app/src/main/java/com/example/database/Daos.kt", "r") as f:
    content = f.read()

# Remove from BookmarkDao
bad = """    @Query("SELECT COUNT(*) FROM topics")
    suspend fun getTopicsCount(): Int

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBookmark(bookmark: BookmarkedQuestionEntity)"""

good = """    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertBookmark(bookmark: BookmarkedQuestionEntity)"""

content = content.replace(bad, good)

# Add to AppDao
old_app = """@Dao
interface AppDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTopics(topics: List<Topic>)"""

new_app = """@Dao
interface AppDao {
    @Query("SELECT COUNT(*) FROM topics")
    suspend fun getTopicsCount(): Int

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTopics(topics: List<Topic>)"""

content = content.replace(old_app, new_app)

with open("app/src/main/java/com/example/database/Daos.kt", "w") as f:
    f.write(content)
