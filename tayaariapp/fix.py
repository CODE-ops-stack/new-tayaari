import re

with open('app/src/main/java/com/example/repository/LocalRepository.kt', 'r', encoding='utf-8') as f:
    text = f.read()

# The file contains duplicated chunks and malformed bookmark functions.
# Let's just find the `bookmarkDao` parts, the `logConfusionEvent` parts, and reconstruct.
# Actually, since I have full context of what it should be, I can just do a regex replace.

# Remove the duplicated middle chunk
text = re.sub(r'bookmarkDao\.insertBookmark\(entity\)\n    }\n\n    suspend fun removeBookmark\(id: String\) = withContext\(Dispatchers\.IO\) {\n        bookmarkDao\.deleteBookmark\(id\)\n    }\n\n    suspend fun logConfusionEvent.*?getRecentFamilyAttempts\(since\)\n    }\n\n\n', '', text, flags=re.DOTALL)

with open('app/src/main/java/com/example/repository/LocalRepository.kt', 'w', encoding='utf-8') as f:
    f.write(text)

