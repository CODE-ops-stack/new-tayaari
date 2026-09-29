import json
import uuid
import random
from collections import defaultdict

class QualityAuditor:
    BOILERPLATE_PHRASES = ["sourced from verified", "placeholder", "is known as", "is called"]

    @staticmethod
    def audit_explanation(q):
        exp = q.get("explanation", "").lower()
        if len(exp) < 30:
            return False, "Explanation too short or missing"
        for phrase in QualityAuditor.BOILERPLATE_PHRASES:
            if phrase in exp:
                return False, f"Boilerplate phrase detected: '{phrase}'"
        if not ("because" in exp or "due to" in exp or "characterized by" in exp or "as a result" in exp or "meaning" in exp or "specifically" in exp or "therefore" in exp or "shows" in exp or "fact" in exp):
             if "according to" not in exp and len(exp) < 60:
                 return False, "Explanation lacks explanatory connectors (why/how)"
        return True, ""

    @staticmethod
    def audit_distractor_plausibility(q):
        val = q.get("validation", {})
        logic = val.get("distractorLogic", "").lower()
        if "absurd" in logic or len(logic) < 10:
            return False, "Absurd distractors or missing distractor logic"
        meta = q.get("metadata", {})
        if not meta.get("distractorCategoryMatched", False):
            return False, "Distractor category mismatch"
        if meta.get("hasCategoryMismatch", False):
            return False, "Absurd or category-mismatch distractors detected"
        return True, ""

    @staticmethod
    def audit_cognitive_demand_and_difficulty(q):
        meta = q.get("metadata", {})
        cog = meta.get("cognitiveDemand", "RECALL")
        diff = meta.get("difficulty", "EASY")
        if cog == "RECALL" and "HARD" in diff:
            return False, "Cannot label a RECALL question as HARD"
        return True, ""

    @staticmethod
    def audit_exam_standards(q):
        meta = q.get("metadata", {})
        exam = meta.get("examTarget", [])
        cog = meta.get("cognitiveDemand", "RECALL")
        if "UPSC" in exam and cog not in ["UNDERSTAND", "APPLY", "INFER", "MULTI_STEP", "COMPARE"]:
            return False, "UPSC target requires higher order cognitive demand"
        return True, ""

    @staticmethod
    def audit_currentness(q):
        meta = q.get("metadata", {})
        if "currentness" not in meta:
            return False, "Missing currentness safety tag"
        if meta["currentness"] not in ["HISTORICAL", "SOURCE_DATE_UNKNOWN", "CURRENT_VERIFIED", "REQUIRES_CURRENT_VERIFICATION"]:
            return False, "Invalid currentness tag"
        return True, ""

    @staticmethod
    def audit_map_safety(q):
        meta = q.get("metadata", {})
        if "Map" in meta.get("format", ""):
            if not meta.get("mapEvidenceSufficient", False): 
                return False, "Map question lacks sufficient map evidence"
        return True, ""

    @staticmethod
    def audit_provenance(q):
        meta = q.get("metadata", {})
        prov = meta.get("provenance", [])
        if not prov:
            return False, "Missing provenance"
        for p in prov:
            if "PAGE" not in p.upper() and "SEC" not in p.upper() and "CH" not in p.upper() and "PYQ" not in p.upper():
                return False, "Provenance lacks concrete page/section/pyq evidence"
        return True, ""

    @staticmethod
    def audit_single_question(q):
        checks = [
            QualityAuditor.audit_explanation,
            QualityAuditor.audit_distractor_plausibility,
            QualityAuditor.audit_cognitive_demand_and_difficulty,
            QualityAuditor.audit_exam_standards,
            QualityAuditor.audit_currentness,
            QualityAuditor.audit_map_safety,
            QualityAuditor.audit_provenance
        ]
        for check in checks:
            passed, reason = check(q)
            if not passed:
                return False, reason
        return True, ""

    @staticmethod
    def audit_batch_leakage(batch):
        leaks = []
        texts = [q["text"].lower() for q in batch]
        answers = [q["options"][q["correctIndex"]].lower() for q in batch]
        
        leaking_indices = set()

        for i, ans in enumerate(answers):
            for j, text in enumerate(texts):
                if i != j and len(ans) > 4 and ans in text:
                    leaks.append(f"Leak: Q{i} answer in Q{j} stem")
                    leaking_indices.add(j) 
        
        for i, ans in enumerate(answers):
            for j, q in enumerate(batch):
                if i != j:
                    wrong_options = [opt.lower() for idx, opt in enumerate(q["options"]) if idx != q["correctIndex"]]
                    if ans in wrong_options:
                        leaks.append(f"Cross-leak: Q{i} answer is a distractor in Q{j}")
                        leaking_indices.add(j)
                        
        return leaks, leaking_indices

    @staticmethod
    def audit_batch_templates_and_facts(batch):
        templates = defaultdict(list)
        concepts = defaultdict(list)
        for i, q in enumerate(batch):
            tpl = q.get("metadata", {}).get("templateId", "unknown")
            concept = q.get("metadata", {}).get("concept", "unknown")
            templates[tpl].append(i)
            concepts[concept].append(i)
        
        violations = []
        bad_indices = set()
        for tpl, indices in templates.items():
            if len(indices) > 2 and tpl != "none" and "pattern" not in tpl:
                violations.append(f"Template '{tpl}' used {len(indices)} times (max 2)")
                bad_indices.update(indices[2:])
                
        for concept, indices in concepts.items():
            if len(indices) > 1 and concept != "unknown":
                violations.append(f"Concept '{concept}' repeated {len(indices)} times (same-fact variation)")
                bad_indices.update(indices[1:])

        return violations, bad_indices


