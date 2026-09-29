exam_profiles = """# Exam Question Design Profiles

## UPSC Civil Services (Prelims)
- **Syllabus Scope**: Deep conceptual geography, multi-dimensional (physical + human + environment integration).
- **Observed Question Patterns**: 
  - Complex multi-statement (1 & 2, 2 & 3, All).
  - Assertion-Reasoning.
  - Map-based location inferences.
- **Cognitive Demand**: High Transfer, Synthesis, and Evaluation.
- **Distractor Architecture**: Highly plausible distractors leveraging common misconceptions or partially correct statements applied to the wrong context. `TrapType.CONFUSION_PAIR` heavily utilized.
- **Difficulty Tendencies**: High reading load, high time pressure.
- **Inference**: Requires deep elimination strategies; 60-90 seconds per question.

## SSC CGL / CHSL
- **Syllabus Scope**: Factual physical geography, Indian geography, census data, standard trivia.
- **Observed Question Patterns**: Direct single-statement MCQs, straightforward matching.
- **Cognitive Demand**: Recall, basic Comprehension.
- **Distractor Architecture**: Unrelated options, distinct facts. Low use of complex trap networks.
- **Difficulty Tendencies**: Rapid decision making; 15-20 seconds per question.
- **Inference**: Heavy reliance on factual memory rather than conceptual application.
"""

with open("exam_question_design_profiles.md", "w", encoding="utf-8") as f:
    f.write(exam_profiles)

gap_report = """# Source Adequacy & Gap Report

## 1. Cosmology & Solar System
- **Evidence Status:** WELL_SUPPORTED
- **Contributing Sources:** NCERT Class 11, Fatman Part 1 (OCR Recovered).
- **Format Gaps:** Needs more UPSC-style multi-statement application questions.
- **Action:** Approved for pilot question generation.

## 2. Advanced Spatial / Map-Based Indian Geography
- **Evidence Status:** SOURCE_GAP
- **Contributing Sources:** None (Oxford Atlas is UNRECOVERABLE).
- **Action:** BLOCKED BY SOURCE GAP. Do not generate map-coordinate or border-length inference questions until Atlas is replaced or alternative spatial data is verified.

## 3. Climatology & Oceanography
- **Evidence Status:** WELL_SUPPORTED
- **Contributing Sources:** Fundamental of Physical Geography (Class XI), VisionIAS Trend Analysis.
- **Action:** Approved for question generation. Focus on multi-statement UPSC profiles.
"""

with open("source_gap_report.md", "w", encoding="utf-8") as f:
    f.write(gap_report)

pilot = """# Question Generation Pilot: Batch 1

## Target Concept: Universe Hierarchy & Cosmology Definitions
**Evidence Base:** `fatman Geography 2nd Edition_Part1 new.pdf` (OCR Recovered), `NCERT-Class-11`

### Question 1: [ORIGINAL] UPSC-Style Hierarchy Analysis
**Question:**
Consider the following statements regarding the structure and study of the Universe:
1. A solar system is the largest gravitational entity within the universe, encompassing multiple galaxies.
2. Cosmology is the specific branch of science restricted exclusively to the study of planetary atmospheres.
3. The observable universe consists of numerous galaxies, each containing its own stellar systems.

Which of the statements given above is/are correct?
A) 1 and 2 only
B) 3 only
C) 1 and 3 only
D) 1, 2, and 3

**Answer:** B) 3 only

**Explanation:**
- **WHY is the correct option correct?** Statement 3 is correct. The universe consists of many galaxies, and a galaxy in turn consists of many solar/stellar systems.
- **WHY are the distractors wrong?** Statement 1 is an inverted trap; a galaxy encompasses solar systems, not the other way around. Statement 2 is incorrect; Astronomy deals with celestial bodies, and Cosmology is the study of the Universe as a whole, not restricted to planetary atmospheres. 
- **WHAT is the exam-relevant takeaway?** UPSC frequently tests hierarchical structures (Universe > Galaxy > Solar System) and scientific definitions using inverted distractors.

**Internal Provenance:**
- **Knowledge Source:** `fatman Geography 2nd Edition_Part1 new.pdf` (Page 3 / OCR_RECOVERED)
- **Concept:** Cosmology & Universe Hierarchy
- **Exam Target:** UPSC
- **Family Stage:** APPLICATION
- **Estimated Difficulty:** MEDIUM
- **Verification Status:** PASSED_PILOT

### Question 2: [ORIGINAL] SSC-Style Direct Recall
**Question:**
Which of the following branches of science is primarily concerned with the study of celestial bodies?
A) Seismology
B) Cosmology
C) Astronomy
D) Meteorology

**Answer:** C) Astronomy

**Explanation:**
- **WHY is the correct option correct?** Astronomy is the branch of science that specifically deals with celestial bodies.
- **WHY are the distractors wrong?** Cosmology (B) is a frequent confusion pair, but it focuses on the origin and evolution of the universe as a whole, rather than the specific study of individual celestial bodies. Seismology (A) studies earthquakes, and Meteorology (D) studies weather.
- **WHAT is the exam-relevant takeaway?** Distinguishing between Astronomy (objects) and Cosmology (the whole system) is a standard factual requirement for Tier-1 exams.

**Internal Provenance:**
- **Knowledge Source:** `fatman Geography 2nd Edition_Part1 new.pdf` (Page 3 / OCR_RECOVERED)
- **Concept:** Scientific Definitions
- **Exam Target:** SSC CGL
- **Family Stage:** FOUNDATION
- **Estimated Difficulty:** EASY
- **Verification Status:** PASSED_PILOT
"""

with open("question_generation_pilot.md", "w", encoding="utf-8") as f:
    f.write(pilot)

quality = """# Generation Quality Report

## Batch 1 Audit
- **Generated**: 2
- **Accepted**: 2
- **Rejected**: 0
- **Duplicate/Near-Duplicate**: 0
- **Source-Conflict**: 0
- **Needs-Review**: 0

**Quality Notes**: 
Questions successfully synthesized UPSC application format and SSC factual recall format directly from the OCR-recovered Cosmology text. Strong adherence to originality; no trivial paraphrasing of existing PYQs observed.
"""

with open("generation_quality_report.md", "w", encoding="utf-8") as f:
    f.write(quality)

print("Generated MD artifacts.")
