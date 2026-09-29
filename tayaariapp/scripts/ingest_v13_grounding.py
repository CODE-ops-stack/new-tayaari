#!/usr/bin/env python3
"""
scripts/ingest_v13_grounding.py
================================
Automated pipeline for Milestone 6:
1. Harvests and synthesizes verified V13 candidate questions from source-material/geography_extracted.txt.
2. Subject every candidate to MultiAgentAuditingGate (Cognitive, Exam-Fit, Adversarial).
3. Applies QuestionRepairEngine if needed and verifies 100% PASS.
4. Formats candidates into DataImporter.kt-compliant Markdown via to_room_markdown().
5. Appends verified entries under Topic 1 in source-material/consolidated_grounding.md.
6. Synchronizes to app/src/main/assets/consolidated_grounding.md.
7. Validates ingestion with DataImporterSimulator to verify 0 rejections on all appended questions.
"""

import os
import sys
import shutil
import re
from typing import List

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from v13_discovery.question_synthesizer import CandidateQuestion, QuestionSynthesizer
from v13_discovery.auditors import MultiAgentAuditingGate, QuestionRepairEngine
from tests.e2e.test_helpers import DataImporterSimulator

def main():
    corpus_path = os.path.join(PROJECT_ROOT, "source-material", "geography_extracted.txt")
    grounding_path = os.path.join(PROJECT_ROOT, "source-material", "consolidated_grounding.md")
    assets_path = os.path.join(PROJECT_ROOT, "app", "src", "main", "assets", "consolidated_grounding.md")

    print(f"[1/6] Loading corpus from: {corpus_path}")
    synthesizer = QuestionSynthesizer()
    raw_candidates = synthesizer.synthesize_from_corpus(corpus_path, min_questions=50)
    print(f"      Harvested {len(raw_candidates)} candidate questions.")

    print("[2/6] Auditing and verifying via MultiAgentAuditingGate...")
    gate = MultiAgentAuditingGate()
    repair_engine = QuestionRepairEngine()

    audited_questions: List[CandidateQuestion] = []
    for idx, q in enumerate(raw_candidates, start=1):
        q.topicId = 1
        q.topicName = "The Earth in the Solar System"
        q.pdfSequenceNumber = f"V13-{idx:03d}"

        report = gate.audit(q)
        if report.overallGate != "PASS":
            q = repair_engine.repair(q, report)
            report2 = gate.audit(q)
            if report2.overallGate != "PASS":
                print(f"      Question {idx} failed audit after repair: {report2.failureReasons}")
                continue

        # Final check: Cognitive, Exam-Fit, Adversarial all PASS
        rep_final = gate.audit(q)
        assert rep_final.cognitiveVerdict == "PASS", f"Question {idx} failed cognitive audit"
        assert rep_final.examFitVerdict == "PASS", f"Question {idx} failed exam-fit audit"
        assert rep_final.adversarialVerdict == "PASS", f"Question {idx} failed adversarial audit"
        assert rep_final.overallGate == "PASS", f"Question {idx} failed overall gate"

        # Verify Explanation strictly precedes Correct Answer
        md = q.to_room_markdown()
        exp_idx = md.find("Explanation:")
        ans_idx = md.find("Correct Answer:")
        assert exp_idx != -1 and ans_idx != -1 and exp_idx < ans_idx, f"Explanation ordering violation in question {idx}"

        audited_questions.append(q)

    print(f"      {len(audited_questions)} questions fully verified and passed by MultiAgentAuditingGate.")

    print(f"[3/6] Reading current grounding file: {grounding_path}")
    with open(grounding_path, "r", encoding="utf-8") as f:
        grounding_content = f.read()

    # Pre-audit validation of existing markdown
    pre_sim = DataImporterSimulator.parse_markdown(grounding_content)
    print(f"      Baseline: totalFound={pre_sim['totalFound']}, accepted={pre_sim['totalAccepted']}, rejected={pre_sim['totalRejected']}")

    # Format new questions into Markdown
    formatted_blocks = []
    formatted_blocks.append("\n### V13 Multi-Agent Audited Discovery Data\n*Total Questions Mapped:* " + str(len(audited_questions)) + "\n")
    for q in audited_questions:
        formatted_blocks.append(q.to_room_markdown().strip() + "\n")

    v13_markdown_chunk = "\n".join(formatted_blocks)

    # Validate that the appended chunk independently parses with 0 rejections
    chunk_test_doc = "# Header\n\n## 1. The Earth in the Solar System\n" + v13_markdown_chunk
    chunk_sim = DataImporterSimulator.parse_markdown(chunk_test_doc)
    print(f"      Chunk validation: totalFound={chunk_sim['totalFound']}, accepted={chunk_sim['totalAccepted']}, rejected={chunk_sim['totalRejected']}")
    assert chunk_sim["totalFound"] == len(audited_questions), f"Expected {len(audited_questions)} found, got {chunk_sim['totalFound']}"
    assert chunk_sim["totalAccepted"] == len(audited_questions), f"Expected {len(audited_questions)} accepted, got {chunk_sim['totalAccepted']}"
    assert chunk_sim["totalRejected"] == 0, f"Chunk had rejections: {chunk_sim['rejections']}"

    # Check if V13 questions already present (avoid duplicate insertions)
    if "### V13 Multi-Agent Audited Discovery Data" in grounding_content:
        print("      Existing V13 block detected. Replacing with latest audited batch...")
        pattern = re.compile(r'\n### V13 Multi-Agent Audited Discovery Data.*?(?=\n## 2\. |\n---|\Z)', re.DOTALL)
        updated_content = pattern.sub("\n" + v13_markdown_chunk.strip() + "\n", grounding_content)
    else:
        # Insert before '## 2. Globe: Latitudes and Longitudes'
        target_marker = "\n## 2. Globe: Latitudes and Longitudes"
        if target_marker in grounding_content:
            parts = grounding_content.split(target_marker, 1)
            updated_content = parts[0] + "\n" + v13_markdown_chunk + "\n" + target_marker + parts[1]
        else:
            raise ValueError(f"Target marker '{target_marker}' not found in grounding file")

    print(f"[4/6] Writing updated grounding file: {grounding_path}")
    with open(grounding_path, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"[5/6] Synchronizing markdown to Android assets: {assets_path}")
    shutil.copy2(grounding_path, assets_path)
    assert os.path.exists(assets_path)

    print("[6/6] Validating full ingestion with DataImporterSimulator...")
    with open(grounding_path, "r", encoding="utf-8") as f:
        full_updated = f.read()
    post_sim = DataImporterSimulator.parse_markdown(full_updated)

    print(f"      Post-sync: totalFound={post_sim['totalFound']}, accepted={post_sim['totalAccepted']}, rejected={post_sim['totalRejected']}")
    newly_accepted = post_sim["totalAccepted"] - pre_sim["totalAccepted"]
    print(f"      Net newly accepted questions: {newly_accepted}")

    assert newly_accepted == len(audited_questions), f"Expected {len(audited_questions)} newly accepted, got {newly_accepted}"
    assert post_sim["totalRejected"] == pre_sim["totalRejected"], f"New rejections introduced! Pre: {pre_sim['totalRejected']}, Post: {post_sim['totalRejected']}"

    print(f"\nSUCCESS: Appended and synchronized {len(audited_questions)} verified V13 questions with 0 rejections.")

if __name__ == "__main__":
    main()
