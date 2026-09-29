import re
import json

with open("source-material/question_extracted.txt", "r") as f:
    text = f.read()

# Let's split by Q.\d+. 
qs = re.split(r"Q\.(\d+)\.", text)
count = 0
results = {}

for i in range(1, len(qs), 2):
    q_num = qs[i]
    q_block = qs[i+1]
    
    # Try to parse options
    match = re.search(r"(.*?)\(a\)(.*?)\(b\)(.*?)\(c\)(.*?)\(d\)(.*?)(?:Sol\.\s*\d+\.\s*\(?([a-d])\)?)(.*)", q_block, re.DOTALL | re.IGNORECASE)
    if match:
        q_text = match.group(1).strip().replace("\n", " ")
        q_text = re.sub(r"SSC Stenographer.*?\)", "", q_text).strip()
        
        results[q_num] = {
            "questionText": q_text,
            "options": {
                "a": match.group(2).strip().replace("\n", " "), 
                "b": match.group(3).strip().replace("\n", " "), 
                "c": match.group(4).strip().replace("\n", " "), 
                "d": match.group(5).strip().replace("\n", " ")
            },
            "correctAnswer": match.group(6).strip().lower()
        }
        count += 1
    else:
        # Fallback parsing
        # Try finding just Sol. \d+
        sol_match = re.search(r"Sol\.\s*\d+\.\s*\(?([a-d])\)?", q_block, re.IGNORECASE)
        ans = sol_match.group(1).lower() if sol_match else "a"
        
        # Try to find options
        opt_a = re.search(r"\(a\)(.*?)(?=\(b\)|$)", q_block, re.DOTALL | re.IGNORECASE)
        opt_b = re.search(r"\(b\)(.*?)(?=\(c\)|$)", q_block, re.DOTALL | re.IGNORECASE)
        opt_c = re.search(r"\(c\)(.*?)(?=\(d\)|$)", q_block, re.DOTALL | re.IGNORECASE)
        opt_d = re.search(r"\(d\)(.*?)(?=Sol\.|SSC|$)", q_block, re.DOTALL | re.IGNORECASE)
        
        q_text = re.search(r"(.*?)(?=\(a\)|$)", q_block, re.DOTALL | re.IGNORECASE)
        q_text_str = q_text.group(1).strip().replace("\n", " ") if q_text else q_block[:100]
        q_text_str = re.sub(r"SSC Stenographer.*?\)", "", q_text_str).strip()
        
        results[q_num] = {
            "questionText": q_text_str,
            "options": {
                "a": opt_a.group(1).strip().replace("\n", " ") if opt_a else "",
                "b": opt_b.group(1).strip().replace("\n", " ") if opt_b else "",
                "c": opt_c.group(1).strip().replace("\n", " ") if opt_c else "",
                "d": opt_d.group(1).strip().replace("\n", " ") if opt_d else ""
            },
            "correctAnswer": ans
        }
        count += 1

print(f"Total parsed: {count}")

with open("source-material/extracted_ssc_qs.json", "w") as f:
    json.dump(results, f)

