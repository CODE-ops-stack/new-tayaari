import json
import os
import random

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run_audit():
    with open(os.path.join(BASE_DIR, "docs", "v13_1_accepted_sample.json")) as f:
        accepted = json.load(f)
        
    random.seed(42)
    sample = random.sample(accepted, min(50, len(accepted)))
    
    issues = []
    
    for q in sample:
        stem = q.get("stem", "").lower()
        ans = q.get("correct_answer_text", "").lower()
        exp = q.get("explanation", "").lower()
        
        if "indus" in ans and "industrial" in exp and "river" not in exp:
            issues.append(f"{q['id']}: Indus/Industrial collision")
            
        if "star" in ans and "started" in exp and "sky" not in exp:
            issues.append(f"{q['id']}: Star/Started collision")
            
        if ans in stem:
            issues.append(f"{q['id']}: Leakage - answer in stem")
            
        opts = [v.lower() for v in q.get("options", {}).values()]
        if len(set(opts)) != 4:
            issues.append(f"{q['id']}: Non-unique options")
            
    print(f"Audit Complete. Issues found: {len(issues)}")
    for i in issues:
        print(i)
        
    audit = {
        "status": "PASS" if len(issues) == 0 else "FAIL",
        "sample_size": len(sample),
        "issues_found": len(issues),
        "issues": issues
    }
    
    with open(os.path.join(BASE_DIR, "docs", "v13_1_quality_audit.json"), "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)

if __name__ == "__main__":
    run_audit()
