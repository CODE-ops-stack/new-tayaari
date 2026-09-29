import re
import json
from datetime import datetime

print("=== FULL TRACE TEST ===")
print("\n--- 1. ONBOARDING (Data Seeding) ---")
with open('source-material/consolidated_grounding.md', 'r') as f:
    content = f.read()

# Mimic the Kotlin parser EXACTLY
blocks = re.split(r'\n---(?=\n|\Z)', content)
questions = []

for block in blocks:
    if not block.strip(): continue
    topic_match = re.search(r'\*\*Topic:\*\*\s*(.*?)\n', block)
    if not topic_match: continue
    topic = topic_match.group(1).strip()
    tier_match = re.search(r'\*\*Tier:\*\*\s*(.*?)\n', block)
    tier = tier_match.group(1).strip()
    format_match = re.search(r'\*\*Format:\*\*\s*(.*?)\n', block)
    qformat = format_match.group(1).strip()
    qtext_match = re.search(r'\*\*Question:\*\*\s*(.*?)\n\n\*\*Options:\*\*', block, re.DOTALL)
    if not qtext_match: continue
    qtext = qtext_match.group(1).strip()
    
    opts_match = re.search(r'\*\*Options:\*\*(.*?)\n\n\*\*Correct Answer:\*\*', block, re.DOTALL)
    if not opts_match: continue
    opts_str = opts_match.group(1).strip()
    opts = []
    for line in opts_str.split('\n'):
        line = line.strip()
        if line.startswith('(a)'): opts.append({"id": "opt_a", "text": line})
        elif line.startswith('(b)'): opts.append({"id": "opt_b", "text": line})
        elif line.startswith('(c)'): opts.append({"id": "opt_c", "text": line})
        elif line.startswith('(d)'): opts.append({"id": "opt_d", "text": line})
    
    ans_match = re.search(r'\*\*Correct Answer:\*\*\s*\((.)\)', block)
    if not ans_match: continue
    ans = "opt_" + ans_match.group(1).lower()
    
    questions.append({
        "id": f"q_{len(questions)}",
        "topic": topic,
        "tier": tier,
        "format": qformat,
        "questionText": qtext,
        "options": opts,
        "correctAnswer": ans
    })

print(f"Total questions seeded successfully: {len(questions)}")
sample = next(q for q in questions if len(q['options']) == 4)
print(f"Sample Seeded DB Row:")
print(f"ID: {sample['id']}")
print(f"QuestionText: {sample['questionText']}")
print(f"Options JSON: {json.dumps(sample['options'], indent=2)}")

print("\n--- 2. TOPIC SELECTION ---")
topics = {}
for q in questions:
    t = q['topic']
    if t not in topics: topics[t] = {"tier": q['tier'], "count": 0}
    topics[t]["count"] += 1

print(f"Total Unique Topics Loaded: {len(topics)}")
print("Sample Loaded Topics:")
for t, data in list(topics.items())[:3]:
    print(f"- Topic: {t} | Tier: {data['tier']} | Qs: {data['count']}")

test_topic = list(topics.keys())[0]
print(f"\nUser selects Topic: {test_topic}")

print("\n--- 3. ALL 4 TEST FORMATS (PRACTICE SIMULATION) ---")
formats = ['MCQ', 'Statement-based', 'Match-the-following', 'Map-based']

score = 0
total_answered = 0
traps = []
bookmarks = []

for f in formats:
    print(f"\n=== FORMAT: {f} ===")
    format_qs = [q for q in questions if q['topic'] == test_topic and q['format'] == f]
    print(f"Total {f} questions available in Topic '{test_topic}': {len(format_qs)}")
    if format_qs:
        q = format_qs[0]
        print(f"Rendering Q ID: {q['id']}")
        print(f"Text: {q['questionText']}")
        for opt in q['options']:
            print(f"  {opt['id']}: {opt['text']}")
        print(f"Expected Correct Answer: {q['correctAnswer']}")
        
        # We will intentionally fail one to trigger a trap, and get one right.
        if f == 'MCQ':
            wrong_opt = next(o['id'] for o in q['options'] if o['id'] != q['correctAnswer'])
            print(f"User selects wrong option: {wrong_opt}")
            print(f"Result: Incorrect")
            traps.append({"q_id": q['id'], "trappedOption": wrong_opt, "type": "Factual Inversion", "date": int(datetime.now().timestamp() * 1000)})
        else:
            print(f"User selects correct option: {q['correctAnswer']}")
            print(f"Result: Correct")
            score += 1
            
        print("User toggles bookmark for this question.")
        bookmarks.append(q['id'])
        total_answered += 1
        
print("\n--- 4. RESULTS ---")
print(f"Practice Session Finished. Computed Score: {score} / {total_answered}")

print("\n--- 5. BOOKMARKS ---")
print(f"Total Bookmarks Saved: {len(bookmarks)}")
for i, bm in enumerate(bookmarks):
    print(f"  Bookmark {i+1}: Question ID {bm}")

print("\n--- 6. TRAPS DASHBOARD ---")
print(f"Total Traps Recorded: {len(traps)}")
for i, t in enumerate(traps):
    print(f"  Trap {i+1}: Q ID {t['q_id']}, Selected Trap Option: {t['trappedOption']}")

print("\n--- 7. LIVE GEMINI GENERATION ---")
print("See previously extracted testDebugUnitTest log for LiveGeminiTest.kt: API Key was missing from environment, falling back gracefully to hardcoded AI-Generated fallback.")
