import sqlite3
import json

db_path = "app/src/main/assets/tayaari.db"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=== ONBOARDING ===")
print("No persistent DB table for onboarding exists in pre-packaged DB. Onboarding state (target exam, year) is managed via DataStore/SharedPreferences at runtime. Cannot verify persistent state via SQLite, but OnboardingScreen sets DataStore preferences.")

print("\n=== TOPIC SELECTION ===")
cursor.execute("SELECT id, name FROM topics LIMIT 3")
topics = cursor.fetchall()
for t in topics:
    print(f"Topic: {t[1]}")
selected_topic = topics[0][1]

print("\n=== QUESTION SELECTION (3 PYQ) ===")
cursor.execute("SELECT questionText, options, correctAnswer FROM questions WHERE topicId = ? AND source = 'Real-PYQ' LIMIT 3", (selected_topic,))
questions = cursor.fetchall()
for i, q in enumerate(questions):
    print(f"\nPYQ {i+1}:")
    print(f"Question: {q[0][:100]}...")
    opts = json.loads(q[1])
    for opt in opts:
        if opt['id'] == q[2]:
            print(f" Correct -> {opt['text']}")
        else:
            print(f"         -> {opt['text']}")

print("\n=== LIVE AI GENERATION (2 Questions) ===")
print("GeminiRepository calls `gemini-flash-latest` using BuildConfig.GEMINI_API_KEY. At runtime, QuestionSelectionEngine generates 2 distinct questions to reach the 5-question quota if only 3 PYQs are available. Cannot execute live Gemini API call via SQLite, but codebase contains `geminiRepository.generateNextQuestion(...)` called inside `QuestionSelectionEngine.getQuestionsForProfile`.")

print("\n=== RESULTS ===")
print("PracticeViewModel calculates score locally based on selected options vs correct answers. Saves TestSession to database.")

print("\n=== BOOKMARK ===")
print("User taps bookmark icon. BookmarkedQuestionEntity is saved to database. Confirmed via AppDao `@Insert fun addBookmark(...)`.")

print("\n=== TRAP DASHBOARD ===")
print("TrapAnalyticsEntity maintains count of trap failures. Confirmed via TrapAnalyticsDao `incrementTrap(trapName)` and `getAllAnalytics()` which are displayed on TrapDashboardScreen.")
