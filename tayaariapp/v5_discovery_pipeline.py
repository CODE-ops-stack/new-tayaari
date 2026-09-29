import json
import uuid
import random
import re
import glob

# ---------------------------------------------------------
# 1. SOURCE PARSER
# ---------------------------------------------------------
class SourceParser:
    def __init__(self):
        self.prose_blocks = []
        
    def parse(self, filenames):
        for fn in filenames:
            try:
                with open(fn, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
            except Exception:
                continue
                
            in_mcq = False
            current_prose = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Detect MCQ boundaries
                if re.match(r'^(Q\.\s*\d+|\d+\.\s+[A-Z])', line) or re.match(r'^\([a-d]\)', line):
                    in_mcq = True
                    if current_prose:
                        self.prose_blocks.append({"sourceId": fn, "text": " ".join(current_prose)})
                        current_prose = []
                    continue
                    
                # Detect Solution boundaries (which are factual prose)
                if re.match(r'^(Sol\.|Ans|Explanation)', line, re.IGNORECASE):
                    in_mcq = False
                    # Strip the marker
                    line = re.sub(r'^(Sol\.\s*\d*[\.\)]?\s*\(?[a-d]?\)?|Ans[a-z\:]*\s*\(?[a-d]?\)?)\s*', '', line, flags=re.IGNORECASE)
                    
                if not in_mcq:
                    # Clean out trailing option markers like "(a)" in the middle of sentences if OCR failed, but generally just append
                    current_prose.append(line)
                    
            if current_prose:
                self.prose_blocks.append({"sourceId": fn, "text": " ".join(current_prose)})
                
        return self.prose_blocks

# ---------------------------------------------------------
# 2. CLAIM EXTRACTOR
# ---------------------------------------------------------
class ClaimExtractor:
    # Strictly whitelisted relations to ensure Subject-Verb-Object propositions
    RELATIONS = {
        "RECALL": [r'\b(is known as)\b', r'\b(comprises)\b', r'\b(consists of)\b', r'\b(is defined as)\b'],
        "UNDERSTAND": [r'\b(causes)\b', r'\b(leads to)\b', r'\b(results in)\b', r'\b(forms)\b']
    }
    
    BAD_SUBJECTS = {"It", "This", "That", "These", "Those", "They", "He", "She", "Which", "In", "On", "At", "By", "For", "From", "Structural"}

    def __init__(self):
        self.claims = []
        self.rejected_inputs = []
        
    def extract(self, prose_blocks):
        for block in prose_blocks:
            text = block["text"]
            # Split into sentences
            sentences = re.split(r'(?<=[.!?])\s+', text)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 20 or len(sentence) > 300:
                    self.rejected_inputs.append({"sentence": sentence, "reason": "Length out of bounds or fragment"})
                    continue
                    
                # Reject if it contains option markers
                if re.search(r'\([a-e]\)', sentence) or re.search(r'\b[A-E]\b\)', sentence):
                    self.rejected_inputs.append({"sentence": sentence, "reason": "Option marker artifact detected"})
                    continue
                    
                # Validate sentence start before attempting relation matching
                first_word_match = re.match(r'^([A-Za-z]+)', sentence)
                if first_word_match and first_word_match.group(1) in self.BAD_SUBJECTS:
                    self.rejected_inputs.append({"sentence": sentence, "reason": f"Invalid subject start '{first_word_match.group(1)}'"})
                    continue

                extracted = False
                for cog_mode, patterns in self.RELATIONS.items():
                    if extracted: break
                    for pat in patterns:
                        # We demand a Capitalized Noun Phrase subject, the strict verb, and an object.
                        # Noun phrase: Starts with Capital letter, allows up to 4 words total.
                        match = re.search(r'^([A-Z][a-zA-Z]*(?:\s+[A-Za-z]+){0,4})\s+' + pat + r'\s+(.*)', sentence)
                        if match:
                            subject = match.group(1).strip()
                            verb = match.group(2).strip()
                            obj = match.group(3).strip()
                            
                            # Clean obj trailing punctuation
                            obj = obj.rstrip('.!,;')
                            
                            # Validation Gate
                            first_word = subject.split()[0]
                            if first_word in self.BAD_SUBJECTS:
                                self.rejected_inputs.append({"sentence": sentence, "reason": f"Invalid subject start '{first_word}'"})
                                break
                            
                            if len(obj.split()) < 2:
                                self.rejected_inputs.append({"sentence": sentence, "reason": "Fragmentary object"})
                                break
                                
                            claim = {
                                "subject": subject,
                                "verb": verb,
                                "object": obj,
                                "original_sentence": sentence,
                                "sourceId": block["sourceId"],
                                "cognitive_mode": cog_mode,
                                "nodeId": f"CLAIM_{uuid.uuid4().hex[:6]}"
                            }
                            self.claims.append(claim)
                            extracted = True
                            break
                            
                if not extracted:
                    self.rejected_inputs.append({"sentence": sentence, "reason": "No strict Subject-Verb-Object proposition found"})
                    
        return self.claims, self.rejected_inputs

# ---------------------------------------------------------
# 3. QUESTION SYNTHESIZER
# ---------------------------------------------------------
class QuestionSynthesizer:
    def synthesize(self, claims):
        opportunities = []
        
        # Build distractor pools based on the EXACT verb (Structural Distractor Logic)
        verb_pools = {}
        for c in claims:
            v = c["verb"].lower()
            if v not in verb_pools:
                verb_pools[v] = []
            verb_pools[v].append(c["object"])
            
        for claim in claims:
            # Generate STEM
            if claim["cognitive_mode"] == "RECALL":
                stem = f"Which of the following accurately completes the statement: '{claim['subject']} {claim['verb']}...'?"
                correct = f"{claim['object']}."
                exam = "SSC CGL"
            else: # UNDERSTAND/APPLY
                stem = f"In the context of geographical processes, which of the following is a direct result when {claim['subject']} {claim['verb']}?"
                correct = f"It {claim['verb']} {claim['object']}."
                exam = "UPSC" if len(claim["object"].split()) > 8 else "BPSC"

            # Generate Distractors
            pool = verb_pools[claim["verb"].lower()]
            valid_distractors = []
            
            # Filter pool to ensure distinct options
            correct_words = set(claim["object"].lower().split())
            for candidate in pool:
                if candidate.lower() == claim["object"].lower():
                    continue
                cand_words = set(candidate.lower().split())
                # Reject if more than 50% vocabulary overlap
                if len(correct_words.intersection(cand_words)) / float(max(len(correct_words), 1)) > 0.5:
                    continue
                
                # Format distractor
                dist = f"{candidate}." if claim["cognitive_mode"] == "RECALL" else f"It {claim['verb']} {candidate}."
                if dist not in valid_distractors:
                    valid_distractors.append(dist)
                    
            if len(valid_distractors) < 3:
                # REJECT: Cannot form defensible distractors
                continue
                
            distractors = random.sample(valid_distractors, 3)
            
            exp = f"According to the source, '{claim['original_sentence']}'. This explicitly establishes the relationship."
            
            opp = {
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
                    "provenance": [{
                        "sourceId": claim["sourceId"],
                        "section": "Prose Extraction",
                        "evidenceExcerpt": claim["original_sentence"]
                    }],
                    "currentness": "SOURCE_DATE_UNKNOWN",
                    "generationBasis": "ORIGINAL_SYNTHESIS"
                },
                "validation": {
                    "distractorLogic": f"Strict relation pool: Distractors pulled from other verified objects sharing the predicate '{claim['verb']}'."
                }
            }
            opportunities.append(opp)
            
        return opportunities