class GeneratorV3:
    def __init__(self, target_count):
        self.target = target_count
        self.questions = []
        self.rejected = []
        self.raw_data = []
        with open("derived_opportunities.json", "r", encoding="utf-8-sig") as f:
            self.raw_data = json.load(f)
        # random.shuffle(self.raw_data) # We process as they come for reproducibility, or shuffle.
        
    def generate(self):
        for data in self.raw_data:
            if len(self.questions) >= self.target:
                break
                
            # The data is already in question opportunity format
            q = data
            opts = q["options"]
            ans = opts[q["correctIndex"]]
            random.shuffle(opts)
            q["correctIndex"] = opts.index(ans)
            q["options"] = opts
            
            passed, reason = QualityAuditor.audit_single_question(q)
            if passed:
                q["status"] = "AUTOMATED_VALIDATED"
                self.questions.append(q)
            else:
                q["status"] = "REJECTED"
                q["rejectionReason"] = reason
                self.rejected.append(q)

    def finalize_batch(self):
        leaks, leak_indices = QualityAuditor.audit_batch_leakage(self.questions)
        templates_issues, template_bad_indices = QualityAuditor.audit_batch_templates_and_facts(self.questions)
        
        bad_indices = leak_indices.union(template_bad_indices)
        
        final_accepted = []
        for i, q in enumerate(self.questions):
            if i in bad_indices:
                q["status"] = "REJECTED"
                q["rejectionReason"] = "Batch level failure: Clue leakage, template repetition, or fact repetition."
                self.rejected.append(q)
            else:
                final_accepted.append(q)
                
        self.questions = final_accepted
        
        upsc_count = sum(1 for q in self.questions if "UPSC" in q["metadata"]["examTarget"])
        recall_count = sum(1 for q in self.questions if q["metadata"]["cognitiveDemand"] == "RECALL")
        higher_order_count = len(self.questions) - recall_count
        
        return {
            "batchId": "BATCH-REAL-CORPUS-V3-SOURCE-DRIVEN",
            "candidates": len(self.questions) + len(self.rejected),
            "accepted": len(self.questions),
            "rejected": len(self.rejected),
            "clue_leakage_detected": len(leaks),
            "template_violations_detected": len(templates_issues),
            "concept_capacity": len(self.raw_data),
            "stats": {
                "percent_recall": round((recall_count / max(1, len(self.questions))) * 100, 1) if self.questions else 0,
                "percent_understand_plus": round((higher_order_count / max(1, len(self.questions))) * 100, 1) if self.questions else 0,
                "upsc_candidates_passing_higher_order_gate": upsc_count,
                "distinct_concepts": len(set(q["metadata"]["concept"] for q in self.questions)),
                "stopped_naturally": len(self.questions) < self.target
            },
            "questions": self.questions,
            "rejections": self.rejected,
            "leak_details": leaks,
            "template_details": templates_issues
        }

if __name__ == "__main__":
    gen = GeneratorV3(30)
    gen.generate()
    report = gen.finalize_batch()
    
    with open("validation_real_corpus_v3.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        
    print(f"Accepted: {report['accepted']}, Rejected: {report['rejected']}")
