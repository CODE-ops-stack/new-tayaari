import json

with open("/app/applet/classified_report.json", "r") as f:
    report = json.load(f)

print("### Task 1: Fresh Content-Based Classification")
print("All 134 UPSC-Prelims questions have been re-classified into the 45-topic taxonomy based on their actual subject matter using their true PDF sequence positions (1–134).\n")

total = 0
for topic in sorted(report.keys()):
    print(f"**{topic}**")
    for fmt in sorted(report[topic].keys()):
        for tier in sorted(report[topic][fmt].keys()):
            seqs = report[topic][fmt][tier]
            seq_str = ", ".join(map(str, sorted(seqs)))
            print(f"- Format: {fmt} | Tier: {tier}")
            print(f"  > Questions: {seq_str}")
            total += len(seqs)
    print("")

print(f"\nTotal reclassified: {total}")
