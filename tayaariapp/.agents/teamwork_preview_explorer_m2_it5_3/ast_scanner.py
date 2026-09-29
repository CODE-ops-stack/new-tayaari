import ast
import json
import re
import sys

def main():
    with open('data/golden_eval_set.json', encoding='utf-8') as f:
        eval_set = json.load(f)

    with open('v13_discovery/semantic_extractor.py', encoding='utf-8') as f:
        se_code = f.read()

    with open('v13_discovery/normalizer.py', encoding='utf-8') as f:
        norm_code = f.read()

    def get_ast_strings(code):
        tree = ast.parse(code)
        strs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                strs.append(node.value)
        return strs

    se_strings = get_ast_strings(se_code)
    norm_strings = get_ast_strings(norm_code)

    print(f"semantic_extractor string literals: {len(se_strings)}")
    print(f"normalizer string literals: {len(norm_strings)}")

    items = eval_set['examples']
    STOPWORDS = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'in', 'on', 'at', 'to', 'for', 'of', 'and', 'or', 'that', 'which', 'with', 'as', 'by'}

    def is_trivial_ngram(words):
        meaningful = [w for w in words if w not in STOPWORDS]
        return len(meaningful) <= 1

    matches = []

    for item in items:
        iid = item['id']
        label = item['expected_label']
        text = item['text']
        words = re.findall(r'[a-zA-Z0-9]+', text.lower())

        for n in range(4, min(15, len(words) + 1)):
            for i in range(len(words) - n + 1):
                chunk_words = words[i:i+n]
                if is_trivial_ngram(chunk_words):
                    continue
                chunk = ' '.join(chunk_words)

                # Check in semantic_extractor strings
                for s in se_strings:
                    s_lower = s.lower()
                    if chunk in s_lower:
                        matches.append(('semantic_extractor.py', iid, label, n, chunk, s[:100].replace('\n', ' ')))

                # Check in normalizer strings
                for s in norm_strings:
                    s_lower = s.lower()
                    if chunk in s_lower:
                        matches.append(('normalizer.py', iid, label, n, chunk, s[:100].replace('\n', ' ')))

    # Deduplicate: for each (file, iid), find maximal n-grams
    seen = {}
    for file, iid, label, n, chunk, snippet in matches:
        key = (file, iid, chunk)
        seen[key] = (file, iid, label, n, chunk, snippet)

    print(f"\nTotal raw matches: {len(matches)}")
    print(f"Total unique (file, iid, chunk) matches: {len(seen)}\n")

    # Filter out sub-ngrams
    all_chunks = sorted(seen.keys(), key=lambda x: -len(x[2]))
    maximal_matches = []
    for file, iid, chunk in all_chunks:
        val = seen[(file, iid, chunk)]
        # check if this chunk is a substring of an already recorded larger chunk for the same file and iid
        if not any(file == m[0] and iid == m[1] and chunk in m[4] and chunk != m[4] for m in maximal_matches):
            maximal_matches.append(val)

    print(f"Maximal matches ({len(maximal_matches)}):")
    for file, iid, label, n, chunk, snippet in sorted(maximal_matches, key=lambda x: (x[0], x[1])):
        print(f"[{file}] {iid} ({label}, n={n}): \"{chunk}\"")
        print(f"   In AST Literal: {snippet}\n")

if __name__ == '__main__':
    main()
