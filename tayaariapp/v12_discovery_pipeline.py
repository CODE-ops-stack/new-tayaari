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
                    
                if re.match(r'^(Q\.\s*\d+|\d+\.\s+[A-Z])', line) or re.match(r'^\([a-e]\)', line, re.IGNORECASE):
                    skip_block = True
                    if current_prose:
                        blocks.append({"sourceId": fn, "type": "PROSE", "text": " ".join(current_prose)})
                        current_prose = []
                    continue
                    
                if re.match(r'^(Sol\.|Ans|Explanation)', line, re.IGNORECASE):
                    skip_block = False
                    line = re.sub(r'^(Sol\.\s*\d*[\.\)]?\s*\(?[a-d]?\)?|Ans[a-z\:]*\s*\(?[a-d]?\)?)\s*', '', line, flags=re.IGNORECASE)
                    
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
# 2. KNOWLEDGE EXTRACTOR
# ---------------------------------------------------------
class KnowledgeExtractor:
    BAD_ENTITIES = {"it", "this", "that", "these", "those", "they", "he", "she", "which", "app", "download", "pinnacle"}
    
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
                if len(sentence) < 20 or len(sentence) > 300:
                    rejected.append({"sentence": sentence, "reason": "Length out of bounds"})
                    continue
                    
                if re.search(r'\([a-e]\)', sentence) or re.search(r'\b[A-E]\b\)', sentence):
                    rejected.append({"sentence": sentence, "reason": "Option marker artifact detected"})
                    continue
                    
                matched = False
                
                # PATTERN 1: COMPARISON
                m_comp = re.match(r'^([A-Z][a-zA-Z\s]+)\s+(is|are|involves|reduces|has|produces|affects)\s+(.*?),?\s+(while|whereas)\s+([a-zA-Z\s]+)\s+(is|are|involves|reduces|has|produces|affects|lies|focuses|grow|grows)\s+(.*)', sentence)
                if m_comp:
                    sx = m_comp.group(1).strip()
                    px = f"{m_comp.group(2)} {m_comp.group(3).strip()}"
                    sy = m_comp.group(5).strip()
                    py = f"{m_comp.group(6)} {m_comp.group(7).strip().rstrip('.!,;')}"
                    
                    if not any(w in self.BAD_ENTITIES for w in sx.lower().split()) and not any(w in self.BAD_ENTITIES for w in sy.lower().split()):
                        nodes.append({
                            "type": "COMPARISON", "subj_x": sx, "pred_x": px, "subj_y": sy, "pred_y": py,
                            "original": sentence, "sourceId": block["sourceId"]
                        })
                        matched = True
                        continue

                # PATTERN 2: DEFINITION
                m_def = re.match(r'^([A-Z][a-zA-Z\s]+)\s+(is known as|refers to|comprises|consists of|includes)\s+(.*)', sentence)
                if m_def:
                    subj = m_def.group(1).strip()
                    verb = m_def.group(2).strip()
                    defn = m_def.group(3).strip().rstrip('.!,;')
                    if not any(w in self.BAD_ENTITIES for w in subj.lower().split()):
                        nodes.append({
                            "type": "DEFINITION", "subj": subj, "verb": verb, "def": defn,
                            "original": sentence, "sourceId": block["sourceId"]
                        })
                        matched = True
                        continue

                # PATTERN 3: CAUSE-EFFECT (Effect due to Cause)
                m_ce1 = re.match(r'^([A-Z][a-zA-Z\s]+)\s+(is due to|occurs because of|is caused by)\s+(.*)', sentence)
                if m_ce1:
                    effect = m_ce1.group(1).strip()
                    verb = m_ce1.group(2).strip()
                    cause = m_ce1.group(3).strip().rstrip('.!,;')
                    if not any(w in self.BAD_ENTITIES for w in effect.lower().split()):
                        nodes.append({
                            "type": "CAUSE_EFFECT_INVERTED", "effect": effect, "verb": verb, "cause": cause,
                            "original": sentence, "sourceId": block["sourceId"]
                        })
                        matched = True
                        continue

                # PATTERN 4: CAUSE-EFFECT (Cause leads to Effect)
                m_ce2 = re.match(r'^([A-Z][a-zA-Z\s]+)\s+(causes|leads to|results in)\s+(.*)', sentence)
                if m_ce2:
                    cause = m_ce2.group(1).strip()
                    verb = m_ce2.group(2).strip()
                    effect = m_ce2.group(3).strip().rstrip('.!,;')
                    if not any(w in self.BAD_ENTITIES for w in cause.lower().split()):
                        nodes.append({
                            "type": "CAUSE_EFFECT", "cause": cause, "verb": verb, "effect": effect,
                            "original": sentence, "sourceId": block["sourceId"]
                        })
                        matched = True
                        continue

                # PATTERN 5: SPATIAL
                m_sp = re.match(r'^([A-Z][a-zA-Z\s]+)\s+(is located in|borders|is situated in|flows through|lies in)\s+(.*)', sentence)
                if m_sp:
                    subj = m_sp.group(1).strip()
                    verb = m_sp.group(2).strip()
                    loc = m_sp.group(3).strip().rstrip('.!,;')
                    if not any(w in self.BAD_ENTITIES for w in subj.lower().split()):
                        nodes.append({
                            "type": "SPATIAL", "subj": subj, "verb": verb, "loc": loc,
                            "original": sentence, "sourceId": block["sourceId"]
                        })
                        matched = True
                        continue

                if not matched:
                    rejected.append({"sentence": sentence, "reason": "Did not match strict structural semantic forms"})
                    
        return nodes, rejected

