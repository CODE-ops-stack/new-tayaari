import json

for f in ['staging_batch_1.json', 'staging_batch_2.json', 'staging_production_v1.json']:
    try:
        d = json.load(open(f, encoding='utf-8-sig'))
        qs = d.get('questions', [])
        print(f"{f}: questions count = {len(qs)}")
        if qs:
            meta = qs[0].get('metadata', {})
            print(f"   Sample: ID={qs[0].get('questionId')} | Demand={meta.get('cognitiveDemand')} | Topic={meta.get('topic')}")
            print(f"   Stem: {qs[0].get('text')}")
    except Exception as e:
        print(f"Error reading {f}: {e}")
