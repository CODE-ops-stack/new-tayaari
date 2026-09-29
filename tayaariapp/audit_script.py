import re
import sys
import json
from collections import defaultdict
import os

input_file = "c:/Users/harsh/Downloads/tayaari/tayaariapp/app/src/main/assets/consolidated_grounding.md"
output_file = "C:/Users/harsh/.gemini/antigravity/brain/5bf0eb04-a07a-444d-95e7-619fe2564e21/content_audit_report.md"

def main():
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"File not found: {input_file}")
        sys.exit(1)

    blocks = re.split(r'\n##\s+', '\n' + content)
    
    topic_counts = defaultdict(int)
    flagged = []
    questions_seen = {}
    duplicates = []

    topic_keywords = {
        '1': ['planet', 'solar', 'sun', 'moon', 'celestial', 'orbit', 'earth', 'star', 'asteroid', 'meteoroid', 'galaxy', 'universe'],
        '2': ['globe', 'latitude', 'longitude', 'equator', 'prime meridian', 'hemisphere', 'tropic', 'pole', 'grid', 'time'],
        '3': ['motion', 'rotation', 'revolution', 'axis', 'season', 'solstice', 'equinox', 'day', 'night', 'year', 'sun'],
        '4': ['map', 'scale', 'symbol', 'direction', 'compass', 'physical', 'political', 'thematic', 'sketch', 'plan'],
        '5': ['domain', 'lithosphere', 'hydrosphere', 'atmosphere', 'biosphere', 'continent', 'ocean', 'gas', 'water', 'life'],
        '6': ['landform', 'mountain', 'plateau', 'plain', 'river', 'glacier', 'valley', 'erosion', 'deposition'],
        '7': ['country', 'india', 'state', 'boundary', 'neighbor', 'peninsula', 'island', 'climate', 'vegetation'],
        '8': ['climate', 'weather', 'monsoon', 'season', 'rain', 'temperature', 'wind', 'forest', 'wildlife']
    }

    # default keywords if topic not matched above
    default_keywords = ['what', 'which', 'how', 'why', 'where', 'explain', 'describe']

    for block in blocks:
        if not block.strip():
            continue
        
        topic_match = re.search(r'-\s*\*\*Topic\*\*:\s*(.+)', block)
        question_match = re.search(r'-\s*\*\*Question\*\*:\s*```[\w]*\n(.*?)```', block, re.DOTALL)
        if not question_match:
            question_match = re.search(r'-\s*\*\*Question\*\*:\s*(.*?)(?=\n-|\Z)', block, re.DOTALL)
            
        if topic_match and question_match:
            topic = topic_match.group(1).strip()
            question_text = question_match.group(1).strip()
            
            topic_counts[topic] += 1
            
            # Find topic number
            num_match = re.match(r'^(\d+)', topic)
            topic_num = num_match.group(1) if num_match else ''
            
            keywords = topic_keywords.get(topic_num, default_keywords)
            
            # Check for keywords
            q_lower = question_text.lower()
            if not any(kw in q_lower for kw in keywords):
                flagged.append({
                    'topic': topic,
                    'question': question_text,
                    'reason': f"Zero overlap with expected keywords for Topic {topic_num}."
                })
                
            # Check for duplicates
            # simplify question for comparison
            sim_q = re.sub(r'[^a-z0-9]', '', q_lower)
            if sim_q in questions_seen:
                duplicates.append({
                    'topic': topic,
                    'question': question_text,
                    'duplicate_of': questions_seen[sim_q]
                })
            else:
                questions_seen[sim_q] = {'topic': topic, 'question': question_text}

    report = ["# Content Audit Report\n\n## Summary\n\n| Topic | Question Count |\n|---|---|"]
    for t, c in sorted(topic_counts.items()):
        report.append(f"| {t} | {c} |")
        
    report.append("\n## Flagged Mismatched Questions\n")
    if not flagged:
        report.append("No mismatched questions found.")
    else:
        for f in flagged:
            report.append(f"**Topic**: {f['topic']}\n**Question**: {f['question']}\n**Reason**: {f['reason']}\n---")
            
    report.append("\n## Duplicate Questions\n")
    if not duplicates:
        report.append("No duplicate questions found.")
    else:
        for d in duplicates:
            report.append(f"**Topic**: {d['topic']}\n**Question**: {d['question']}\n**Duplicate of Topic**: {d['duplicate_of']['topic']}\n---")
            
    with open("audit_out.txt", "w", encoding='utf-8') as f:
        f.write('\n'.join(report))
    print("Done")

if __name__ == "__main__":
    main()
