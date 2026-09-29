import json
import uuid
import random
import re
import glob
from collections import defaultdict

# ---------------------------------------------------------
# 1. SOURCE PARSER
# ---------------------------------------------------------
class SourceParser:
    def parse(self, filenames):
        blocks = []
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
                if re.match(r'^(Q\.\s*\d+|\d+\.\s+[A-Z])', line) or re.match(r'^\([a-e]\)', line, re.IGNORECASE):
                    skip_block = True
                    if current_prose:
                        blocks.append({"sourceId": fn, "type": "PROSE", "text": " ".join(current_prose)})
                        current_prose = []
                    continue
                    
                if re.match(r'^(Sol\.|Ans|Explanation)', line, re.IGNORECASE):
                    skip_block = False
                    line = re.sub(r'^(Sol\.\s*\d*[\.\)]?\s*\(?[a-d]?\)?|Ans[a-z\:]*\s*\(?[a-d]?\)?)\s*', '', line, flags=re.IGNORECASE)
                    
                # Tables or metadata
                if "|" in line or line.startswith("http") or line.startswith("www"):
                    if current_prose:
                        blocks.append({"sourceId": fn, "type": "PROSE", "text": " ".join(current_prose)})
                        current_prose = []
                    blocks.append({"sourceId": fn, "type": "TABLE_OR_META", "text": line})
                    continue
                    
                if not skip_block:
                    current_prose.append(line)
                    
            if current_prose:
                blocks.append({"sourceId": fn, "type": "PROSE", "text": " ".join(current_prose)})
                
        return blocks

# ---------------------------------------------------------
# 2. CLAIM EXTRACTOR
# ---------------------------------------------------------
class KnowledgeExtractor:
    # A massive dictionary of structural relationships in geography
    RELATIONS = {
        "DEFINITION": [r'\b(is known as|refers to|is defined as|is characterized by|comprises|consists of)\b'],
        "CAUSE_EFFECT": [r'\b(causes|leads to|results in|produces|generates)\b', r'\b(because of|due to)\b'],
        "SPATIAL": [r'\b(is located in|borders|is situated in|lies in|flows through|originates in)\b'],
        "DISTRIBUTION": [r'\b(is found in|are found in|is abundant in|is distributed across)\b'],
        "COMPARISON": [r'\b(whereas|while|compared to|differs from|unlike)\b']
    }
    
    BAD_ENTITIES = {"it", "this", "that", "these", "those", "they", "he", "she", "which", "app", "download", "pinnacle", "a", "an"}
    
    def extract(self, blocks):
        nodes = []
        rejected = []
        
        for block in blocks:
            if block["type"] != "PROSE":
                rejected.append({"sentence": block["text"][:50], "reason": f"Block type is {block['type']}"})
                continue
                
            sentences = re.split(r'(?<=[.!?])\s+', block["text"])
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) < 15 or len(sentence) > 400:
                    rejected.append({"sentence": sentence, "reason": "Length out of bounds"})
                    continue
                    
                if re.search(r'\([a-e]\)', sentence) or re.search(r'\b[A-E]\b\)', sentence):
                    rejected.append({"sentence": sentence, "reason": "Option marker artifact detected"})
                    continue
                    
                matched = False
                for rel_type, patterns in self.RELATIONS.items():
                    if matched: break
                    for pat in patterns:
                        # Find the pattern anywhere in the sentence
                        match = re.search(r'(.*?)\s+' + pat + r'\s+(.*)', sentence, re.IGNORECASE)
                        if match:
                            left = match.group(1).strip()
                            verb = match.group(2).strip()
                            right = match.group(3).strip().rstrip('.!,;')
                            
                            if rel_type == "CAUSE_EFFECT" and verb.lower() in ["because of", "due to"]:
                                # inverted syntax: "Due to X, Y"
                                if "," in right:
                                    parts = right.split(",", 1)
                                    cause = parts[0].strip()
                                    effect = parts[1].strip()
                                else:
                                    cause = right
                                    effect = left
                            else:
                                cause = left
                                effect = right
                                
                            # Subject validation
                            subject_words = [w.lower() for w in cause.split()][:2]
                            if not subject_words or any(w in self.BAD_ENTITIES for w in subject_words):
                                rejected.append({"sentence": sentence, "reason": f"Invalid subject/entity start in '{cause}'"})
                                matched = True
                                break
                                
                            if len(effect.split()) < 2:
                                rejected.append({"sentence": sentence, "reason": "Fragmentary object/effect"})
                                matched = True
                                break
                                
                            nodes.append({
                                "type": rel_type,
                                "left": cause,
                                "verb": verb,
                                "right": effect,
                                "original": sentence,
                                "sourceId": block["sourceId"]
                            })
                            matched = True
                            break
                            
                if not matched:
                    rejected.append({"sentence": sentence, "reason": "No structural geography relationship found"})
                    
        return nodes, rejected

