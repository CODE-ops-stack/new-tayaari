"""
forensic_ast_analysis.py
Independent static AST and literal string forensic analysis script for Milestone 2 Iteration 4.
Checks:
1. 12 banned domain phrases in AST literals and raw code
2. Golden evaluation set strings (all 111 items) in AST literals and regex patterns
3. Test IDs, eval bypasses, and facade implementations
4. Presence and genuine implementation of all 14 semantic intents
"""

import ast
import json
import os
import re
import sys

REPO_ROOT = r"c:\Users\harsh\Downloads\tayaari\tayaariapp"
SEMANTIC_EXTRACTOR_PATH = os.path.join(REPO_ROOT, "v13_discovery", "semantic_extractor.py")
NORMALIZER_PATH = os.path.join(REPO_ROOT, "v13_discovery", "normalizer.py")
GOLDEN_EVAL_PATH = os.path.join(REPO_ROOT, "data", "golden_eval_set.json")

BANNED_PHRASES = [
    'longitudinal compressional',
    'lowest mean density',
    'very big and hot',
    'comprises immense reserves',
    'yellow dwarf',
    'satellite container port',
    'nearly all planets in',
    'denudational process in which',
    'tectonic process of',
    'plunges beneath',
    'transported and deposited by',
    'geologists|scientists|geographers|plate tectonics'
]

ALL_14_INTENTS = [
    "definition",
    "attribute",
    "cause/effect",
    "comparison",
    "spatial",
    "distribution",
    "classification",
    "quantity",
    "sequence",
    "condition",
    "exception",
    "process",
    "part-of",
    "member-of"
]


def extract_ast_strings(file_path):
    """Extracts all string constants from AST nodes with line numbers."""
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    tree = ast.parse(code, filename=file_path)
    string_nodes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lineno = getattr(node, 'lineno', 0)
            col_offset = getattr(node, 'col_offset', 0)
            string_nodes.append((lineno, col_offset, node.value))
    return code, string_nodes


def run_banned_phrases_check(file_path, code, string_nodes):
    findings = []
    # 1. Check raw code lines
    lines = code.splitlines()
    for idx, line in enumerate(lines, 1):
        for banned in BANNED_PHRASES:
            if "|" in banned:
                pattern = re.compile(banned, re.IGNORECASE)
                if pattern.search(line):
                    findings.append({
                        "file": file_path,
                        "line": idx,
                        "type": "banned_regex_match",
                        "banned_phrase": banned,
                        "content": line.strip()
                    })
            else:
                if banned.lower() in line.lower():
                    findings.append({
                        "file": file_path,
                        "line": idx,
                        "type": "banned_string_match",
                        "banned_phrase": banned,
                        "content": line.strip()
                    })
    # 2. Check AST string constants specifically
    for lineno, col, val in string_nodes:
        for banned in BANNED_PHRASES:
            if "|" in banned:
                pattern = re.compile(banned, re.IGNORECASE)
                if pattern.search(val):
                    findings.append({
                        "file": file_path,
                        "line": lineno,
                        "type": "ast_string_banned_regex",
                        "banned_phrase": banned,
                        "content": val
                    })
            else:
                if banned.lower() in val.lower():
                    findings.append({
                        "file": file_path,
                        "line": lineno,
                        "type": "ast_string_banned_literal",
                        "banned_phrase": banned,
                        "content": val
                    })
    return findings


def get_ngrams(text, n=4):
    words = re.findall(r'[A-Za-z0-9\-]+', text.lower())
    if len(words) < n:
        return []
    return [" ".join(words[i:i+n]) for i in range(len(words) - n + 1)]


