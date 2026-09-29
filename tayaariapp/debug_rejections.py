import json
from full_discovery_pipeline import CorpusMiner
miner = CorpusMiner(["source-material/geography_extracted.txt", "source-material/supplementary_corpus.txt"])
nodes, rejected = miner.discover_nodes()
for r in rejected:
    print(r["reason"], " | ", r["sentence"][:80])
