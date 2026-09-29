import json
import re

with open("/app/applet/classified_questions.json", "r") as f:
    questions = json.load(f)

# The questions often have multiple 'Q1.', 'Q2.', etc. inside the text.
# We will split text based on Q[0-9]+\.
split_questions = []

global_seq_num = 1

for q in questions:
    text = q['text'].strip()
    
    # Split text by Q followed by number and dot
    # Use re.split to keep the delimiters or findall
    
    # Let's find all questions inside
    matches = list(re.finditer(r'(Q\d+\.)', text))
    
    if not matches:
        # No explicit Q1. found, maybe just one question
        split_q = q.copy()
        split_q['text'] = text
        split_q['seq_num'] = global_seq_num
        global_seq_num += 1
        split_questions.append(split_q)
    else:
        for i, match in enumerate(matches):
            start = match.start()
            if i + 1 < len(matches):
                end = matches[i+1].start()
            else:
                end = len(text)
                
            q_text = text[start:end].strip()
            
            # Create a new question object
            split_q = q.copy()
            split_q['text'] = q_text
            split_q['seq_num'] = global_seq_num
            global_seq_num += 1
            
            # Special case for sugar industry
            if "by-products of sugar industry" in q_text:
                split_q['new_topic'] = "39. Land Resources and Agriculture"
            elif "length of daytime and nighttime" in q_text:
                split_q['new_topic'] = "3. Motions of the Earth"
            
            # Automatically assign Format and Tier based on the text
            # Recompute format and tier
            if "Consider the following statements" in q_text or "Which of the following statements" in q_text or "Which of the statements given above" in q_text or "How many of the statements" in q_text:
                fmt = "Statement-based"
                tier = "Medium"
            elif "Consider the following pairs" in q_text or "How many of the above pairs" in q_text:
                fmt = "Matching Pairs"
                tier = "Medium"
            elif "Assertion" in q_text and "Reason" in q_text or "Statement-I" in q_text and "Statement-II" in q_text:
                fmt = "Assertion-Reason"
                tier = "Advanced"
            else:
                fmt = "Direct Fact"
                tier = "Basic"
                
            split_q['format'] = fmt
            split_q['tier'] = tier
            
            split_questions.append(split_q)

print(f"Total split questions: {len(split_questions)}")

with open("split_questions.json", "w") as f:
    json.dump(split_questions, f, indent=2)

