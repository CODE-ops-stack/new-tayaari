import json
import os

files = [
    "batch1_part1.json",
    "batch1_part2.json",
    "batch1_part3.json",
    "batch1_part4.json",
    "batch1_part5.json"
]

all_candidates = []
accepted = []
rejected = []
review = []

for f in files:
    path = os.path.join(r"C:\Users\harsh\Downloads\tayaari\tayaariapp", f)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as file:
                data = json.load(file)
                all_candidates.extend(data)
        except Exception as e:
            print(f"Error reading {f}: {e}")

duplicates = set()
question_texts = set()

for q in all_candidates:
    text = q.get("questionText", "").strip().lower()
    
    # 1. Duplicate Check
    if text in question_texts:
        q["rejectReason"] = "EXACT_DUPLICATE"
        rejected.append(q)
        continue
    question_texts.add(text)
    
    # 2. Field Check
    if not all([q.get("options"), q.get("correctAnswer"), q.get("explanation"), q.get("metadata")]):
        q["rejectReason"] = "MISSING_FIELDS"
        rejected.append(q)
        continue
        
    # 3. Correct Answer Format Check
    valid_ids = [opt["id"] for opt in q["options"]]
    if q["correctAnswer"] not in valid_ids:
        q["rejectReason"] = "INVALID_CORRECT_ANSWER"
        rejected.append(q)
        continue
        
    # 4. Source Conflict Check
    exp = q["explanation"]
    if "conflict" in exp.get("wrongReason", "").lower() or "conflict" in exp.get("correctReason", "").lower():
        q["rejectReason"] = "SOURCE_CONFLICT"
        review.append(q)
        continue
        
    accepted.append(q)

staging_data = {
    "batchId": "BATCH_1",
    "totalGenerated": len(all_candidates),
    "totalAccepted": len(accepted),
    "totalRejected": len(rejected),
    "totalReview": len(review),
    "questions": accepted
}

with open("staging_batch_1.json", "w", encoding="utf-8") as out:
    json.dump(staging_data, out, indent=2)

print(f"Batch 1 Quality Gate Results:")
print(f"Generated: {len(all_candidates)}")
print(f"Accepted: {len(accepted)}")
print(f"Rejected: {len(rejected)}")
print(f"Review Required: {len(review)}")

for r in rejected:
    print(f"REJECTED: {r.get('id')} - {r.get('rejectReason')}")
    
for r in review:
    print(f"REVIEW: {r.get('id')} - {r.get('rejectReason')}")
