import shutil
import difflib
import time

file_path = "c:/Users/harsh/Downloads/tayaari/tayaariapp/app/src/main/assets/consolidated_grounding.md"
backup_path = file_path + ".bak"

print("Starting processing...")
shutil.copy2(file_path, backup_path)

with open(file_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
i = 0
n = len(lines)

reassignments = {
    "Q617": "35. Transport and Communication",
    "Q510": "43. Transport and Communication (India)",
    "Q95": "21. Movements of Ocean Water",
    "Q848": "37. Population: Distribution, Density, Growth and Composition",
    "Q659": "37. Population: Distribution, Density, Growth and Composition",
    "Q723": "37. Population: Distribution, Density, Growth and Composition",
    "Q767": "15. Composition and Structure of Atmosphere",
    "Q893": "13. Geomorphic Processes",
    "Q883": "28. Natural Hazards and Disasters",
}

questions_seen = []
duplicates_removed = 0
reassigned_count = 0

out_lines = []

def is_similar(q1, q2):
    l1, l2 = len(q1), len(q2)
    if l1 == 0 or l2 == 0:
        return l1 == l2
    if min(l1, l2) / max(l1, l2) < 0.8:
        return False
    sm = difflib.SequenceMatcher(None, q1, q2)
    if sm.quick_ratio() > 0.9:
        return sm.ratio() > 0.9
    return False

start_time = time.time()

while i < n:
    if lines[i].startswith("- **Topic**:"):
        block_start = i
        question_start = -1
        first_ticks = -1
        second_ticks = -1
        
        j = i
        while j < n:
            if lines[j].startswith("- **Question**:"):
                question_start = j
            elif lines[j].strip() == "```" and question_start != -1:
                if first_ticks == -1:
                    first_ticks = j
                else:
                    second_ticks = j
                    break
            # if we encounter another topic before second ticks, this block is broken. Break out
            elif j > i and lines[j].startswith("- **Topic**:"):
                break
            j += 1
            
        if second_ticks != -1:
            block_lines = lines[i:second_ticks+1]
            q_text_lines = lines[first_ticks+1:second_ticks]
            q_text = "".join(q_text_lines).strip()
            
            q_num = None
            for key in reassignments:
                if q_text.startswith(key + ".") or q_text.startswith(key + " "):
                    q_num = key
                    break
            
            if q_num and reassignments[q_num] not in block_lines[0]:
                block_lines[0] = f"- **Topic**: {reassignments[q_num]}\n"
                reassigned_count += 1
                
            is_dup = False
            for seen_q in questions_seen:
                if is_similar(q_text, seen_q):
                    is_dup = True
                    break
            
            if is_dup:
                duplicates_removed += 1
            else:
                questions_seen.append(q_text)
                out_lines.extend(block_lines)
            
            i = second_ticks + 1
            continue
            
    out_lines.append(lines[i])
    i += 1

with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(out_lines)

print(f"Duplicates removed: {duplicates_removed}")
print(f"Questions reassigned: {reassigned_count}")
print(f"Time taken: {time.time() - start_time:.2f} seconds")