def run_golden_eval_check(file_path, code, string_nodes, golden_data):
    findings = []
    # Load golden data
    items = golden_data if isinstance(golden_data, list) else golden_data.get("items", golden_data.get("examples", []))
    
    # Check for test IDs like POS-001, NEG-001
    for idx, line in enumerate(code.splitlines(), 1):
        for item in items:
            item_id = item.get("id") or item.get("code") or item.get("example_id")
            if item_id and item_id.lower() in line.lower():
                findings.append({
                    "file": file_path,
                    "line": idx,
                    "type": "test_id_in_code",
                    "item_id": item_id,
                    "content": line.strip()
                })

    # Collect n-grams from golden items
    # Skip extremely generic stopwords n-grams
    stop_ngrams = {
        "is an example of", "is defined as a", "in the form of", "is one of the",
        "as a result of", "is known as the", "refers to the process", "on the basis of"
    }

    golden_ngrams = {}
    for item in items:
        text = item.get("text", "") or item.get("raw_text", "") or item.get("sentence", "")
        item_id = item.get("id", "unknown")
        # 4-grams and 5-grams
        for n in [4, 5]:
            for ng in get_ngrams(text, n):
                if ng not in stop_ngrams:
                    golden_ngrams[ng] = (item_id, text)

    # Search AST string constants
    for lineno, col, val in string_nodes:
        val_lower = val.lower()
        # Check if AST string matches any 4-gram or 5-gram from golden set
        for ng, (item_id, orig_text) in golden_ngrams.items():
            if ng in val_lower:
                # Filter out pure regex syntax or generic phrases
                # Check if it's substantive domain content
                findings.append({
                    "file": file_path,
                    "line": lineno,
                    "type": "golden_ngram_match",
                    "item_id": item_id,
                    "ngram": ng,
                    "ast_val": val[:100],
                    "orig_text": orig_text[:100]
                })

    return findings


