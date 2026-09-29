with open('tests/e2e/test_e2e_tier3_pairwise.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the two occurrences of dict format with list format
content = content.replace(
    'cq.options = {"a": "Granite", "b": "Sandstone", "c": "Basalt", "d": "Marble"}',
    'cq.options = [{"id": "opt_a", "text": "Granite"}, {"id": "opt_b", "text": "Sandstone"}, {"id": "opt_c", "text": "Basalt"}, {"id": "opt_d", "text": "Marble"}]'
)

with open('tests/e2e/test_e2e_tier3_pairwise.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')