# ---------------------------------------------------------
# 3. INTENT SYNTHESIZER
# ---------------------------------------------------------
class IntentSynthesizer:
    def synthesize(self, nodes):
        opportunities = []
        
        # Build global distractor pools
        pools = defaultdict(list)
        for n in nodes:
            if n["type"] == "DEFINITION": pools["DEFINITION"].append(n["def"])
            elif n["type"] == "CAUSE_EFFECT_INVERTED": pools["CAUSE"].append(n["cause"])
            elif n["type"] == "CAUSE_EFFECT": pools["EFFECT"].append(n["effect"])
            elif n["type"] == "SPATIAL": pools["LOC"].append(n["loc"])
            elif n["type"] == "COMPARISON":
                pools["PRED_X"].append(n["pred_x"])
                pools["PRED_Y"].append(n["pred_y"])
                
        for node in nodes:
            valid_distractors = []
            
            if node["type"] == "COMPARISON":
                stem = f"Which of the following statements accurately compares {node['subj_x']} and {node['subj_y']}?"
                correct = f"{node['subj_x'].capitalize()} {node['pred_x']}, whereas {node['subj_y']} {node['pred_y']}."
                
                # Distractor 1: Swap
                valid_distractors.append(f"{node['subj_x'].capitalize()} {node['pred_y']}, whereas {node['subj_y']} {node['pred_x']}.")
                
                # Distractors 2 & 3: Mix with other verified predicates
                pool_x = [p for p in pools["PRED_X"] if p != node["pred_x"]]
                pool_y = [p for p in pools["PRED_Y"] if p != node["pred_y"]]
                
                if pool_y:
                    valid_distractors.append(f"{node['subj_x'].capitalize()} {node['pred_x']}, whereas {node['subj_y']} {random.choice(pool_y)}.")
                if pool_x:
                    valid_distractors.append(f"{node['subj_x'].capitalize()} {random.choice(pool_x)}, whereas {node['subj_y']} {node['pred_y']}.")
                    
                exam = "UPSC"
                demand = "COMPARE"
                dist_logic = "Swapped predicates and cross-polled verified predicates to test deep conceptual distinction."
                
            elif node["type"] == "DEFINITION":
                stem = f"Which of the following best describes the geographic concept of '{node['subj']}'?"
                correct = f"It {node['verb']} {node['def']}."
                
                pool = [p for p in pools["DEFINITION"] if p != node["def"]]
                for p in pool:
                    if len(set(p.lower().split()).intersection(set(node['def'].lower().split()))) < 2:
                        valid_distractors.append(f"It {node['verb']} {p}.")
                        
                exam = "SSC CGL"
                demand = "RECALL"
                dist_logic = "Cross-polled verified definitions from the corpus."
                
            elif node["type"] == "CAUSE_EFFECT_INVERTED":
                stem = f"Which of the following is the primary geographic reason why {node['effect']}?"
                correct = f"It {node['verb']} {node['cause']}."
                
                pool = [p for p in pools["CAUSE"] if p != node["cause"]]
                for p in pool:
                    valid_distractors.append(f"It {node['verb']} {p}.")
                    
                exam = "UPSC" if len(node['cause'].split()) > 6 else "BPSC"
                demand = "UNDERSTAND"
                dist_logic = "Cross-polled verified causes from the corpus."
                
            elif node["type"] == "CAUSE_EFFECT":
                stem = f"What is a direct geographical consequence of {node['cause']}?"
                correct = f"It {node['verb']} {node['effect']}."
                
                pool = [p for p in pools["EFFECT"] if p != node["effect"]]
                for p in pool:
                    valid_distractors.append(f"It {node['verb']} {p}.")
                    
                exam = "UPSC" if len(node['effect'].split()) > 6 else "BPSC"
                demand = "UNDERSTAND"
                dist_logic = "Cross-polled verified effects from the corpus."
                
            elif node["type"] == "SPATIAL":
                stem = f"Which of the following accurately describes the spatial location of {node['subj']}?"
                correct = f"It {node['verb']} {node['loc']}."
                
                pool = [p for p in pools["LOC"] if p != node["loc"]]
                for p in pool:
                    valid_distractors.append(f"It {node['verb']} {p}.")
                    
                exam = "SSC CGL"
                demand = "RECALL"
                dist_logic = "Cross-polled verified spatial locations from the corpus."
                
            # Filter and finalize distractors
            unique_distractors = list(set(valid_distractors))
            if len(unique_distractors) < 3:
                continue
                
            final_distractors = random.sample(unique_distractors, 3)
            exp = f"According to {node['sourceId']}: '{node['original']}'. This confirms the {demand.lower()} relationship and invalidates the distractors."
            
            opportunities.append({
                "text": stem,
                "options": [correct] + final_distractors,
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
                    "distractorLogic": dist_logic
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
            if q["text"] in texts_seen or q["options"][q["correctIndex"]] in answers_seen:
                rejected_count += 1
                continue
                
            if len(q["text"]) < 20 or "{" in q["text"]:
                rejected_count += 1
                continue
                
            opts = q["options"]
            ans = opts[q["correctIndex"]]
            random.shuffle(opts)
            q["correctIndex"] = opts.index(ans)
            q["options"] = opts
            q["questionId"] = f"Q-PROD-V12-{str(uuid.uuid4())[:8]}"
            
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
        opportunities = IntentSynthesizer().synthesize(nodes)
        accepted, gate_rejected = BatchAuditor().audit(opportunities)
        
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
            "EXAMPLES": accepted[:20],
            "REJECTED EXAMPLES": rejected[:10]
        }
        with open("docs/v12_discovery_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
            
        print(f"V12 Discovery Complete. Valid Nodes: {len(nodes)}, Accepted: {len(accepted)}")

if __name__ == "__main__":
    DiscoveryEngine().run()
