with open('tests/e2e/test_e2e_tier3_pairwise.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the lines to fix
for i, line in enumerate(lines):
    if 'for opt in cq.options.values():' in line:
        print(f'Line {i+1}: {line.rstrip()}')
        lines[i] = '        for opt in cq.options:\n'
    if 'len(set(cq.options.values()))' in line:
        print(f'Line {i+1}: {line.rstrip()}')
        lines[i] = '        self.assertEqual(len(set(opt.get("text", "") for opt in cq.options)), 4)\n'

with open('tests/e2e/test_e2e_tier3_pairwise.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')