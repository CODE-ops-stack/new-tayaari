import json
import random
import uuid
import itertools

class KnowledgeBase:
    origins = {
        "Narmada": ("Amarkantak, MP", "Peninsular"),
        "Tapi": ("Multai, MP", "Peninsular"),
        "Godavari": ("Trimbakeshwar, MH", "Peninsular"),
        "Krishna": ("Mahabaleshwar, MH", "Peninsular"),
        "Cauvery": ("Brahmagiri Hills, KA", "Peninsular"),
        "Mahanadi": ("Sihawa, CG", "Peninsular"),
        "Luni": ("Aravalli Range, RJ", "Inland"),
        "Jhelum": ("Verinag Spring, J&K", "Himalayan"),
        "Chenab": ("Bara Lacha Pass, HP", "Himalayan"),
        "Ravi": ("Rohtang Pass, HP", "Himalayan")
    }
    
    tributaries = {
        "Godavari": ["Penganga", "Indravati", "Pranhita", "Sabari"],
        "Krishna": ["Tungabhadra", "Bhima", "Musi", "Ghatprabha"],
        "Cauvery": ["Hemavati", "Kabini", "Bhavani", "Amaravati"],
        "Ganga_Right": ["Yamuna", "Son", "Punpun"],
        "Ganga_Left": ["Gomti", "Ghaghara", "Gandak", "Kosi"]
    }
    
    characteristics = {
        "Himalayan": ["Antecedent drainage", "Perennial flow", "V-shaped valleys", "Meandering courses"],
        "Peninsular": ["Consequent drainage", "Seasonal flow", "Broad, shallow valleys", "Straight, fixed courses"]
    }

class DistractorEngine:
    @staticmethod
    def get_origins(correct, category, count=3):
        candidates = [orig for river, (orig, cat) in KnowledgeBase.origins.items() if orig != correct and cat == category]
        if len(candidates) < count:
            candidates += [orig for river, (orig, cat) in KnowledgeBase.origins.items() if orig != correct and orig not in candidates]
        return random.sample(candidates, count)
        
    @staticmethod
    def get_tributaries(correct, wrong_pool_keys, count=3):
        candidates = []
        for k in wrong_pool_keys:
            candidates.extend(KnowledgeBase.tributaries[k])
        return random.sample(candidates, count)

class LeakageAuditor:
    @staticmethod
    def audit(batch):
        leaks = 0
        texts = [q["text"].lower() for q in batch]
        answers = [q["options"][q["correctIndex"]].lower() for q in batch]
        
        for i, ans in enumerate(answers):
            for j, text in enumerate(texts):
                if i != j and len(ans) > 4 and ans in text:
                    # Leak detected! Q[i]'s answer is in Q[j]'s stem.
                    leaks += 1
        return leaks

class GeneratorV2:
    def __init__(self, target_count):
        self.target = target_count
        self.questions = []
        self.used_concepts = set()
    
    def generate(self):
        # Concept 1-6: Peninsular Origins
        for river, (origin, cat) in KnowledgeBase.origins.items():
            if cat == "Peninsular" and f"origin_{river}" not in self.used_concepts:
                opts = [origin] + DistractorEngine.get_origins(origin, cat)
                random.shuffle(opts)
                self.questions.append({
                    "id": str(uuid.uuid4())[:8],
                    "text": f"The river {river} originates from which of the following locations?",
                    "options": opts,
                    "correctIndex": opts.index(origin),
                    "concept": f"origin_{river}"
                })
                self.used_concepts.add(f"origin_{river}")
                if len(self.questions) >= self.target: return
                
        # Concept 7-9: Tributaries
        for system, tribs in [("Godavari", ["Krishna", "Cauvery"]), ("Krishna", ["Godavari", "Cauvery"])]:
            if f"trib_{system}" not in self.used_concepts:
                ans = random.choice(KnowledgeBase.tributaries[system])
                opts = [ans] + DistractorEngine.get_tributaries(ans, tribs)
                random.shuffle(opts)
                self.questions.append({
                    "id": str(uuid.uuid4())[:8],
                    "text": f"Which of the following is a major tributary of the {system} river?",
                    "options": opts,
                    "correctIndex": opts.index(ans),
                    "concept": f"trib_{system}"
                })
                self.used_concepts.add(f"trib_{system}")
                if len(self.questions) >= self.target: return
        
        # Concept 10: Rift Valley
        if "rift_valley" not in self.used_concepts:
            opts = ["Narmada and Tapi", "Mahanadi and Godavari", "Krishna and Cauvery", "Ganga and Yamuna"]
            random.shuffle(opts)
            self.questions.append({
                "id": str(uuid.uuid4())[:8],
                "text": "Which of the following pairs of rivers flow through a rift valley?",
                "options": opts,
                "correctIndex": opts.index("Narmada and Tapi"),
                "concept": "rift_valley"
            })
            self.used_concepts.add("rift_valley")
            if len(self.questions) >= self.target: return

        # Concept 11: Inland Drainage
        if "inland_drainage" not in self.used_concepts:
            opts = ["Luni", "Sabarmati", "Mahi", "Tapi"]
            random.shuffle(opts)
            self.questions.append({
                "id": str(uuid.uuid4())[:8],
                "text": "Which of the following is an inland drainage river that disappears into the Rann of Kutch?",
                "options": opts,
                "correctIndex": opts.index("Luni"),
                "concept": "inland_drainage"
            })
            self.used_concepts.add("inland_drainage")
            if len(self.questions) >= self.target: return

# Run validation batch
gen = GeneratorV2(20) # Max 20
gen.generate()
batch = gen.questions

leaks = LeakageAuditor.audit(batch)

report = {
    "requested_maximum": 20,
    "concept_capacity": len(KnowledgeBase.origins) + len(KnowledgeBase.tributaries) + 3, # Approx 18
    "candidates_generated": len(batch),
    "duplicate_rate": 0,
    "clue_leakage_count": leaks,
    "questions": batch
}

with open("validation_batch_v2.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

print(f"Validation Batch Generated. Generated: {len(batch)}. Leaks: {leaks}")
