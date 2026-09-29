import json

def self_audit():
    with open("validation_batch_v3.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    questions = data["questions"]
    print(f"Self-Auditing {len(questions)} candidates...")
    
    passed = True
    for q in questions:
        print(f"Auditing Question: {q['questionId']} - {q['text'][:50]}...")
        
        # 1. Fact Check (simulation)
        meta = q.get("metadata", {})
        
        # 2. Explanation
        exp = q.get("explanation", "")
        if len(exp) < 20 or "sourced" in exp.lower():
            print("  FAIL: Explanation insufficient.")
            passed = False
            
        # 3. Distractor plausibility
        if not meta.get("distractorCategoryMatched"):
            print("  FAIL: Distractor mismatch.")
            passed = False
            
        # 4. Cognitive Demand vs Exam
        cog = meta.get("cognitiveDemand")
        exam = meta.get("examTarget", [])
        if "UPSC" in exam and cog == "RECALL":
            print("  FAIL: UPSC question is RECALL.")
            passed = False
            
        # 5. Difficulty 
        diff = meta.get("difficulty")
        if cog == "RECALL" and diff == "HARD":
            print("  FAIL: RECALL labeled as HARD.")
            passed = False
            
    if data["clue_leakage"] > 0 or data["template_violations"] > 0:
        print(f"  FAIL: Batch contains leaks ({data['clue_leakage']}) or template violations ({data['template_violations']}).")
        passed = False
        
    if passed:
        print("Self-Audit: PASS")
    else:
        print("Self-Audit: FAIL")
        
self_audit()
