file = 'app/src/main/java/com/example/database/Daos.kt'
with open(file, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('    suspend fun getDueItemsCountSync(currentTime: Long): Int', '    suspend fun getDueItemsCountSync(currentTime: Long): Int\n\n    @Query("SELECT * FROM revision_items")\n    suspend fun getAllRevisionItems(): List<RevisionItemEntity>')

with open(file, 'w', encoding='utf-8') as f:
    f.write(text)
