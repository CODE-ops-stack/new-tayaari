import re

with open("app/src/main/java/com/example/database/Daos.kt", "r") as f:
    text = f.read()

text = text.replace("""    @Query("DELETE FROM questions WHERE examRelevance = 'UPSC'")
    suspend fun clearAllQuestions()
    @Query("DELETE FROM questions")
    suspend fun deleteUpscQuestions(): Int""", """    @Query("DELETE FROM questions")
    suspend fun clearAllQuestions(): Int
    
    @Query("DELETE FROM questions WHERE examRelevance = 'UPSC'")
    suspend fun deleteUpscQuestions(): Int""")

with open("app/src/main/java/com/example/database/Daos.kt", "w") as f:
    f.write(text)
