import os
import sys
import time
import json
import uuid

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from v13_discovery import normalizer
from v13_1_generator.extractor import extract_knowledge
from v13_1_generator.synthesizer import build_contracts, assemble_question
from v13_1_generator.validator import validate_question
from v13_1_generator.batch_auditor import audit_batch
from v13_1_generator.contracts import GeneratedQuestion

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE_FILES = [
    ("NCERT Class VI Geography",              "source-material/geography_extracted.txt",         "ncert_vi_geo",          "HISTORICAL"),
    ("NCERT/Fatman Composite Extract 2",       "source-material/geography_extracted_2.txt",       "ncert_fatman_ext2",     "HISTORICAL"),
    ("NCERT Class XI Physical Geography",      "source-material/ncert_xi_physical_geo.txt",       "ncert_xi_phys_geo",     "HISTORICAL"),
    ("NCERT Class XI India Environment",       "source-material/ncert_xi_india_env.txt",          "ncert_xi_india_env",    "HISTORICAL"),
    ("NCERT Class XII Human Geography",        "source-material/ncert_xii_human_geo.txt",         "ncert_xii_human_geo",   "HISTORICAL"),
    ("NCERT Class XII India Economy",          "source-material/ncert_xii_india_economy.txt",     "ncert_xii_india_econ",  "HISTORICAL"),
    ("NCERT Class IX Geography",               "source-material/ncert_ix_geo.txt",                "ncert_ix_geo",          "HISTORICAL"),
    ("NCERT Class X Geography",                "source-material/ncert_x_geo.txt",                 "ncert_x_geo",           "HISTORICAL"),
    ("Supplementary Verified Corpus",          "source-material/supplementary_corpus.txt",        "supp_corpus",           "HISTORICAL"),
]

def generate_v13_1_batch(max_candidates: int = 150):
    candidates = []
    rejected = []
    
    for source_label, rel_path, source_id, default_currentness in SOURCE_FILES:
        abs_path = os.path.join(BASE_DIR, rel_path)
        if not os.path.exists(abs_path):
            continue
            
        normalizer_inst = normalizer.DocumentNormalizer()
        blocks = normalizer_inst.normalize_file(abs_path)
        
        for block in blocks:
            if len(candidates) >= max_candidates: break
            sentences = getattr(block, "clean_sentences", []) or []
            
            for sent in sentences:
                if len(candidates) >= max_candidates: break
                
                # Phase 4 & 5
                intent = extract_knowledge(source_id, sent)
                if not intent:
                    continue
                    
                # Phase 6 & 8
                contracts = build_contracts(intent)
                if not contracts:
                    continue
                answer_contract, distractor_contract = contracts
                
                # Phase 7
                question = assemble_question(intent, answer_contract, distractor_contract)
                if not question:
                    continue
                    
                question.id = f"q_{uuid.uuid4().hex[:8]}"
                
                # Phase 9, 10, 11
                val_result = validate_question(question)
                if val_result.is_valid:
                    candidates.append(question)
                else:
                    rejected.append({
                        "id": question.id,
                        "reasons": val_result.failure_reasons,
                        "stem": question.stem,
                        "evidence": sent
                    })
                    
    # Phase 12
    final_accepted, batch_rejections = audit_batch(candidates)
    
    for c in candidates:
        if c.id in batch_rejections:
            rejected.append({
                "id": c.id,
                "reasons": [batch_rejections[c.id]],
                "stem": c.stem,
                "evidence": c.explanation
            })
            
    return final_accepted, rejected

def run():
    print("Running V13.1 Generator Repair Pipeline...")
    accepted, rejected = generate_v13_1_batch()
    print(f"Accepted: {len(accepted)}")
    print(f"Rejected: {len(rejected)}")
    
    # Dump for Phase 14 & 15 artifacts
    with open(os.path.join(BASE_DIR, "docs", "v13_1_accepted_sample.json"), "w", encoding="utf-8") as f:
        json.dump([q.__dict__ for q in accepted], f, indent=2)
        
    with open(os.path.join(BASE_DIR, "docs", "v13_1_rejected_sample.json"), "w", encoding="utf-8") as f:
        json.dump(rejected, f, indent=2)
        
    print("Done. Wrote sample artifacts.")
    
if __name__ == "__main__":
    run()
