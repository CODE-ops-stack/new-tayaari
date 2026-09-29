import os
import json
import urllib.request

api_key = None
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY="):
                api_key = line.strip().split("=", 1)[1].strip()

# Complex educational sentence from golden eval set POS-001 or POS-041
test_sentence = "While nearly all planets in the Solar System rotate counter-clockwise from west to east on their axes, Venus and Uranus are unique exceptions that rotate clockwise in retrograde motion from east to west."

knowledge_node_schema = {
    "type": "object",
    "properties": {
        "is_valid_knowledge": {
            "type": "boolean",
            "description": "True if sentence is a valid educational fact. False if it is an incomplete fragment, watermark, question token, or broken reading order."
        },
        "rejection_reason": {
            "type": "string",
            "description": "If is_valid_knowledge is false, state why (e.g., mcq_leakage, watermark, fragment, broken_reading_order, anaphoric_unresolved)."
        },
        "intent_type": {
            "type": "string",
            "enum": [
                "definition", "attribute", "cause/effect", "comparison", "spatial",
                "distribution", "classification", "quantity", "sequence",
                "condition", "exception", "process", "part-of", "member-of", "none"
            ]
        },
        "primary_entity": {
            "type": "string",
            "description": "The central entity or subject being defined, described, or analyzed."
        },
        "predicate": {
            "type": "string",
            "description": "The factual claim, property, action, or relation asserted about the primary entity."
        },
        "secondary_entities": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Related concepts, comparing entities, constituent parts, or geographical anchors."
        },
        "conditions": {
            "type": "string",
            "description": "Any boundary conditions, temporal qualifiers, or prerequisites (null if none)."
        },
        "quantitative_data": {
            "type": "object",
            "properties": {
                "value": {"type": "number"},
                "unit": {"type": "string"},
                "parameter": {"type": "string"}
            },
            "description": "Numerical measurement if present."
        }
    },
    "required": ["is_valid_knowledge", "intent_type", "primary_entity", "predicate", "secondary_entities"]
}

system_prompt = """You are an expert educational knowledge representation engine for high-stakes Indian exams (UPSC, BPSC, SSC).
Analyze the input text and extract structured educational facts into one of the 14 semantic intents:
- definition: core formal definition of a concept or term.
- attribute: inherent physical, chemical, or operational properties.
- cause/effect: mechanism where X causes Y or Y occurs due to X.
- comparison: contrast or similarity between two or more entities.
- spatial: geographical location, trajectory, boundaries, or orientation.
- distribution: geographic/demographic prevalence, concentration, or percentage spread.
- classification: taxonomy, types, categories, or divisions based on criteria.
- quantity: numerical measurements, dimensions, percentages, time spans, or constants.
- sequence: chronological order, stages of life cycle, or step-by-step evolution.
- condition: prerequisite conditions or rules required for an event/phenomenon to occur.
- exception: divergence or anomaly departing from a general rule/norm.
- process: dynamic multi-step physical or biological mechanism.
- part-of: compositional relationship (constituent part forming a whole).
- member-of: instance/exemplar belonging to an ontological set or group.

If the text contains exam options ('(a)', '(b)'), headers, watermarks, fragments ending abruptly, or unresolved pronouns ('They are big...'), mark is_valid_knowledge as false.
"""

payload = {
    "systemInstruction": {
        "parts": [{"text": system_prompt}]
    },
    "contents": [{
        "parts": [{"text": f"Extract knowledge from: \"{test_sentence}\""}]
    }],
    "generationConfig": {
        "responseMimeType": "application/json",
        "responseSchema": knowledge_node_schema,
        "temperature": 0.0
    }
}

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"},
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=15) as response:
        res = json.loads(response.read().decode("utf-8"))
        extracted = json.loads(res["candidates"][0]["content"]["parts"][0]["text"])
        print("EXTRACTION RESULT:")
        print(json.dumps(extracted, indent=2))
except Exception as e:
    print("Error:", e)
