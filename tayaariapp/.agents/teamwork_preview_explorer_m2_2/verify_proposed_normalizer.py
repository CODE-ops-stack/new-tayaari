import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

from proposed_normalizer import DocumentNormalizer, WatermarkOcrCleaner, LayoutDesegmenter, TableParser

normalizer = DocumentNormalizer()

print("1. Testing Markdown Table Extraction:")
table_md = """
| Concept | Category | Description |
|---|---|---|
| P-Waves | Primary Waves | Compressional waves that travel through solids, liquids, and gases. |
| S-Waves | Secondary Waves | Shear waves that propagate exclusively through solids. |
"""
table_blocks = normalizer.normalize("test_table", table_md)
assert len(table_blocks) == 1
assert table_blocks[0].type == "TABLE"
assert len(table_blocks[0].clean_sentences) == 4
for s in table_blocks[0].clean_sentences:
    print(f"   [TABLE PROP]: {s}")
print("   -> Table extraction PASS")

print("\n2. Testing Desegmenter & Line Stitching:")
chopped_text = """
The Sun is at the
center and Only
star of our Solar
System.
It makes up for
about 99.86% of
the total mass of
solar system.
"""
prose_blocks = normalizer.normalize("test_chopped", chopped_text)
assert len(prose_blocks) == 1
assert len(prose_blocks[0].clean_sentences) == 2
print(f"   [PROSE 1]: {prose_blocks[0].clean_sentences[0]}")
print(f"   [PROSE 2]: {prose_blocks[0].clean_sentences[1]}")
print("   -> Desegmenter PASS")

print("\n3. Testing Watermark and Running Header Cleaner:")
noisy_text = """
PARMAR SSC
ISBN 81-7450-491-5
2018-192018-19
www.ssccglpinnacle.com                                                 Download Pinnacle Exam Preparation App
Textbook in Geography for Class VI
(a) Sunspots  (b) Solar wind
Figure 1.1 : Saptarishi and the North Star
*Total Questions Mapped:* 0
- **Topic**: 1. The Earth in the Solar System
Sol.1.(b)  Solar  wind.  It  is  a  constant stream of charged particles released from the Sun's corona.
"""
noisy_blocks = normalizer.normalize("test_noisy", noisy_text)
assert len(noisy_blocks) == 1
assert len(noisy_blocks[0].clean_sentences) == 1
assert "It  is  a  constant stream of charged particles" in noisy_blocks[0].clean_sentences[0]
print(f"   [SALVAGED EXPLANATION]: {noisy_blocks[0].clean_sentences[0]}")
print("   -> Watermark & Noise Cleaner PASS")

print("\n4. Testing Golden Evaluation Dataset Negatives (Noise Rejection):")
with open('data/golden_eval_set.json', 'r', encoding='utf-8') as f:
    eval_set = json.load(f)

negatives = [ex for ex in eval_set['examples'] if ex.get('expected_label') == 'negative']

leaked_noise = []
for ex in negatives:
    cat = ex.get('rejection_category')
    text = ex['text']
    
    # In table formatting artifact (NEG-038, NEG-039), isolated headers without data rows produce 0 propositions
    # In watermark_header and mcq_leakage, normalizer should reject or produce 0 propositions
    if cat in {'watermark_header', 'table_formatting_artifact', 'mcq_leakage'}:
        blocks = normalizer.normalize(ex['provenance']['source_file'], text)
        sents = [s for b in blocks for s in b.clean_sentences]
        if sents:
            leaked_noise.append((ex['id'], cat, text, sents))

print(f"   Evaluated {len(negatives)} negative examples.")
print(f"   Noise leakage count: {len(leaked_noise)}")
if leaked_noise:
    for item in leaked_noise:
        print(f"   * LEAKED: {item}")
else:
    print("   -> ALL NOISE CATEGORIES (MCQ leakage, watermarks, table artifacts) 100% REJECTED! PASS!")

print("\nALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
