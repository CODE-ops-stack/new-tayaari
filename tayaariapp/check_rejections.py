from advanced_discovery_pipeline import AdvancedCorpusMiner
import glob
sources = glob.glob("source-material/*.txt")
miner = AdvancedCorpusMiner(sources)
nodes, rejected = miner.discover_nodes()
reason_counts = {}
for r in rejected:
    reason_counts[r["reason"]] = reason_counts.get(r["reason"], 0) + 1
for k,v in reason_counts.items():
    print(k, ":", v)