def run_facade_and_bypass_check(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()
    tree = ast.parse(code, filename=file_path)
    findings = []
    
    for node in ast.walk(tree):
        # Check function defs that just return constant or pass
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if len(node.body) == 1:
                stmt = node.body[0]
                if isinstance(stmt, ast.Pass):
                    findings.append({
                        "file": file_path,
                        "line": node.lineno,
                        "type": "facade_empty_pass",
                        "func": node.name
                    })
                elif isinstance(stmt, ast.Return) and isinstance(stmt.value, ast.Constant):
                    # Check if it's a dummy return like return True or return "clean"
                    if node.name not in ["__str__", "__repr__", "is_valid"]:
                        findings.append({
                            "file": file_path,
                            "line": node.lineno,
                            "type": "facade_constant_return",
                            "func": node.name,
                            "val": stmt.value.value
                        })
        # Check If conditions that check test environment or test names
        if isinstance(node, ast.If):
            # Check for conditions like "pytest" in sys.modules, or test_ in var names
            cond_src = ast.unparse(node.test)
            suspicious = ["pytest", "unittest", "POS-", "NEG-", "golden", "eval_set"]
            for s in suspicious:
                if s.lower() in cond_src.lower():
                    findings.append({
                        "file": file_path,
                        "line": node.lineno,
                        "type": "suspicious_test_bypass_if",
                        "condition": cond_src
                    })
    return findings


def verify_14_intents(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        code = f.read()

    results = {}
    for intent in ALL_14_INTENTS:
        # Check if intent appears in PATTERNS or rule sets
        # Format in PATTERNS: ("intent_name", re.compile(...))
        intent_slug = intent.replace("/", "_").replace("-", "_")
        escaped_intent = re.escape(intent)
        pattern_str = rf'\(["\']({escaped_intent}|{intent_slug})["\']\s*,\s*re\.compile'
        has_pattern = bool(re.search(pattern_str, code, re.IGNORECASE))
        
        # Check if intent appears in fallback / rule extractors
        has_logic = bool(re.search(rf'["\']{escaped_intent}["\']|["\']{intent_slug}["\']', code, re.IGNORECASE))
        
        results[intent] = {
            "has_compiled_pattern": has_pattern,
            "has_logic_reference": has_logic
        }
    return results


def main():
    print("=" * 60)
    print("FORENSIC AST & INTEGRITY AUDIT: Milestone 2 Iteration 4")
    print("=" * 60)

    # 1. Parse AST
    se_code, se_strings = extract_ast_strings(SEMANTIC_EXTRACTOR_PATH)
    norm_code, norm_strings = extract_ast_strings(NORMALIZER_PATH)
    print(f"[OK] Parsed semantic_extractor.py: {len(se_strings)} AST string constants extracted.")
    print(f"[OK] Parsed normalizer.py: {len(norm_strings)} AST string constants extracted.")

    # 2. Banned phrases check
    print("\n--- 1. BANNED PHRASES CHECK ---")
    se_banned = run_banned_phrases_check(SEMANTIC_EXTRACTOR_PATH, se_code, se_strings)
    norm_banned = run_banned_phrases_check(NORMALIZER_PATH, norm_code, norm_strings)
    all_banned = se_banned + norm_banned
    print(f"Total banned phrase violations found: {len(all_banned)}")
    for b in all_banned:
        print(f"  [VIOLATION] {b['file']}:{b['line']} - Phrase: '{b['banned_phrase']}' | Line: {b['content']}")

    # 3. Golden eval set matching
    print("\n--- 2. GOLDEN EVALUATION SET (111 items) STRING & N-GRAM CHECK ---")
    with open(GOLDEN_EVAL_PATH, "r", encoding="utf-8") as f:
        golden_data = json.load(f)
    items = golden_data if isinstance(golden_data, list) else golden_data.get("items", golden_data.get("examples", []))
    print(f"Loaded {len(items)} golden evaluation items from {GOLDEN_EVAL_PATH}")
    
    se_golden = run_golden_eval_check(SEMANTIC_EXTRACTOR_PATH, se_code, se_strings, golden_data)
    norm_golden = run_golden_eval_check(NORMALIZER_PATH, norm_code, norm_strings, golden_data)
    all_golden = se_golden + norm_golden
    print(f"Total golden eval string / n-gram violations found: {len(all_golden)}")
    for g in all_golden:
        print(f"  [MATCH] {g['file']}:{g['line']} - Item: {g.get('item_id')} | Match: '{g.get('ngram') or g.get('item_id')}' | AST Val: {g.get('ast_val')}")

    # 4. Facade & Test Bypass Check
    print("\n--- 3. FACADE IMPLEMENTATIONS & TEST BYPASS CHECK ---")
    se_facade = run_facade_and_bypass_check(SEMANTIC_EXTRACTOR_PATH)
    norm_facade = run_facade_and_bypass_check(NORMALIZER_PATH)
    all_facade = se_facade + norm_facade
    print(f"Total suspicious facade/bypass nodes found: {len(all_facade)}")
    for f in all_facade:
        print(f"  [FACADE/BYPASS] {f['file']}:{f['line']} - Type: {f['type']} | Detail: {f.get('func') or f.get('condition')}")

    # 5. 14 Semantic Intents Verification
    print("\n--- 4. 14 SEMANTIC INTENTS IMPLEMENTATION VERIFICATION ---")
    intent_results = verify_14_intents(SEMANTIC_EXTRACTOR_PATH)
    missing_intents = []
    for intent, stat in intent_results.items():
        status_str = "OK" if stat["has_compiled_pattern"] and stat["has_logic_reference"] else "INCOMPLETE"
        print(f"  - Intent '{intent}': pattern={stat['has_compiled_pattern']}, logic={stat['has_logic_reference']} -> {status_str}")
        if not (stat["has_compiled_pattern"] and stat["has_logic_reference"]):
            missing_intents.append(intent)
    print(f"Missing or incomplete intents: {missing_intents}")

    print("\n" + "=" * 60)
    print("SUMMARY")
    print(f"Banned phrases: {len(all_banned)}")
    print(f"Golden eval matches: {len(all_golden)}")
    print(f"Facades / Bypasses: {len(all_facade)}")
    print(f"Missing intents: {len(missing_intents)}")
    print("=" * 60)

    if len(all_banned) == 0 and len(all_golden) == 0 and len(all_facade) == 0 and len(missing_intents) == 0:
        print("VERDICT: CLEAN (Static AST Analysis PASSED)")
        return 0
    else:
        print("VERDICT: INTEGRITY VIOLATION DETECTED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
