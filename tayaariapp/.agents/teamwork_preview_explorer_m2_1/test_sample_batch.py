import os
import json
import urllib.request

api_key = None
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.strip().split("=", 1)[1].strip()

# Load golden eval set
with open("data/golden_eval_set.json", "r", encoding="utf-8") as f:
    gold = json.load(f)

test_ids = ["POS-001", "POS-009", "POS-013", "POS-025", "POS-033", "POS-037",
            "NEG-001", "NEG-011", "NEG-020", "NEG-029", "NEG-038", "NEG-047"]

sample_cases = [ex for ex in gold["examples"] if ex["id"] in test_ids]

knowledge_node_schema = {
    "type": "object",
    "properties": {
        "is_valid_knowledge": {
            "type": "boolean",
            "description": "True ONLY if text is a complete, self-contained, fact-bearing educational statement. False if it has MCQ option labels, headers, watermarks, abrupt fragment ends, or unresolved pronouns (e.g. starting with They/It/These without antecedent)."
        },
        "rejection_category": {
            "type": "string",
            "enum": ["none", "mcq_leakage", "watermark_header", "syntactic_fragment", "broken_reading_order", "table_formatting_artifact", "anaphoric_unresolved"]
        },
        "intent_type": {
            "type": "string",
            "enum": [
                "definition", "attribute", "cause/effect", "comparison", "spatial",
                "distribution", "classification", "quantity", "sequence",
                "condition", "exception", "process", "part-of", "member-of", "none"
            ]
        },
        "primary_entity": {"type": "string"},
        "predicate": {"type": "string"},
        "secondary_entities": {
            "type": "array",
            "items": {"type": "string"}
        }
    },
    "required": ["is_valid_knowledge", "rejection_category", "intent_type", "primary_entity", "predicate", "secondary_entities"]
}

system_prompt = """You are an educational knowledge representation engine.
Evaluate whether the input text is a valid educational proposition or noise.
Valid intents: definition, attribute, cause/effect, comparison, spatial, distribution, classification, quantity, sequence, condition, exception, process, part-of, member-of.
Reject noise into:
- mcq_leakage: contains (a), (b), (c), Question, Option markers
- watermark_header: contains brand/book headers (PARMAR SSC, ISBN, www...)
- syntactic_fragment: broken/truncated clauses ending in 'and', 'with', '...'
- broken_reading_order: concatenated multi-column text lacking sentence syntax
- table_formatting_artifact: markdown pipes |---|
- anaphoric_unresolved: pronouns like 'They', 'It', 'These' with no antecedent in the sentence
"""

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"

print(f"Testing {len(sample_cases)} golden eval cases...")
for ex in sample_cases:
    payload = {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [{"text": f"Evaluate: \"{ex['text']}\""}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": knowledge_node_schema,
            "temperature": 0.0
        }
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            parsed = json.loads(res["candidates"][0]["content"]["parts"][0]["text"])
            
            # Check match
            expected_valid = (ex["expected_label"] == "positive")
            got_valid = parsed["is_valid_knowledge"]
            intent_match = (parsed["intent_type"] == ex["intent"]) if expected_valid else (parsed["rejection_category"] != "none")
            
            status = "PASS" if (expected_valid == got_valid and intent_match) else "FAIL"
            print(f"[{status}] {ex['id']} (Expected: {ex['expected_label']}/{ex['intent'] or ex.get('rejection_category')}) -> Got: valid={got_valid}, intent={parsed['intent_type']}, rej={parsed['rejection_category']}")
            if expected_valid:
                print(f"      Entity: '{parsed['primary_entity']}' | Predicate: '{parsed['predicate'][:60]}...'")
    except Exception as e:
        print(f"[ERR] {ex['id']}: {e}")
