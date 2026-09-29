import re

sentences = [
    "Pastoral farming involves livestock, while dairy farming focuses on milk production.",
    "Bhabar is a narrow belt near the Shiwalik foothills, while the Terai lies south of it.",
    "Fog reduces visibility to less than one kilometer, while mist reduces visibility to one to two kilometers.",
    "The Chota Nagpur plateau comprises immense reserves of metallic minerals.",
    "The phenomenon of seasons is due to the revolution of earth around the sun."
]

for s in sentences:
    print(f"--- {s}")
    
    # 1. Comparison
    m_comp = re.match(r'^([A-Z][a-zA-Z\s]+)\s+(is|are|involves|reduces|has|produces|affects)\s+(.*?),?\s+(while|whereas)\s+([a-zA-Z\s]+)\s+(is|are|involves|reduces|has|produces|affects|lies|focuses)\s+(.*)', s)
    if m_comp:
        print("MATCHED COMPARISON:")
        print(f"Subj X: {m_comp.group(1)}")
        print(f"Pred X: {m_comp.group(2)} {m_comp.group(3)}")
        print(f"Subj Y: {m_comp.group(5)}")
        print(f"Pred Y: {m_comp.group(6)} {m_comp.group(7)}")
        continue
        
    # 2. Definition
    m_def = re.match(r'^([A-Z][a-zA-Z\s]+)\s+(is known as|refers to|comprises|consists of)\s+(.*)', s)
    if m_def:
        print("MATCHED DEFINITION:")
        print(f"Subj: {m_def.group(1)}")
        print(f"Def: {m_def.group(3)}")
        continue
        
    # 3. Cause Effect (due to)
    m_ce = re.match(r'^([A-Z][a-zA-Z\s]+)\s+(is due to|occurs because of)\s+(.*)', s)
    if m_ce:
        print("MATCHED CAUSE-EFFECT:")
        print(f"Effect: {m_ce.group(1)}")
        print(f"Cause: {m_ce.group(3)}")
        continue
        
    print("NO MATCH")
