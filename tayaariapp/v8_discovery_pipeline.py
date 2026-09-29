import json
import uuid
import random
import re
import glob

# ---------------------------------------------------------
# 1. SOURCE PARSER
# ---------------------------------------------------------
class SourceParser:
    def parse(self, filenames):
        prose_blocks = []
        for fn in filenames:
            try:
                with open(fn, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            except Exception:
                continue
                
            current_prose = []
            skip_block = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Explicit MCQ markers
                if re.match(r'^(Q\.\s*\d+|\d+\.\s+[A-Z])', line) or re.match(r'^\([a-d]\)', line):
                    skip_block = True
                    if current_prose:
                        prose_blocks.append({"sourceId": fn, "text": " ".join(current_prose)})
                        current_prose = []
                    continue
                    
                # Explicit Solution markers
                if re.match(r'^(Sol\.|Ans|Explanation)', line, re.IGNORECASE):
                    skip_block = False
                    line = re.sub(r'^(Sol\.\s*\d*[\.\)]?\s*\(?[a-d]?\)?|Ans[a-z\:]*\s*\(?[a-d]?\)?)\s*', '', line, flags=re.IGNORECASE)
                    
                if not skip_block:
                    current_prose.append(line)
                    
            if current_prose:
                prose_blocks.append({"sourceId": fn, "text": " ".join(current_prose)})
                
        return prose_blocks

# ---------------------------------------------------------
# 2. CLAIM EXTRACTOR
# ---------------------------------------------------------
class ClaimExtractor:
    RELATIONS = {
        "RECALL": [r'\b(is known as)\b', r'\b(comprises)\b', r'\b(consists of)\b', r'\b(is defined as)\b', r'\b(is characterized by)\b', r'\b(includes)\b', r'\b(represents)\b'],
        "UNDERSTAND": [r'\b(causes)\b', r'\b(leads to)\b', r'\b(results in)\b', r'\b(generates)\b', r'\b(produces)\b']
    }
    
    BAD_WORDS = {"it", "this", "that", "these", "those", "they", "he", "she", "which", "in", "on", "at", "by", "for", "from", "structural", "thus", "hence", "therefore", "because", "when", "if", "app", "download", "pinnacle", "a", "an"}

    def extract(self, prose_blocks):
        claims = []
        rejected_inputs = []
        for block in prose_blocks:
            text = block["text"]
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 20 or len(sentence) > 300:
                    rejected_inputs.append({"sentence": sentence, "reason": "Length out of bounds or fragment"})
                    continue
                    
                if re.search(r'\([a-e]\)', sentence) or re.search(r'\b[A-E]\b\)', sentence) or re.match(r'^[a-e]\)', sentence):
                    rejected_inputs.append({"sentence": sentence, "reason": "Option marker artifact detected"})
                    continue
                    
                extracted = False
                for cog_mode, patterns in self.RELATIONS.items():
                    if extracted: break
                    for pat in patterns:
                        match = re.search(r'\b([A-Z][a-zA-Z]*(?:\s+[a-zA-Z]+){0,3})\s+' + pat + r'\s+([^.!?]+)', sentence)
                        if match:
                            subject = match.group(1).strip()
                            verb = match.group(2).strip()
                            obj = match.group(3).strip()
                            
                            subj_words = [w.lower() for w in subject.split()]
                            
                            # Check if ANY bad word is in the subject (e.g. "which", "that")
                            if any(w in self.BAD_WORDS for w in subj_words):
                                rejected_inputs.append({"sentence": sentence, "reason": f"Invalid word in subject '{subject}'"})
                                extracted = True
                                break
                            
                            if len(obj.split()) < 3:
                                rejected_inputs.append({"sentence": sentence, "reason": "Fragmentary object"})
                                extracted = True
                                break
                                
                            claims.append({
                                "subject": subject,
                                "verb": verb,
                                "object": obj,
                                "original_sentence": sentence,
                                "sourceId": block["sourceId"],
                                "cognitive_mode": cog_mode
                            })
                            extracted = True
                            break
                            
                if not extracted:
                    rejected_inputs.append({"sentence": sentence, "reason": "No strict Subject-Verb-Object proposition found"})
                    
        return claims, rejected_inputs

# ---------------------------------------------------------
# 3. QUESTION SYNTHESIZER
# ---------------------------------------------------------
class QuestionSynthesizer:
    def synthesize(self, claims):
        opportunities = []
            
        for claim in claims:
            if claim["cognitive_mode"] == "RECALL":
                stem = f"Which of the following accurately completes the statement: '{claim['subject']} {claim['verb']}...'?"
                correct = f"{claim['object']}."
                exam = "SSC CGL"
            else:
                stem = f"In the context of geographical processes, which of the following is a direct result when {claim['subject']} {claim['verb']}?"
                correct = f"It {claim['verb']} {claim['object']}."
                exam = "UPSC" if len(claim["object"].split()) > 10 else "BPSC"

            pool = [c["object"] for c in claims if c["cognitive_mode"] == claim["cognitive_mode"] and c["object"] != claim["object"]]
            
            valid_distractors = []
            correct_words = set(claim["object"].lower().split())
            
            for candidate in pool:
                cand_words = set(candidate.lower().split())
                if len(correct_words.intersection(cand_words)) / float(max(len(correct_words), 1)) > 0.4:
                    continue
                
                dist = f"{candidate}." if claim["cognitive_mode"] == "RECALL" else f"It {claim['verb']} {candidate}."
                if dist not in valid_distractors:
                    valid_distractors.append(dist)
                    
            if len(valid_distractors) < 3:
                continue
                
            distractors = random.sample(valid_distractors, 3)
            exp = f"According to the source, '{claim['original_sentence']}'. This explicitly establishes the relationship."
            
            opportunities.append({
                "text": stem,
                "options": [correct] + distractors,
                "correctIndex": 0,
                "explanation": exp,
                "metadata": {
                    "examTarget": [exam],
                    "topic": "Geography", 
                    "concept": f"{claim['subject']} ({claim['verb']})",
                    "format": "Standard",
                    "difficulty": "MODERATE",
                    "cognitiveDemand": claim["cognitive_mode"],
                    "provenance": [{"sourceId": claim["sourceId"], "section": "Prose Extraction", "evidenceExcerpt": claim["original_sentence"]}],
                    "currentness": "SOURCE_DATE_UNKNOWN",
                    "generationBasis": "ORIGINAL_SYNTHESIS"
                },
                "validation": {
                    "distractorLogic": "Strict relation pool: Distractors pulled from other verified extracted objects of the same cognitive domain, rejecting topic overlaps."
                }
            })
            
        return opportunities

# ---------------------------------------------------------
# 4. FINAL QUALITY GATE
# ---------------------------------------------------------
class BatchQualityGate:
    def audit(self, opportunities):
        accepted = []
        texts_seen = set()
        answers_seen = set()
        
        for q in opportunities:
            if q["text"] in texts_seen or q["options"][q["correctIndex"]] in answers_seen:
                continue
            if len(q["text"]) < 30 or "{" in q["text"]:
                continue
                
            opts = q["options"]
            ans = opts[q["correctIndex"]]
            random.shuffle(opts)
            q["correctIndex"] = opts.index(ans)
            q["options"] = opts
            q["questionId"] = f"Q-PROD-V8-DISC-{str(uuid.uuid4())[:8]}"
            q["status"] = "AUTOMATED_VALIDATED"
            
            texts_seen.add(q["text"])
            answers_seen.add(ans)
            accepted.append(q)
            
        return accepted

class DiscoveryEngine:
    def run(self):
        sources = glob.glob("source-material/*.txt")
        if not sources: sources = ["source-material/geography_extracted.txt"]
            
        prose_blocks = SourceParser().parse(sources)
        claims, rejected_inputs = ClaimExtractor().extract(prose_blocks)
        opportunities = QuestionSynthesizer().synthesize(claims)
        accepted = BatchQualityGate().audit(opportunities)
        
        report = {
            "Valid claims": len(claims),
            "Question opportunities": len(opportunities),
            "Accepted": len(accepted),
            "Rejected": len(rejected_inputs) + (len(opportunities) - len(accepted)),
            "Examples": accepted[:10],
            "RejectedExamples": rejected_inputs[:10]
        }
        with open("v8_discovery_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        print(f"Discovery Complete. Nodes Valid: {len(claims)}, Accepted: {len(accepted)}")

if __name__ == "__main__":
    DiscoveryEngine().run()
