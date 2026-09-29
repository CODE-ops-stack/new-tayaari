import json
import re

with open("source-material/extracted_ssc_qs.json", "r") as f:
    extracted_qs = json.load(f)

with open("source-material/consolidated_grounding.md", "r") as f:
    md_content = f.read()

def process_batch(start_q, end_q):
    blocks = re.split(r"\n## (?=\d+\. )", "\n" + md_content)
    new_blocks = [blocks[0]]
    
    extracted_count = 0
    
    for i in range(1, len(blocks)):
        block = blocks[i]
        topic_name = re.match(r"^(\d+\. [^\n]+)", block).group(1)
        
        ssc_idx = block.find("### SSC Stenographer Data")
        if ssc_idx == -1:
            new_blocks.append(block)
            continue
            
        upsc_part = block[:ssc_idx]
        ssc_part = block[ssc_idx:]
        
        new_ssc_part = "### SSC Stenographer Data (925-Question Set)\n"
        
        lines = ssc_part.split("\n")
        current_tags = ""
        
        for idx, line in enumerate(lines):
            if line.startswith("- **Format Type**"):
                current_tags = line
            elif line.startswith("  > Questions:"):
                ids = [x.strip() for x in line.replace("  > Questions:", "").split(",")]
                
                tier = re.search(r"\*\*Tier\*\*: (.*?) \|", current_tags).group(1)
                fmt = re.search(r"\*\*Format Type\*\*: (.*?) \|", current_tags).group(1)
                rel = re.search(r"\*\*Exam-Relevance\*\*: (.*?) \|", current_tags).group(1)
                src = re.search(r"\*\*Source\*\*: (.*?) \|", current_tags).group(1)
                exam = re.search(r"\*\*Specific-Exam\*\*: (.*?)$", current_tags).group(1)
                
                unextracted_ids = []
                
                for q_id in ids:
                    q_num_int = int(q_id)
                    if start_q <= q_num_int <= end_q and q_id in extracted_qs:
                        q_data = extracted_qs[q_id]
                        new_ssc_part += f"\n- **Topic**: {topic_name}\n"
                        new_ssc_part += f"- **Tier**: {tier}\n"
                        new_ssc_part += f"- **Format**: {fmt}\n"
                        new_ssc_part += f"- **Exam-Relevance**: {rel}\n"
                        new_ssc_part += f"- **Source**: {src}\n"
                        new_ssc_part += f"- **Specific-Exam**: {exam}\n"
                        new_ssc_part += f"- **PDF-Sequence-Number**: {q_id}\n"
                        
                        opts = q_data['options']
                        opts_str = f"a) {opts['a']}\nb) {opts['b']}\nc) {opts['c']}\nd) {opts['d']}"
                        
                        formatted = f"- **Question**:\n```\nQ{q_id}. {q_data['questionText']}\n{opts_str}\nCorrect answer: option {q_data['correctAnswer']}\n```\n"
                        new_ssc_part += formatted
                        extracted_count += 1
                    else:
                        unextracted_ids.append(q_id)
                
                if unextracted_ids:
                    # Append remaining IDs in old format
                    new_ssc_part += f"\n{current_tags}\n  > Questions: {', '.join(unextracted_ids)}\n"
            elif line.strip() and not line.startswith("### SSC"):
                # keep other stuff?
                pass
                
        new_blocks.append(upsc_part + new_ssc_part)

    with open("source-material/consolidated_grounding.md", "w") as f:
        f.write("\n## ".join(new_blocks).replace("\n## \n## ", "\n## ").strip() + "\n")
        
    print(f"Extracted {extracted_count} questions")

process_batch(1, 200)
