import json
import re
from typing import Dict, Any, Optional, List, Tuple

# Pre-compiled Noise Patterns for Gate
NOISE_PATTERNS = {
    "mcq_leakage": [
        r'^\s*\(?[a-eA-E]\)[\s\.\)]',
        r'^\s*Question\s*\d+',
        r'^\s*Q\.\s*\d+',
        r'^\s*Option\s+[A-D]\b',
        r'\(a\)\s+.*\s+\(b\)',
        r'^\s*Ans(?:wer)?\s*[:\.]',
        r'^\s*Sol(?:ution)?\s*[:\.]',
        r'Which of the following\s+(?:statements?\s+)?(?:is|are)\s+(?:not\s+)?(?:correct|true)',
        r'Select the correct\s+(?:code|answer)\b'
    ],
    "watermark_header": [
        r'\bPARMAR\s+SSC\b',
        r'\bISBN\s*[\d\-]+',
        r'www\.[a-z0-9\-\.]+\.(?:com|org|in|net)',
        r'^Chapter\s+\d+\b',
        r'^NCERT\s+Class\s+\d+',
        r'^\s*Page\s+\d+\s+of\s+\d+',
        r'^\s*\d{1,3}\s*$' # isolated page numbers
    ],
    "table_formatting_artifact": [
        r'^\s*\|',
        r'\|\s*[-:]+[-| :]+\|',
        r'\bTopic\s*\|\s*Tier\b'
    ],
    "syntactic_fragment": [
        r'\b(?:and|or|but|with|that|which|whose|because|while|whereas|although)\s*[\.\!\?]?\s*$',
        r'\.\.\.\s*$',
        r'^\s*(?:In addition to|As well as|Out of total water resources|Due to which)\s*[\.\,]?\s*$'
    ],
    "anaphoric_unresolved": [
        r'^\s*(?:They|These|Those|He|She|It)\s+(?:are|is|have|has|were|was|can|do|does)\b'
    ],
    "broken_reading_order": [
        r'^[A-Z][a-z]+[A-Z][a-z]+[A-Z][a-z]+', # camel/concatenated words without space
        r'^(?:[A-Z][a-zA-Z\s]{3,20}\s+){4,}[A-Z][a-zA-Z\s]{3,20}$' # series of title words without finite verbs
    ]
}

def check_noise(text: str) -> Optional[str]:
    """Returns rejection category if text is noise, else None."""
    for category, patterns in NOISE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE if category != "broken_reading_order" else 0):
                return category
    
    # Minimum length and verb check
    words = text.split()
    if len(words) < 5:
        return "syntactic_fragment"
    
    # Check for presence of at least one verb-like auxiliary or common finite verb
    has_finite_verb = bool(re.search(
        r'\b(is|are|was|were|has|have|had|can|could|may|might|will|would|shall|should|'
        r'causes?|flows?|constitutes?|progresses?|divides?|classified|forms?|measures?|'
        r'rotates?|contains?|extends?|occurs?|features?|exhibits?|develops?|originates?|'
        r'sheds?|belongs?|traverses?|surrounds?|lies|vibrates?)\b',
        text, re.IGNORECASE
    ))
    if not has_finite_verb:
        return "broken_reading_order"
        
    return None

# Test against golden eval set
with open("data/golden_eval_set.json", "r", encoding="utf-8") as f:
    gold = json.load(f)

noise_correct = 0
noise_total = 0
false_rejections = 0

for ex in gold["examples"]:
    detected = check_noise(ex["text"])
    if ex["expected_label"] == "negative":
        noise_total += 1
        if detected is not None:
            noise_correct += 1
        else:
            print(f"[MISS NEGATIVE] ({ex['id']}) [{ex.get('rejection_category')}]: {ex['text'][:70]}...")
    else:
        if detected is not None:
            false_rejections += 1
            print(f"[FALSE REJECTION] ({ex['id']}) [{ex['intent']}]: Rejected as {detected} -> {ex['text'][:70]}...")

print(f"\nNoise Filter Results:")
print(f"Negative noise correctly rejected: {noise_correct}/{noise_total} ({noise_correct/noise_total*100:.1f}%)")
print(f"False rejections on positives: {false_rejections}/{len(gold['examples'])-noise_total}")