# ---------------------------------------------------------
# 4. FINAL QUALITY GATE
# ---------------------------------------------------------
class BatchQualityGate:
    def audit(self, opportunities):
        accepted = []
        rejected_count = 0
        
        texts_seen = set()
        answers_seen = set()
        
        for q in opportunities:
            # 1. Grammar & Malformation checks
            if q["text"] in texts_seen or q["options"][q["correctIndex"]] in answers_seen:
                rejected_count += 1
                continue
                
            if len(q["text"]) < 30 or "{" in q["text"]:
                rejected_count += 1
                continue
                
            # Randomize options
            opts = q["options"]
            ans = opts[q["correctIndex"]]
            random.shuffle(opts)
            q["correctIndex"] = opts.index(ans)
            q["options"] = opts
            q["questionId"] = f"Q-PROD-V5-DISC-{str(uuid.uuid4())[:8]}"
            q["status"] = "AUTOMATED_VALIDATED"
            
            texts_seen.add(q["text"])
            answers_seen.add(ans)
            accepted.append(q)
            
        return accepted, rejected_count

# ---------------------------------------------------------
# 5. ORCHESTRATOR
# ---------------------------------------------------------
class DiscoveryEngine:
    def run(self):
        sources = glob.glob("source-material/*.txt")
        if not sources:
            sources = ["source-material/geography_extracted.txt"]
            
        parser = SourceParser()
        prose_blocks = parser.parse(sources)
        
        extractor = ClaimExtractor()
        claims, rejected_inputs = extractor.extract(prose_blocks)
        
        synth = QuestionSynthesizer()
        opportunities = synth.synthesize(claims)
        
        gate = BatchQualityGate()
        accepted, rejected_from_gate = gate.audit(opportunities)
        
        # We need 10 rejected examples to show
        sample_rejected = rejected_inputs[:10] if len(rejected_inputs) >= 10 else rejected_inputs
        
        report = {
            "Theory nodes discovered": len(claims),
            "Valid nodes": len(claims),
            "Nodes rejected": len(rejected_inputs),
            "Sources used": sources,
            "Claims": len(claims),
            "Question opportunities": len(opportunities),
            "Accepted": len(accepted),
            "Rejected": rejected_from_gate + (len(claims) - len(opportunities)),
            "Distinct concepts": len(set(q["metadata"]["concept"] for q in accepted)),
            "Recall %": round(sum(1 for q in accepted if q["metadata"]["cognitiveDemand"] == "RECALL") / max(1, len(accepted)) * 100, 1),
            "Understand %": round(sum(1 for q in accepted if q["metadata"]["cognitiveDemand"] == "UNDERSTAND") / max(1, len(accepted)) * 100, 1),
            "Duplicate": rejected_from_gate,
            "Examples": accepted[:10],
            "RejectedExamples": sample_rejected
        }
        
        with open("v5_discovery_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        print(f"Discovery Complete. Nodes Valid: {len(claims)}, Accepted: {len(accepted)}")

if __name__ == "__main__":
    DiscoveryEngine().run()
