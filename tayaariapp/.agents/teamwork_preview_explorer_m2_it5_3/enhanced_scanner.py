import ast
import json
import re

with open('data/golden_eval_set.json', encoding='utf-8') as f:
    eval_set = json.load(f)

with open('v13_discovery/semantic_extractor.py', encoding='utf-8') as f:
    se_code = f.read()

with open('v13_discovery/normalizer.py', encoding='utf-8') as f:
    norm_code = f.read()

items = eval_set['examples']

# Find all string literals in both files
def get_ast_strings_with_lines(code):
    tree = ast.parse(code)
    strs = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            strs.append((node.lineno if hasattr(node, 'lineno') else 0, node.value))
    return strs

se_strs = get_ast_strings_with_lines(se_code)
norm_strs = get_ast_strings_with_lines(norm_code)

print(f"Scanning across {len(items)} golden items...")

findings = []

for item in items:
    iid = item['id']
    label = item['expected_label']
    text = item['text']

    # 1. Check if concatenated words or phrases appear in normalizer.py
    for line, s in norm_strs:
        # Check if s (if len >= 10) appears in item text
        clean_s = re.sub(r'[^a-zA-Z0-9]', '', s).lower()
        clean_t = re.sub(r'[^a-zA-Z0-9]', '', text).lower()
        if len(clean_s) >= 12 and clean_s in clean_t:
            findings.append(('normalizer.py', line, iid, label, s, "Normalizer literal matches sanitized item text"))

    # 2. Check for sequence / quantity / specific phrases in semantic_extractor.py
    for line, s in se_strs:
        # If string contains regex with fragments matching this item
        # e.g. check "arrive.*first", "commenced approximately"
        if "commenced approximately" in s and iid == "POS-034":
            findings.append(('semantic_extractor.py', line, iid, label, "commenced approximately.*followed by", "Regex branch matches POS-034"))
        if "arrive" in s and "followed sequentially" in s and iid == "POS-036":
            findings.append(('semantic_extractor.py', line, iid, label, "arrive(?:s)? first.*followed sequentially by", "Regex branch matches POS-036"))

print(f"\nTargeted Audit Findings ({len(findings)}):")
for f in findings:
    print(f"[{f[0]}:{f[1]}] Item {f[2]} ({f[3]}): '{f[4]}' -> {f[5]}")
