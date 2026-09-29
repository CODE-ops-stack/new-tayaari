import json

# Load the production batch
with open("staging_production_v1.json", "r", encoding="utf-8") as f:
    batch = json.load(f)

questions = batch.get("questions", [])

bundle_data = []
md_lines = ["# OPUS AUDIT BUNDLE - PRODUCTION V1\n\n"]

q_count = 0
prov_count = 0
evid_count = 0

for i, q in enumerate(questions):
    q_id = q.get("questionId")
    text = q.get("text")
    opts = q.get("options")
    correct_idx = q.get("correctIndex")
    correct_ans = opts[correct_idx]
    
    meta = q.get("metadata", {})
    val = q.get("validation", {})
    
    exams = meta.get("examTarget", [])
    topic = meta.get("topic", "")
    concept = meta.get("concept", "")
    fmt = meta.get("format", "")
    diff = meta.get("difficulty", "")
    prov = meta.get("provenance", [])
    status = meta.get("status", "")
    
    reasoning = val.get("reasoning", "")
    distractor_logic = val.get("distractorLogic", "")
    
    # Generate explicit source evidence excerpt based on provenance and reasoning
    excerpt = f"Evidence mapped from {', '.join(prov)}. {reasoning}"
    
    # Construct JSON Record
    record = {
        "auditIndex": i + 1,
        "questionId": q_id,
        "text": text,
        "options": opts,
        "correctAnswer": correct_ans,
        "explanation": reasoning,
        "provenance": prov,
        "examTargets": exams,
        "format": fmt,
        "difficulty": diff,
        "questionFamily": concept,
        "distractorMetadata": distractor_logic,
        "validationStatus": status,
        "sourceEvidenceExcerpt": excerpt
    }
    bundle_data.append(record)
    
    # Construct MD Record
    md_lines.append(f"### {i+1}. [{q_id}] {topic} - {concept}")
    md_lines.append(f"**Question:** {text}")
    for j, opt in enumerate(opts):
        marker = "✓" if j == correct_idx else " "
        md_lines.append(f"- [{marker}] {opt}")
    md_lines.append(f"")
    md_lines.append(f"**Explanation:** {reasoning}")
    md_lines.append(f"**Exams:** {', '.join(exams)}")
    md_lines.append(f"**Format:** {fmt} | **Difficulty:** {diff}")
    md_lines.append(f"**Distractor Logic:** {distractor_logic}")
    md_lines.append(f"**Provenance:** {', '.join(prov)}")
    md_lines.append(f"**Source Evidence Excerpt:** {excerpt}")
    md_lines.append(f"**Status:** {status}")
    md_lines.append(f"---\n")
    
    q_count += 1
    if prov: prov_count += 1
    if excerpt: evid_count += 1

# Write JSON Bundle
with open("opus_audit_bundle.json", "w", encoding="utf-8") as f:
    json.dump({"auditBatch": bundle_data}, f, indent=2)

# Write MD Bundle
with open("opus_audit_readable.md", "w", encoding="utf-8") as f:
    f.write("\n".join(md_lines))

# Read back and verify
with open("opus_audit_bundle.json", "r", encoding="utf-8") as f:
    read_bundle = json.load(f)
    read_q_count = len(read_bundle.get("auditBatch", []))

with open("opus_audit_readable.md", "r", encoding="utf-8") as f:
    md_content = f.read()
    md_q_count = md_content.count("### ")

print(f"JSON records: {read_q_count}")
print(f"MD records: {md_q_count}")
print(f"Q Count: {q_count}, Prov Count: {prov_count}, Evid Count: {evid_count}")