# ---------------------------------------------------------
# 3. QUESTION SYNTHESIZER
# ---------------------------------------------------------
class OpportunityEngine:
    def synthesize(self, nodes):
        opportunities = []
        
        # Build category-specific distractor pools
        pools = defaultdict(list)
        for n in nodes:
            pools[n["type"]].append(n["right"])
            
        for node in nodes:
            exam = "SSC CGL"
            demand = "RECALL"
            
            if node["type"] == "DEFINITION":
                stem = f"Which of the following accurately describes '{node['left']}'?"
                correct = f"It {node['verb']} {node['right']}."
            elif node["type"] == "SPATIAL":
                stem = f"Which of the following accurately completes the geographic relationship: '{node['left']} {node['verb']}...'?"
                correct = f"{node['right']}."
            elif node["type"] == "DISTRIBUTION":
                stem = f"In the context of geographic distribution, where is '{node['left']}' primarily found?"
                correct = f"It {node['verb']} {node['right']}."
            elif node["type"] == "CAUSE_EFFECT":
                stem = f"What is a direct consequence of '{node['left']}'?"
                correct = f"It {node['verb']} {node['right']}."
                demand = "UNDERSTAND"
                if len(node["right"].split()) > 8:
                    demand = "APPLY"
                    exam = "UPSC"
            elif node["type"] == "COMPARISON":
                stem = f"When comparing geographic features, how does '{node['left']}' differ according to verified evidence?"
                correct = f"It differs in that {node['right']}."
                demand = "COMPARE"
                exam = "UPSC"
            else:
                continue
                
            # Filter pool
            candidate_pool = pools[node["type"]]
            valid_distractors = []
            correct_words = set(node["right"].lower().split())
            
            for cand in candidate_pool:
                if cand.lower() == node["right"].lower(): continue
                cand_words = set(cand.lower().split())
                if len(correct_words.intersection(cand_words)) / max(len(correct_words), 1) > 0.4:
                    continue
                    
                if node["type"] in ["DEFINITION", "CAUSE_EFFECT", "DISTRIBUTION"]:
                    dist = f"It {node['verb']} {cand}."
                elif node["type"] == "COMPARISON":
                    dist = f"It differs in that {cand}."
                else:
                    dist = f"{cand}."
                    
                if dist not in valid_distractors:
                    valid_distractors.append(dist)
                    
            if len(valid_distractors) < 3:
                continue
                
            distractors = random.sample(valid_distractors, 3)
            exp = f"According to {node['sourceId']}: '{node['original']}'. This confirms the {node['type'].lower()} relationship."
            
            opportunities.append({
                "text": stem,
                "options": [correct] + distractors,
                "correctIndex": 0,
                "explanation": exp,
                "metadata": {
                    "examTarget": [exam],
                    "topic": "Geography",
                    "concept": node["type"],
                    "cognitiveDemand": demand,
                    "provenance": [{"sourceId": node["sourceId"], "evidenceExcerpt": node["original"]}]
                },
                "validation": {
                    "distractorLogic": f"Semantic class: Sourced from other {node['type']} relationships in the corpus."
                }
            })
            
        return opportunities

# ---------------------------------------------------------
# 4. FINAL QUALITY GATE & AUDIT
# ---------------------------------------------------------
class BatchAuditor:
    def audit(self, opportunities):
        accepted = []
        rejected_count = 0
        
        texts_seen = set()
        answers_seen = set()
        
        for q in opportunities:
            # Exact duplicate check
            if q["text"] in texts_seen or q["options"][q["correctIndex"]] in answers_seen:
                rejected_count += 1
                continue
                
            # Formatting checks
            if len(q["text"]) < 20 or "{" in q["text"]:
                rejected_count += 1
                continue
                
            opts = q["options"]
            ans = opts[q["correctIndex"]]
            random.shuffle(opts)
            q["correctIndex"] = opts.index(ans)
            q["options"] = opts
            q["questionId"] = f"Q-PROD-V9-{str(uuid.uuid4())[:8]}"
            
            texts_seen.add(q["text"])
            answers_seen.add(ans)
            accepted.append(q)
            
        return accepted, rejected_count

class DiscoveryEngine:
    def run(self):
        sources = glob.glob("source-material/*.txt")
        if not sources: sources = ["source-material/geography_extracted.txt"]
            
        blocks = SourceParser().parse(sources)
        nodes, rejected = KnowledgeExtractor().extract(blocks)
        opportunities = OpportunityEngine().synthesize(nodes)
        accepted, gate_rejected = BatchAuditor().audit(opportunities)
        
        # Calculate funnels
        cog_mix = defaultdict(int)
        for q in accepted:
            cog_mix[q["metadata"]["cognitiveDemand"]] += 1
            
        report = {
            "SOURCES PROCESSED": len(sources),
            "SOURCE UNITS": len(blocks),
            "VALID NODES": len(nodes),
            "REJECTED NODES": len(rejected),
            "OPPORTUNITIES": len(opportunities),
            "ACCEPTED": len(accepted),
            "REJECTED BY GATE": gate_rejected,
            "COGNITIVE MIX": dict(cog_mix),
            "EXAMPLES": accepted[:10],
            "REJECTED EXAMPLES": rejected[:10]
        }
        with open("v9_discovery_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        print(f"V9 Discovery Complete. Valid Nodes: {len(nodes)}, Accepted: {len(accepted)}")

if __name__ == "__main__":
    DiscoveryEngine().run()
