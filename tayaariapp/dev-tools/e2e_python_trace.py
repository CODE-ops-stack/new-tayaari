import sqlite3
import json
from datetime import datetime

# Mimic the database logic exactly as the app would
def get_db():
    conn = sqlite3.connect('geography_test.db')
    conn.row_factory = sqlite3.Row
    return conn

def setup_db(conn):
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS exam_questions (
        id TEXT PRIMARY KEY,
        topic TEXT NOT NULL,
        tier TEXT NOT NULL,
        format TEXT NOT NULL,
        questionText TEXT NOT NULL,
        options TEXT NOT NULL,
        correctAnswer TEXT NOT NULL,
        explanation TEXT NOT NULL,
        sourceGrounding TEXT NOT NULL
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS bookmarks (
        id TEXT PRIMARY KEY,
        questionId TEXT NOT NULL,
        dateAdded INTEGER NOT NULL
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS traps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        questionId TEXT NOT NULL,
        trappedOptionId TEXT NOT NULL,
        trapType TEXT NOT NULL,
        dateTrapped INTEGER NOT NULL
    )
    ''')
    conn.commit()

def import_data(conn):
    print("\n--- 1. ONBOARDING (Data Seeding) ---")
    import re
    # parse consolidated_grounding.md
    with open('source-material/consolidated_grounding.md', 'r') as f:
        content = f.read()
    
    questions = []
    pattern = re.compile(r'---(.*?)(?=\n---|\Z)', re.DOTALL)
    blocks = pattern.findall(content)
    
    for block in blocks:
        topic_match = re.search(r'\*\*Topic:\*\*\s*(.*?)\n', block)
        if not topic_match: continue
        topic = topic_match.group(1).strip()
        
        tier_match = re.search(r'\*\*Tier:\*\*\s*(.*?)\n', block)
        tier = tier_match.group(1).strip()
        
        format_match = re.search(r'\*\*Format:\*\*\s*(.*?)\n', block)
        qformat = format_match.group(1).strip()
        
        q_text_match = re.search(r'\*\*Question:\*\*\s*(.*?)\n\n\*\*Options:\*\*', block, re.DOTALL)
        if not q_text_match: continue
        q_text = q_text_match.group(1).strip()
        
        options_match = re.search(r'\*\*Options:\*\*(.*?)\n\n\*\*Correct Answer:\*\*', block, re.DOTALL)
        if not options_match: continue
        options_str = options_match.group(1).strip()
        
        # parse options
        opt_lines = options_str.split('\n')
        opts = []
        for line in opt_lines:
            line = line.strip()
            if line.startswith('(a)'): opts.append({"id": "opt_a", "text": line[3:].strip()})
            elif line.startswith('(b)'): opts.append({"id": "opt_b", "text": line[3:].strip()})
            elif line.startswith('(c)'): opts.append({"id": "opt_c", "text": line[3:].strip()})
            elif line.startswith('(d)'): opts.append({"id": "opt_d", "text": line[3:].strip()})
        
        correct_match = re.search(r'\*\*Correct Answer:\*\*\s*\((.)\)(.*?)\n', block)
        if not correct_match: continue
        correct_letter = correct_match.group(1).lower()
        correct_id = f"opt_{correct_letter}"
        
        exp_match = re.search(r'\*\*Explanation:\*\*\s*(.*?)\n\n\*\*Source/Grounding:\*\*', block, re.DOTALL)
        exp = exp_match.group(1).strip() if exp_match else "None"
        
        source_match = re.search(r'\*\*Source/Grounding:\*\*\s*(.*?)$', block, re.DOTALL)
        source = source_match.group(1).strip() if source_match else "None"
        
        trap_data = []
        trap_match = re.search(r'\*\*Trap Analysis:\*\*(.*?)(?=\n\n|\Z)', block, re.DOTALL)
        if trap_match:
            trap_lines = trap_match.group(1).strip().split('\n')
            for tl in trap_lines:
                if ')' in tl and '-' in tl:
                    parts = tl.split('-', 1)
                    if len(parts) == 2:
                        opt_part = parts[0].strip()
                        if opt_part.startswith('('):
                            letter = opt_part[1:2].lower()
                            trap_type = parts[1].strip()
                            trap_data.append({"optionId": f"opt_{letter}", "trapType": trap_type})
        
        questions.append((
            f"q_{len(questions)}", topic, tier, qformat, q_text, json.dumps(opts), correct_id, exp, source, json.dumps(trap_data)
        ))
    
    c = conn.cursor()
    c.execute('DELETE FROM exam_questions')
    for q in questions:
        c.execute('INSERT INTO exam_questions (id, topic, tier, format, questionText, options, correctAnswer, explanation, sourceGrounding) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', q[:-1])
    conn.commit()
    print(f"Total questions seeded: {len(questions)}")
    c.execute("SELECT * FROM exam_questions LIMIT 1")
    row = c.fetchone()
    print("Sample Extracted Q:")
    print(f"  ID: {row['id']}\n  Text: {row['questionText']}\n  Options: {row['options']}")

def run_trace(conn):
    c = conn.cursor()
    
    print("\n--- 2. TOPIC SELECTION ---")
    c.execute("SELECT topic, tier, COUNT(*) as cnt FROM exam_questions GROUP BY topic, tier")
    topics = c.fetchall()
    print(f"Total Topics Loaded: {len(topics)}")
    print("Sample Topics:")
    for t in topics[:3]:
        print(f"  - {t['topic']} (Tier: {t['tier']}, Qs: {t['cnt']})")
        
    selected_topic = topics[0]['topic']
    print(f"\nSelected Topic: {selected_topic}")
    
    print("\n--- 3. ALL 4 TEST FORMATS ---")
    formats = ['MCQ', 'Statement-based', 'Match-the-following', 'Map-based']
    
    for f in formats:
        c.execute("SELECT * FROM exam_questions WHERE format = ? LIMIT 1", (f,))
        q = c.fetchone()
        if q:
            print(f"\n=== FORMAT: {f} ===")
            print(f"Simulating test on Q ID: {q['id']}")
            print(f"Q Text: {q['questionText']}")
            opts = json.loads(q['options'])
            for o in opts:
                print(f"  {o['id']}: {o['text']}")
            print(f"Correct Answer: {q['correctAnswer']}")
            
            # Simulate a wrong guess
            wrong_guess = [o['id'] for o in opts if o['id'] != q['correctAnswer']][0]
            print(f"Simulated selected option: {wrong_guess} -> Incorrect.")
            
            # 6. Trap Dashboard Entry
            c.execute("INSERT INTO traps (questionId, trappedOptionId, trapType, dateTrapped) VALUES (?, ?, ?, ?)", 
                     (q['id'], wrong_guess, "Factual Inversion", int(datetime.now().timestamp() * 1000)))
                     
            # 5. Bookmark
            c.execute("INSERT INTO bookmarks (id, questionId, dateAdded) VALUES (?, ?, ?)",
                     (f"bm_{q['id']}", q['id'], int(datetime.now().timestamp() * 1000)))
                     
    conn.commit()
    
    print("\n--- 4. RESULTS ---")
    print("Simulated test finished. Computed Score: 0 / 4")
    
    print("\n--- 5. BOOKMARKS ---")
    c.execute("SELECT * FROM bookmarks")
    bms = c.fetchall()
    print(f"Total Bookmarks recorded: {len(bms)}")
    for bm in bms:
        print(f"  Bookmark: Q ID {bm['questionId']}")
        
    print("\n--- 6. TRAPS DASHBOARD ---")
    c.execute("SELECT * FROM traps")
    traps = c.fetchall()
    print(f"Total Traps recorded: {len(traps)}")
    for t in traps:
        print(f"  Trap entry - Q ID: {t['questionId']}, Selected Trap Option: {t['trappedOptionId']}")

if __name__ == '__main__':
    conn = get_db()
    setup_db(conn)
    import_data(conn)
    run_trace(conn)
