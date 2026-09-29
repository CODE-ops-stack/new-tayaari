import os
import sys
import glob
import json
import re
from collections import defaultdict
import fitz  # PyMuPDF

def analyze_corpus():
    workspace_root = r"c:\Users\harsh\Downloads\tayaari"
    tayaariapp_root = r"c:\Users\harsh\Downloads\tayaari\tayaariapp"
    source_mat_dir = os.path.join(tayaariapp_root, "source-material")
    
    results = {
        "pdf_files": [],
        "text_markdown_files": [],
        "json_files": [],
        "totals": {
            "pdf_count": 0,
            "pdf_pages": 0,
            "pdf_words": 0,
            "text_md_count": 0,
            "text_md_words": 0,
            "json_count": 0,
            "json_items": 0,
            "total_words_all": 0
        },
        "subject_distribution": defaultdict(lambda: {"files": 0, "words": 0, "pages": 0}),
        "structural_challenges": {
            "ocr_fragments": [],
            "multi_word_entities": [],
            "tables": [],
            "complex_sentences": [],
            "headers_footers": []
        },
        "v12_svo_evaluation": {
            "sentences_evaluated": 0,
            "svo_matched": 0,
            "svo_rejected": 0,
            "rejection_reasons": defaultdict(int),
            "lost_knowledge_breakdown": defaultdict(int),
            "matched_by_pattern": defaultdict(int)
        }
    }
    
    # 1. Analyze all PDFs
    pdf_paths = glob.glob(os.path.join(source_mat_dir, "*.pdf"))
    for pdf_path in sorted(pdf_paths):
        fn = os.path.basename(pdf_path)
        size_bytes = os.path.getsize(pdf_path)
        doc = None
        try:
            doc = fitz.open(pdf_path)
            pages = len(doc)
            text_extracted = ""
            for pno in range(pages):
                text_extracted += doc[pno].get_text()
            words = len(text_extracted.split())
            chars = len(text_extracted)
            extractable = chars > 1000
        except Exception as e:
            pages = 0
            words = 0
            chars = 0
            extractable = False
            error = str(e)
        finally:
            if doc: doc.close()
            
        # Classify subject and type
        lower_name = fn.lower()
        if "ncert" in lower_name or "class" in lower_name or "fundamental" in lower_name or "india physical" in lower_name or "people and economy" in lower_name or "our environmemnt" in lower_name or "social science" in lower_name or "practical work" in lower_name:
            source_type = "NCERT Textbook"
        elif "pyq" in lower_name or "question" in lower_name or "trend analysis" in lower_name:
            source_type = "Exam PYQ Compendium"
        elif "atlas" in lower_name:
            source_type = "Atlas / Spatial Map"
        elif "fatman" in lower_name or "pmf ias" in lower_name or "lotusarise" in lower_name or "geography 4.0" in lower_name or "geogrophy" in lower_name or "ccab2" in lower_name or "newgeography" in lower_name or "environment (" in lower_name:
            source_type = "Standard Reference / Coaching Notes"
        else:
            source_type = "Reference / Other"

        # Subject classification
        if "environment" in lower_name:
            subj = "Environment & Ecology"
        elif "physical" in lower_name or "dynamo" in lower_name or "geomagnetism" in lower_name:
            subj = "Physical Geography & Geophysics"
        elif "human" in lower_name or "people and economy" in lower_name:
            subj = "Human & Economic Geography"
        elif "social science" in lower_name:
            subj = "General Social Science & Geography"
        elif "atlas" in lower_name:
            subj = "Cartography & Spatial Index"
        elif "question" in lower_name or "pyq" in lower_name:
            subj = "Geography Exam Questions (PYQ)"
        else:
            subj = "General Geography"

        results["pdf_files"].append({
            "filename": fn,
            "size_mb": round(size_bytes / (1024 * 1024), 2),
            "pages": pages,
            "extractable": extractable,
            "words": words,
            "chars": chars,
            "source_type": source_type,
            "subject": subj
        })
        results["totals"]["pdf_count"] += 1
        results["totals"]["pdf_pages"] += pages
        results["totals"]["pdf_words"] += words
        results["totals"]["total_words_all"] += words
        results["subject_distribution"][subj]["files"] += 1
        results["subject_distribution"][subj]["words"] += words
        results["subject_distribution"][subj]["pages"] += pages

    # 2. Analyze Text and Markdown files
    text_md_files = [
        os.path.join(source_mat_dir, "consolidated_grounding.md"),
        os.path.join(source_mat_dir, "consolidated_grounding_merged.md"),
        os.path.join(source_mat_dir, "geography_extracted.txt"),
        os.path.join(source_mat_dir, "geography_extracted_2.txt"),
        os.path.join(source_mat_dir, "question_extracted.txt"),
        os.path.join(source_mat_dir, "supplementary_corpus.txt"),
        os.path.join(source_mat_dir, "geography-syllabus.md"),
        os.path.join(source_mat_dir, "geography-syllabus-gs.md"),
        os.path.join(source_mat_dir, "pyq-analysis-prelims.md"),
        os.path.join(source_mat_dir, "examiner-pattern-guide.md"),
        os.path.join(source_mat_dir, "file-categories.md"),
        os.path.join(source_mat_dir, "exam-complexity-profiles.md"),
        os.path.join(source_mat_dir, "design-system.md"),
        os.path.join(tayaariapp_root, "exam_question_design_profiles.md")
    ]
    
    for fpath in text_md_files:
        if not os.path.exists(fpath):
            continue
        fn = os.path.basename(fpath)
        size_bytes = os.path.getsize(fpath)
        with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        lines = content.splitlines()
        words = len(content.split())
        chars = len(content)
        
        # Determine format and role
        if fn.endswith(".md"):
            if "syllabus" in fn or "guide" in fn or "profiles" in fn or "design" in fn or "categories" in fn:
                role = "Syllabus / Specification / Design Profile"
            else:
                role = "Grounding Knowledge Synthesis"
        else:
            if "question" in fn:
                role = "Extracted Exam PYQ & Explanations"
            else:
                role = "Extracted Textbook Prose"
                
        subj = "Geography & General Studies"
        results["text_markdown_files"].append({
            "filename": fn,
            "size_kb": round(size_bytes / 1024, 2),
            "lines": len(lines),
            "words": words,
            "chars": chars,
            "role": role,
            "subject": subj
        })
        results["totals"]["text_md_count"] += 1
        results["totals"]["text_md_words"] += words
        results["totals"]["total_words_all"] += words
        results["subject_distribution"][subj]["files"] += 1
        results["subject_distribution"][subj]["words"] += words

    # 3. Analyze JSON files (Databases / Question Banks / Registries)
    json_targets = [
        os.path.join(source_mat_dir, "extracted_ssc_qs.json"),
        os.path.join(tayaariapp_root, "source_registry.json"),
        os.path.join(tayaariapp_root, "syllabus_knowledge_map.json"),
        os.path.join(tayaariapp_root, "corpus_data.json"),
        os.path.join(tayaariapp_root, "staging_batch_1.json"),
        os.path.join(tayaariapp_root, "staging_batch_2.json"),
        os.path.join(tayaariapp_root, "staging_production_v1.json"),
        os.path.join(tayaariapp_root, "derived_opportunities.json"),
        os.path.join(tayaariapp_root, "oxford_atlas_spatial_index.json"),
        os.path.join(tayaariapp_root, "pyq_index.json"),
        os.path.join(tayaariapp_root, "theory_nodes.json"),
        os.path.join(tayaariapp_root, "generic_theory_nodes.json")
    ]
    for jpath in json_targets:
        if not os.path.exists(jpath):
            continue
        fn = os.path.basename(jpath)
        size_kb = round(os.path.getsize(jpath) / 1024, 2)
        try:
            with open(jpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                item_count = len(data)
                schema_type = f"Array of {type(data[0]).__name__ if data else 'Empty'}"
            elif isinstance(data, dict):
                item_count = len(data.keys())
                schema_type = "Dictionary / Key-Value Mapping"
            else:
                item_count = 1
                schema_type = type(data).__name__
        except Exception as e:
            item_count = 0
            schema_type = f"Parse Error: {e}"

        results["json_files"].append({
            "filename": fn,
            "size_kb": size_kb,
            "item_count": item_count,
            "schema_type": schema_type
        })
        results["totals"]["json_count"] += 1
        results["totals"]["json_items"] += item_count

    # 4. Deep Linguistic & Structural Challenge Profiling
    # Sample lines/paragraphs from extracted text and consolidated grounding
    sample_texts = []
    for fn in ["consolidated_grounding.md", "geography_extracted.txt", "geography_extracted_2.txt", "question_extracted.txt"]:
        fp = os.path.join(source_mat_dir, fn)
        if os.path.exists(fp):
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                sample_texts.extend(f.readlines())

    ocr_noise_samples = []
    multi_word_samples = []
    table_samples = []
    complex_sentence_samples = []
    header_samples = []
    
    # Compile regexes for V12 SVO extractor simulation
    BAD_ENTITIES = {"it", "this", "that", "these", "those", "they", "he", "she", "which", "app", "download", "pinnacle"}
    comp_re = re.compile(r'^([A-Z][a-zA-Z\s]+)\s+(is|are|involves|reduces|has|produces|affects)\s+(.*?),?\s+(while|whereas)\s+([a-zA-Z\s]+)\s+(is|are|involves|reduces|has|produces|affects|lies|focuses|grow|grows)\s+(.*)')
    def_re = re.compile(r'^([A-Z][a-zA-Z\s]+)\s+(is known as|refers to|comprises|consists of|includes)\s+(.*)')
    ce1_re = re.compile(r'^([A-Z][a-zA-Z\s]+)\s+(is due to|occurs because of|is caused by)\s+(.*)')
    ce2_re = re.compile(r'^([A-Z][a-zA-Z\s]+)\s+(causes|leads to|results in)\s+(.*)')
    sp_re = re.compile(r'^([A-Z][a-zA-Z\s]+)\s+(is located in|borders|is situated in|flows through|lies in)\s+(.*)')

    # Semantic knowledge intent patterns that SVO misses
    proc_re = re.compile(r'\b(formed by|undergoes|step|cycle|sequence|gradually|transforms into|first|then|subsequently|cooling and solidification|weathering and erosion)\b', re.IGNORECASE)
    cond_re = re.compile(r'\b(if|when|provided that|unless|subject to|in the presence of|under high pressure|at temperatures exceeding)\b', re.IGNORECASE)
    class_re = re.compile(r'\b(classified into|divided into|types of|categories|broad groups|forms of)\b', re.IGNORECASE)
    quant_re = re.compile(r'\b(\d+(\.\d+)?\s*(%|percent|km|km²|metres|meters|g/cm³|degrees|latitude|longitude|bar))\b', re.IGNORECASE)
    attr_re = re.compile(r'\b(characterized by|exhibits|contains high amounts of|rich in|composed of|features include)\b', re.IGNORECASE)
    caus_flex_re = re.compile(r'\b(because|as a result of|thereby|giving rise to|driven by|facilitated by|owing to|responsible for)\b', re.IGNORECASE)
    comp_flex_re = re.compile(r'\b(in contrast|unlike|differ from|higher than|lower than|faster than|slower than|distinguished from)\b', re.IGNORECASE)
    spatial_flex_re = re.compile(r'\b(flanked by|stretches from|extends between|bounded by|draining into|situated along|distributed across)\b', re.IGNORECASE)

    svo_matched_count = 0
    svo_rejected_count = 0
    
    lost_counts = defaultdict(int)
    rejection_reasons = defaultdict(int)
    matched_patterns = defaultdict(int)

    # Let's inspect sentences
    for line in sample_texts:
        line_clean = line.strip()
        if not line_clean:
            continue
            
        # Detect OCR noise
        if re.search(r'\s{2,}', line_clean) or re.search(r'[a-z]\s-\s[a-z]', line_clean) or re.search(r'', line_clean) or re.search(r'\b[b-df-hj-np-tv-z]{5,}\b', line_clean):
            if len(ocr_noise_samples) < 15:
                ocr_noise_samples.append(line_clean)
                
        # Detect Tables
        if "|" in line_clean:
            if len(table_samples) < 10:
                table_samples.append(line_clean)
                
        # Detect Headings
        if (line_clean.startswith("#") or (len(line_clean.split()) < 5 and line_clean.isupper() and len(line_clean) > 3)):
            if len(header_samples) < 10:
                header_samples.append(line_clean)

        # Split sentences for extraction evaluation
        sents = re.split(r'(?<=[.!?])\s+', line_clean)
        for s in sents:
            s = s.strip()
            if not s: continue
            
            # Detect multi-word entities in educational texts
            mwe = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,}\b', s)
            if mwe and len(multi_word_samples) < 15:
                multi_word_samples.extend(mwe[:3])
                
            # Detect complex sentences with multiple clauses
            if (s.count(',') >= 3 or (";" in s) or ("—" in s)) and len(s.split()) > 20:
                if len(complex_sentence_samples) < 10:
                    complex_sentence_samples.append(s)

            # Test V12 SVO regex extractor
            if len(s) < 20 or len(s) > 300:
                rejection_reasons["Length out of bounds (<20 or >300 chars)"] += 1
                svo_rejected_count += 1
                continue
                
            if re.search(r'\([a-e]\)', s) or re.search(r'\b[A-E]\b\)', s):
                rejection_reasons["MCQ option marker artifact detected"] += 1
                svo_rejected_count += 1
                continue

            matched = False
            
            # Pattern 1: COMPARISON
            m = comp_re.match(s)
            if m:
                sx = m.group(1).strip()
                sy = m.group(5).strip()
                if not any(w in BAD_ENTITIES for w in sx.lower().split()) and not any(w in BAD_ENTITIES for w in sy.lower().split()):
                    matched = True
                    matched_patterns["COMPARISON"] += 1
            
            # Pattern 2: DEFINITION
            if not matched:
                m = def_re.match(s)
                if m:
                    subj = m.group(1).strip()
                    if not any(w in BAD_ENTITIES for w in subj.lower().split()):
                        matched = True
                        matched_patterns["DEFINITION"] += 1

            # Pattern 3: CAUSE_EFFECT_INVERTED
            if not matched:
                m = ce1_re.match(s)
                if m:
                    effect = m.group(1).strip()
                    if not any(w in BAD_ENTITIES for w in effect.lower().split()):
                        matched = True
                        matched_patterns["CAUSE_EFFECT_INVERTED"] += 1

            # Pattern 4: CAUSE_EFFECT
            if not matched:
                m = ce2_re.match(s)
                if m:
                    cause = m.group(1).strip()
                    if not any(w in BAD_ENTITIES for w in cause.lower().split()):
                        matched = True
                        matched_patterns["CAUSE_EFFECT"] += 1

            # Pattern 5: SPATIAL
            if not matched:
                m = sp_re.match(s)
                if m:
                    subj = m.group(1).strip()
                    if not any(w in BAD_ENTITIES for w in subj.lower().split()):
                        matched = True
                        matched_patterns["SPATIAL"] += 1

            if matched:
                svo_matched_count += 1
            else:
                svo_rejected_count += 1
                rejection_reasons["Failed strict SVO regex syntax"] += 1
                
                # Check what type of knowledge was lost
                if proc_re.search(s):
                    lost_counts["PROCESS_OR_SEQUENCE"] += 1
                if cond_re.search(s):
                    lost_counts["CONDITIONALITY"] += 1
                if class_re.search(s):
                    lost_counts["CLASSIFICATION_TAXONOMY"] += 1
                if quant_re.search(s):
                    lost_counts["QUANTITATIVE_NUMERICAL"] += 1
                if attr_re.search(s):
                    lost_counts["ATTRIBUTE_OR_COMPOSITION"] += 1
                if caus_flex_re.search(s):
                    lost_counts["CAUSE_EFFECT_FLEXIBLE"] += 1
                if comp_flex_re.search(s):
                    lost_counts["COMPARISON_FLEXIBLE"] += 1
                if spatial_flex_re.search(s):
                    lost_counts["SPATIAL_TOPOLOGICAL_FLEXIBLE"] += 1

    results["structural_challenges"]["ocr_noise_samples"] = ocr_noise_samples[:10]
    results["structural_challenges"]["multi_word_entities"] = list(set(multi_word_samples))[:15]
    results["structural_challenges"]["table_samples"] = table_samples[:6]
    results["structural_challenges"]["complex_sentences"] = complex_sentence_samples[:6]
    results["structural_challenges"]["header_samples"] = header_samples[:6]

    results["v12_svo_evaluation"]["sentences_evaluated"] = svo_matched_count + svo_rejected_count
    results["v12_svo_evaluation"]["svo_matched"] = svo_matched_count
    results["v12_svo_evaluation"]["svo_rejected"] = svo_rejected_count
    results["v12_svo_evaluation"]["svo_match_rate_pct"] = round(svo_matched_count / (svo_matched_count + svo_rejected_count) * 100, 2) if (svo_matched_count + svo_rejected_count) > 0 else 0
    results["v12_svo_evaluation"]["rejection_reasons"] = dict(rejection_reasons)
    results["v12_svo_evaluation"]["lost_knowledge_breakdown"] = dict(lost_counts)
    results["v12_svo_evaluation"]["matched_by_pattern"] = dict(matched_patterns)

    # Dump results to JSON
    out_file = os.path.join(r"c:\Users\harsh\Downloads\tayaari\tayaariapp\.agents\teamwork_preview_explorer_survey_2", "deep_corpus_analysis.json")
    with open(out_file, "w", encoding="utf-8") as out_f:
        json.dump(results, out_f, indent=2)
    print(f"Deep analysis complete! Dumped to {out_file}")
    print(f"Total PDFs: {results['totals']['pdf_count']} ({results['totals']['pdf_pages']} pages, {results['totals']['pdf_words']} words)")
    print(f"Total Text/MD files: {results['totals']['text_md_count']} ({results['totals']['text_md_words']} words)")
    print(f"Total Grand Words: {results['totals']['total_words_all']}")
    print(f"SVO Evaluated: {results['v12_svo_evaluation']['sentences_evaluated']}, Matched: {svo_matched_count}, Rejected: {svo_rejected_count} ({results['v12_svo_evaluation']['svo_match_rate_pct']}%)")
    print("Lost Knowledge Breakdown:")
    for k, v in results['v12_svo_evaluation']['lost_knowledge_breakdown'].items():
        print(f"  {k}: {v}")

if __name__ == "__main__":
    analyze_corpus()
